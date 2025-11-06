#!/usr/bin/env bash

set -euo pipefail

pattern='^(feat|fix|docs|chore|refactor|test|perf|build|ci|revert)(\(.+\))?: .+'

base_ref="${BASE_REF:-origin/main}"

git fetch origin +refs/heads/*:refs/remotes/origin/* >/dev/null 2>&1 || true

range="$(git rev-list --no-merges --left-right ${base_ref}...HEAD | awk '/^>/{print $0}' | wc -l)"

log_cmd=(git log --pretty=%s ${base_ref}..HEAD)

# اسم الجوب في Actions لازم يمرّر BASE_REF=${{ github.base_ref }}

invalid=0

while IFS= read -r msg; do
  [[ "$msg" =~ ^Merge ]] && continue   # سماح لرسائل دمج GitHub

  if ! [[ "$msg" =~ $pattern ]]; then
    echo "❌ Invalid commit message: $msg"
    invalid=1
  fi
done < <("${log_cmd[@]}")

if [[ $invalid -eq 1 ]]; then
  echo "❌ Commit messages must follow Conventional Commits."
  exit 1
fi

echo "✅ commit messages OK"
