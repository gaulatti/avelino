#!/usr/bin/env python3
"""Restore frozen Linux source and optional installed FileInput package bytes."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
digest = lambda data: hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--snapshot", default="file-input-qt-v18")
    parser.add_argument("--package", action="store_true")
    args = parser.parse_args()
    root = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
    spec = importlib.util.spec_from_file_location("linux_boundary", root / "scripts/check-linux-boundary.py")
    boundary = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(boundary)
    directory = HERE.parent
    replay = json.loads((HERE / "source-replay.json").read_text())
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)

    def safe(name):
        path = PurePosixPath(name)
        assert not path.is_absolute() and ".." not in path.parts and not boundary.forbidden_path(name), name
        return path

    def unbundle(record, folder):
        chunks = {}
        for item in record["archives"]:
            archive = folder / item["archive"]
            assert digest(archive.read_bytes()) == item["sha256"]
            manifest = json.loads((folder / item["manifest"]).read_text())
            with tarfile.open(archive) as stream:
                members = stream.getmembers()
                assert len(members) == len(manifest) == item["members"]
                assert sum(m.size for m in members) == item["expandedBytes"] < 44 * 1024 * 1024
                for member in members:
                    safe(member.name)
                    assert member.isfile()
                    data = stream.extractfile(member).read()
                    expected = manifest[member.name]
                    assert len(data) == expected["bytes"] and digest(data) == expected["sha256"]
                    key = (item["archive"], member.name)
                    assert key not in chunks
                    chunks[key] = data
        files = {}
        for name, expected in record["files"].items():
            safe(name)
            parts, offset = [], 0
            for part in expected["parts"]:
                assert part["offset"] == offset
                data = chunks.pop((part["archive"], part["member"]))
                assert len(data) == part["bytes"] and digest(data) == part["sha256"]
                parts.append(data)
                offset += len(data)
            data = b"".join(parts)
            assert len(data) == expected["bytes"] and digest(data) == expected["sha256"]
            files[name] = data
        assert not chunks
        return files

    archived = unbundle(replay, HERE)
    tree = {row.split(b"\t", 1)[1].decode(): row.split(b"\t", 1)[0].split()[2].decode()
            for row in subprocess.check_output(["git", "ls-tree", "-rz", "--full-tree", replay["baseRevision"]], cwd=root).split(b"\0") if row}
    values = {}
    with subprocess.Popen(["git", "cat-file", "--batch"], cwd=root, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        for name, item in replay["snapshots"][args.snapshot].items():
            safe(name)
            sha = item["sha256"]
            if sha not in values:
                obj = replay["objects"][sha]
                safe(obj["sourcePath"])
                if "gitBlob" in obj:
                    assert tree[obj["sourcePath"]] == obj["gitBlob"]
                    process.stdin.write((obj["gitBlob"] + "\n").encode())
                    process.stdin.flush()
                    header = process.stdout.readline().split()
                    assert header[:2] == [obj["gitBlob"].encode(), b"blob"]
                    data = process.stdout.read(int(header[2]))
                    assert process.stdout.read(1) == b"\n"
                else:
                    data = archived[obj["archivePath"]]
                assert len(data) == obj["bytes"] and digest(data) == sha
                values[sha] = data
            data = values[sha]
            assert len(data) == item["bytes"]
            target = output / "source" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            target.chmod(item["mode"])
        process.stdin.close()
        assert process.wait() == 0
    if args.package:
        package = json.loads((directory / "package/archive.json").read_text())
        for name, data in unbundle(package, directory).items():
            target = output / "package" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            target.chmod(package["files"][name]["mode"])
    result = dict(accepted=False, snapshot=args.snapshot, sourceFiles=len(replay["snapshots"][args.snapshot]),
                  packageRestored=args.package, sourceAndPackageBytesVerified=True)
    (output / "reconstructed.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
