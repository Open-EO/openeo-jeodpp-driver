#!/usr/bin/env bash
#

set -xeuo pipefail

echo "password_encryption = 'scram-sha-256'" | tee -a /var/lib/postgresql/data/postgresql.conf

# restart postgres so that the changes apply
pg_ctl -D "$PGDATA" -m fast -w stop
pg_ctl -D "$PGDATA" -w start

# At this stage POSTGRES_USER has already been created
# This means that we need to re-hash its password
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB}" <<-EOSQL
    ALTER USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';
EOSQL

# Set the search path of the superuser
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB}" <<-EOSQL
    ALTER ROLE ${POSTGRES_USER} SET search_path = public,${PROJECT_NAME};
EOSQL

# I can't find the link now, but this was also suggested.
# I am commenting out though, since this might cause problems with pycsw functions
#psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB}" <<-EOSQL
#    ALTER DEFAULT PRIVILEGES FOR ROLE ${POSTGRES_USER} REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
#EOSQL
