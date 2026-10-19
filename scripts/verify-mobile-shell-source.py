#!/usr/bin/env python3
"""Audit native shell observations without accepting desktop parity."""
import hashlib
import itertools
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "evidence/reference-investigations"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(directory):
    files = json.loads((directory / "files.json").read_text())["files"]
    assert set(files) == {str(p.relative_to(directory)) for p in directory.rglob("*")
                          if p.is_file() and p != directory / "files.json"}
    for name, checksum in files.items():
        assert not Path(name).is_absolute() and ".." not in Path(name).parts
        assert digest(directory / name) == checksum, name


def verify():
    reference = json.loads((ROOT / "reference/source-manifest.json").read_text())["references"]["desktop"]
    slots = BASE / "mobile-shell-slots-20261019"
    host = BASE / "desktop-shell-host-20261019"
    for directory in [slots, host]:
        inventory(directory)
        provenance = json.loads((directory / "provenance.json").read_text())
        assert provenance["reference"] == reference["revision"]
        for key in ["independentRebuild", "independentReplay", "physicalInput", "screenCapture",
                    "accepted", "existingExpectedImagesChanged"]:
            assert provenance[key] is False
        assert provenance["reusedSourceLibraryObject"] is True
        for run in provenance["runs"]:
            inputs = json.loads((directory / run["run"] / "inputs.json").read_text())
            assert inputs["reference"] == reference["revision"]
            assert inputs["sourceArchiveSha256"] == reference["sha256"]
            assert inputs["pinnedSourceFiles"] == len(reference["files"]) == 53
            assert inputs["helperSha256"] == run["helperSha256"]
            assert inputs["reusedLibraryObject"] is True and inputs["independentLibraryRebuild"] is False
            assert inputs["libraryObjectSha256"] == "0d98b215928f864cb6874be5426360db0861eb44a049af40e556aca9e319c025"
    cases = {"standard", "no-header", "no-footer", "empty-content", "all-empty", "fixed-content",
             "zero-content", "zero-header", "hidden-header", "short", "short-fixed", "short-empty",
             "narrow", "narrow-fixed", "narrow-empty", "fractional", "large-footer", "wide"}
    previous = None
    pairs = 0
    for version in [1, 2]:
        directory = slots / f"run-v{version}"
        assert json.loads((directory / "result.json").read_text())["exitCode"] == 0
        data = json.loads((directory / "output/measurements.json").read_text())
        assert data["reference"] == reference["revision"] and data["accepted"] is False
        assert len(data["profiles"]) == 72
        assert {(r["case"], r["dark"], r["dpr"]) for r in data["profiles"]} == set(itertools.product(cases,[False,True],[1,2]))
        for row in data["profiles"]:
            bare = directory / "output" / (row["name"] + ".png")
            measured = directory / "output" / (row["name"] + "-measured.png")
            assert row["measurementByteIdentical"] is True
            assert digest(bare) == row["bareSha256"] == row["measuredSha256"] == digest(measured)
            assert bare.read_bytes() == measured.read_bytes()
            with Image.open(bare) as image, Image.open(measured) as witness:
                assert image.convert("RGBA").tobytes() == witness.convert("RGBA").tobytes()
            if previous is not None:
                assert bare.read_bytes() == (previous / bare.name).read_bytes()
            pairs += 1
        previous = directory / "output"
    rows = data["profiles"]
    for row in rows:
        frames = row["frames"]
        if row["case"] == "all-empty":
            assert frames["component"] == dict(x=0,y=119.5,width=360,height=1)
        if row["case"] == "empty-content":
            assert "content" not in frames and frames["component"]["height"] == 61
        if row["case"] == "zero-content":
            assert frames["content"]["width"] == frames["content"]["height"] == 0
            assert frames["component"]["height"] == 240
        if row["case"] == "narrow-fixed":
            assert frames["component"]["width"] == 200 and frames["component"]["x"] == -50
        if row["case"] == "short-fixed":
            assert frames["component"]["height"] == 161 and frames["component"]["y"] == -68.5
    assert json.loads((host / "run-v1/result.json").read_text())["exitCode"] == 1
    assert "extraneous argument label" in (host / "run-v1/compile.log").read_text()
    hosted = json.loads((host / "run-v2/output/measurements.json").read_text())
    assert len(hosted["records"]) == 16 and hosted["physicalInput"] is hosted["screenCapture"] is hosted["accepted"] is False
    for record in hosted["records"]:
        assert record["visible"] is record["key"] is False
        if record["kind"] == "mobile":
            segments = [v for v in record["views"] if "segments" in v]
            assert len(segments) == int(record["state"])
            if record["state"]:
                assert segments[0]["frame"]["width"] == 78 and segments[0]["frame"]["height"] == 36
                assert all(s["enabled"] for s in segments[0]["segments"])
                assert record["programmaticAction"] == dict(dispatched=True,selectedSegment=1,selectionAfter="saved")
        directory = host / "run-v2/output"
        assert digest(directory / (record["name"] + ".png")) == record["contentSha256"]
        assert digest(directory / (record["name"] + "-chrome.png")) == record["chromeSha256"]
    for version in [3, 4]:
        data = json.loads((host / f"run-v{version}/output/measurements.json").read_text())
        assert len(data["records"]) == 6
        for row in data["records"]:
            assert row["owner"] in ["echo", "ignore", "delay"]
            states = row["history"]
            saved = next(s for s in states if s["step"] == "action-1-settled")
            assert saved["selectedSegment"] == 1
            assert saved["selection"] == ("saved" if row["owner"] == "echo" else "news")
            assert states[-1]["step"] == "external-unknown" and states[-1]["selectedSegment"] == -1
            if version == 4:
                disabled = next(s for s in states if s["step"] == "parent-disabled")
                assert disabled["enabled"] is False
                assert disabled["selectedSegment"] == (1 if row["owner"] == "echo" else 0)
                restored = next(s for s in states if s["step"] == "external-news")
                assert restored["selection"] == "news" and restored["selectedSegment"] == 0
    return dict(nativeSlotProfiles=72,measurementIdentityPairs=pairs,unchangedBareControls=72,
                hostedRecords=16,callerOwners=3,physicalInput=False,accepted=False)


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
