#!/usr/bin/env python3
"""Audit the Linux teardown correction without accepting native mirror parity."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "evidence/development/item-lifetime-20261017"


def verify():
    read = lambda name: json.loads((DIRECTORY / name).read_text())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    report = read("validation.json")
    assert report["accepted"] is False and report["physicalDisplay"] is False
    assert report["baseGit"] == "a411c51b58810bf7df84eb72ae3271637c1274ab"
    assert report["baselineCases"] == 40 and report["baselineSurvived"] == 24
    assert report["baselineIncorrectTypeAborts"] == 16
    assert report["fixedMatrixChecksPerScale"] == 42 and report["fixedScales"] == [1, 2]
    assert report["sourceAbsentConsumerModes"] == 37
    assert report["installedCatalogs"] == report["unchangedCatalogPairs"] == 151
    assert report["expectedImagesChanged"] is False and report["readerAcceptance"] == "pending"
    assert report["approvedExceptions"] == [] and report["tolerance"] == "none"
    files = read("files.json")
    assert set(files) == {str(f.relative_to(DIRECTORY)) for f in DIRECTORY.rglob("*")
                          if f.is_file() and f.name != "files.json"}
    for name, expected in files.items():
        path = DIRECTORY / name
        assert path.stat().st_size == expected["bytes"] and digest(path) == expected["sha256"], name
    baseline = read("attempts/item-lifetime-matrix-baseline-v1/result.json")["repros"]
    inputs = read("attempts/item-lifetime-matrix-baseline-v1/inputs.json")
    for name, sha in inputs["sourceFiles"].items():
        data = subprocess.check_output(["git", "show", report["baseGit"] + ":" + name], cwd=ROOT)
        assert hashlib.sha256(data).hexdigest() == sha, name
    assert sum(value == 0 for value in baseline.values()) == 24
    assert sum(value == 133 for value in baseline.values()) == 16
    classes = dict(inherited="InheritedControl", radio="RadioGroupBase", charts="ChartRenderer",
                   spotlight="SpotlightRows", mask="SoftwareContentMask")
    for name, code in baseline.items():
        if code:
            kind = name.removeprefix("repro-").rsplit("-", 1)[0]
            log = (DIRECTORY / "attempts/item-lifetime-matrix-baseline-v1" / (name + ".log")).read_text()
            assert f"ASSERT failure in {classes[kind]}:" in log
    fixed = read("attempts/item-lifetime-fixed-v1/inputs.json")
    assert fixed["containsFileInputImplementation"] is False
    for name, sha in report["sourceOverlay"].items():
        assert digest(DIRECTORY / "overlay" / name) == sha == fixed["files"][name]
    for scale in [1, 2]:
        log = DIRECTORY / f"attempts/item-lifetime-signal-tests-v2/tests-dpr{scale}.log"
        assert "Totals: 42 passed, 0 failed" in log.read_text()
        qml = DIRECTORY / f"attempts/item-lifetime-fixed-v1/qml-tests-dpr{scale}.log"
        assert "Totals: 3 passed, 0 failed" in qml.read_text()
    supplement = DIRECTORY / "attempts/item-lifetime-signal-tests-v2/itemlifetime.cpp"
    assert supplement.read_bytes() == (DIRECTORY / "overlay/tests/components/itemlifetime.cpp").read_bytes()
    assert read("attempts/item-lifetime-package-v1/result.json")["exitCode"] == 0
    assert read("portable-replay/result.json")["sourceBuildReplayPassed"] is True
    assert all(step["exitCode"] == 0 for step in read("portable-replay/commands.json"))
    restored = read("portable-replay/source-files.json")
    for path in (DIRECTORY / "overlay").rglob("*"):
        if path.is_file():
            assert restored[str(path.relative_to(DIRECTORY / "overlay"))] == digest(path)
    regression = read("catalog-regression.json")
    assert regression["status"] == "passed" and len(regression["records"]) == 151
    for row in regression["records"]:
        for suffix, key in [("", "sha256"), (".json", "metadataSha256")]:
            path = DIRECTORY / "catalogs" / (row["path"] + suffix)
            assert digest(path) == row[key]
            assert path.read_bytes() == (ROOT / regression["baseline"] / (row["path"] + suffix)).read_bytes()
    print("Qt lifetime: 40 corrected cases at both scales, QML removal, 37 installed modes and 151 unchanged catalogs; native acceptance pending")


if __name__ == "__main__":
    verify()
