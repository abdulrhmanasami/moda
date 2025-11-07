#!/usr/bin/env bash

set -euo pipefail

V_FILE=$(cat VERSION | tr -d '[:space:]')

V_README=$(grep -Eo 'v[0-9]+\.[0-9]+\.[0-9]+' README.md | head -n1 | sed 's/^v//')

V_TAG=$(git tag --list "v0.1.0" | head -n1 | sed 's/^v//' || echo "0.1.0")

echo "VERSION=$V_FILE README=$V_README TAG=$V_TAG"

[[ "$V_FILE" == "$V_README" ]] || { echo "README version mismatch"; exit 1; }

[[ "$V_FILE" == "$V_TAG"    ]] || { echo "Tag version mismatch"; exit 1; }
