#!/bin/sh
set -eu
PYTHON=${PYTHON:-python3}
"$PYTHON" -m pip install -e .
acr-evidence build --manifest config/drupal-core-example.json --issues tests/fixtures/issues.json --output site
"$PYTHON" -m http.server 8000 --directory site
