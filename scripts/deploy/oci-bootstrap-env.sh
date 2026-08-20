#!/usr/bin/env bash
# APP_DIR and SSH_USER are local configuration that is meant to expand on this
# side before each remote command is sent, so SC2029 is the intended behavior.
# shellcheck disable=SC2029
#
# Install the runtime configuration and deployment assets on the OCI Ampere A1
# host, then set restrictive permissions on the secret-bearing file.
#
# Runs from a workstation. The local env file is copied over SSH and never
# passed as a command argument, so secrets do not appear in process lists,
# shell history, or OpenTofu state.
#
#   ./oci-bootstrap-env.sh --host 203.0.113.10 --env-file ./.env.oci
#
# Re-running is safe: it overwrites the runtime configuration and refreshes the
# compose file, Caddyfile, and deploy script.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

SSH_HOST=""
SSH_USER="ubuntu"
SSH_KEY=""
ENV_FILE=""
APP_DIR="/opt/python-tts"

log() {
  printf '[oci-bootstrap] %s\n' "$*"
}

fail() {
  printf '[oci-bootstrap] ERROR: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage:
  oci-bootstrap-env.sh --host <ip-or-hostname> --env-file <path> [options]

Required:
  --host <host>       Instance public IP or hostname
  --env-file <path>   Local runtime env file built from .env.oci.example

Options:
  --user <user>       SSH user (default: ubuntu)
  --ssh-key <path>    SSH private key (default: ssh agent / ~/.ssh config)
  --app-dir <path>    Remote application directory (default: /opt/python-tts)
  -h, --help          Show this help

Host key verification is never disabled. If the host is unknown, add it to
known_hosts first:
  ssh-keyscan -H <host> >> ~/.ssh/known_hosts
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --host)
      SSH_HOST="${2:-}"
      shift 2
      ;;
    --user)
      SSH_USER="${2:-}"
      shift 2
      ;;
    --ssh-key)
      SSH_KEY="${2:-}"
      shift 2
      ;;
    --env-file)
      ENV_FILE="${2:-}"
      shift 2
      ;;
    --app-dir)
      APP_DIR="${2:-}"
      shift 2
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      usage >&2
      fail "Unknown argument: $1"
      ;;
  esac
done

[ -n "${SSH_HOST}" ] || { usage >&2; fail "--host is required."; }
[ -n "${ENV_FILE}" ] || { usage >&2; fail "--env-file is required."; }
[ -f "${ENV_FILE}" ] || fail "Env file not found: ${ENV_FILE}"

# A file with placeholders would deploy a bot that cannot log in to Discord.
for key in DISCORD_TOKEN BOT_SPEAK_TOKEN BOT_IMAGE; do
  value="$(sed -n "s/^[[:space:]]*${key}=//p" "${ENV_FILE}" | tail -n 1 | tr -d '\r')"
  [ -n "${value}" ] || fail "${key} is empty in ${ENV_FILE}. Fill it in before bootstrapping."
done

if grep -Eq '^[[:space:]]*BOT_SPEAK_TOKEN=(change_me|changeme)$' "${ENV_FILE}"; then
  fail "BOT_SPEAK_TOKEN still holds a placeholder. Generate one with: openssl rand -hex 32"
fi

# StrictHostKeyChecking is deliberately left at its default. Disabling it would
# accept any key presented and allow a man-in-the-middle to capture the tokens
# this script uploads.
ssh_opts=()
scp_opts=()
if [ -n "${SSH_KEY}" ]; then
  [ -f "${SSH_KEY}" ] || fail "SSH key not found: ${SSH_KEY}"
  ssh_opts+=(-i "${SSH_KEY}")
  scp_opts+=(-i "${SSH_KEY}")
fi

remote="${SSH_USER}@${SSH_HOST}"

log "Verifying the host is a prepared Docker host..."
ssh "${ssh_opts[@]}" "${remote}" "command -v docker >/dev/null && docker compose version >/dev/null" \
  || fail "Docker or the Compose plugin is not ready on ${SSH_HOST}. Wait for cloud-init to finish, then retry."

log "Ensuring ${APP_DIR} exists..."
ssh "${ssh_opts[@]}" "${remote}" "sudo mkdir -p '${APP_DIR}/configs' '${APP_DIR}/caddy/data' '${APP_DIR}/caddy/config' '${APP_DIR}/scripts' '${APP_DIR}/logs' && sudo chown -R '${SSH_USER}':'${SSH_USER}' '${APP_DIR}' && sudo chown -R 1000:1000 '${APP_DIR}/configs'"

log "Uploading deployment assets..."
scp "${scp_opts[@]}" -q \
  "${REPO_ROOT}/docker-compose.oci.yml" \
  "${remote}:${APP_DIR}/compose.yaml"
scp "${scp_opts[@]}" -q \
  "${REPO_ROOT}/deploy/oci/Caddyfile" \
  "${remote}:${APP_DIR}/caddy/Caddyfile"
scp "${scp_opts[@]}" -q \
  "${REPO_ROOT}/scripts/deploy/oci-deploy.sh" \
  "${remote}:${APP_DIR}/scripts/oci-deploy.sh"
ssh "${ssh_opts[@]}" "${remote}" "chmod 0755 '${APP_DIR}/scripts/oci-deploy.sh'"

# Upload the secret file to a private path first, then move it into place, so
# it is never briefly world readable.
log "Installing the runtime configuration..."
scp "${scp_opts[@]}" -q "${ENV_FILE}" "${remote}:${APP_DIR}/.env.runtime.incoming"
ssh "${ssh_opts[@]}" "${remote}" "chmod 0600 '${APP_DIR}/.env.runtime.incoming' && mv '${APP_DIR}/.env.runtime.incoming' '${APP_DIR}/.env.runtime' && chmod 0600 '${APP_DIR}/.env.runtime'"

log "Verifying installed permissions..."
ssh "${ssh_opts[@]}" "${remote}" "stat -c '%a %U:%G %n' '${APP_DIR}/.env.runtime'"

cat <<EOF

[oci-bootstrap] Done. Deploy a released version with:

  ssh ${remote} '${APP_DIR}/scripts/oci-deploy.sh v1.2.3'

The runtime configuration is installed at ${APP_DIR}/.env.runtime with mode 0600.
It is not stored in OpenTofu state and is not part of any repository file.
EOF
