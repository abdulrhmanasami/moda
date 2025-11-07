#!/usr/bin/env bash
set -euo pipefail
CH=${1:-rc}         # rc | ga
VER=${2:-0.1.0-rc.1}
git tag -a "$VER" -m "release: $CH $VER"
git push origin "$VER"
echo "Tagged & pushed: $VER"
