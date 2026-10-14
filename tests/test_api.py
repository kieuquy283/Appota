"""Unit tests for FastAPI endpoints in api/index.py."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.index import app
from src.store import load_seed


class ApiEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.seed = load_seed()

    def setUp(self):
        config_patch = patch("src.service.load_config")
        env_patch = patch.dict("os.environ", {"LLM_API_KEY": "", "OPENAI_API_KEY": "", "EMBEDDING_MODEL": ""})
        config_patch.start()
        env_patch.start()
        self.addCleanup(config_patch.stop)
        self.addCleanup(env_patch.stop)

    def test_health_check(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "ok")

    def test_list_demo_users_sanitized(self):
        res = self.client.get("/users")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(len(data), 1)

        # Ensure only public fields are exposed and no internal flags/secrets leak
        allowed_keys = {"user_id", "name", "company", "department", "team", "role", "employment_type"}
        for user in data:
            self.assertTrue(set(user.keys()).issubset(allowed_keys))
            self.assertIn("user_id", user)
            self.assertIn("name", user)
            self.assertNotIn("active", user)
            self.assertNotIn("level", user)

    def test_answer_different_users_yield_different_results(self):
        # U01 is Alpha (Holding), U03 is Gamma (Fintech)
        res_u01 = self.client.post("/answer", json={"user_id": "U01", "question": "Tôi có bao nhiêu ngày nghỉ phép?"})
        self.assertEqual(res_u01.status_code, 200)
        data_u01 = res_u01.json()
        self.assertEqual(data_u01["status"], "ANSWER")
        self.assertIn("15", data_u01["answer"])

        res_u03 = self.client.post("/answer", json={"user_id": "U03", "question": "Tôi có bao nhiêu ngày nghỉ phép?"})
        self.assertEqual(res_u03.status_code, 200)
        data_u03 = res_u03.json()
        self.assertEqual(data_u03["status"], "ANSWER")
        self.assertIn("12", data_u03["answer"])

        # Answers and citations must differ
        self.assertNotEqual(data_u01["answer"], data_u03["answer"])
        u01_titles = [c["title"] for c in data_u01["citations"]]
        u03_titles = [c["title"] for c in data_u03["citations"]]
        self.assertNotEqual(u01_titles, u03_titles)

    def test_answer_response_contract_no_leaks(self):
        res = self.client.post("/answer", json={"user_id": "U01", "question": "Tôi có bao nhiêu ngày nghỉ phép?"})
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # Check top-level contract
        self.assertIn("status", data)
        self.assertIn("answer", data)
        self.assertIn("citations", data)
        self.assertNotIn("trace", data)

        # Check citations contract
        self.assertGreater(len(data["citations"]), 0)
        for c in data["citations"]:
            self.assertIn("title", c)
            self.assertIn("section", c)
            self.assertIn("excerpt", c)
            self.assertNotIn("document_id", c)
            self.assertNotIn("version", c)

    def test_empty_question_rejected(self):
        res = self.client.post("/answer", json={"user_id": "U01", "question": "   "})
        self.assertEqual(res.status_code, 400)

    def test_unknown_user_rejected(self):
        res = self.client.post("/answer", json={"user_id": "NON_EXISTENT_999", "question": "Chính sách nghỉ phép?"})
        self.assertEqual(res.status_code, 404)

    def test_internal_secret_key_protection(self):
        with patch.dict("os.environ", {"INTERNAL_API_SECRET": "secret-12345"}):
            # Unauthorized call without header
            res_no_key = self.client.post("/answer", json={"user_id": "U01", "question": "Nghỉ phép?"})
            self.assertEqual(res_no_key.status_code, 401)

            # Unauthorized call with wrong header
            res_wrong_key = self.client.post(
                "/answer",
                json={"user_id": "U01", "question": "Nghỉ phép?"},
                headers={"x-internal-key": "wrong-key"},
            )
            self.assertEqual(res_wrong_key.status_code, 401)

            # Authorized call with correct header
            res_auth = self.client.post(
                "/answer",
                json={"user_id": "U01", "question": "Nghỉ phép?"},
                headers={"x-internal-key": "secret-12345"},
            )
            self.assertEqual(res_auth.status_code, 200)
