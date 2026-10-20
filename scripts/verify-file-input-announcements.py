#!/usr/bin/env python3
"""Audit the scoped chooser-announcement correction without accepting parity."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "evidence/development/file-input-announcements-20261017"


def verify():
    read = lambda name: json.loads((DIRECTORY / name).read_text())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    report = read("validation.json")
    assert report["accepted"] is False and report["implementationStatus"] == "in-progress"
    assert report["desktopCandidateCoverage"] == [75, 80]
    assert report["tolerance"] == "none" and report["approvedExceptions"] == []
    assert report["expectedImagesChanged"] is False and report["physicalDisplay"] is False
    assert report["nativeReaderComparison"] == report["completeChooser"] == "pending"
    assert report["finalFullQtSuiteRerun"] is False
    files = read("files.json")
    assert set(files) == {str(p.relative_to(DIRECTORY)) for p in DIRECTORY.rglob("*")
                          if p.is_file() and p.name != "files.json"}
    for name, row in files.items():
        path = DIRECTORY / name
        assert path.stat().st_size == row["bytes"] and digest(path) == row["sha256"], name

    binding = read("source-binding.json")
    assert binding["baseGit"] == "59fd2e8d2c97fe3d89a3b71aaa1760ddd6807040"
    assert binding["finalProducer"] == "file-input-qt-v21"
    assert binding["changedFiles"] == ["src/Avelino/FileChooserDialog.qml", "tests/components/fileinput-ui.cpp"]
    assert len(binding["files"]) == 549
    tree = {row.split(b"\t", 1)[1].decode(): row.split(b"\t", 1)[0].split()[2].decode()
            for row in subprocess.check_output(["git", "ls-tree", "-rz", "--full-tree", binding["baseGit"]], cwd=ROOT).split(b"\0") if row}
    with subprocess.Popen(["git", "cat-file", "--batch"], cwd=ROOT,
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE) as git:
        for name, row in binding["files"].items():
            assert tree[name] == row["baseBlob"]
            git.stdin.write((row["baseBlob"] + "\n").encode())
            git.stdin.flush()
            header = git.stdout.readline().split()
            assert header[:2] == [row["baseBlob"].encode(), b"blob"]
            data = git.stdout.read(int(header[2]))
            assert git.stdout.read(1) == b"\n"
            assert hashlib.sha256(data).hexdigest() == row["baseSha256"], name
            for snapshot, source in binding["snapshots"].items():
                if name in binding["changedBySnapshot"][snapshot]:
                    folder = "overlay" if snapshot == binding["finalProducer"] else "source-overlays/" + snapshot
                    assert digest(DIRECTORY / folder / name) == source[name]
                else:
                    assert source[name] == row["baseSha256"]
            assert binding["snapshots"][binding["finalProducer"]][name] == row["finalSha256"]
        git.stdin.close()
        assert git.wait() == 0

    prefix = "attempts/file-input-qt-v21/"
    assert read(prefix + "inputs.json")["files"] == binding["snapshots"][binding["finalProducer"]]
    assert read(prefix + "result.json")["exitCode"] == 0
    steps = read(prefix + "commands.json")
    assert [s["name"] for s in steps] == ["configure", "foundation-build", "foundation-tests",
                                         "backend-build", "backend-tests", "ui-build", "ui-tests", "install"]
    assert all(s["exitCode"] == 0 for s in steps)
    for name in ["foundation-tests", "backend-tests", "ui-tests"]:
        assert "100% tests passed, 0 tests failed out of 2" in (DIRECTORY / (prefix + name + ".log")).read_text()
    assert "initialLocationErrorAndClosedAnnouncement" in (DIRECTORY / "final-ui-LastTest.log").read_text()

    prefix = "attempts/file-input-announcement-package-v3/"
    package = read(prefix + "inputs.json")
    assert package["producer"] == binding["finalProducer"]
    assert package["consumerSourceChanged"] is False
    assert package["consumerSha256"] == "e5f2fe965c45add427880e7473305b424828f84bbcb0717a80204c525b0141ff"
    old_package = json.loads((ROOT / "evidence/development/file-input-20261017/package/inputs.json").read_text())
    for name, sha in old_package["consumerFiles"].items():
        assert binding["snapshots"][binding["finalProducer"]]["tests/consumer/" + name] == sha
    images = read("attempts/recovered-toolchain-v1/image-inspect.json")
    assert package["imageId"] == images[package["image"]]["Id"]
    assert images[package["image"]]["Architecture"] == "arm64"
    assert read("attempts/recovered-toolchain-v1/qt-version.json")["qt"] == "6.8.3"
    assert read(prefix + "result.json")["consumerSourceAbsent"] is True
    commands = read(prefix + "commands.json")
    assert len(commands) == 8 and all(c["exitCode"] == 0 for c in commands)
    baseline = ROOT / "evidence/development/file-input-20261017/captures"
    contexts = list((DIRECTORY / (prefix + "output")).glob("*.json"))
    assert len(contexts) == 8
    closed = []
    for path in contexts:
        current = json.loads(path.read_text())
        previous = json.loads((baseline / path.name).read_text())
        assert current["closed"] == previous["closed"] and current["sizing"] == previous["sizing"]
        assert current["accepted"] is False and current["nativeRasterAcceptance"] == "pending"
        for row in current["closed"]:
            name = path.stem + "-" + row["configuration"]["id"] + ".png"
            image = path.parent / name
            assert image.read_bytes() == (baseline / name).read_bytes(), name
            closed.append(image)
    assert len(closed) == 256
    visual = read(prefix + "visual-binding.json")
    assert visual["byteIdenticalClosedImages"] == visual["pairs"] == 256
    assert visual["closedAndSizingMetadataUnchanged"] is True

    for version, count, platform in [(6, 4, "xcb"), (7, 5, "wayland")]:
        prefix = f"attempts/file-input-error-reader-v{version}/"
        inputs = read(prefix + "inputs.json")
        assert inputs["producer"] == binding["finalProducer"]
        assert inputs["packageFiles"] == package["packageFiles"]
        assert inputs["imageId"] == images[inputs["image"]]["Id"]
        assert read(prefix + "session-result.json")["exitCode"] == 0
        assert read(prefix + "exercise-result.json")["exitCode"] == 0
        speech_result = read(prefix + "speech-observations.json")
        assert speech_result["status"] == "passed" and speech_result["logReadAfterSessionExit"] is True
        assert speech_result["announcementEvents"] == speech_result["orcaErrorUtterances"] == count
        assert speech_result["physicalAudioHeard"] is False and speech_result["speechDispatcher"]
        result = read(prefix + "operator-errors-v2/result.json")
        assert result["status"] == "passed" and result["accepted"] is False
        assert result["physicalListening"] is False and result["audioOutput"] == "ALSA null device"
        assert result["nativeReaderComparison"] == "pending" and result["profile"]["platform"] == platform
        events = [json.loads(line) for line in (DIRECTORY / (prefix + "events.jsonl")).read_text().splitlines()]
        announcements = [event for event in events if event["event"] == "object:announcement"]
        assert announcements == result["announcementEvents"] and len(announcements) == count
        assert all(e["detail1"] == 2 and e["message"] == "No such file or directory" for e in announcements)
        phases = {p["phase"] for p in result["phases"]}
        assert {"identical-location-retry-announced", "location-recovered", "retained-initial-error-on-reopen",
                "cancelled-no-extra-announcement", "final-cancel-no-extra-announcement"} <= phases
        if version == 7:
            assert "initial-error-announced" in phases and result["profile"]["dpr"] == 2
        speech = (DIRECTORY / (prefix + "orca-debug.log")).read_text()
        assert speech.count("SPEECH OUTPUT: 'No such file or directory") == count
        assert "Orca 46.1" in (DIRECTORY / (prefix + "orca-stdout.log")).read_text() or "orca\t46.1" in (DIRECTORY / (prefix + "package-versions.txt")).read_text()

    inventory = json.loads((ROOT / "docs/parity-inventory.json").read_text())
    assert next(e for e in inventory["desktop"]["entries"] if e["id"] == "BleeckerFileInput")["status"] == "pending"
    print("FileInput announcements: fresh six-target Qt checks, X11/Wayland Orca, 256 unchanged closed images; full parity pending")


if __name__ == "__main__":
    verify()
