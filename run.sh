#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$PROJECT_DIR/mboozle.log"

# Uptime Kuma Push URL (leave empty "" if you don't want Kuma push)
KUMA_URL=""

cd "$PROJECT_DIR"

# Detect docker-compose vs docker compose
if command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    echo "Error: Docker Compose not found" >> "$LOG_FILE"
    [ -n "$KUMA_URL" ] && curl -fsS "$KUMA_URL?status=down&msg=Docker+Compose+not+found" || true
    exit 1
fi

START_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Push helpers (only run if KUMA_URL is set)
success_push() {
    if [ -n "$KUMA_URL" ]; then
        curl -fsS "$KUMA_URL?status=up&msg=Mboozle+rclone+Succeeded" || true
    fi
}
failure_push() {
    if [ -n "$KUMA_URL" ]; then
        curl -fsS "$KUMA_URL?status=down&msg=Mboozle+rclone+Failed" || true
    fi
}

# Traps
trap success_push EXIT
trap failure_push ERR

# Run in foreground, wait until done
$DOCKER_COMPOSE up --build 2>&1 | tee -a "$LOG_FILE"