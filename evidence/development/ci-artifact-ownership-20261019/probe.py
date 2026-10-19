"""Exercise CI's host/root ownership boundary with real Linux permissions."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

uid = gid = 1001
base = Path(tempfile.mkdtemp(prefix="avelino-artifact-ownership-"))
base.chmod(0o755)
seed = "mkdir -p artifacts/package/consumer artifacts/package/install\nprintf '%s\\n' 'obsolete consumer fixture' > artifacts/package/consumer/main.cpp\ntouch artifacts/package/install/obsolete-fixture\n"
source = Path("/opt/qt/share/avelino/qt-software-opacity")


def identity():
    os.setgroups([])
    os.setgid(gid)
    os.setuid(uid)


def host(workspace, command):
    result = subprocess.run(["bash", "-e", "-c", command], cwd=workspace,
                            preexec_fn=identity, capture_output=True, text=True)
    return {"command": command, "uid": uid, "gid": gid,
            "exitCode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


rows = []
for fixed in [False, True]:
    workspace = base / ("fixed" if fixed else "before")
    workspace.mkdir()
    os.chown(workspace, uid, gid)
    preparation = None
    if fixed:
        preparation = host(workspace, "mkdir -p artifacts/linux/toolchain")
        assert preparation["exitCode"] == 0
    else:
        # Docker's absent bind-source directory was root-owned in the actual
        # x86 CI failure; reproduce that same ownership with the Linux kernel.
        (workspace / "artifacts/linux/toolchain").mkdir(parents=True)
    target = workspace / "artifacts/linux/toolchain"
    subprocess.run(["cp", "-R", str(source), str(target) + "/"], check=True)
    original = {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in source.rglob("*") if p.is_file()}
    copied = target / source.name
    assert all(hashlib.sha256((copied / name).read_bytes()).hexdigest() == checksum
               for name, checksum in original.items())
    result = host(workspace, seed)
    assert result["exitCode"] == (0 if fixed else 1), result
    if fixed:
        assert (workspace / "artifacts/package/consumer/main.cpp").read_text() == "obsolete consumer fixture\n"
        assert (workspace / "artifacts/package/install/obsolete-fixture").is_file()
    else:
        assert "Permission denied" in result["stderr"]
    rows.append({"fixed": fixed, "hostPreparation": preparation, "rootCopyPreservedFiles": len(original),
                 "artifactsOwnerUid": (workspace / "artifacts").stat().st_uid,
                 "toolchainCopyOwnerUid": copied.stat().st_uid, "seed": result})
print(json.dumps({"rows": rows, "actualLinuxPermissions": True,
                  "fullWorkflowExecuted": False, "accepted": False}, indent=2))
