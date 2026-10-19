#!/usr/bin/env python3
"""Recompute the retained shell checkpoint without granting mirror acceptance."""
import hashlib
import itertools
import json
from pathlib import Path
import re

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / "evidence/development/mobile-shell-20261019"
NATIVE = ROOT / "evidence/reference-investigations/mobile-shell-slots-20261019/run-v2/output"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def difference(first, second):
    with Image.open(first) as a, Image.open(second) as b:
        a, b = a.convert("RGBA"), b.convert("RGBA")
        if a.size != b.size:
            return None
        delta = ImageChops.difference(a, b)
        mask = delta.getchannel("R")
        for channel in ["G", "B", "A"]:
            mask = ImageChops.lighter(mask, delta.getchannel(channel))
        return a.width * a.height - mask.histogram()[0]


def verify():
    read = lambda name: json.loads((CAPSULE / name).read_text())
    manifest = read("files.json")["files"]
    assert set(manifest) | {"files.json"} == {
        str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob("*") if p.is_file()}
    for name, checksum in manifest.items():
        assert not Path(name).is_absolute() and ".." not in Path(name).parts
        assert digest(CAPSULE / name) == checksum, name
    result = read("result.json")
    assert result["fullCoreTests"] == 55 and result["contractTests"] == 792
    assert result["sourceProfiles"] == 72 and result["bodyGeometryPassed"] == 144
    for name in ["sourcePinsChanged", "expectedImagesChanged", "physicalDisplay",
                 "readerAcceptance", "accepted", "fullMirrorAccepted"]:
        assert result[name] is False
    for name, checksum in read("implementation-inputs.json").items():
        assert digest(CAPSULE / "implementation-inputs" / name) == checksum
        assert digest(ROOT / name) == checksum, name
    compiled = read("compiled-v5/result.json")
    assert compiled["exitCode"] == 0 and compiled["freshConsumerBuild"] is True
    assert compiled["fullCoreTestsPassed"] is compiled["sourceInputsUnchanged"] is True
    core = (CAPSULE / "compiled-v5/core-tests.log").read_text()
    assert "100% tests passed, 0 tests failed out of 55" in core
    assert len(re.findall(r"^\s*\d+/55 Test.*Passed", core, re.M)) == 55
    for dpr in [1, 2]:
        text = (CAPSULE / f"compiled-v5/mobile-shell-preflight-dpr{dpr}.log").read_text()
        assert "40 passed, 0 failed" in text
    assert read("compiled-v6/result.json")["exitCode"] == 0
    final = read("compiled-v7/result.json")
    assert final["exitCode"] == 0 and final["freshConsumerBuild"] is True
    inherited = read("compiled-v7/core-inheritance.json")
    assert inherited["fullSuiteTests"] == 55 and inherited["fullSuiteRepeated"] is False
    changes = {"tests/consumer/MobileShell.qml", "src/Avelino/DesktopSectionPicker.qml",
               "tests/consumer/mobileshellchecks.h"}
    assert set(inherited["sourceChangesSinceFullSuite"]) == changes
    assert inherited["logSha256"] == digest(CAPSULE / "compiled-v5/core-tests.log")
    previous_inputs = read("compiled-v5/inputs.json")["sourceFiles"]
    final_inputs = read("compiled-v7/inputs.json")["sourceFiles"]
    assert {n for n in final_inputs if final_inputs[n] != previous_inputs[n]} == changes
    before = (CAPSULE / "compiled-v5/implementation-inputs/tests/consumer/MobileShell.qml").read_bytes()
    after = (CAPSULE / "implementation-inputs/tests/consumer/MobileShell.qml").read_bytes()
    assert after.replace(b"function ownerState()", b"function ownerState():var") == before
    assert read("runtime-v1/result.json")["exitCode"] == 1
    failed = (CAPSULE / "runtime-v1/mobile-shell-light-text1-dpr1.log").read_text()
    assert '"requests":null' in failed and "Native caller/display history differs" in failed
    assert read("runtime-v2/result.json")["exitCode"] == 0
    assert "Cannot set activeFocusOnTab" in (CAPSULE / "runtime-v2/mobile-shell-light-text1-dpr1.log").read_text()
    for dpr in [1, 2]:
        text = (CAPSULE / f"compiled-v7/mobile-shell-preflight-dpr{dpr}.log").read_text()
        assert "40 passed, 0 failed" in text
    assert read("compiled-v2/result.json")["exitCode"] == 1
    assert "fixed_control" in (CAPSULE / "compiled-v2/mobile-shell-preflight-dpr1.log").read_text()
    assert read("compiled-v3/disk-failure.json")["driverExitCode"] != 0
    assert read("compiled-v4/result.json")["exitCode"] == 1
    assert "Cannot create fresh OTP trace output directory" in (CAPSULE / "compiled-v4/core-tests.log").read_text()
    contracts = read("contracts/result.json")
    assert contracts["exitCode"] == 0
    assert re.search(r"^Ran 792 tests in [\d.]+s\n\nOK$",
                     (CAPSULE / "contracts/contracts.log").read_text(), re.M)
    sources = {row["name"]: row for row in json.loads((NATIVE / "measurements.json").read_text())["profiles"]}
    expected_inputs = json.loads((ROOT / "tests/consumer/native-mobile-shell-input-witnesses.json").read_text())
    comparison = read("runtime/comparison.json")
    assert comparison["rawPixels"] is True and comparison["pixelTolerance"] == 0
    rows = comparison["rows"]
    assert len(rows) == 144 and len({(r["context"], r["profile"]) for r in rows}) == 144
    contexts = set()
    exact = 0
    for row in rows:
        source = sources[row["profile"]]
        context = row["context"]
        contexts.add(context)
        report = read("runtime/offscreen/" + context + ".json")
        assert report["qt"] == "6.8.3" and report["platform"] == "offscreen"
        assert report["dpr"] == source["dpr"]
        assert report["appearance"] == ("dark" if source["dark"] else "light")
        assert context == f"{report['appearance']}-text{report['textScale']:g}-dpr{report['dpr']:g}"
        assert report["geometryPassed"] == 18 and report["structuralChecks"] == "passed"
        assert report["nativeStateChecks"] == 25 and report["pointerActions"] == 12
        assert report["qtSpaceActivation"] is True and report["qtAccessibilityInterfaces"] == 2
        assert report["qtFocusScope"] is True and report["qtTabFocusEntries"] == 1
        assert "Cannot set activeFocusOnTab" not in (CAPSULE / "runtime" / ("mobile-shell-" + context + ".log")).read_text()
        for key in ["physicalDisplay", "readerAcceptance", "accepted",
                    "nativeKeyboardEquivalentVerified", "nativeToolbarRasterAccepted"]:
            assert report[key] is False
        assert len(report["nativeOwnerHistories"]) == 3
        for actual, expected in zip(report["nativeOwnerHistories"], expected_inputs["histories"]):
            assert actual["owner"] == expected["owner"]
            settled = [step for step in expected["history"]
                       if not step["step"].endswith("-immediate") and step["step"] != "right-arrow"]
            assert len(settled) == len(actual["steps"])
            for observed, native in zip(actual["steps"], settled):
                assert all(observed[key] == value for key, value in native.items())
        layout = next(r for r in report["layouts"] if r["name"] == row["profile"])
        assert layout["frames"] == source["frames"] and layout["geometryPassed"] is True
        capture = CAPSULE / "runtime/offscreen" / layout["capture"]
        overscan = CAPSULE / "runtime/offscreen" / layout["overscanCapture"]
        viewport = layout["captureViewport"]
        assert viewport["x"] == viewport["y"] == 0
        with Image.open(overscan) as raw, Image.open(capture) as retained:
            assert raw.width >= viewport["width"] and raw.height >= viewport["height"]
            crop = raw.crop((0, 0, viewport["width"], viewport["height"]))
            assert crop.size == retained.size and crop.convert("RGBA").tobytes() == retained.convert("RGBA").tobytes()
        reference = NATIVE / (source["name"] + ".png")
        assert digest(reference) == row["sourceSha256"] and digest(capture) == row["sha256"]
        changed = difference(reference, capture)
        assert row["dimensionsMatch"] is True and changed is not None
        assert changed == row["changedPixels"]
        exact += changed == 0
    assert contexts == {f"{theme}-text{scale}-dpr{dpr}" for theme, scale, dpr in
                        itertools.product(["light", "dark"], ["1", "1.5"], [1, 2])}
    runtime = read("runtime/result.json")
    assert runtime["exitCode"] == 0 and runtime["bodyCaptures"] == runtime["bodyGeometryPassed"] == 144
    assert runtime["exactPixels"] == exact and runtime["pixelDimensionFailures"] == 0
    sessions = list((CAPSULE / "runtime/display").glob("mobile-shell-*.json"))
    assert {tuple(p.stem.removeprefix("mobile-shell-").split("-")) for p in sessions} == set(
        itertools.product(["xcb", "wayland"], ["software", "opengl"], ["standard", "scaled"]))
    for path in sessions:
        report = json.loads(path.read_text())
        assert report["structuralChecks"] == "passed" and report["nativeStateChecks"] == 25
        assert report["qtFocusScope"] is True and report["qtTabFocusEntries"] == 1
        assert "Cannot set activeFocusOnTab" not in path.with_suffix(".log").read_text()
        assert report["physicalDisplay"] is report["hardwareAcceleration"] is False
        assert digest(path.with_suffix(".png")) == report["windowCaptureSha256"]
        assert digest(path.parent / report["sessionCapture"]) == report["sessionCaptureSha256"]
    identity = read("runtime/body-focus-identity.json")
    assert identity["count"] == identity["byteIdentical"] == len(identity["rows"]) == 144
    for row in identity["rows"]:
        before = CAPSULE / "runtime-v2/offscreen" / row["path"]
        after = CAPSULE / "runtime/offscreen" / row["path"]
        assert before.read_bytes() == after.read_bytes()
        assert digest(after) == row["sha256"] and row["byteIdentical"] is True
    for name, count, parent, folder in [
        ("footer-replay", 120, "footer-layout-20261019", "captures"),
        ("button-group-replay", 184, "button-group-layout-20261019", "runtime/captures"),
    ]:
        replay = read(name + "/result.json")
        assert replay["exitCode"] == 0 and replay["captures"] == replay["byteIdentical"] == count
        for row in read(name + "/comparison.json")["rows"]:
            old = ROOT / "evidence/development" / parent / folder / row["path"]
            new = CAPSULE / name / "output" / row["path"]
            assert old.read_bytes() == new.read_bytes()
            assert digest(old) == row["expected"] == row["actual"]
    cold = read("date-replay/raw-image-comparison.json")
    assert cold["count"] == cold["identical"] == len(cold["rows"]) == 437
    for row in cold["rows"]:
        assert row["identical"] is True
        assert digest(CAPSULE / "date-replay/output" / row["path"]) == row["actual"] == row["expected"]
    assert read("date-replay/literal-validation.json")["checks"] == 128
    smoke = read("installed-smoke/result.json")
    assert smoke["exitCode"] == 0 and smoke["consumerSmokeCommands"] == 43
    assert smoke["sourceProjectsMounted"] is smoke["otherInstalledScriptStepsExecuted"] is False
    assert smoke["sourceSha256"] == digest(ROOT / "scripts/check-installed.sh")
    gallery = read("gallery/result.json")
    assert gallery["exitCode"] == 0 and gallery["sourceFree"] is True
    assert len(gallery["captures"]) == 4 and gallery["nativeToolbarRasterAccepted"] is False
    for row in gallery["captures"]:
        path = CAPSULE / "gallery/output" / row["path"]
        assert digest(path) == row["sha256"]
        assert digest(Path(str(path) + ".json")) == row["metadataSha256"]
        metadata = json.loads(Path(str(path) + ".json").read_text())
        assert metadata["mobileShell"]["toolbarCount"] == 2
        with Image.open(path) as image:
            assert image.size == (1120 * metadata["dpr"], 780 * metadata["dpr"])
    print(f"Mobile shell candidate: 144 native layouts, {exact} exact body images, 25 caller states in eight package contexts; 55 core, 792 contract and 43 smoke checks; mirror acceptance pending")


if __name__ == "__main__":
    verify()
