#!/usr/bin/env python3
"""Audit actual Docker COPY controls without claiming a full toolchain build."""
import hashlib
import json
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / "evidence/development/qt-rectangle-build-context-20261020"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    members = json.loads((CAPSULE / "files.json").read_text())
    actual = {str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob("*")
              if p.is_file() and p.name != "files.json"}
    assert actual == set(members)
    for name, checksum in members.items():
        assert digest(CAPSULE / name) == checksum, name
    inputs = json.loads((CAPSULE / "inputs.json").read_text())
    result = json.loads((CAPSULE / "result.json").read_text())
    canonical = (ROOT / "tools/Dockerfile").read_bytes()
    assert canonical == (CAPSULE / "canonical.Dockerfile").read_bytes()
    assert digest(CAPSULE / "canonical.Dockerfile") == inputs["canonicalDockerfileSha256"]
    copies = [line for line in canonical.decode().splitlines() if line.startswith("COPY ")]
    assert (CAPSULE / "Dockerfile").read_text() == "FROM scratch\n" + "\n".join(copies) + "\n"
    assert digest(CAPSULE / "Dockerfile") == inputs["probeDockerfileSha256"]
    sources = [name for line in copies for name in shlex.split(line)[1:-1]]
    assert len(sources) == len(set(sources)) == 12
    assert set(sources) == set(inputs["sources"])
    for name, checksum in inputs["sources"].items():
        assert digest(ROOT / name) == checksum == digest(CAPSULE / "exported" / Path(name).name), name
    assert len(list((CAPSULE / "exported").iterdir())) == 12
    before = subprocess.check_output(
        ["git", "show", inputs["sourceRevision"] + ":.dockerignore"], cwd=ROOT)
    assert before == (CAPSULE / "before.dockerignore").read_bytes()
    additions = ["install-qt-software-rectangle.sh", "qt-software-rectangle.patch",
                 "qt-software-rectangle.cpp", "check-qt-software-rectangle.sh"]
    expected = before + "".join("!tools/" + name + "\n" for name in additions).encode()
    assert expected == (CAPSULE / "after.dockerignore").read_bytes() == (ROOT / ".dockerignore").read_bytes()
    assert digest(CAPSULE / "before.dockerignore") == result["beforeIgnoreSha256"]
    assert digest(CAPSULE / "after.dockerignore") == result["afterIgnoreSha256"]
    negative = json.loads((CAPSULE / "negative-command.json").read_text())
    positive = json.loads((CAPSULE / "positive-command.json").read_text())
    assert negative["exitCode"] != 0 and positive["exitCode"] == 0
    assert '"/tools/qt-software-rectangle.patch": not found' in (CAPSULE / "negative.log").read_text()
    assert "exporting to client" in (CAPSULE / "positive.log").read_text()
    ci = json.loads((CAPSULE / "ci-run.json").read_text())
    assert ci["headSha"] == "f16180ebb50490721851180738c904cbeabedffd"
    assert ci["conclusion"] == "failure"
    log = (CAPSULE / "ci-build-failure.log").read_text()
    for runner in ["ubuntu-24.04", "ubuntu-24.04-arm"]:
        job = next(j for j in ci["jobs"] if j["name"] == f"build-runtime-package ({runner})")
        assert job["conclusion"] == "failure"
        assert any(f"build-runtime-package ({runner})\t" in line and
                   '"/tools/qt-software-rectangle.patch": not found' in line
                   for line in log.splitlines())
    assert result["exitCode"] == 0 and result["exportedFiles"] == 12
    assert result["negativeControlFailedAsExpected"] and result["positiveBuildPassed"]
    assert result["byteIdentitiesMatched"]
    for key in ["fullToolchainBuild", "applicationCompilation", "nativeAcceptance", "accepted"]:
        assert result[key] is False
    return dict(exportedCopyInputs=12, negativeControl=True, positiveControl=True,
                fullToolchainBuild=False, accepted=False)


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
