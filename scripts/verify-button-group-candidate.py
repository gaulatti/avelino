#!/usr/bin/env python3
"""Decode the compiled group checkpoint; full mirror acceptance stays pending."""
import hashlib
import itertools
import json
from pathlib import Path
import re
import subprocess

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / "evidence/development/button-group-layout-20261019"
NATIVE = ROOT / "evidence/reference-investigations/button-group-slots-20261019"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed_pixels(before, after):
    with Image.open(before) as a, Image.open(after) as b:
        a, b = a.convert("RGBA"), b.convert("RGBA")
        assert a.size == b.size
        difference = ImageChops.difference(a, b)
        mask = difference.getchannel("R")
        for channel in ["G", "B", "A"]:
            mask = ImageChops.lighter(mask, difference.getchannel(channel))
        return a.width * a.height - mask.histogram()[0]


def verify():
    read = lambda name: json.loads((CAPSULE / name).read_text())
    manifest = read("files.json")
    actual = {str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob("*") if p.is_file()}
    assert actual == set(manifest["files"]) | {"files.json"}
    for name, checksum in manifest["files"].items():
        assert not Path(name).is_absolute() and ".." not in Path(name).parts
        assert digest(CAPSULE / name) == checksum, name
    result = read("result.json")
    assert result["fullCoreTests"] == 55 and result["profiles"] == result["geometryPassed"] == 184
    for key in ["sourcePinsChanged", "expectedImagesChanged", "physicalDisplay",
                "readerAcceptance", "accepted", "fullMirrorAccepted"]:
        assert result[key] is False
    for name, checksum in read("implementation-inputs.json").items():
        assert digest(CAPSULE / "implementation-inputs" / name) == checksum, name
        if name in {"tests/components/CMakeLists.txt", "tests/components/main.cpp", "tests/consumer/main.cpp",
                    "samples/AvelinoCatalog/CMakeLists.txt", "samples/AvelinoCatalog/main.cpp"}:
            # Additive shell routing changes the shared entrypoints. Bind this
            # older compiled receipt to its actual producer; the group-owned
            # implementation and fixture inputs below remain live checks.
            original = subprocess.check_output(["git", "show", "86334226962e67d2a102b6bed720fe723a7eaae3:" + name], cwd=ROOT)
            assert hashlib.sha256(original).hexdigest() == checksum, name
        else:
            assert digest(ROOT / name) == checksum, name
    for version in [1, 2]:
        assert read(f"compiled-v{version}/result.json")["exitCode"] == 1
        assert read(f"compiled-v{version}/interruption.json")["exitCode"] == 143
        assert "FAIL!" in (CAPSULE / f"compiled-v{version}/core-tests.log").read_text()
    for version in [3, 6]:
        assert read(f"compiled-v{version}/result.json")["exitCode"] == 0
        assert all(row["exitCode"] == 0 for row in read(f"compiled-v{version}/commands.json"))
        for dpr in [1, 2]:
            text = (CAPSULE / f"compiled-v{version}/button-group-preflight-dpr{dpr}.log").read_text()
            assert len(re.findall(r"^PASS\s+:.*::test_source_frames\(", text, re.M)) == 92
            assert "0 failed" in text
    core = (CAPSULE / "compiled-v3/core-tests.log").read_text()
    assert "100% tests passed, 0 tests failed out of 55" in core
    assert len(re.findall(r"^\s*\d+/55 Test.*Passed", core, re.M)) == 55
    inherited = read("compiled-v6/core-inheritance.json")
    assert set(inherited["sourceChangesSinceFullSuite"]) == {"samples/AvelinoCatalog/main.cpp", "tests/consumer/ButtonGroupCase.qml"}
    assert inherited["sharedRowEngineUnchanged"] is True and inherited["fullSuiteRepeated"] is False
    assert inherited["logSha256"] == digest(CAPSULE / "compiled-v3/core-tests.log")
    previous, final = [read(f"compiled-v{v}/inputs.json")["sourceFiles"] for v in [3, 6]]
    assert {n for n in final if final[n] != previous[n]} == {"samples/AvelinoCatalog/main.cpp", "tests/consumer/ButtonGroupCase.qml"}
    fixture = (CAPSULE / "implementation-inputs/tests/consumer/ButtonGroupCase.qml").read_bytes()
    assert hashlib.sha256(fixture.replace(b'case "default": case "mixed-buttons":', b'case "mixed-buttons":', 1)).hexdigest() == previous["tests/consumer/ButtonGroupCase.qml"]
    contracts = read("contracts/result.json")
    assert contracts["exitCode"] == 0 and contracts["totals"][0][0] == "792"
    assert re.search(r"^Ran 792 tests in [\d.]+s\n\nOK$", (CAPSULE / "contracts/contracts.log").read_text(), re.M)
    source = json.loads((NATIVE / "captures.json").read_text())
    definitions = {r["variant"]: r for r in json.loads((NATIVE / "fixtures.json").read_text())["fixtures"]}
    runtime_definitions = read("runtime/fixtures.json")["fixtures"]
    assert len(runtime_definitions) == len(definitions) == 23
    for definition in runtime_definitions:
        definition = dict(definition)
        expected_empty = definition.pop("expectedEmpty")
        assert definition == definitions[definition["variant"]]
        frames = [r["frames"]["component"] for r in source["captures"] if r["variant"] == definition["variant"]]
        assert len(frames) == 8 and all(expected_empty is (f["width"] == 0 or f["height"] == 0) for f in frames)
    comparisons = {r["source"]: r for r in read("runtime/comparison.json")["results"]}
    assert source["reference"] == "fe8a1d462fbd793d883fb92086a16aa2947e32c9"
    assert len(source["captures"]) == len(comparisons) == 184
    exact = labels = 0
    for row in source["captures"]:
        record = comparisons[row["path"]]
        path = CAPSULE / "runtime/captures" / record["capture"]
        metadata = json.loads(Path(str(path) + ".json").read_text())
        assert metadata["qt"] == "6.8.3" and metadata["dpr"] == row["dpr"] and metadata["platform"] == "offscreen"
        assert digest(path) == record["sha256"] and digest(Path(str(path) + ".json")) == record["metadataSha256"]
        label_match = True
        for name, frame in row["frames"].items():
            actual_frame = metadata["buttonGroupFrames"][name]
            matches = all(actual_frame[axis] == value for axis, value in frame.items())
            if name in {"component", "first", "second"}:
                assert matches, (row["path"], name)
            else:
                label_match &= matches
        reference = NATIVE / record["pixelReference"]
        assert changed_pixels(reference, path) == record["changedPixels"]
        assert record["geometryPassed"] is True and record["labelGeometryPassed"] is label_match
        exact += record["changedPixels"] == 0
        labels += label_match
    runtime = read("runtime/result.json")
    assert runtime["exitCode"] == 0 and runtime["groupGeometryPassed"] == 184
    assert runtime["exactPixels"] == exact and runtime["labelGeometryPassed"] == labels
    commands = read("runtime/commands.json")
    assert len(commands) == 194 and all(r["exitCode"] == 0 for r in commands)
    assert commands[0]["name"] == "source-absence" and commands[-1]["name"] == "composition-display"
    composition = [r for r in commands if r["name"].startswith("composition-") and r["name"] != "composition-display"]
    assert len(composition) == 8
    for row in composition:
        text = (CAPSULE / "runtime" / (row["name"] + ".log")).read_text()
        assert "Installed ButtonGroup: five bare slot cases and pointer/keyboard activation passed" in text
    sessions = list((CAPSULE / "runtime/display").glob("composition-*.json"))
    assert {tuple(p.stem.removeprefix("composition-").split("-")) for p in sessions} == set(itertools.product(["xcb", "wayland"], ["software", "opengl"], ["standard", "scaled"]))
    for path in sessions:
        row = json.loads(path.read_text())
        assert row["compositionChecks"] == row["focusResizeChecks"] == "passed"
        assert row["physicalDisplay"] is row["hardwareAcceleration"] is False
        assert digest(path.with_suffix(".png")) == row["windowCaptureSha256"]
        assert digest(path.parent / row["sessionCapture"]) == row["sessionCaptureSha256"]
    alias = read("legacy-alias-identity.json")
    assert alias["byteIdentical"] == len(alias["rows"]) == 8
    for row in alias["rows"]:
        assert (CAPSULE / row["slotCapture"]).read_bytes() == (CAPSULE / row["legacyCapture"]).read_bytes()
        assert digest(CAPSULE / row["slotCapture"]) == row["sha256"]
    cold = read("cold-replay/raw-image-comparison.json")
    assert cold["count"] == cold["identical"] == len(cold["rows"]) == 437
    parent = ROOT / "evidence/development/date-range-fields-20261018"
    assert cold["parentManifestSha256"] == digest(parent / "files.json")
    expected = {r["fixture"]: r["candidateSHA256"] for r in
                json.loads((parent / "strict/comparison.json").read_text())["results"]}
    expected.update({r["candidateName"]: r["candidateSHA256"] for r in
                     json.loads((parent / "chinese-comparison.json").read_text())["results"]})
    assert len(expected) == 437
    for row in cold["rows"]:
        assert row["identical"] is True
        assert digest(CAPSULE / "cold-replay/output" / row["path"]) == expected[row["path"]] == row["expected"] == row["actual"]
    compilation = read("cold-replay/consumer-build-provenance.json")
    assert compilation["actualFreshConsumerCompilationProducer"] == "button-group-compiled-v5"
    assert compilation["consumerRecompiledDuringColdReplay"] is compilation["capturedBytesChanged"] is compilation["originalResultChanged"] is False
    assert compilation["originalResultSha256"] == digest(CAPSULE / "cold-replay/result.json")
    consumer = read("runtime/inputs.json")["runtimePackageFiles"]["consumer-build/InstalledConsumer"]
    assert set(compilation["consumerElfSha256"].values()) == {consumer}
    assert read("cold-replay/inputs.json")["consumerSha256"] == consumer
    literals = read("cold-replay/literal-validation.json")
    assert literals["checks"] == 128 and literals["nativeValueComparisons"] == 64
    for row in literals["profiles"]:
        path = CAPSULE / "cold-replay/output" / row["path"]
        assert digest(path) == row["sha256"]
        values = json.loads(path.read_text())["literalInput"]
        assert len(values) == 16 and all(v["samePixels"] and v["before"] == v["after"] for v in values)
    legacy = read("legacy-before/comparison.json")["rows"]
    assert len(legacy) == 8
    for row in legacy:
        source_path = NATIVE / "canonical" / row["source"]
        assert changed_pixels(source_path, CAPSULE / "legacy-before/captures" / row["before"]) == row["beforeChangedPixels"]
        assert changed_pixels(source_path, CAPSULE / "legacy-after" / row["after"]) == row["afterChangedPixels"]
    invalid = read("empty-contract/result.json")
    assert invalid["exitCode"] == 0 and invalid["rejected"] == len(invalid["rows"]) == 4
    for row in invalid["rows"]:
        assert row["expectedExitCode"] == row["actualExitCode"] == 6 and row["captureCreated"] is False
    smoke = read("installed-smoke/result.json")
    assert smoke["exitCode"] == 0 and smoke["consumerSmokeCommands"] == 42
    assert smoke["sourceProjectsMounted"] is smoke["otherInstalledScriptStepsExecuted"] is smoke["accepted"] is False
    source_script = ROOT / "scripts/check-installed.sh"
    # Retain the exact 42 original commands while the current script adds the
    # independently verified desktop-shell command.
    current_script = source_script.read_text()
    mobile_line = "QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software consumer-build/InstalledConsumer --mobile-shell\n"
    assert current_script.count(mobile_line) == 1
    original_script = current_script.replace(mobile_line, "", 1)
    assert smoke["sourceSha256"] == hashlib.sha256(original_script.encode()).hexdigest()
    original = [line for line in original_script.splitlines()
                if line.startswith("QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software consumer-build/InstalledConsumer")]
    assert smoke["originalCommands"] == original and len(original) == 42
    expected = [line.replace("consumer-build/InstalledConsumer", "/package/consumer-build/InstalledConsumer")
                .replace("$date_checks_dir", "/output/date").replace("$hero_checks_dir", "/output/hero") for line in original]
    assert smoke["executedCommands"] == expected
    footer = read("footer-replay/result.json")
    assert footer["exitCode"] == 0 and footer["captures"] == footer["byteIdentical"] == 120
    footer_directory = ROOT / "evidence/development/footer-layout-20261019"
    assert read("footer-replay/inputs.json")["previousFooterManifestSha256"] == digest(footer_directory / "files.json")
    for row in read("footer-replay/comparison.json")["rows"]:
        old = footer_directory / "captures" / row["path"]
        new = CAPSULE / "footer-replay/output" / row["path"]
        assert old.read_bytes() == new.read_bytes()
        assert digest(old) == row["expected"] == row["actual"]
    print(f"ButtonGroup candidate:184 native layouts,{exact} exact investigation images,55 core and792 contract tests,8 package and8 virtual display contexts,437 unchanged cold captures; mirror acceptance pending")


if __name__ == "__main__":
    verify()
