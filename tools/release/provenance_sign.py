#!/usr/bin/env python3

import os, json, hashlib, base64, subprocess, time

from pathlib import Path



ROOT=Path(__file__).resolve().parents[2]



def sha256(p:Path)->str:

    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()



def main():

    channel=os.environ.get("REL_CHANNEL","rc")

    version=os.environ.get("REL_VERSION","0.1.0-rc.1")

    out=ROOT/"dist"/channel/version

    man=out/"MANIFEST.json"

    sbom=out/"SBOM_LITE.json"

    sums=out/"CHECKSUMS.sha256"



    prov={

      "provenanceVersion":"1.0",

      "buildType":"release-pack",

      "buildTime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),

      "materials":{

        "manifest":{"path":"MANIFEST.json","sha256":sha256(man)},

        "sbom":{"path":"SBOM_LITE.json","sha256":sha256(sbom)},

        "checksums":{"path":"CHECKSUMS.sha256","sha256":sha256(sums)}

      },

      "source":{

        "repo": os.environ.get("GITHUB_REPOSITORY",""),

        "ref": os.environ.get("GITHUB_REF",""),

        "sha": os.environ.get("GITHUB_SHA",""),

        "run_id": os.environ.get("GITHUB_RUN_ID","")

      },

      "identity":{

        "signer": os.environ.get("RELEASE_SIGNING_KEY_ID","unknown")

      }

    }

    (out/"PROVENANCE.json").write_text(json.dumps(prov,indent=2),encoding="utf-8")



    # توقيع CHECKSUMS.sha256 بمفتاح RSA من Secrets

    key=os.environ.get("RELEASE_SIGNING_KEY_PEM")

    if not key: raise SystemExit("missing RELEASE_SIGNING_KEY_PEM")

    (out/"CHECKSUMS.sha256.sig").write_bytes(

        subprocess.check_output(["openssl","dgst","-sha256","-sign","/dev/stdin","-binary", str(sums)], input=key.encode())

    )

    print("[OK] PROVENANCE.json + CHECKSUMS.sha256.sig created")



if __name__=="__main__":

    main()
