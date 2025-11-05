#!/usr/bin/env python3

import sys, xml.etree.ElementTree as ET


# خرائط عتبات لكل نمط حزمة

THRESHOLDS = {
    "backend": 0.70,  # Backend code coverage
    # Add more as packages are created
}


def read_coverage(path="coverage.xml"):

    tree = ET.parse(path)

    root = tree.getroot()

    out = {}

    for pkg in root.iterfind(".//packages/package"):

        name = pkg.get("name", "")

        lines_valid = 0

        lines_covered = 0

        for cls in pkg.iterfind("./classes/class"):

            lines = cls.find("./lines")

            if lines is None:
                continue

            for ln in lines.iter("line"):

                lines_valid += 1

                if int(ln.get("hits", "0")) > 0:

                    lines_covered += 1

        out[name] = (lines_covered, lines_valid)

    return out


def ratio(c, v):
    return c / (v or 1)


def main():

    cov = read_coverage()

    fails = []

    for pat, thr in THRESHOLDS.items():

        # اجمع كل الحزم اللي اسمها يبدأ بالنمط

        covered = valid = 0

        for name, (c, v) in cov.items():

            if name.startswith(pat):

                covered += c
                valid += v

        r = ratio(covered, valid)

        if r < thr:

            fails.append((pat, r, thr))

        print(f"[{pat}] {r:.3f} (thr {thr:.2f})")

    if fails:

        print("❌ Package coverage gate failed:")

        for pat, r, thr in fails:

            print(f"  - {pat}: {r:.3f} < {thr:.2f}")

        sys.exit(1)

    print("✅ Package coverage gates PASS")


if __name__ == "__main__":

    main()
