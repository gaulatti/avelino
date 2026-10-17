"""Freeze the FileInput development checkpoint, retaining incomplete parity gates."""
from pathlib import Path
import hashlib
import io
import json
import shutil
import stat
import subprocess
import tarfile

ROOT = Path.cwd()
RUNS = ROOT / "artifacts/resumed-avelino-20261016"
DEST = ROOT / "evidence/development/file-input-20261017"
BASE = "a411c51b58810bf7df84eb72ae3271637c1274ab"
LIMIT = 44 * 1024 * 1024
PART = 16 * 1024 * 1024
digest = lambda data: hashlib.sha256(data).hexdigest()
read = lambda path: json.loads(path.read_text())


def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def bundle(folder, prefix, values):
    """Keep every tar below the expanded-size guard, including large ELF files."""
    folder.mkdir(parents=True, exist_ok=True)
    archives, files = [], {}
    archive = None
    total = 0
    members = {}
    number = 0

    def close():
        if archive is None:
            return
        archive.close()
        path = folder / f"{prefix}-{number}.tar.gz"
        manifest = folder / f"{prefix}-{number}-manifest.json"
        manifest.write_text(json.dumps(members, indent=2) + "\n")
        archives.append(dict(archive=path.name, manifest=manifest.name,
                             sha256=digest(path.read_bytes()), expandedBytes=total,
                             members=len(members)))

    for name, data, mode in values:
        assert not Path(name).is_absolute() and ".." not in Path(name).parts
        row = dict(bytes=len(data), sha256=digest(data), mode=mode, parts=[])
        # Empty files still receive an archive member and a verifiable identity.
        for part_number, offset in enumerate(range(0, max(1, len(data)), PART)):
            value = data[offset:offset + PART]
            if archive is None or total + len(value) >= LIMIT:
                close()
                number += 1
                archive = tarfile.open(folder / f"{prefix}-{number}.tar.gz", "w:gz")
                members = {}
                total = 0
            member = name + f"/part-{part_number:04d}"
            info = tarfile.TarInfo(member)
            info.size = len(value)
            info.mode = 0o644
            archive.addfile(info, io.BytesIO(value))
            record = dict(bytes=len(value), sha256=digest(value))
            members[member] = record
            row["parts"].append(dict(archive=f"{prefix}-{number}.tar.gz", member=member,
                                     offset=offset, **record))
            total += len(value)
        files[name] = row
    close()
    return dict(archives=archives, files=files)


def main():
    for name in ["file-input-qt-v18", "file-input-package-pilot-v9", "file-input-display-v5", "file-input-source-replay-v2"]:
        assert read(RUNS / name / "result.json")["exitCode"] == 0, name
    for number in range(1, 5):
        assert read(RUNS / f"file-input-atspi-v{number}/session-result.json")["exitCode"] == 0
    for number in range(1, 3):
        assert read(RUNS / f"file-input-wayland-operator-v{number}/session-result.json")["exitCode"] == 0
    comparison = read(RUNS / "file-input-comparison-v5/observations.json")
    assert comparison["pairs"] == comparison["contractStates"] == 256
    assert comparison["accepted"] is False
    assert not DEST.exists()
    DEST.mkdir()

    snapshots, objects, paths = {}, {}, {}
    producers = [RUNS / f"file-input-qt-v{i}" for i in range(1, 19)]
    producers.append(RUNS / "file-input-alias-regression-v1")
    for directory in producers:
        inputs = read(directory / "inputs.json")
        snapshot = {}
        for name, sha in inputs["files"].items():
            path = directory / "source" / name
            data = path.read_bytes()
            assert digest(data) == sha, (directory.name, name)
            snapshot[name] = dict(sha256=sha, bytes=len(data), mode=stat.S_IMODE(path.stat().st_mode))
            paths.setdefault(sha, (name, data))
        snapshots[directory.name] = snapshot
    for i in range(1, 10):
        directory = RUNS / f"file-input-package-pilot-v{i}"
        snapshot = {}
        for path in sorted((directory / "consumer").rglob("*")):
            if path.is_file():
                name = str(path.relative_to(directory / "consumer"))
                data = path.read_bytes()
                sha = digest(data)
                snapshot[name] = dict(sha256=sha, bytes=len(data), mode=stat.S_IMODE(path.stat().st_mode))
                paths.setdefault(sha, ("tests/consumer/" + name, data))
        snapshots[directory.name] = snapshot

    git_tree = {row.split(b"\t", 1)[1].decode(): row.split(b"\t", 1)[0].split()[2].decode()
                for row in subprocess.check_output(["git", "ls-tree", "-rz", "--full-tree", BASE]).split(b"\0") if row}
    unknown = []
    for sha, (name, data) in paths.items():
        record = dict(sourcePath=name, sha256=sha, bytes=len(data))
        blob = git_tree.get(name)
        if blob and digest(subprocess.check_output(["git", "cat-file", "blob", blob])) == sha:
            record["gitBlob"] = blob
        else:
            record["archivePath"] = "objects/" + sha + "/" + name
            unknown.append((record["archivePath"], data, 0o644))
        objects[sha] = record
    replay = dict(baseRevision=BASE, accepted=False, buildCacheInputs=False,
                  snapshots=snapshots, objects=objects, **bundle(DEST / "replay", "source-blobs", unknown))
    (DEST / "replay/source-replay.json").write_text(json.dumps(replay, indent=2) + "\n")

    for directory in sorted(RUNS.glob("file-input-*")):
        if not directory.is_dir() or directory.name in ["file-input-build", "file-input-package-pilot-v9", "file-input-display-v5"]:
            continue
        for path in directory.iterdir():
            if path.is_file() and (path.suffix in [".json", ".log", ".py", ".cpp", ".txt", ".sh"] or path.name == "Dockerfile"):
                copy(path, DEST / "attempts" / directory.name / path.name)
        for subdir in ["output", "ui-output"]:
            if (directory / subdir).exists():
                for path in (directory / subdir).rglob("*"):
                    if path.is_file():
                        copy(path, DEST / "attempts" / directory.name / subdir / path.relative_to(directory / subdir))
        if directory.name.startswith("file-input-atspi-"):
            for path in directory.rglob("*"):
                relative = path.relative_to(directory)
                if path.is_file() and not any(part in ["install", "__pycache__"] for part in relative.parts):
                    copy(path, DEST / "accessibility" / directory.name / relative)
        if directory.name.startswith("file-input-wayland-operator-"):
            for path in directory.rglob("*"):
                relative = path.relative_to(directory)
                if path.is_file() and not any(part in ["install", "__pycache__"] for part in relative.parts):
                    copy(path, DEST / "runtime/external-operator" / directory.name / relative)
        if directory.name.startswith("file-input-display-"):
            for path in directory.joinpath("output").rglob("*"):
                if path.is_file():
                    copy(path, DEST / "attempts" / directory.name / "output" / path.relative_to(directory / "output"))

    producer = RUNS / "file-input-qt-v18"
    package = RUNS / "file-input-package-pilot-v9"
    for source, target in [(producer, "qt"), (package, "package"), (RUNS / "file-input-display-v5", "runtime")]:
        for path in source.iterdir():
            if path.is_file() and path.suffix in [".json", ".log", ".py", ".sh"]:
                copy(path, DEST / target / path.name)
    copy(producer / "../file-input-build/build/Testing/Temporary/LastTest.log", DEST / "qt/final-focused-LastTest.log")
    for path in package.joinpath("output").rglob("*"):
        if path.is_file():
            copy(path, DEST / "captures" / path.relative_to(package / "output"))
    catalog_package = RUNS / "file-input-package-pilot-v7"
    for path in catalog_package.joinpath("catalog-evidence").rglob("*"):
        if path.is_file():
            copy(path, DEST / "catalogs" / path.relative_to(catalog_package / "catalog-evidence"))
    for path in RUNS.joinpath("file-input-display-v5/output").rglob("*"):
        if path.is_file():
            copy(path, DEST / "runtime/output" / path.relative_to(RUNS / "file-input-display-v5/output"))
    for path in RUNS.joinpath("file-input-comparison-v5").iterdir():
        if path.is_file():
            copy(path, DEST / "comparison" / path.name)

    installed = [(str(path.relative_to(package)), path.read_bytes(), stat.S_IMODE(path.stat().st_mode))
                 for path in sorted((package / "install").rglob("*")) if path.is_file()]
    binary = package / "consumer-build/InstalledConsumer"
    installed.append((str(binary.relative_to(package)), binary.read_bytes(), 0o755))
    (DEST / "package/archive.json").write_text(json.dumps(bundle(DEST, "installed-package", installed), indent=2) + "\n")
    for path in catalog_package.iterdir():
        if path.is_file() and path.suffix in [".json", ".log", ".py", ".sh"]:
            copy(path, DEST / "full-package" / path.name)
    copy(Path(__file__).resolve(), DEST / "tools/seal-file-input.py")
    copy(RUNS / "reconstruct-file-input.py", DEST / "replay/reconstruct.py")
    for path in RUNS.glob("file-input-*"):
        if path.is_file() and path.suffix in [".json", ".log"]:
            copy(path, DEST / "checks" / path.name)
    print("Frozen source, package, attempts, captures and session evidence; parity report still required")


if __name__ == "__main__":
    main()
