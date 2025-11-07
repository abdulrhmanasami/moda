#!/usr/bin/env bash

set -euo pipefail

if [[ "${ALLOW_BASELINE_UPDATE:-0}" != "1" ]]; then

  echo "Baseline update not allowed"; exit 1

fi

cp reports/REALITY_TEST.json         governance/baselines/REALITY_BASELINE.json

cp reports/DOCMAP_SYNC.json          governance/baselines/DOCMAP_BASELINE.json

cp reports/CLEAN_RELEASE_REPORT.json governance/baselines/CLEAN_BASELINE.json 2>/dev/null || true

git add governance/baselines/*.json
