import html
import unittest
from datetime import date
from unittest.mock import patch, MagicMock

from src.models import AnswerResult, Citation
from src.service import answer_question, list_demo_users
from src.store import load_seed
import app


class ChatCitationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = load_seed()

    def setUp(self):
        # Reset session state mock for app tests
        app.st.session_state = {
            "chat_messages": [],
            "current_user_id": None,
            "pending_prompt": None,
        }

    def test_multi_turn_history_order_preserved(self):
        """Test sending multiple queries preserves order and isolates citations."""
        app.submit_question("Tôi có bao nhiêu ngày nghỉ phép?", "U01")
        app.submit_question("Tôi được WFH mấy ngày?", "U01")

        messages = app.st.session_state["chat_messages"]
        self.assertEqual(len(messages), 4)

        # First turn
        self.assertEqual(messages[0]["role"], "user")
        self.assertIn("nghỉ phép", messages[0]["content"])
        self.assertEqual(messages[1]["role"], "assistant")
        self.assertEqual(messages[1]["status"], "ANSWER")
        self.assertEqual([c.document_id for c in messages[1]["citations"]], ["ALPHA-LEAVE"])

        # Second turn
        self.assertEqual(messages[2]["role"], "user")
        self.assertIn("WFH", messages[2]["content"])
        self.assertEqual(messages[3]["role"], "assistant")
        self.assertEqual(messages[3]["status"], "ANSWER")
        self.assertEqual([c.document_id for c in messages[3]["citations"]], ["ALPHA-WFH-POLICY"])

        # Citations are distinct and not merged
        self.assertNotEqual(messages[1]["citations"], messages[3]["citations"])

    def test_citations_strictly_bounded_to_llm_context(self):
        """Verify that every citation in an ANSWER status matches guarded LLM context."""
        result = answer_question("U01", "Tôi có bao nhiêu ngày nghỉ phép?", seed=self.seed)
        self.assertEqual(result.status, "ANSWER")
        self.assertTrue(result.citations)

        llm_docs = set(result.trace["llm_context_document_ids"])
        llm_vers = set(result.trace["llm_context_version_ids"])

        for c in result.citations:
            self.assertIn(c.document_id, llm_docs)
            self.assertIn(c.version, llm_vers)

    def test_user_context_citation_isolation(self):
        """Alice (U01) and Carol (U03) querying same question receive company-specific citations."""
        app.submit_question("Tôi có bao nhiêu ngày nghỉ phép?", "U01")
        alice_msg = app.st.session_state["chat_messages"][-1]

        # Reset for Carol to simulate switching context
        app.reset_conversation()
        self.assertEqual(len(app.st.session_state["chat_messages"]), 0)

        app.submit_question("Tôi có bao nhiêu ngày nghỉ phép?", "U03")
        carol_msg = app.st.session_state["chat_messages"][-1]

        self.assertEqual(alice_msg["citations"][0].document_id, "ALPHA-LEAVE")
        self.assertEqual(carol_msg["citations"][0].document_id, "NOVA-LEAVE")
        self.assertIn("15", alice_msg["content"])
        self.assertIn("12", carol_msg["content"])

    def test_abstain_status_no_false_citations(self):
        """ABSTAIN produces missing_evidence reason and no fabricated citations."""
        app.submit_question("Tôi có được WFH thứ Sáu không?", "U01")
        last_msg = app.st.session_state["chat_messages"][-1]

        self.assertEqual(last_msg["status"], "ABSTAIN")
        self.assertEqual(len(last_msg["citations"]), 0)
        self.assertEqual(last_msg["reason"], "missing_evidence")

    def test_conflict_status_lists_conflicting_citations(self):
        """CONFLICT status provides citations of both conflicting equal-authority documents."""
        app.submit_question("Tôi được WFH mấy ngày?", "U03")
        last_msg = app.st.session_state["chat_messages"][-1]

        self.assertEqual(last_msg["status"], "CONFLICT")
        self.assertEqual(len(last_msg["citations"]), 2)
        doc_ids = {c.document_id for c in last_msg["citations"]}
        self.assertEqual(doc_ids, {"NOVA-WFH-POLICY-A", "NOVA-WFH-POLICY-B"})

    def test_reset_conversation(self):
        """Calling reset_conversation wipes messages without residue."""
        app.submit_question("Tôi có bao nhiêu ngày nghỉ phép?", "U01")
        self.assertEqual(len(app.st.session_state["chat_messages"]), 2)

        app.reset_conversation()
        self.assertEqual(app.st.session_state["chat_messages"], [])
        self.assertIsNone(app.st.session_state["pending_prompt"])

    def test_user_switch_clears_history_automatically(self):
        """Simulate user selector changing user ID triggers reset_conversation."""
        app.st.session_state["current_user_id"] = "U01"
        app.submit_question("Tôi có bao nhiêu ngày nghỉ phép?", "U01")
        self.assertEqual(len(app.st.session_state["chat_messages"]), 2)

        # Mock streamlit sidebar widgets to return Carol (U03)
        users = list_demo_users()
        carol = next(u for u in users if u["user_id"] == "U03")
        with patch.object(app.st.sidebar, "selectbox", return_value=app.format_user_label(carol)):
            selected = app.render_sidebar(users)

        self.assertEqual(selected["user_id"], "U03")
        self.assertEqual(app.st.session_state["current_user_id"], "U03")
        self.assertEqual(len(app.st.session_state["chat_messages"]), 0)

    def test_error_handling_preserves_previous_messages(self):
        """An error during processing adds an ERROR message without losing history."""
        app.submit_question("Tôi có bao nhiêu ngày nghỉ phép?", "U01")
        self.assertEqual(len(app.st.session_state["chat_messages"]), 2)

        with patch("app.answer_question", side_effect=RuntimeError("Simulated backend failure")):
            app.submit_question("Câu hỏi gây lỗi", "U01")

        messages = app.st.session_state["chat_messages"]
        self.assertEqual(len(messages), 4)
        self.assertEqual(messages[0]["content"], "Tôi có bao nhiêu ngày nghỉ phép?")
        self.assertEqual(messages[2]["content"], "Câu hỏi gây lỗi")
        self.assertEqual(messages[3]["status"], "ERROR")
        self.assertIn("Simulated backend failure", messages[3]["content"])

    def test_html_escaping_safety(self):
        """Ensure malicious HTML/script injections are escaped."""
        evil_input = "<script>alert('pwned')</script><b>Bold</b>"
        escaped = html.escape(evil_input)
        self.assertNotIn("<script>", escaped)
        self.assertIn("&lt;script&gt;", escaped)

        # Check render_status escapes answer text
        msg = {
            "status": "ANSWER",
            "content": evil_input,
            "reason": None,
        }
        with patch.object(app.st, "markdown") as mock_md:
            app.render_status(msg)
            rendered_html = mock_md.call_args[0][0]
            self.assertNotIn("<script>", rendered_html)
            self.assertIn("&lt;script&gt;", rendered_html)

    def test_inline_citation_format(self):
        """Verify inline citation [1] is attached in offline extractive answer."""
        result = answer_question("U01", "Tôi có bao nhiêu ngày nghỉ phép?", seed=self.seed)
        self.assertTrue(result.answer.endswith("[1]"))


if __name__ == "__main__":
    unittest.main()
