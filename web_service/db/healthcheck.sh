#!/bin/bash
#

set -xeuo pipefail

#export PGPASSWORD="${POSTGRES_PASSWORD:-}"

pg_isready \
  --host="${DB_HOST}" \
  --port="${DB_PORT}" \
  --username="${POSTGRES_USER}" \
  --dbname="${POSTGRES_DB}" \
  --timeout=3
