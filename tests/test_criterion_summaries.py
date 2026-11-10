import json
import tempfile
import unittest
from pathlib import Path

from acr_evidence.criterion_summaries import summarize_collection


def collection():
    return {
        "issues": [
            {
                "id": "drupal:1",
                "title": "Image alternative text is missing in the media widget",
                "status": {"label": "Active"},
                "evidence_status": "full",
                "surface": {"surface": "authoring"},
                "description_text": "Authors can insert an image without a text alternative.",
                "wcag_candidates": ["1.1.1"],
            },
            {
                "id": "drupal:2",
                "title": "Decorative images are announced",
                "status": {"label": "Needs work"},
                "evidence_status": "inventory",
                "surface": {"surface": "web"},
                "wcag_candidates": ["1.1.1"],
            },
        ]
    }


class Response:
    class Choice:
        class Message:
            content = json.dumps({
                "web": "Public pages may announce decorative images that should be ignored.",
                "authoring": "Authors may be able to add images without a text alternative.",
            })

        message = Message()

    choices = [Choice()]


class Client:
    def __init__(self):
        self.calls = 0

    def chat_completion(self, **kwargs):
        self.calls += 1
        return Response()


class CriterionSummaryTests(unittest.TestCase):
    def test_summary_is_cached_and_reused(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "acr-summaries.json"
            client = Client()
            first = summarize_collection(
                collection(), output, model="org/model", token="test",
                client_factory=lambda **kwargs: client,
            )
            self.assertEqual("accepted", first["criteria"]["1.1.1"]["status"])
            self.assertEqual(1, client.calls)
            second = summarize_collection(
                collection(), output, model="org/model", token="test",
                client_factory=lambda **kwargs: (_ for _ in ()).throw(AssertionError("should reuse")),
            )
            self.assertEqual("accepted", second["criteria"]["1.1.1"]["status"])

    def test_json_with_trailing_prose_is_accepted(self):
        class ProseClient:
            def chat_completion(self, **kwargs):
                class Message:
                    content = '{"web": "Users may miss decorative-image semantics.", "authoring": "Authors may lack a clear alt-text prompt."}\n\nExplanation follows.'
                class Choice:
                    message = Message()
                class Response:
                    choices = [Choice()]
                return Response()

        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "acr-summaries.json"
            result = summarize_collection(
                collection(), output, model="org/model", token="test",
                client_factory=lambda **kwargs: ProseClient(),
            )
            self.assertEqual("accepted", result["criteria"]["1.1.1"]["status"])

    def test_cloudflare_provider_uses_client(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "acr-summaries-cloudflare.json"
            result = summarize_collection(
                collection(), output, provider="cloudflare",
                model="@cf/meta/llama-3.1-8b-instruct", token="test",
                account_id="account123", client_factory=lambda **kwargs: Client(),
            )
            self.assertEqual("accepted", result["criteria"]["1.1.1"]["status"])
            self.assertEqual("cloudflare", result["criteria"]["1.1.1"]["provider"])

    def test_invalid_response_is_rejected(self):
        class BadClient:
            def chat_completion(self, **kwargs):
                class Message:
                    content = json.dumps({"web": "There are 99 active issues.", "authoring": "No issue."})
                class Choice:
                    message = Message()
                class Response:
                    choices = [Choice()]
                return Response()

        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "acr-summaries.json"
            result = summarize_collection(
                collection(), output, model="org/model", token="test",
                client_factory=lambda **kwargs: BadClient(),
            )
            self.assertEqual("rejected", result["criteria"]["1.1.1"]["status"])


if __name__ == "__main__":
    unittest.main()
