#!/usr/bin/env bash
#
# Deploy an immutable released bot image on a single-node Docker host.
#
# Runs ON the instance, on any supported target: OCI Ampere A1 (arm64) and GCP
# e2-micro (amd64) both use this script. It never builds application source:
# the released multi-arch GHCR image is the only artifact. Rolling back is the
# same operation with an earlier tag.
#
#   ./vm-deploy.sh v1.2.3        deploy a released version
#   ./vm-deploy.sh --rollback    redeploy the recorded previous version
#
# Exit codes: 0 success, 1 usage or validation failure, 2 health check failure.
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/python-tts}"
COMPOSE_FILE="${COMPOSE_FILE:-${APP_DIR}/compose.yaml}"
RUNTIME_ENV_FILE="${RUNTIME_ENV_FILE:-${APP_DIR}/.env.runtime}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:10000/health}"
READY_URL="${READY_URL:-http://127.0.0.1:10000/ready}"
HEALTH_RETRIES="${HEALTH_RETRIES:-30}"
HEALTH_DELAY_SECONDS="${HEALTH_DELAY_SECONDS:-5}"

# The released image is a multi-platform manifest. Deploy the platform this
# host actually runs, so the same script serves arm64 and amd64 targets.
detect_architecture() {
  case "$(uname -m)" in
    aarch64 | arm64) printf 'arm64' ;;
    x86_64 | amd64) printf 'amd64' ;;
    *) printf 'unsupported' ;;
  esac
}

TARGET_ARCH="${TARGET_ARCH:-$(detect_architecture)}"

log() {
  printf '[vm-deploy] %s\n' "$*"
}

fail() {
  printf '[vm-deploy] ERROR: %s\n' "$*" >&2
  exit "${2:-1}"
}

usage() {
  cat <<'USAGE'
Usage:
  vm-deploy.sh <release_tag>   Deploy an immutable released tag, e.g. v1.2.3
  vm-deploy.sh --rollback      Redeploy PREVIOUS_APP_VERSION from the runtime env file

Environment overrides:
  APP_DIR, COMPOSE_FILE, RUNTIME_ENV_FILE, HEALTH_URL, READY_URL,
  HEALTH_RETRIES, HEALTH_DELAY_SECONDS, TARGET_ARCH
USAGE
}

# Reads one key from the runtime env file without sourcing it. Sourcing a file
# that holds DISCORD_TOKEN would export secrets into this shell and into any
# child process, including error output.
read_env_value() {
  local key="$1"
  local file="$2"
  [ -f "${file}" ] || return 0
  sed -n "s/^[[:space:]]*${key}=//p" "${file}" | tail -n 1 | tr -d '\r'
}

# Rewrites a single key in place, preserving mode 0600 and every other line.
write_env_value() {
  local key="$1"
  local value="$2"
  local file="$3"
  local tmp
  tmp="$(mktemp "${file}.XXXXXX")"
  chmod 600 "${tmp}"

  if grep -q "^[[:space:]]*${key}=" "${file}"; then
    # The value is a semantic tag validated above, so it is safe in the
    # replacement, but keep awk out of regex interpretation regardless.
    awk -v key="${key}" -v value="${value}" '
      $0 ~ "^[[:space:]]*" key "=" { print key "=" value; next }
      { print }
    ' "${file}" > "${tmp}"
  else
    cat "${file}" > "${tmp}"
    printf '%s=%s\n' "${key}" "${value}" >> "${tmp}"
  fi

  mv "${tmp}" "${file}"
  chmod 600 "${file}"
}

compose() {
  docker compose \
    --env-file "${RUNTIME_ENV_FILE}" \
    --project-directory "${APP_DIR}" \
    -f "${COMPOSE_FILE}" \
    "$@"
}

wait_for_endpoint() {
  local url="$1"
  local label="$2"
  local attempt=1

  while [ "${attempt}" -le "${HEALTH_RETRIES}" ]; do
    if curl --fail --silent --show-error --max-time 10 "${url}" >/dev/null 2>&1; then
      log "${label} passed after ${attempt} attempt(s)."
      return 0
    fi
    log "Waiting for ${label} (${attempt}/${HEALTH_RETRIES})..."
    sleep "${HEALTH_DELAY_SECONDS}"
    attempt=$((attempt + 1))
  done

  return 1
}

main() {
  if [ "$#" -ne 1 ]; then
    usage >&2
    fail "Exactly one argument is required."
  fi

  case "$1" in
    -h | --help)
      usage
      exit 0
      ;;
  esac

  [ "${TARGET_ARCH}" != "unsupported" ] \
    || fail "Unsupported host architecture: $(uname -m). Set TARGET_ARCH explicitly if this is wrong."

  [ -f "${COMPOSE_FILE}" ] || fail "Compose file not found: ${COMPOSE_FILE}"
  [ -f "${RUNTIME_ENV_FILE}" ] || fail "Runtime env file not found: ${RUNTIME_ENV_FILE}. Run vm-bootstrap-env.sh first."

  local bot_image current_version requested_version
  bot_image="$(read_env_value BOT_IMAGE "${RUNTIME_ENV_FILE}")"
  current_version="$(read_env_value APP_VERSION "${RUNTIME_ENV_FILE}")"

  [ -n "${bot_image}" ] || fail "BOT_IMAGE is not set in ${RUNTIME_ENV_FILE}."

  # The runtime env file must actually carry the secrets before a deploy can
  # succeed; failing here is clearer than a container that starts and exits.
  [ -n "$(read_env_value DISCORD_TOKEN "${RUNTIME_ENV_FILE}")" ] \
    || fail "DISCORD_TOKEN is empty in ${RUNTIME_ENV_FILE}."
  [ -n "$(read_env_value BOT_SPEAK_TOKEN "${RUNTIME_ENV_FILE}")" ] \
    || fail "BOT_SPEAK_TOKEN is empty in ${RUNTIME_ENV_FILE}."

  if [ "$1" = "--rollback" ]; then
    requested_version="$(read_env_value PREVIOUS_APP_VERSION "${RUNTIME_ENV_FILE}")"
    [ -n "${requested_version}" ] || fail "PREVIOUS_APP_VERSION is not recorded. Pass an explicit tag instead."
    # Stored in registry form; the validation below expects the git tag form.
    requested_version="v${requested_version#v}"
    log "Rolling back to the recorded previous version."
  else
    requested_version="$1"
  fi

  # Immutable tags only. "latest" moves under a running deployment and makes
  # the deployed state unknowable.
  if ! printf '%s' "${requested_version}" | grep -Eq '^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$'; then
    fail "Invalid release tag '${requested_version}'. Expected a semantic tag such as v1.2.3."
  fi

  log "Current version: ${current_version:-none}"
  log "Requested version: ${requested_version}"

  # The release workflow publishes through docker/metadata-action with
  # type=semver,pattern={{version}}, which strips the leading "v": the tag
  # v1.2.3 becomes the registry tag 1.2.3. Operators and documentation use the
  # git tag form, so accept it and resolve to the published tag here.
  local registry_tag="${requested_version#v}"
  local target_image="${bot_image}:${registry_tag}"

  # Verify the tag exists and carries an image for this host's architecture
  # before touching the running deployment.
  log "Verifying ${target_image} exists and supports linux/${TARGET_ARCH}..."
  local manifest
  if ! manifest="$(docker manifest inspect "${target_image}" 2>&1)"; then
    fail "Image not found or not readable: ${target_image}"
  fi

  # jq is installed by cloud-init. Match on os AND architecture so an
  # attestation entry can never be mistaken for a runnable image.
  if ! printf '%s' "${manifest}" | jq -e --arg arch "${TARGET_ARCH}" \
    '[.manifests[]? | select(.platform.os == "linux" and .platform.architecture == $arch)] | length > 0' \
    >/dev/null 2>&1; then
    fail "Image ${target_image} has no linux/${TARGET_ARCH} manifest entry. This host cannot run it."
  fi
  log "linux/${TARGET_ARCH} manifest entry confirmed."

  log "Pulling ${target_image}..."
  docker pull --platform "linux/${TARGET_ARCH}" "${target_image}" >/dev/null

  # Record the rollback target before changing the running version, so an
  # interrupted deploy still leaves a recoverable previous tag.
  if [ -n "${current_version}" ] && [ "${current_version}" != "${registry_tag}" ]; then
    write_env_value PREVIOUS_APP_VERSION "${current_version}" "${RUNTIME_ENV_FILE}"
    log "Recorded previous version: ${current_version}"
  fi

  # APP_VERSION is interpolated straight into the compose image reference, so it
  # must hold the registry tag rather than the git tag.
  write_env_value APP_VERSION "${registry_tag}" "${RUNTIME_ENV_FILE}"

  local compose_profiles=()
  if [ -n "$(read_env_value PUBLIC_HOSTNAME "${RUNTIME_ENV_FILE}")" ]; then
    compose_profiles=(--profile https)
    log "PUBLIC_HOSTNAME is set: the https profile is included."
  fi

  log "Updating the running deployment..."
  compose "${compose_profiles[@]}" up -d --no-build --remove-orphans

  log "Validating /health..."
  if ! wait_for_endpoint "${HEALTH_URL}" "health check"; then
    log "Health check failed. Container status:"
    compose ps || true
    compose logs --tail 50 bot || true
    fail "Deployment of ${requested_version} failed the health check. Run 'vm-deploy.sh --rollback' to restore ${current_version:-the previous version}." 2
  fi

  log "Validating /ready..."
  if ! wait_for_endpoint "${READY_URL}" "readiness check"; then
    log "Readiness check failed. Container status:"
    compose ps || true
    compose logs --tail 50 bot || true
    fail "Deployment of ${requested_version} failed the readiness check. Run 'vm-deploy.sh --rollback' to restore ${current_version:-the previous version}." 2
  fi

  # Conservative cleanup: dangling layers only. Tagged images stay so a
  # rollback does not need to re-pull over a slow link.
  log "Pruning dangling images..."
  docker image prune --force --filter "dangling=true" >/dev/null 2>&1 || true

  compose ps
  log "Deployed ${requested_version} successfully."
}

main "$@"
