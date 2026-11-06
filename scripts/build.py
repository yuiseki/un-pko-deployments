"""Collect one year's deployment GeoJSON made by Geo-Ref-skills into data/<year>/, with one point per line.

    python scripts/build.py --src <geojson dir> --year 2025 --refs 4412 4522 ... --out data

- data/<year>/geojson/<mission>_<date>_<sha12>.geojson: the files as Geo-Ref-skills wrote them;
- data/<year>/points.jsonl: every point of those files, one per line, in a fixed order, with the file's
  disclaimer and provenance on each line.
Nothing is written if a UN map reference number (given with --refs) appears anywhere in the output.
"""
import argparse
import json
import re
import shutil
from pathlib import Path

DISCLAIMER_JA = "正確性は一切保証しません。位置、部隊名、規模、兵科は間違っている可能性があります。国連の公式の製品ではありません。"


def rows(fc, name):
    out = []
    for f in fc["features"]:
        lon, lat = f["geometry"]["coordinates"]
        out.append({"file": name, "mission": fc["mission"], "map_date": fc["map_date"], "lon": lon, "lat": lat,
                    **{k: v for k, v in f["properties"].items() if k not in ("mission", "date")},
                    "based_on": fc["based_on"], "source_sha256": fc["source_sha256"], "tool_commit": fc["tool_commit"],
                    "disclaimer": fc["disclaimer"]})
    return sorted(out, key=lambda r: (r["mission"], r["map_date"], r["file"], r["stack"], r["label"], r["inner"], r["lon"], r["lat"]))


def leaked(text, refs):
    return [r for r in refs if re.search(r"(?<!\d)" + re.escape(r) + r"(?!\d)", text)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True)
    ap.add_argument("--year", required=True)
    ap.add_argument("--refs", nargs="+", required=True)
    ap.add_argument("--out", default="data")
    a = ap.parse_args()
    files = sorted(Path(a.src).glob("*.geojson"))
    allrows, texts = [], []
    for p in files:
        fc = json.loads(p.read_text())
        assert fc.get("disclaimer") and "NO WARRANTY" in fc["disclaimer"], p
        assert all("NO WARRANTY" in f["properties"].get("no_warranty", "") for f in fc["features"]), p
        allrows += rows(fc, p.name)
        texts.append(p.name + p.read_text())
    lines = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in allrows)
    bad = leaked("".join(texts) + lines, a.refs)
    if bad:
        raise SystemExit(f"reference numbers found: {bad}")
    d = Path(a.out) / a.year
    (d / "geojson").mkdir(parents=True, exist_ok=True)
    for p in files:
        shutil.copyfile(p, d / "geojson" / p.name)
    (d / "points.jsonl").write_text(lines)
    print(json.dumps({"files": len(files), "points": len(allrows)}))


if __name__ == "__main__":
    main()
