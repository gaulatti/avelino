#!/usr/bin/env python3
"""Verify immutable reference artifacts in separate clean extraction directories."""
import hashlib
import json
from pathlib import Path
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def verify_reference(record, directory):
    artifact = ROOT / record["artifact"]
    assert hashlib.sha256(artifact.read_bytes()).hexdigest() == record["sha256"], artifact
    expected = {entry["path"]: entry for entry in record["files"]}
    with tarfile.open(artifact, "r:gz") as archive:
        members = archive.getmembers()
        assert all(member.isdir() or member.isfile() for member in members), "Unexpected symlink/member"
        actual = {member.name for member in members if member.isfile()}
        assert actual == set(expected), "Artifact scope mismatch"
        archive.extractall(directory, filter="data")
    for name, entry in expected.items():
        data = (directory / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == entry["sha256"], name
        blob = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        assert blob == entry["gitBlob"], name
    assert json.loads((directory / "Package.resolved").read_text()) == record["dependencies"]


def main():
    manifest = json.loads((ROOT / "reference/source-manifest.json").read_text())
    for kind in ["desktop", "television"]:
        with tempfile.TemporaryDirectory(prefix=f"avelino-{kind}-verify-") as clean:
            verify_reference(manifest["references"][kind], Path(clean))
        print(f"{kind}: clean extraction verified ({manifest['references'][kind]['revision']})")
    token = manifest["references"]["bleecker"]
    assert hashlib.sha256((ROOT / token["artifact"]).read_bytes()).hexdigest() == token["sha256"]
    print("bleecker: canonical token source verified")


if __name__ == "__main__":
    main()
