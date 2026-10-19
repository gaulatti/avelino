#!/usr/bin/env python3
"""Publish unchanged native slot observations for the independent consumer."""
import argparse
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evidence/reference-investigations/mobile-shell-slots-20261019/run-v2/output/measurements.json"
TARGET = ROOT / "tests/consumer/native-mobile-shell-witnesses.json"
INPUT_SOURCE = ROOT / "evidence/reference-investigations/desktop-shell-host-20261019/run-v4/output/measurements.json"
INPUT_TARGET = ROOT / "tests/consumer/native-mobile-shell-input-witnesses.json"


def generate():
    source = json.loads(SOURCE.read_text())
    assert source["reference"] == "fe8a1d462fbd793d883fb92086a16aa2947e32c9"
    assert len(source["profiles"]) == 72 and all(r["measurementByteIdentical"] for r in source["profiles"])
    for row in source["profiles"]:
        image = SOURCE.parent / (row["name"] + ".png")
        row["pixelWidth"], row["pixelHeight"] = struct.unpack(">II", image.read_bytes()[16:24])
    return json.dumps(source, indent=2, sort_keys=True) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    input_source = json.loads(INPUT_SOURCE.read_text())
    histories = [r for r in input_source["records"] if not r["measured"]]
    assert len(histories) == 3 and {r["owner"] for r in histories} == {"echo", "ignore", "delay"}
    input_data = json.dumps({"reference": input_source["reference"], "histories": histories,
                             "physicalInput": False, "accepted": False}, indent=2, sort_keys=True) + "\n"
    for target, data in [(TARGET, generate()), (INPUT_TARGET, input_data)]:
        if args.check:
            assert target.read_text() == data, "Mobile shell witnesses differ from the unchanged source measurements"
        else:
            target.write_text(data)
