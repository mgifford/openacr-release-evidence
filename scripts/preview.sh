#!/bin/sh
set -eu
python -m pip install -e .
acr-evidence build --manifest config/drupal-core-example.json --issues tests/fixtures/issues.json --output site
python -m http.server 8000 --directory site
