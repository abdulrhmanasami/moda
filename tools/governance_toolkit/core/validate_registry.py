#!/usr/bin/env python3

import json, sys, hashlib, os, subprocess

REG = "governance/studies/registry.json"

CHK = "governance/studies/meta/checksums.csv"


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def load_checksums():
    m = {}
    if not os.path.exists(CHK):
        return m
    for line in open(CHK, encoding="utf-8"):
        if not line.strip() or line.startswith("study_id,"):
            continue
        parts = line.strip().split(",")
        if len(parts) >= 3:
            study_id, file_path, checksum = parts[0], parts[1], parts[2]
            m[file_path] = checksum
    return m


def main():
    data = json.load(open(REG, encoding="utf-8"))
    if not data.get("version"):
        sys.exit("registry: missing `version`")
    if not isinstance(data.get("studies"), list):
        sys.exit("registry: `studies` must be list")
    locked = data.get("lock", {}).get("enabled", False)
    if not locked:
        sys.exit("registry: lock.enabled is false")

    checksums = load_checksums()
    for s in data["studies"]:
        cp = s.get("canonical_path")
        assert cp, "missing canonical_path"
        if not os.path.exists(cp):
            sys.exit(f"missing file: {cp}")
        if cp in checksums:
            if sha(cp) != checksums[cp]:
                sys.exit(f"checksum mismatch: {cp}")
        # aliases are strings, not dicts - they should exist as symlinks or be removed
        for al in s.get("aliases", []):
            if isinstance(al, str) and os.path.exists(al):
                print(
                    f"WARNING: alias file still exists: {al} (should be removed or symlinked)"
                )
    print("OK: registry locked & consistent")


if __name__ == "__main__":
    main()
