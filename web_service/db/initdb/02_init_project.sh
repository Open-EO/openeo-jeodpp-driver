#!/usr/bin/env bash
#

# https://stackoverflow.com/q/2951875
# https://stackoverflow.com/a/22183640

set -xeuo pipefail

# Create schema
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB}" <<-EOSQL
    CREATE SCHEMA "${PROJECT_NAME}";
EOSQL

# Create application user, grant USAGE on the schema and set the SEARCH Path
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB}" <<-EOSQL
    CREATE USER ${DB_PROJECT_USER} WITH ENCRYPTED PASSWORD '${DB_PROJECT_PASS}';
    GRANT USAGE ON SCHEMA "${PROJECT_NAME}" TO ${DB_PROJECT_USER};
    ALTER ROLE ${DB_PROJECT_USER} SET search_path = ${PROJECT_NAME},public;
EOSQL

# Grant priviledges to the user
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB}" <<-EOSQL
    ALTER DEFAULT PRIVILEGES FOR ROLE ${POSTGRES_USER} IN SCHEMA ${PROJECT_NAME} GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ${DB_PROJECT_USER};
    ALTER DEFAULT PRIVILEGES FOR ROLE ${POSTGRES_USER} IN SCHEMA ${PROJECT_NAME} GRANT SELECT, USAGE ON SEQUENCES TO ${DB_PROJECT_USER};
    ALTER DEFAULT PRIVILEGES FOR ROLE ${POSTGRES_USER} IN SCHEMA ${PROJECT_NAME} GRANT EXECUTE ON FUNCTIONS TO ${DB_PROJECT_USER};
EOSQL

# NOTE
# We don't need a GRANT on all tables/sequences etc because we don't have any tables yet.
#     GRANT SELECT, UPDATE ON ALL TABLES IN SCHEMA public TO restricted_user;
