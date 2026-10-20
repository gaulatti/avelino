#!/usr/bin/env python3
"""Verify the incomplete FileInput checkpoint without approving mirror parity."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "evidence/development/file-input-20261017"


def verify():
    read = lambda name: json.loads((DIRECTORY / name).read_text())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    report = read("validation.json")
    assert report["accepted"] is False and report["implementationStatus"] == "in-progress"
    assert report["reference"] == "fe8a1d462fbd793d883fb92086a16aa2947e32c9"
    assert report["desktopCandidateCoverage"] == [75, 80]
    assert report["tolerance"] == "none" and report["approvedExceptions"] == []
    assert report["expectedImagesChanged"] is False and report["physicalDisplay"] is False
    for gate in ["nativeRaster", "directSizing", "nativeTypes", "completeChooser",
                 "nativeAccessibility", "physicalInput", "physicalReader", "independentMachine"]:
        assert report["gates"][gate] == "pending", gate
    assert report["linuxPlatform"] == "linux/arm64"
    assert set(report["missingNativeSurfaces"]) == {
        "sidebar", "back/forward", "view controls", "location menu", "search", "selection preview"}
    files = read("files.json")
    assert set(files) == {str(f.relative_to(DIRECTORY)) for f in DIRECTORY.rglob("*")
                          if f.is_file() and f.name != "files.json"}
    for name, expected in files.items():
        path = DIRECTORY / name
        assert path.stat().st_size == expected["bytes"] and digest(path) == expected["sha256"], name

    replay = read("replay/source-replay.json")
    sources = replay["snapshots"]
    assert len([name for name in sources if name.startswith("file-input-qt-v")]) == 18
    final = sources["file-input-qt-v18"]
    changed = sorted(name for name in final.keys() | sources["file-input-qt-v14"].keys()
                     if final.get(name) != sources["file-input-qt-v14"].get(name))
    assert changed == sorted(read("qt/regression-source-binding.json")["changedFiles"])
    assert read("qt/result.json")["exitCode"] == 0
    assert all(step["exitCode"] == 0 for step in read("qt/commands.json"))
    full = (DIRECTORY / "attempts/file-input-qt-v14/all-qt-tests.log").read_text()
    assert "100% tests passed, 0 tests failed out of 47" in full
    assert read("attempts/file-input-source-replay-v2/result.json")["exitCode"] == 0
    fresh = read("attempts/file-input-source-replay-v2/source-files.json")
    assert fresh == {name: row["sha256"] for name, row in sources["file-input-qt-v17"].items()}
    assert [name for name, row in final.items() if row != sources["file-input-qt-v17"][name]] == ["tests/consumer/fileinputchecks.h"]
    assert all(step["exitCode"] == 0 for step in read("attempts/file-input-source-replay-v2/commands.json"))
    assert read("full-package/result.json")["exitCode"] == 0
    full_steps = read("full-package/commands.json")
    assert next(s for s in full_steps if s["name"] == "installed-suite")["exitCode"] == 0
    script = (DIRECTORY / "full-package/check-installed.sh").read_text()
    assert sum(line.startswith("QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software consumer-build/InstalledConsumer")
               for line in script.splitlines()) == 38
    assert read("package/result.json")["exitCode"] == 0
    assert all(step["exitCode"] == 0 for step in read("package/commands.json"))
    package = read("package/inputs.json")
    assert package["consumerFiles"] == {name: row["sha256"] for name, row in sources["file-input-package-pilot-v9"].items()}
    for name, sha in package["consumerFiles"].items():
        assert final["tests/consumer/" + name]["sha256"] == sha
    portable = read("portable-replay/result.json")
    assert portable["exitCode"] == 0 and portable["restoredPackageRuntime"] is True
    assert portable["libraryAndConsumerSourceAbsent"] is True and portable["unchangedClosedImages"] == 32
    assert all(step["exitCode"] == 0 for step in read("portable-replay/commands.json"))
    for row in portable["pairs"]:
        assert digest(DIRECTORY / "captures" / row["path"]) == row["sha256"]

    comparison_spec = importlib.util.spec_from_file_location("file_input_pixels", ROOT / "scripts/compare-file-input-candidate.py")
    comparison = importlib.util.module_from_spec(comparison_spec)
    comparison_spec.loader.exec_module(comparison)
    with tempfile.TemporaryDirectory(prefix="avelino-file-input-audit-") as directory:
        directory = Path(directory)
        comparison.compare(DIRECTORY / "captures", directory / "comparison")
        actual = json.loads((directory / "comparison/observations.json").read_text())
        assert actual == read("comparison/observations.json")
        assert actual["pairs"] == actual["contractStates"] == 256
        assert actual["exactPixels"] == 0 and actual["completeFrames"] == 232
        subprocess.run(["python3", str(DIRECTORY / "replay/reconstruct.py"),
                        "--output", str(directory / "restored"), "--package"], check=True, cwd=ROOT,
                       stdout=subprocess.DEVNULL)
        binary = directory / "restored/package/consumer-build/InstalledConsumer"
        assert binary.read_bytes().startswith(b"\x7fELF")
        assert digest(binary) == read("runtime/inputs.json")["consumerSha256"]
        for name, sha in package["packageFiles"].items():
            assert digest(directory / "restored/package/install" / name) == sha

    legacy = read("checks/file-input-legacy-catalog-comparison-v3.json")
    assert legacy["byteIdenticalPairs"] == len(legacy["pairs"]) == 151
    for row in legacy["pairs"]:
        for name, sha in [("image", "imageSha256"), ("metadata", "metadataSha256")]:
            candidate = DIRECTORY / "catalogs" / row[name]
            assert digest(candidate) == row[sha]
            assert candidate.read_bytes() == (ROOT / legacy["baseline"] / row[name]).read_bytes()

    assert read("runtime/result.json")["exitCode"] == 0
    profiles = {}
    for path in (DIRECTORY / "runtime/output").glob("file-input-*.json"):
        row = json.loads(path.read_text())
        key = row["platform"], row["graphicsApi"], row["dpr"]
        assert key not in profiles
        profiles[key] = row
        assert row["fixture"] == "file-input" and row["structuralChecks"] == "passed"
        assert row["accepted"] is False and row["physicalDisplay"] is False and row["hardwareAcceleration"] is False
        assert len(row["closed"]) == len(row["sizing"]) == row["nativeContractStatesMatch"] == 32
        assert row["images"] == 35 and len(row["actions"]) == 6
        assert row["popupCaptureMethod"] == "QQuickItem::grabToImage of the entire popup window content item at native DPR; no cropping or resizing"
        assert row["nativeRasterAcceptance"] == row["physicalInputAcceptance"] == row["readerAcceptance"] == "pending"
    assert set(profiles) == {(protocol, renderer, scale) for protocol in ["xcb", "wayland"]
                             for renderer in [1, 3] for scale in [1, 2]}
    for version in [1, 2]:
        prefix = f"runtime/external-operator/file-input-wayland-operator-v{version}/"
        assert read(prefix + "operator-result-v2.json")["status"] == "passed"
        assert len(read(prefix + "operator-result-v2.json")["cycles"]) == 3
        observation = read(prefix + "render-observation.json")
        assert observation["eglSwapBuffersErrors"] == 0 and observation["physicalDisplay"] is False

    operator = read("accessibility/file-input-atspi-v4/operator-v1/operator-report.json")
    location = read("accessibility/file-input-atspi-v4/operator-location-v3/operator-report.json")
    assert operator["status"] == location["status"] == "passed"
    assert len(operator["phases"]) == 22 and len(location["phases"]) == 4
    speech = read("accessibility/file-input-atspi-v4/speech-observations.json")
    assert speech["physicalAudioHeard"] is False and speech["audioOutput"] == "ALSA null device"
    assert speech["nativeReaderComparison"] == "pending"
    assert all(speech["phraseChecks"][name] for name in
               ["Choose file…", "Files in /probe/fixtures", "one.txt", "photo.png", "child.txt", "Folder location"])
    assert speech["phraseChecks"]["No such file or directory"] is False
    observed = sources["file-input-qt-v16"]
    assert all(final[name] == row for name, row in observed.items() if name.startswith(("src/", "samples/")))
    inventory = json.loads((ROOT / "docs/parity-inventory.json").read_text())
    entry = next(e for e in inventory["desktop"]["entries"] if e["id"] == "BleeckerFileInput")
    assert entry["status"] == "pending"
    print("FileInput: 256 retained comparisons, 151 unchanged catalogs, eight display profiles and AT-SPI/Orca software observations; complete mirror pending")


if __name__ == "__main__":
    verify()
