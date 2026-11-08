import unittest
from unittest.mock import patch

from acr_evidence.adapters import http


class Response:
    url = "https://example.test/data.json"

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit):
        return b'{"ok": true}'


class HttpRetryTests(unittest.TestCase):
    def test_retries_timeout_then_succeeds(self):
        with patch("acr_evidence.adapters.http.urlopen", side_effect=[TimeoutError("slow"), Response()]) as opened, patch(
            "acr_evidence.adapters.http.time.sleep"
        ):
            self.assertEqual({"ok": True}, http.fetch_json("https://example.test/data.json", retries=1))
        self.assertEqual(2, opened.call_count)

    def test_does_not_retry_insecure_url(self):
        with self.assertRaises(ValueError):
            http.fetch_json("http://example.test/data.json")


if __name__ == "__main__":
    unittest.main()
