#!/usr/bin/env python3
"""Check footer source measurements and image identity without accepting parity."""
import hashlib
import itertools
import json
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "evidence/reference-investigations/footer-slots-20261019"
CASES = {"absent", "empty-group", "zero", "empty-text", "text", "block",
         "two-blocks", "group-blocks", "hidden-block", "zero-then-block",
         "two-texts", "text-and-block", "long-text", "conditional-absent",
         "conditional-block"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read("investigation.json")
    reference = json.loads((ROOT / "reference/source-manifest.json").read_text())["references"]["desktop"]
    assert report["reference"] == reference["revision"]
    assert report["sourceArchiveSha256"] == reference["sha256"]
    for flag in ["accepted", "fullMirrorAccepted", "existingExpectedImagesChanged",
                 "independentLibraryRebuild", "independentReplay", "windowSessionObserved", "physicalInput"]:
        assert report[flag] is False, flag
    actual = {str(p.relative_to(directory)) for p in directory.rglob("*") if p.is_file()}
    assert actual == set(report["files"]) | {"investigation.json"}
    for name, checksum in report["files"].items():
        path = Path(name)
        assert not path.is_absolute() and ".." not in path.parts
        assert digest(directory / path) == checksum, name
    inputs = read("inputs.json")
    provenance = read("tooling-provenance.json")
    assert inputs["reference"] == provenance["reference"] == reference["revision"]
    assert inputs["sourceArchiveSha256"] == reference["sha256"]
    assert inputs["helperSha256"] == provenance["externalHelperSha256"]
    assert inputs["reusedLibraryObject"] is provenance["reusedSourceVerifiedLibraryObject"] is True
    assert inputs["independentLibraryRebuild"] is provenance["independentLibraryRebuild"] is False
    assert provenance["independentReplay"] is provenance["accepted"] is False
    assert inputs["libraryObjectSha256"] == "0d98b215928f864cb6874be5426360db0861eb44a049af40e556aca9e319c025"
    fixtures = read("fixtures.json")["fixtures"]
    assert len(fixtures) == len(CASES) == 15
    definitions = {row["variant"]: row for row in fixtures}
    assert set(definitions) == CASES
    data = read("captures.json")
    assert data["reference"] == reference["revision"] and data["accepted"] is False
    captures = data["captures"]
    contexts = set(itertools.product(CASES, ["light", "dark"], [1, 1.5], [1, 2]))
    assert len(captures) == 120
    assert {(c["variant"], c["appearance"], c["textScale"], c["dpr"]) for c in captures} == contexts
    raw = read("measurements.json")
    assert raw["reference"] == reference["revision"] and raw["accepted"] is False
    records = {row["path"]: row for row in raw["captures"]}
    assert len(records) == len(raw["captures"]) == 240
    identity = read("identity-audit.json")
    assert identity["reference"] == reference["revision"]
    audits = {row["path"]: row for row in identity["rows"]}
    assert len(audits) == len(identity["rows"]) == 120
    overlaps = 0
    overlap_directory = ROOT / provenance["sourceOverlapDirectory"]
    for row in captures:
        assert row["source"] == reference["revision"] and row["captureMethod"] == "SwiftUI.ImageRenderer"
        assert row["api"] == "BleeckerFooter" and (row["width"], row["height"]) == (400, 180)
        for key, value in definitions[row["variant"]].items():
            assert row[key] == value, (row["path"], key)
        bare, measured = records[row["path"]], records[row["layoutWitnessPath"]]
        assert bare["measured"] is False and measured["measured"] is True
        assert measured["path"] == bare["path"].replace(".png", "-measured.png")
        for record in [bare, measured]:
            assert record["fixture"] == row["variant"]
            assert record["dark"] is (row["appearance"] == "dark")
            assert record["textScale"] == row["textScale"] and record["dpr"] == row["dpr"]
        assert row["frames"] == measured["frames"] and row["fonts"] == measured["fonts"]
        assert bare["frames"]["component"] == row["componentRect"] == row["frames"]["component"]
        assert row["componentSize"] == {key: row["componentRect"][key] for key in ["width", "height"]}
        for frame in row["frames"].values():
            assert set(frame) == {"x", "y", "width", "height"}
            assert all(math.isfinite(value) for value in frame.values())
            assert frame["width"] >= 0 and frame["height"] >= 0
        component = row["componentRect"]
        assert component["width"] == 300 and component["x"] == 50
        assert component["y"] == (180 - component["height"]) / 2
        for font in row["fonts"].values():
            assert font["postScriptName"] == "LibreFranklin-Regular" and font["size"] == 12
        bare_path, measured_path = directory / row["path"], directory / row["layoutWitnessPath"]
        assert bare_path.read_bytes() == measured_path.read_bytes()
        audit = audits[row["path"]]
        assert audit["frames"] == row["frames"]
        assert digest(bare_path) == digest(measured_path) == row["sha256"] == bare["sha256"] == measured["sha256"] == audit["bareSha256"] == audit["instrumentedSha256"]
        assert audit["measurementByteIdentical"] is audit["measurementPixelIdentical"] is True
        with Image.open(bare_path) as image, Image.open(measured_path) as witness:
            expected_size = (400 * row["dpr"], 180 * row["dpr"])
            assert image.size == witness.size == expected_size
            assert image.convert("RGBA").tobytes() == witness.convert("RGBA").tobytes()
        if row["variant"] in {"empty-text", "text", "block"}:
            legacy = "empty" if row["variant"] == "empty-text" else row["variant"]
            expected_path = row["path"].replace("footer-slots-" + row["variant"], "footer-" + legacy)
            assert audit["existingSourcePath"] == expected_path
            assert bare_path.read_bytes() == (overlap_directory / expected_path).read_bytes()
            assert digest(bare_path) == audit["existingSourceSha256"]
            overlaps += 1
        else:
            assert "existingSourcePath" not in audit
    assert overlaps == report["existingSourceOverlap"] == identity["existingSourceByteIdentical"] == 24
    assert report["captures"] == report["transparentMeasurementPairs"] == identity["measurementByteIdentical"] == 120
    return {"sourceProfiles": 120, "measurementIdentityPairs": 120,
            "unchangedSourceOverlaps": 24, "independentReplay": False, "accepted": False}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
