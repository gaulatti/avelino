"""Recover immutable reference artifacts into an ignored cache, never the source tree."""
import hashlib
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def resolve_reference(record, root=ROOT):
    relative = PurePosixPath(record["artifact"])
    assert relative.parts[:2] == (".cache", "reference-sources")
    assert not relative.is_absolute() and ".." not in relative.parts
    artifact = root / relative
    if artifact.exists():
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == record["sha256"], artifact
        return artifact
    storage = record["storage"]
    assert storage["kind"] == "git-history"
    assert re.fullmatch(r"[0-9a-f]{40}", storage["revision"])
    source = PurePosixPath(storage["path"])
    assert not source.is_absolute() and ".." not in source.parts
    result = subprocess.run(
        ["git", "show", f"{storage['revision']}:{source}"], cwd=root,
        capture_output=True, check=False,
    )
    if result.returncode:
        raise RuntimeError(
            f"Reference history object is unavailable. Fetch it explicitly with "
            f"`git fetch origin {storage['revision']}` and rerun verification."
        )
    assert hashlib.sha256(result.stdout).hexdigest() == record["sha256"], source
    artifact.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=artifact.parent, delete=False) as pending:
        pending.write(result.stdout)
        temporary = Path(pending.name)
    temporary.replace(artifact)
    return artifact
