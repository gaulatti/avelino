#!/usr/bin/env python3
"""Verify source slot measurements without changing expected captures or acceptance."""
import hashlib
import itertools
import json
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "evidence/reference-investigations/button-group-slots-20261019"
CASES = {
    "mixed-buttons", "absent", "empty-group", "zero", "block", "two-blocks",
    "group-blocks", "hidden-block", "zero-then-block", "conditional-absent",
    "conditional-block", "spacing-zero", "spacing-fractional", "constrained-110",
    "wide-300", "spacing-negative", "spacing-overlap", "spacing-very-large",
    "rtl-blocks", "rtl-buttons", "fractional-blocks", "constrained-zero", "constrained-20",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    reference = json.loads((ROOT / "reference/source-manifest.json").read_text())["references"]["desktop"]
    report = read("investigation.json")
    assert report["reference"] == reference["revision"]
    assert report["sourceArchiveSha256"] == reference["sha256"]
    for key in ["accepted", "fullMirrorAccepted", "existingExpectedImagesChanged",
                "independentLibraryRebuild", "independentReplay", "windowSessionObserved",
                "physicalInput", "broadHelperRasterEquivalentToCanonical"]:
        assert report[key] is False, key
    actual = {str(p.relative_to(directory)) for p in directory.rglob("*") if p.is_file()}
    assert actual == set(report["files"]) | {"investigation.json"}
    for name, checksum in report["files"].items():
        assert not Path(name).is_absolute() and ".." not in Path(name).parts
        assert digest(directory / name) == checksum, name
    definitions = read("fixtures.json")
    assert definitions["reference"] == reference["revision"]
    definitions = {row["variant"]: row for row in definitions["fixtures"]}
    assert set(definitions) == CASES and len(definitions) == report["cases"] == 23
    provenance = read("tooling-provenance.json")
    assert provenance["reference"] == reference["revision"]
    assert provenance["reusedSourceVerifiedLibraryObject"] is True
    assert provenance["independentLibraryRebuild"] is provenance["independentReplay"] is False
    captures = read("captures.json")
    assert captures["reference"] == reference["revision"] and captures["accepted"] is False
    captures = captures["captures"]
    expected = set(itertools.product(CASES, ["light", "dark"], [1, 1.5], [1, 2]))
    assert len(captures) == report["captures"] == report["transparentMeasurementPairs"] == 184
    assert {(r["variant"], r["appearance"], r["textScale"], r["dpr"]) for r in captures} == expected
    records = {}
    for run in provenance["runs"]:
        prefix = run["run"]
        inputs, result, measurements = [read(prefix + "/" + n) for n in
                                       ["inputs.json", "result.json", "measurements.json"]]
        assert inputs["reference"] == result["reference"] == measurements["reference"] == reference["revision"]
        assert inputs["sourceArchiveSha256"] == reference["sha256"]
        assert inputs["libraryObjectSha256"] == "0d98b215928f864cb6874be5426360db0861eb44a049af40e556aca9e319c025"
        assert inputs["reusedLibraryObject"] is True and inputs["independentLibraryRebuild"] is False
        assert inputs["helperSha256"] == result["helperSha256"] == run["helperSha256"]
        assert result["exitCode"] == 0
        for row in measurements["captures"]:
            name = prefix + "/" + row["path"]
            assert name not in records
            records[name] = row
    assert len(records) == 368
    for row in captures:
        assert row["source"] == reference["revision"] and row["captureMethod"] == "SwiftUI.ImageRenderer"
        for key, value in definitions[row["variant"]].items():
            assert row[key] == value, (row["path"], key)
        bare, measured = records[row["path"]], records[row["layoutWitnessPath"]]
        assert bare["measured"] is False and measured["measured"] is True
        for record in [bare, measured]:
            assert record["fixture"] == row["variant"]
            assert record["dark"] is (row["appearance"] == "dark")
            assert record["textScale"] == row["textScale"] and record["dpr"] == row["dpr"]
        assert measured["frames"] == row["frames"] and measured["fonts"] == row["fonts"]
        assert bare["frames"]["component"] == row["frames"]["component"] == row["componentRect"]
        for frame in row["frames"].values():
            assert set(frame) == {"x", "y", "width", "height"}
            assert all(math.isfinite(v) for v in frame.values())
            assert frame["width"] >= 0 and frame["height"] >= 0
        component = row["frames"]["component"]
        assert component["x"] == (320 - component["width"]) / 2
        assert component["y"] == (180 - component["height"]) / 2
        if row["variant"] == "spacing-overlap":
            assert component["width"] == 80
            assert row["frames"]["second"]["x"] - component["x"] == -120
        before, after = directory / row["path"], directory / row["layoutWitnessPath"]
        assert before.read_bytes() == after.read_bytes()
        assert digest(before) == row["sha256"] == bare["sha256"] == measured["sha256"]
        with Image.open(before) as image, Image.open(after) as witness:
            assert image.size == witness.size == (320 * row["dpr"], 180 * row["dpr"])
            assert image.convert("RGBA").tobytes() == witness.convert("RGBA").tobytes()
    control = read("canonical/full-order-comparison.json")
    inputs = read("canonical/inputs.json")
    assert inputs["helperSha256"] == provenance["canonicalHelperSha256"] == "b4d26ad3acd0bbc9cd68212cd3895fdad0c9101a8088acd8aac9c9565c2cad8e"
    assert control["captureOrder"] == "Original full fixture order"
    assert control["canonicalHelperUnchanged"] is True and control["independentLibraryRebuild"] is False
    assert control["captures"] == control["byteIdentical"] == control["pixelIdentical"] == len(control["rows"]) == 8
    for row in control["rows"]:
        current = ROOT / "evidence/reference-proposals/desktop-20261012" / row["path"]
        replay = directory / "canonical" / row["path"]
        assert digest(current) == digest(replay) == row["sha256"] == row["referenceSha256"]
        assert current.read_bytes() == replay.read_bytes()
        assert row["changedPixels"] == 0 and row["byteIdentical"] is True
    return {"sourceProfiles": 184, "measurementIdentityPairs": 184,
            "unchangedCanonicalControls": 8, "independentLibraryRebuild": False, "accepted": False}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
