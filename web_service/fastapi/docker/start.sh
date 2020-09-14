#! /usr/bin/env bash
set -xeuo pipefail

# Start uvicorn
exec \
  uvicorn \
  --bind 0.0.0.0:8000 \
  --log-level "${LOG_LEVEL}" \
  webapp:app

