#!/usr/bin/env bash

set -euo pipefail

EVENT="${GITHUB_EVENT_NAME:-}"

# نتحقق فقط على pull_request

if [[ "$EVENT" != "pull_request" ]]; then
  echo "SKIP (event=$EVENT)"; exit 0
fi

BODY="$(jq -r '.pull_request.body // ""' "$GITHUB_EVENT_PATH")"
TITLE="$(jq -r '.pull_request.title // ""' "$GITHUB_EVENT_PATH")"

TEXT="${TITLE}
${BODY}"

if echo "$TEXT" | grep -E -q 'ST-[0-9]{3}'; then
  echo "✅ Studies referenced found."
  exit 0
else
  echo "❌ Missing study references (ST-xxx) in PR title/body."
  echo "Please reference relevant studies (e.g., ST-003) per template."
  exit 1
fi
