#!/usr/bin/env python3
"""Verify the CI ownership failure, Linux reproducer and exact workflow repair."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "evidence/development/ci-artifact-ownership-20261019"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ownership_step(workflow):
    marker=b'      - name: Preserve Qt software-renderer build evidence\n'
    assert workflow.count(marker)==1, 'The ownership-preserving toolchain step must remain present'
    return marker+workflow.split(marker,1)[1].split(b'\n      - ',1)[0]


def verify(directory=DIRECTORY):
    directory = Path(directory)
    report = json.loads((directory / "files.json").read_text())
    files = {str(p.relative_to(directory)) for p in directory.rglob("*") if p.is_file()}
    assert files == set(report["files"]) | {"files.json"}
    for name, checksum in report["files"].items():
        assert not Path(name).is_absolute() and ".." not in Path(name).parts
        assert digest(directory / name) == checksum, name
    assert report["fullWorkflowExecuted"] is report["accepted"] is False
    before, after = [(directory / name).read_bytes() for name in ["linux-before.yml.txt", "linux-after.yml.txt"]]
    recorded = subprocess.check_output(["git", "show",
        "3a93a7fdb6f14ba4cf2ed1b02f0d4ddd96021b41:.github/workflows/linux.yml"], cwd=ROOT)
    assert before == recorded
    expected = before.replace(b'        run: |\n          docker run --rm -v "$PWD/artifacts:/evidence"',
        b'        run: |\n          mkdir -p artifacts/linux/toolchain\n          docker run --rm -v "$PWD/artifacts/linux/toolchain:/evidence"', 1)
    expected = expected.replace(b'            mkdir -p /evidence/linux/toolchain\n            cp -R /opt/qt/share/avelino/qt-software-opacity /evidence/linux/toolchain/',
        b'            cp -R /opt/qt/share/avelino/qt-software-opacity /evidence/', 1)
    current = (ROOT / ".github/workflows/linux.yml").read_bytes()
    # The later rectangle stage has its own SDK receipt. Preserve this repair's
    # exact ownership and copy destination while allowing that additive receipt.
    current = current.replace(b'            cp -R /opt/qt/share/avelino/qt-software-rectangle /evidence/\n', b'', 1)
    assert before != after == expected
    assert ownership_step(current)==ownership_step(after), 'The live toolchain copy must retain its prepared leaf mount and copy destination'
    job = (directory / "x86-job-118142225917.log.txt").read_text()
    assert "mkdir: cannot create directory ‘artifacts/package’: Permission denied" in job
    assert "Process completed with exit code 1" in job
    command = json.loads((directory / "command.json").read_text())
    assert command["exitCode"] == 0 and command["probeSha256"] == digest(directory / "probe.py")
    probe = json.loads((directory / "probe.stdout.json").read_text())
    assert probe["actualLinuxPermissions"] is True
    assert probe["fullWorkflowExecuted"] is probe["accepted"] is False
    assert len(probe["rows"]) == 2
    old, fixed = probe["rows"]
    assert old["fixed"] is False and fixed["fixed"] is True
    assert old["artifactsOwnerUid"] == old["toolchainCopyOwnerUid"] == fixed["toolchainCopyOwnerUid"] == 0
    assert fixed["artifactsOwnerUid"] == fixed["seed"]["uid"] == 1001
    assert old["seed"]["exitCode"] == 1 and "Permission denied" in old["seed"]["stderr"]
    assert fixed["hostPreparation"]["command"] == "mkdir -p artifacts/linux/toolchain"
    assert fixed["hostPreparation"]["exitCode"] == fixed["seed"]["exitCode"] == 0
    assert old["seed"]["command"] == fixed["seed"]["command"]
    assert old["rootCopyPreservedFiles"] == fixed["rootCopyPreservedFiles"] > 0
    return {"linuxOwnershipReproduced": True, "fixedSeedPassed": True,
            "liveWorkflowMatchesRepair": True, "remoteCiPassed": False, "accepted": False}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
