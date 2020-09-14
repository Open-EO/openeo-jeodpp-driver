#! /usr/bin/env bash

set -xeuo pipefail

echo "Waiting for the database to get ready"
python3 /usr/local/bin/wait_for_port.py --timeout 30 --host db 5432

#echo 'DB ready! Applying migrations'
#alembic --raiseerr upgrade head

echo 'Starting application webserver'

