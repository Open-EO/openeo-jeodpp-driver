#!/usr/bin/env bash
#
# https://medium.com/@adrian.gheorghe.dev/using-docker-secrets-in-your-environment-variables-7a0609659aab
#

set -eo pipefail

inject_env() {
  local variable="${1}"
  local secret_file=/run/secrets/"${variable}"
  local value=''

  value="$(cat "${secret_file}")"
  export "${variable}"="${value}"
}

for file in /run/secrets/*
do
  filename=$(basename "${file}")
  inject_env "${filename}"
done

set -xu

echo 'Executing prestart script'
/usr/local/bin/prestart.sh

exec gosu ${USER_ID}:${GROUP_ID} "$@"

