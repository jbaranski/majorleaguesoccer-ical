#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Install n (Node version manager) using the existing Node/npm
npm install -g n

# Install Node 24 to /usr/local (n's default prefix)
n 24

# Prepend /usr/local/bin so Node 24 shadows the container's older Node —
# must be set in both this process and the env file for future shell invocations
export PATH="/usr/local/bin:$PATH"
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo 'export PATH="/usr/local/bin:$PATH"' >> "$CLAUDE_ENV_FILE"
fi

# Install project dependencies with Node 24
cd "$CLAUDE_PROJECT_DIR/client" && npm ci
