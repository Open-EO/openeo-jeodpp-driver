#!/usr/bin/env bash
#

set -xeuo pipefail

psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB}" <<-EOSQL
    CREATE EXTENSION pgcrypto; CREATE EXTENSION "uuid-ossp";
EOSQL
