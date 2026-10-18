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
    history_path = ROOT / "evidence/reference-investigations/date-range-20261018/history-output/histories.json"
    history_source = json.loads(history_path.read_text())
    modes = {row["mode"]: row for row in history_source["modes"]}
    steps = []
    for row, public in zip(modes[1]["steps"], modes[0]["steps"], strict=True):
        assert row["step"] == public["step"]
        name = row["step"]
        action = dict(kind="configuration", configuration=row["configuration"])
        if name == "initial": action = dict(kind="initial", configuration=row["configuration"])
        elif name == "external-start": action = dict(kind="externalStart", value=1711929600.75)
        elif name == "external-end": action = dict(kind="externalEnd", value=1709164800.25)
        elif name == "dark": action = dict(kind="appearance", dark=True)
        elif name == "restore": action = dict(kind="restore", configuration=row["configuration"], dark=False)
        state = row["state"]; pickers = state["nativeControls"]["datePickers"]
        steps.append(dict(step=name, action=action, configuration=row["configuration"], dark=row["dark"],
            model=state["model"], displayed=[p["date"] for p in pickers], nativeInstances=row["nativeInstances"],
            frames=dict(state["frames"], start=pickers[0]["alignmentFrame"], end=pickers[1]["alignmentFrame"]),
            referenceCapture=public["path"]))
    assert len(steps) == 17
    provenance = json.loads((ROOT / "evidence/reference-investigations/date-range-20261018/provenance/helper-files.json").read_text())
    history = dict(source=str(history_path.relative_to(ROOT)), sourceSha256=hashlib.sha256(history_path.read_bytes()).hexdigest(),
        actionSource=provenance["history-v1"]["tool/DateHistory.swift"], textScale=1, dpr=1, steps=steps)
    return dict(schemaVersion=2, accepted=False, reference="fe8a1d462fbd793d883fb92086a16aa2947e32c9",
        source=str(SOURCE.relative_to(ROOT)), sourceSha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(), closed=closed, history=history)

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args=parser.parse_args()
    expected=json.dumps(generate(), indent=2, ensure_ascii=False)+"\n"
    if args.check:
        if not DEST.is_file() or DEST.read_text()!=expected: raise SystemExit("DateRangePicker witnesses are stale")
    else: DEST.write_text(expected)
    print("DateRangePicker: 384 closed observations and 17 typed history steps; acceptance remains pending")

if __name__ == "__main__": main()
