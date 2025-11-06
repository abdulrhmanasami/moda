#!/usr/bin/env bash

set -euo pipefail

pattern='^(feat|fix|docs|chore|refactor|test|perf|build|ci|revert)(\(.+\))?: .+'

base_ref="${BASE_REF:-main}"

echo "🔍 Checking commits from ${base_ref} to HEAD"

# Fetch latest changes
echo "📥 Fetching latest changes..."
git fetch origin +refs/heads/*:refs/remotes/origin/* >/dev/null 2>&1 || true

# Check if base_ref exists
if ! git show-ref --verify --quiet "refs/remotes/origin/${base_ref}"; then
  echo "⚠️  Base ref ${base_ref} not found, using origin/main"
  base_ref="origin/main"
fi

echo "📋 Checking commits: git log --pretty=%s ${base_ref}..HEAD"

# Get commit messages
commit_messages=$(git log --pretty=%s "${base_ref}"..HEAD 2>/dev/null || echo "")

if [[ -z "$commit_messages" ]]; then
  echo "ℹ️  No commits to check (possibly already merged or no new commits)"
  echo "✅ commit messages OK"
  exit 0
fi

echo "📝 Found commits to check:"
echo "$commit_messages" | nl

invalid=0

while IFS= read -r msg; do
  [[ "$msg" =~ ^Merge ]] && continue   # سماح لرسائل دمج GitHub

  if ! [[ "$msg" =~ $pattern ]]; then
    echo "❌ Invalid commit message: $msg"
    invalid=1
  fi
done <<< "$commit_messages"

if [[ $invalid -eq 1 ]]; then
  echo "❌ Commit messages must follow Conventional Commits."
  exit 1
fi

echo "✅ commit messages OK"
