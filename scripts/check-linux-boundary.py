#!/usr/bin/env python3
"""Reject Apple source/projects in the Git index, including inside archives."""
import bz2
import gzip
import io
import lzma
from pathlib import Path, PurePosixPath
import subprocess
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
APPLE_SUFFIXES = {
    ".swift", ".swiftinterface", ".swiftmodule", ".swiftdoc", ".swiftsourceinfo",
    ".xcodeproj", ".xcworkspace", ".xcassets", ".xcconfig", ".pbxproj",
    ".storyboard", ".xib", ".ipa", ".dsym",
}
APPLE_NAMES = {".swiftpm", "package.resolved"}
MAX_EXPANDED_BYTES = 64 * 1024 * 1024
MAX_DEPTH = 5


def forbidden_path(name):
    path = PurePosixPath(name.replace("\\", "/").replace("!", "/").lower())
    return any(part in APPLE_NAMES or PurePosixPath(part).suffix in APPLE_SUFFIXES
               for part in path.parts)


def inspect_payload(name, data, depth=0, budget=None):
    """Inspect recognized tar/zip/compressed bytes regardless of their filename."""
    if forbidden_path(name) or name.lower().endswith("-package.resolved"):
        return [f"{name}: Apple source/project file"]
    if depth > MAX_DEPTH:
        return [f"{name}: archive nesting exceeds inspection limit"]
    if budget is None:
        budget = [MAX_EXPANDED_BYTES]
    errors = []

    def inspect_member(member_name, content):
        budget[0] -= len(content)
        if budget[0] < 0:
            errors.append(f"{name}: expanded archive exceeds inspection limit")
            return False
        errors.extend(inspect_payload(f"{name}!{member_name}", content, depth + 1, budget))
        return True

    stream = io.BytesIO(data)
    if zipfile.is_zipfile(stream):
        with zipfile.ZipFile(stream) as archive:
            for member in archive.infolist():
                if member.is_dir():
                    if forbidden_path(member.filename):
                        errors.append(f"{name}!{member.filename}: Apple project directory")
                    continue
                if member.file_size > budget[0]:
                    return errors + [f"{name}: expanded archive exceeds inspection limit"]
                if not inspect_member(member.filename, archive.read(member)):
                    break
        return errors
    try:
        archive = tarfile.open(fileobj=io.BytesIO(data), mode="r:*")
    except tarfile.ReadError:
        archive = None
    if archive is not None:
        with archive:
            for member in archive:
                if forbidden_path(member.name):
                    errors.append(f"{name}!{member.name}: Apple source/project file")
                elif member.isfile():
                    if member.size > budget[0]:
                        return errors + [f"{name}: expanded archive exceeds inspection limit"]
                    if not inspect_member(member.name, archive.extractfile(member).read()):
                        break
        return errors
    for magic, opener, extension in [
        (b"\x1f\x8b", lambda stream: gzip.GzipFile(fileobj=stream), ".gz"),
        (b"BZh", bz2.BZ2File, ".bz2"),
        (b"\xfd7zXZ\x00", lzma.LZMAFile, ".xz"),
    ]:
        if data.startswith(magic):
            with opener(io.BytesIO(data)) as compressed:
                content = compressed.read(budget[0] + 1)
            inner_name = name[:-len(extension)] if name.lower().endswith(extension) else "compressed-content"
            inspect_member(inner_name, content)
            return errors
    if name.lower().endswith((".tar", ".tgz", ".tar.gz", ".tar.bz2", ".tar.xz", ".zip", ".7z", ".rar")):
        return [f"{name}: archive format is unsupported or invalid; cannot establish Linux-only contents"]
    return []


def check_index(root=ROOT):
    paths = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
    errors = []
    for name in filter(None, paths):
        data = subprocess.check_output(["git", "show", f":{name}"], cwd=root)
        try:
            errors.extend(inspect_payload(name, data))
        except (OSError, EOFError, ValueError, tarfile.TarError, zipfile.BadZipFile, RuntimeError) as error:
            errors.append(f"{name}: cannot inspect archive ({type(error).__name__})")
    return errors


if __name__ == "__main__":
    violations = check_index()
    if violations:
        raise SystemExit("Linux-only boundary failed:\n" + "\n".join(violations))
    print("Linux-only boundary verified: no tracked Apple source/projects, including archive contents")
