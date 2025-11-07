#!/usr/bin/env python3
import argparse, hashlib, io, json, os, re, subprocess, tarfile, time
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo

ROOT = Path(__file__).resolve().parents[2]
CFG  = ROOT / "governance" / "release_pack.config.json"
NOW  = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def load_cfg():
    return json.loads(CFG.read_text(encoding="utf-8"))

def git(cmd):
    return subprocess.check_output(["git"]+cmd, cwd=ROOT).decode().strip()

def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256(); h.update(b); return h.hexdigest()

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1<<20), b""):
            h.update(chunk)
    return h.hexdigest()

def match_any(path, globs):
    from fnmatch import fnmatch
    s = str(path.as_posix())
    return any(fnmatch(s, g) for g in globs)

def list_files(include, exclude):
    res = []
    for g in include:
        for p in ROOT.glob(g):
            if p.is_file() and not match_any(p, exclude):
                res.append(p)
            elif p.is_dir():
                for f in p.rglob("*"):
                    if f.is_file() and not match_any(f, exclude):
                        res.append(f)
    # إزالة التكرار + ترتيب ثابت
    return sorted(set(res), key=lambda x: x.as_posix())

def fixed_zipinfo(rel):
    zi = ZipInfo(rel.as_posix())
    zi.date_time = (1980,1,1,0,0,0)      # reproducible
    zi.compress_type = ZIP_DEFLATED
    zi.external_attr = 0o644 << 16       # permissions
    return zi

def guess_lang(p: Path):
    ext = p.suffix.lower()
    return {
        ".py":"Python",".ts":"TypeScript",".tsx":"TypeScript",".js":"JavaScript",
        ".json":"JSON",".yml":"YAML",".yaml":"YAML",".md":"Markdown",
        ".tf":"Terraform",".tpl":"Helm",".sh":"Shell",".toml":"TOML"
    }.get(ext, "Other")

def make_archives(files, out_dir: Path, name_base: str):
    # ZIP
    zip_path = out_dir / f"{name_base}.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED, compresslevel=9) as z:
        for f in files:
            rel = f.relative_to(ROOT)
            zi = fixed_zipinfo(rel)
            with f.open("rb") as fp:
                z.writestr(zi, fp.read())
    # TAR.GZ
    tgz_path = out_dir / f"{name_base}.tar.gz"
    with tarfile.open(tgz_path, "w:gz", format=tarfile.GNU_FORMAT, compresslevel=9) as t:
        for f in files:
            rel = f.relative_to(ROOT)
            ti = t.gettarinfo(str(f), arcname=str(rel))
            # تطبيع الوقت/الحقوق
            ti.mtime = 0
            ti.uid = ti.gid = 0
            ti.uname = ti.gname = "root"
            ti.mode = 0o644
            with f.open("rb") as fp:
                t.addfile(ti, fp)
    return zip_path, tgz_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", required=True, choices=["rc","ga"])
    parser.add_argument("--version", required=True)
    args = parser.parse_args()

    cfg = load_cfg()
    channel = args.channel
    version = args.version

    # فحوصات تقارير مطلوبة
    for req in cfg["checks"]["require_reports"]:
        rp = ROOT / "reports" / req
        if not rp.exists():
            raise SystemExit(f"[FAIL] missing report: reports/{req}")

    files = list_files(cfg["include"], cfg["exclude"])
    total_bytes = sum(f.stat().st_size for f in files)
    total_mb = total_bytes / (1024*1024)
    if total_mb > float(cfg["checks"]["max_total_mb"]):
        raise SystemExit(f"[FAIL] bundle size {total_mb:.2f}MB > {cfg['checks']['max_total_mb']}MB")

    out_dir = ROOT / cfg["out_dir"] / channel / version
    out_dir.mkdir(parents=True, exist_ok=True)

    # SBOM-lite
    sbom = {
        "bomFormat":"CycloneDX-lite","specVersion":"1.0",
        "metadata":{
            "timestamp":NOW,
            "git":{
                "commit": git(["rev-parse","HEAD"]),
                "branch": git(["rev-parse","--abbrev-ref","HEAD"])
            },
            "build":{
                "channel":channel,"version":version,"builder":"ReleasePackOrchestrator"
            }
        },
        "components":[]
    }
    manifest = {"files":[], "build": sbom["metadata"], "created": NOW}

    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        h = sha256_file(f)
        manifest["files"].append({"path":rel,"bytes":f.stat().st_size,"sha256":h})
        sbom["components"].append({
            "name": rel, "type":"file", "language": guess_lang(f),
            "hashes":{"SHA-256":h}, "size": f.stat().st_size
        })

    (out_dir/"SBOM_LITE.json").write_text(json.dumps(sbom, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir/"MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    base = f"moda_{channel}_{version}"
    z, t = make_archives(files, out_dir, base)

    checksums = {
        z.name: sha256_file(z),
        t.name: sha256_file(t),
        "MANIFEST.json": sha256_file(out_dir/"MANIFEST.json"),
        "SBOM_LITE.json": sha256_file(out_dir/"SBOM_LITE.json")
    }
    (out_dir/"CHECKSUMS.sha256").write_text(
        "\n".join(f"{v}  {k}" for k,v in checksums.items())+"\n",
        encoding="utf-8"
    )

    # ملاحظات وإرشادات
    (out_dir/"RELEASE_NOTES.md").write_text(f"""# Release Notes — {channel.upper()} {version}

- Build Time: {NOW}
- Commit: {sbom['metadata']['git']['commit']}
- Reports: REALITY_TEST / CLAIMS_EVIDENCE / DRIFT_GUARD ✓

""", encoding="utf-8")
    (out_dir/"README_RELEASE.md").write_text(f"""# Verify & Unpack

## Verify checksums
sha256sum -c CHECKSUMS.sha256

## Unpack
unzip {z.name} -d ./unpacked_zip
mkdir -p ./unpacked_tgz && tar -xzf {t.name} -C ./unpacked_tgz

""", encoding="utf-8")

    print(f"[OK] Release pack ready: {out_dir}")
    print(f"ZIP : {z.name}")
    print(f"TAR : {t.name}")
    print(f"SIZE: {total_mb:.2f} MB")

if __name__ == "__main__":
    main()
