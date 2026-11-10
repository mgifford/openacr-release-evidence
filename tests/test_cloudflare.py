import json
import unittest
from unittest.mock import patch

from acr_evidence.ai import CloudflareChatClient, CloudflareError


class _Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, _limit=None):
        return json.dumps(self.payload).encode()


class CloudflareClientTests(unittest.TestCase):
    def test_chat_completion_uses_workers_ai_endpoint(self):
        seen = {}

        def fake_urlopen(request, timeout=None):
            seen["url"] = request.full_url
            seen["body"] = json.loads(request.data)
            seen["auth"] = request.get_header("Authorization")
            return _Response({"result": {"response": "A short barrier summary."}})

        client = CloudflareChatClient("account123", "token123", "@cf/meta/llama-3.1-8b-instruct")
        with patch("acr_evidence.ai.urlopen", fake_urlopen):
            response = client.chat_completion([{"role": "user", "content": "test"}], max_tokens=200)
        self.assertEqual("A short barrier summary.", response.choices[0].message.content)
        self.assertIn("/accounts/account123/ai/run/@cf/meta/llama-3.1-8b-instruct", seen["url"])
        self.assertEqual("Bearer token123", seen["auth"])
        self.assertEqual(200, seen["body"]["max_tokens"])

    def test_missing_credentials_are_rejected(self):
        with self.assertRaises(CloudflareError):
            CloudflareChatClient("", "", "@cf/meta/llama-3.1-8b-instruct")

    def test_non_workers_model_is_rejected(self):
        with self.assertRaises(CloudflareError):
            CloudflareChatClient("account123", "token", "meta-llama/Llama-3.1-8B-Instruct")


if __name__ == "__main__":
    unittest.main()
