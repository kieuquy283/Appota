"""The API path is exercised with a fake HTTP response, never a real key."""

from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError
from unittest.mock import patch

from src.config import load_config
from src.retrieval import retrieve
from src.service import answer_question


class LlmConfigurationTests(unittest.TestCase):
    def test_dotenv_loads_local_key_without_overriding_host_environment(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, ".env").write_text(
                "LLM_API_KEY=local-demo-key\nLLM_MODEL=local-demo-model\n", encoding="utf-8"
            )
            with patch("src.config.PROJECT_ROOT", Path(folder)), patch.dict(
                os.environ, {"LLM_MODEL": "host-model"}, clear=True
            ):
                load_config()
                self.assertEqual(os.environ["LLM_API_KEY"], "local-demo-key")
                self.assertEqual(os.environ["LLM_MODEL"], "host-model")

    def test_answer_uses_api_only_after_authorization_and_keeps_citation(self):
        seen = {}

        def fake_urlopen(request, timeout):
            seen["url"] = request.full_url
            seen["authorization"] = request.get_header("Authorization")
            seen["payload"] = json.loads(request.data)
            response = {"choices": [{"message": {"content": json.dumps({
                "answer": "Theo chính sách, bạn có 15 ngày phép [S1].",
                "citation_source_ids": ["S1"],
            })}}]}
            return io.BytesIO(json.dumps(response).encode())

        settings = {
            "LLM_API_KEY": "demo-key", "LLM_MODEL": "demo-model",
            "LLM_BASE_URL": "https://example.invalid/v1", "EMBEDDING_MODEL": "",
        }
        with patch.dict(os.environ, settings), patch("src.llm.request.urlopen", side_effect=fake_urlopen):
            result = answer_question("U01", "Tôi có bao nhiêu ngày nghỉ phép?")

        self.assertEqual(result.status, "ANSWER")
        self.assertEqual(result.trace["generation_mode"], "llm")
        self.assertEqual(seen["url"], "https://example.invalid/v1/chat/completions")
        self.assertEqual(seen["authorization"], "Bearer demo-key")
        self.assertEqual(seen["payload"]["model"], "demo-model")
        evidence = seen["payload"]["messages"][1]["content"]
        self.assertIn("ALPHA-LEAVE", evidence)
        self.assertNotIn("ALPHA-HR-COMPENSATION", evidence)
        self.assertIn("[1]", result.answer)
        self.assertEqual(result.citations[0].document_id, "ALPHA-LEAVE")
        self.assertTrue(result.citations[0].excerpt)

    def test_embedding_uses_openrouter_endpoint_and_short_policy_passage(self):
        calls = []

        def fake_urlopen(req, timeout):
            calls.append((req.full_url, json.loads(req.data)))
            return io.BytesIO(json.dumps({"data": [{"embedding": [1.0, 0.0]}]}).encode())

        long_content = "3. Nghỉ phép: 15 ngày mỗi năm. " + "Quy định bổ sung. " * 200
        source = {"document_id": "AP-LEAVE", "title": "Quy định nghỉ phép", "version": "3",
                  "section": "Nghỉ phép", "topic": "leave_days", "content": long_content}
        settings = {"EMBEDDING_API_KEY": "demo-key", "EMBEDDING_MODEL": "liquid/lfm-2.5-embedding-350m:free",
                    "EMBEDDING_BASE_URL": "https://openrouter.ai/api/v1"}
        with patch.dict(os.environ, settings), patch("src.retrieval.request.urlopen", side_effect=fake_urlopen):
            found = retrieve("Tôi có bao nhiêu ngày nghỉ phép?", [source], "leave_days")

        self.assertEqual(found, [source])
        self.assertEqual(len(calls), 2)
        self.assertTrue(all(url == "https://openrouter.ai/api/v1/embeddings" for url, _ in calls))
        self.assertTrue(all(body["model"] == settings["EMBEDDING_MODEL"] for _, body in calls))
        self.assertLess(len(calls[1][1]["input"]), 800)
        self.assertIn("15 ngày", calls[1][1]["input"])

    def test_chat_falls_back_to_free_model_with_same_authorized_evidence(self):
        calls = []

        def fake_urlopen(req, timeout):
            body = json.loads(req.data)
            calls.append(body)
            if body["model"] in ("primary-model", "google/gemma-4-26b-a4b-it:free"):
                raise HTTPError(req.full_url, 429, "Too Many Requests", {}, None)
            response = {"choices": [{"message": {"content": json.dumps({
                "answer": "Bạn có 15 ngày nghỉ phép [S1].", "source_ids": ["S1"]
            })}}]}
            return io.BytesIO(json.dumps(response).encode())

        settings = {"LLM_API_KEY": "demo-key", "LLM_MODEL": "primary-model",
                    "LLM_FALLBACK_MODELS": "google/gemma-4-26b-a4b-it:free,nvidia/nemotron-3-ultra-550b-a55b:free",
                    "LLM_BASE_URL": "https://example.invalid/v1", "EMBEDDING_MODEL": ""}
        with patch.dict(os.environ, settings), patch("src.llm.request.urlopen", side_effect=fake_urlopen):
            result = answer_question("U01", "Tôi có bao nhiêu ngày nghỉ phép?")

        self.assertEqual([call["model"] for call in calls],
                         ["primary-model", "google/gemma-4-26b-a4b-it:free",
                          "nvidia/nemotron-3-ultra-550b-a55b:free"])
        self.assertEqual(calls[0]["messages"], calls[2]["messages"])
        self.assertNotIn("response_format", calls[2])
        self.assertNotIn("ALPHA-HR-COMPENSATION", calls[2]["messages"][1]["content"])
        self.assertEqual(result.status, "ANSWER")
        self.assertTrue(result.trace["llm_fallback_used"])
        self.assertEqual(result.trace["llm_model"], "nvidia/nemotron-3-ultra-550b-a55b:free")
        self.assertEqual(result.citations[0].document_id, "ALPHA-LEAVE")


if __name__ == "__main__":
    unittest.main()
