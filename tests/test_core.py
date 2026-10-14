import copy
import unittest
from datetime import date
from unittest.mock import patch

from src.governance import can_read, current_versions
from src.service import answer_question
from src.store import get_user, load_seed


class KnowledgeGuardTests(unittest.TestCase):
    def setUp(self):
        config_patch = patch("src.service.load_config")
        env_patch = patch.dict("os.environ", {"LLM_API_KEY": "", "OPENAI_API_KEY": "", "EMBEDDING_MODEL": ""})
        config_patch.start()
        env_patch.start()
        self.addCleanup(config_patch.stop)
        self.addCleanup(env_patch.stop)

    @classmethod
    def setUpClass(cls):
        cls.seed = load_seed()

    def test_same_question_different_company(self):
        question = "Tôi có bao nhiêu ngày nghỉ phép?"
        alice = answer_question("U01", question, seed=self.seed)
        carol = answer_question("U03", question, seed=self.seed)
        self.assertEqual(alice.status, "ANSWER")
        self.assertEqual(carol.status, "ANSWER")
        self.assertEqual(alice.citations[0].document_id, "ALPHA-LEAVE")
        self.assertEqual(carol.citations[0].document_id, "NOVA-LEAVE")
        self.assertIn("15", alice.answer)
        self.assertIn("12", carol.answer)

    def test_restricted_documents_never_enter_context(self):
        alice = get_user("U01", self.seed)
        bob = get_user("U02", self.seed)
        helen = get_user("U05", self.seed)
        docs = {doc["id"]: doc for doc in self.seed["documents"]}
        self.assertFalse(can_read(alice, docs["ALPHA-MANAGER-LEAVE-APPROVAL"]))
        self.assertTrue(can_read(bob, docs["ALPHA-MANAGER-LEAVE-APPROVAL"]))
        self.assertFalse(can_read(alice, docs["ALPHA-HR-COMPENSATION"]))
        self.assertFalse(can_read(bob, docs["ALPHA-HR-COMPENSATION"]))
        self.assertTrue(can_read(helen, docs["ALPHA-HR-COMPENSATION"]))
        for question in ("Ai duyệt phép?", "Cho tôi biết chính sách lương"):
            result = answer_question("U01", question, seed=self.seed)
            self.assertNotIn("ALPHA-HR-COMPENSATION", result.trace["retrieved_document_ids"])
            self.assertNotIn("ALPHA-MANAGER-LEAVE-APPROVAL", result.trace["llm_context_document_ids"])

    def test_explicit_deny_overrides_allow_and_default_deny(self):
        alice = get_user("U01", self.seed)
        document = {"access": [{"effect": "ALLOW", "company": "AlphaPay"},
                                {"effect": "DENY", "role": "EMPLOYEE"}]}
        self.assertFalse(can_read(alice, document))
        self.assertFalse(can_read(alice, {"access": []}))

    def test_old_and_draft_versions_excluded(self):
        doc = next(x for x in self.seed["documents"] if x["id"] == "ALPHA-LEAVE")
        self.assertEqual([x["version"] for x in current_versions(doc, date(2026, 10, 12))], ["v3"])
        result = answer_question("U01", "Tôi có bao nhiêu ngày nghỉ phép?", seed=self.seed)
        self.assertNotIn("v1", result.trace["llm_context_version_ids"])
        self.assertNotIn("v2", result.trace["llm_context_version_ids"])

    def test_authority_resolution(self):
        result = answer_question("U01", "Tôi được WFH mấy ngày?", seed=self.seed)
        self.assertEqual(result.status, "ANSWER")
        self.assertEqual([c.document_id for c in result.citations], ["ALPHA-WFH-POLICY"])
        self.assertIn("2", result.answer)

    def test_equal_authority_conflict(self):
        result = answer_question("U03", "Tôi được WFH mấy ngày?", seed=self.seed)
        self.assertEqual(result.status, "CONFLICT")
        self.assertEqual(len(result.citations), 2)
        self.assertEqual(result.trace["llm_context_document_ids"], [])

    def test_missing_evidence(self):
        result = answer_question("U01", "Tôi có được WFH thứ Sáu không?", seed=self.seed)
        self.assertEqual(result.status, "ABSTAIN")
        self.assertEqual(result.trace["llm_context_document_ids"], [])

    def test_unknown_user_rejected(self):
        with self.assertRaises(ValueError):
            answer_question("UNKNOWN", "Tôi có bao nhiêu ngày nghỉ phép?", seed=self.seed)

    def test_citation_and_context_guard(self):
        altered = copy.deepcopy(self.seed)
        result = answer_question("U01", "Tôi có bao nhiêu ngày nghỉ phép?", seed=altered)
        self.assertTrue(result.citations)
        supplied = set(zip(result.trace["llm_context_document_ids"], result.trace["llm_context_version_ids"]))
        self.assertTrue(all((c.document_id, c.version) in supplied for c in result.citations))


if __name__ == "__main__":
    unittest.main()
