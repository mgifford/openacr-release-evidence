"""Minimal safe HTTPS fetch with retry and byte limits."""
import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

USER_AGENT = "openacr-release-evidence/0.1 (+https://github.com/gsa/openacr; accessibility research)"


def fetch_json(url, headers=None, retries=2):
    if not url.startswith("https://"):
        raise ValueError("HTTPS required")
    h = {"Accept": "application/json", "User-Agent": USER_AGENT, **(headers or {})}
    for attempt in range(retries + 1):
        try:
            req = Request(url, headers=h)
            with urlopen(req, timeout=20) as response:
                if response.url.startswith("http://"):
                    raise ValueError("Insecure redirect")
                payload = response.read(2_000_001)
                if len(payload) > 2_000_000:
                    raise ValueError("Response exceeds 2 MB limit")
                return json.loads(payload)
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retries:
                raise
        except (TimeoutError, URLError):
            if attempt == retries:
                raise
        time.sleep(min(2 ** attempt, 8))
