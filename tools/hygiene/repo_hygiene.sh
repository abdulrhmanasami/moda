# @Study:ST-019
#!/usr/bin/env bash

set -euo pipefail

echo "[HYGIENE] checking forbidden files…"

# Simple check for common forbidden files
forbidden_files=(
    ".DS_Store"
    "__MACOSX"
)

for file in "${forbidden_files[@]}"; do
    if find . -name "$file" -not -path './.git/*' | grep -q .; then
        echo "❌ Forbidden file found: $file"
        exit 1
    fi
done

# Check file sizes (>2MB)
echo "[HYGIENE] checking file sizes…"
if find . -type f -not -path './.git/*' -size +2M | grep -q .; then
    echo "❌ Large files found:"
    find . -type f -not -path './.git/*' -size +2M
    exit 1
fi

echo "✅ Hygiene PASS"
