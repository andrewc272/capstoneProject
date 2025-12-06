#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_ROOT="$REPO_ROOT"
COMPOSE_FILE="$COMPOSE_ROOT/docker-compose.yml"
ENV_FILE="$COMPOSE_ROOT/.env"
COMPOSE_CMD="docker compose"
COMPOSE_ARGS=()

if ! command -v docker &>/dev/null; then
  echo "[dev] Docker is required but not installed. Install Docker Desktop for macOS first." >&2
  exit 1
fi

# Prefer the new `docker compose` subcommand, but fall back to docker-compose if needed.
if ! docker compose version &>/dev/null; then
  if command -v docker-compose &>/dev/null; then
    COMPOSE_CMD="docker-compose"
  else
    echo "[dev] Neither 'docker compose' nor 'docker-compose' is available." >&2
    exit 1
  fi
fi

ensure_env_file() {
  if [[ ! -f "$COMPOSE_FILE" ]]; then
    echo "[dev] Unable to find docker-compose.yml at $COMPOSE_FILE" >&2
    exit 1
  fi

  if [[ -f "$ENV_FILE" ]]; then
    return
  fi

  echo "[dev] Creating .env with a generated SECRET_KEY placeholder."
  SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  cat >"$ENV_FILE" <<EOF
SECRET_KEY=$SECRET_KEY
# Uncomment and fill in if you plan to use the OpenAI cloud bots.
# OPENAI_API_KEY=sk-your-key
CAPSTONE_HOST_PORT=5000
# Set to 1 to start the OpenAI bot containers (requires OPENAI_API_KEY).
CAPSTONE_ENABLE_CLOUD_BOTS=0
# If you are running Ollama on the host for local agents, keep this value.
OLLAMA_URL=http://host.docker.internal:11434
EOF
}

usage() {
  cat <<EOF
Usage: $(basename "$0") <command> [args]

Commands:
  up           Build (if needed) and start the stack in the foreground.
  up -d        Same as above but detached (pass -d or other args through).
  down         Stop and remove containers defined in docker-compose.yml.
  build        Build/rebuild images.
  logs [name]  Tail logs for all services or the specified service.

Examples:
  $0 up
  $0 up -d
  $0 logs flask-app
EOF
}

configure_profiles() {
  [[ -f "$ENV_FILE" ]] || return
  local value
  value=$(grep -E "^CAPSTONE_ENABLE_CLOUD_BOTS=" "$ENV_FILE" | tail -n 1 | cut -d= -f2- || true)
  value=$(echo "$value" | tr '[:upper:]' '[:lower:]')
  if [[ "$value" == "1" || "$value" == "true" || "$value" == "yes" ]]; then
    COMPOSE_ARGS+=("--profile" "cloud-bots")
  fi
}

run_compose() {
  local extra_args=()
  if [[ "${COMPOSE_ARGS+x}" ]]; then
    set +u
    extra_args=("${COMPOSE_ARGS[@]}")
    set -u
  fi
  if ((${#extra_args[@]})); then
    (cd "$COMPOSE_ROOT" && $COMPOSE_CMD -f "$COMPOSE_FILE" "${extra_args[@]}" "$@")
  else
    (cd "$COMPOSE_ROOT" && $COMPOSE_CMD -f "$COMPOSE_FILE" "$@")
  fi
}

main() {
  if [[ $# -lt 1 ]]; then
    usage
    exit 1
  fi

  subcommand="$1"
  shift || true

  if [[ "$subcommand" == "up" || "$subcommand" == "build" ]]; then
    ensure_env_file
    configure_profiles
    if [[ "$subcommand" == "up" ]]; then
      run_compose up "$@"
    else
      run_compose build "$@"
    fi
  elif [[ "$subcommand" == "down" ]]; then
    ensure_env_file
    configure_profiles
    run_compose down "$@"
  elif [[ "$subcommand" == "logs" ]]; then
    ensure_env_file
    configure_profiles
    run_compose logs -f "$@"
  elif [[ "$subcommand" == "-h" || "$subcommand" == "--help" || "$subcommand" == "help" ]]; then
    usage
  else
    echo "[dev] Unknown command: $subcommand" >&2
    usage
    exit 1
  fi
}

main "$@"
