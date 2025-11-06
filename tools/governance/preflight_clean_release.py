#!/usr/bin/env python3

import os, sys, json, fnmatch, hashlib

from pathlib import Path



ROOT = Path(__file__).resolve().parents[2]

CONFIG_PATH = ROOT / "governance" / "preflight.config.json"



DEFAULT = {

  "allowed_root_files": [".editorconfig", ".gitattributes", "README.md", "LICENSE", "CHANGELOG.md", "CONTRIBUTING.md", "package.json", "pyproject.toml", "docker-compose.yml", "Dockerfile", "env.example"],

  "allowed_root_dirs": [".github","SECURITY","studies","governance","infrastructure","src","tools","scripts","tests","docs","htmlcov","logs","release","requirements"],

  "forbidden_globs": ["**/.DS_Store","**/Thumbs.db","**/__MACOSX/**", "**/*.pyc", "**/__pycache__/**", "**/.pytest_cache/**", "**/node_modules/**", "**/*.log"],

  "forbidden_extensions_outside_dist": [".zip",".rar",".7z",".tar",".tgz",".gz",".exe",".msi",".dmg",".pkg",".deb",".rpm"],

  "dist_like_dirs": ["dist","release","artifacts","htmlcov"],

  "max_file_bytes": 5*1024*1024,

  "fail_on_orphans": True,

  "fail_on_missing": True

}



def load_cfg():

  if CONFIG_PATH.exists():

    with open(CONFIG_PATH,"r",encoding="utf-8") as f:

      return {**DEFAULT, **json.load(f)}

  return DEFAULT



def in_any(path:Path, names:set[str])->bool:

  return any(part in names for part in path.parts)



def is_under_any(path:Path, dirs:set[str])->bool:

  return any(d in path.parts for d in dirs)



def checksum(path:Path)->str:

  h=hashlib.sha256()

  with open(path,"rb") as f:

    for chunk in iter(lambda: f.read(1<<20), b""):

      h.update(chunk)

  return h.hexdigest()



def main():

  cfg = load_cfg()

  allowed_root_files = set(cfg["allowed_root_files"])

  allowed_root_dirs  = set(cfg["allowed_root_dirs"])

  dist_like_dirs     = set(cfg["dist_like_dirs"])



  errors, warns = [], []

  findings = {"root": {"illegal_files": [], "illegal_dirs": []},

              "forbidden_matches": [], "oversized": [], "archives_outside_dist": [],

              "summary": {}}



  # 1) تحقق الجذر

  for item in ROOT.iterdir():

    if item.is_file():

      if item.name not in allowed_root_files:

        findings["root"]["illegal_files"].append(str(item.relative_to(ROOT)))

    elif item.is_dir():

      if item.name not in allowed_root_dirs:

        findings["root"]["illegal_dirs"].append(str(item.relative_to(ROOT)))



  # 2) عناصر ممنوعة (globs)

  for pattern in cfg["forbidden_globs"]:

    for p in ROOT.rglob("*"):

      if fnmatch.fnmatch(str(p), pattern):

        findings["forbidden_matches"].append(str(p.relative_to(ROOT)))



  # 3) ملفات ضخمة

  max_bytes = int(cfg["max_file_bytes"])

  for p in ROOT.rglob("*"):

    if p.is_file():

      try:

        if p.stat().st_size > max_bytes and not is_under_any(p, dist_like_dirs):

          findings["oversized"].append({"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size})

      except OSError:

        continue



  # 4) أرشيفات خارج dist

  forbidden_ext = set(cfg["forbidden_extensions_outside_dist"])

  for p in ROOT.rglob("*"):

    if p.is_file():

      if any(str(p).lower().endswith(ext) for ext in forbidden_ext):

        if not is_under_any(p, dist_like_dirs):

          findings["archives_outside_dist"].append(str(p.relative_to(ROOT)))



  # 5) مانيفست صغير

  total_files = sum(1 for _ in ROOT.rglob("*") if _.is_file())

  total_bytes = sum(_.stat().st_size for _ in ROOT.rglob("*") if _.is_file())

  findings["summary"] = {

    "total_files": total_files,

    "total_megabytes": round(total_bytes/1024/1024, 3)

  }



  # 6) تقرير

  out_dir = ROOT / "reports"

  out_dir.mkdir(parents=True, exist_ok=True)

  (out_dir / "CLEAN_RELEASE_REPORT.md").write_text(

    "# Clean Release Report\n\n"

    f"- Illegal root files: {len(findings['root']['illegal_files'])}\n"

    f"- Illegal root dirs: {len(findings['root']['illegal_dirs'])}\n"

    f"- Forbidden matches: {len(findings['forbidden_matches'])}\n"

    f"- Oversized files: {len(findings['oversized'])}\n"

    f"- Archives outside dist: {len(findings['archives_outside_dist'])}\n"

    f"- Total files: {findings['summary']['total_files']}\n"

    f"- Size (MB): {findings['summary']['total_megabytes']}\n",

    encoding="utf-8"

  )

  with open(out_dir / "CLEAN_RELEASE_REPORT.json","w",encoding="utf-8") as f:

    json.dump(findings, f, ensure_ascii=False, indent=2)



  # 7) الإخفاق

  if findings["root"]["illegal_files"] or findings["root"]["illegal_dirs"] or \

     findings["forbidden_matches"] or findings["oversized"] or \

     findings["archives_outside_dist"]:

    print("❌ Preflight failed. See reports/CLEAN_RELEASE_REPORT.*")

    sys.exit(1)

  print("✅ Preflight clean.")

  return 0



if __name__ == "__main__":

  sys.exit(main())
