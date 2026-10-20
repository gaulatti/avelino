#!/usr/bin/env python3
"""Project retained native DateRangePicker observations into consumer resources."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evidence/reference-investigations/date-range-20261018/output/captures.json"
DEST = ROOT / "tests/consumer/native-date-range-witnesses.json"

def generate():
    source = json.loads(SOURCE.read_text())
    closed = []
    for row in source["rows"]:
        state = row["states"][row["modes"].index(1)]
        pickers = state["nativeControls"]["datePickers"]
        closed.append(dict(configuration=row["configuration"], appearance=row["appearance"],
            textScale=row["textScale"], dpr=row["dpr"], referenceCapture=row["paths"][0],
            model=state["model"], displayed=[p["date"] for p in pickers],
            frames=dict(state["frames"], start=pickers[0]["alignmentFrame"], end=pickers[1]["alignmentFrame"])))
    assert len(closed) == 384
    return dict(schemaVersion=1, accepted=False, reference="fe8a1d462fbd793d883fb92086a16aa2947e32c9",
        source=str(SOURCE.relative_to(ROOT)), sourceSha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(), closed=closed)

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args=parser.parse_args()
    expected=json.dumps(generate(), indent=2, ensure_ascii=False)+"\n"
    if args.check:
        if not DEST.is_file() or DEST.read_text()!=expected: raise SystemExit("DateRangePicker witnesses are stale")
    else: DEST.write_text(expected)
    print("DateRangePicker: 384 source observations; acceptance remains pending")

if __name__ == "__main__": main()
