#! /usr/bin/env bash

set -xeuo pipefail

# Start Gunicorn
exec \
  uvicorn \
  --reload \
  --bind 0.0.0.0:8000 \
  --log-level "${LOG_LEVEL}" \
  webapp:app
