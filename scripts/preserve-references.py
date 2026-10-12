#!/usr/bin/env python3
"""Explicit initial preservation; never called by CI or reference verification."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "desktop": "fe8a1d462fbd793d883fb92086a16aa2947e32c9",
    "television": "f5ac479bfceaa7eab23c1716ac47420ac53dae25",
}
SCOPE = ["Package.swift", "Package.resolved", "Sources"]


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def sha(data):
    return hashlib.sha256(data).hexdigest()


def preserve(repo):
    destination = ROOT / "reference/source-manifest.json"
    if destination.exists():
        raise SystemExit("References already exist; use an explicitly reviewed baseline update.")
    records = {}
    for kind, revision in PINS.items():
        archive = gzip.compress(git(repo, "archive", "--format=tar", revision, *SCOPE), mtime=0)
        relative = f"reference/sources/sabella-{kind}-{revision}.tar.gz"
        output = ROOT / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(archive)
        entries = git(repo, "ls-tree", "-r", "-z", revision, "--", *SCOPE).split(b"\0")
        files = []
        for entry in filter(None, entries):
            metadata, name = entry.split(b"\t", 1)
            mode, _, blob = metadata.decode().split()
            content = git(repo, "cat-file", "blob", blob)
            files.append({"path": name.decode(), "gitBlob": blob, "mode": mode, "sha256": sha(content)})
        records[kind] = {
            "repository": "https://github.com/gaulatti/sabella",
            "revision": revision,
            "tree": git(repo, "rev-parse", f"{revision}^{{tree}}").decode().strip(),
            "commitMetadata": git(repo, "show", "-s", "--format=fuller", revision).decode(),
            "artifact": relative, "sha256": sha(archive), "scope": SCOPE,
            "files": files,
            "dependencies": json.loads(git(repo, "show", f"{revision}:Package.resolved")),
        }
    records["bleecker"] = {
        "repository": "https://github.com/gaulatti/bleecker",
        "revision": "0bd7032e42d4c346c6e2201ad2feff96e635f73f",
        "artifact": "tokens/bleecker-source.ts",
        "sha256": "8e76c8f1aded0b61edd3309b3ae75f607ccda679b90b4e29f4d10b45ae2c99d9",
    }
    records["orchard"] = {
        "repository": "https://github.com/gaulatti/orchard",
        "revision": "31fa020e74b9ee37c50d0fa21fac85eabc766a7e",
        "role": "Peer workflow reference; not the visual baseline or scope authority",
    }
    environment = {
        "os": subprocess.check_output(["sw_vers"]).decode().strip(),
        "xcode": subprocess.check_output(["xcodebuild", "-version"]).decode().strip(),
        "swift": subprocess.check_output(["xcrun", "swift", "--version"]).decode().strip(),
        "sdk": subprocess.check_output(["xcrun", "--sdk", "macosx", "--show-sdk-version"]).decode().strip(),
        "captureTooling": "Pending: recorded separately per actual capture; no image acceptance yet",
    }
    destination.write_text(json.dumps({"schemaVersion": 1, "references": records, "preservationEnvironment": environment}, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sabella", type=Path, required=True)
    args = parser.parse_args()
    preserve(args.sabella)
