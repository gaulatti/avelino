#!/usr/bin/env python3
"""Rebuild the recorded failing and corrected Linux lifetimes in fresh trees."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = "a46a8dca78f6d630b7be1352757e3d0fe01c44c9"
IMAGE = "avelino-toolchain:data-metrics-qt6.8.3"
IMAGE_ID = "sha256:48d88f958d93310bf887e4318b27713b7ecbb8b9f6a7d276087e599c9b6383d8"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    actual_image = subprocess.check_output([
        "docker", "--context", "colima-avelino-verify", "image", "inspect", IMAGE,
        "--format", "{{.Id}}"], text=True).strip()
    if actual_image != IMAGE_ID:
        raise SystemExit(f"Recorded toolchain changed: {actual_image}")
    recorded = json.loads((HERE / "fixed/inputs.json").read_text())["files"]
    for file in (HERE / "overlay").rglob("*"):
        if file.is_file():
            name = str(file.relative_to(HERE / "overlay"))
            if hashlib.sha256(file.read_bytes()).hexdigest() != recorded[name]:
                raise SystemExit(f"Recorded overlay changed: {name}")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    archive = subprocess.check_output([
        "git", "archive", BASE, "CMakeLists.txt", "src", "samples", "tests", "assets", "cmake"
    ], cwd=ROOT)
    commands = []
    for variant, expected in [("baseline", 133), ("fixed", 0)]:
        work = output / variant
        source = work / "source"
        source.mkdir(parents=True)
        with tarfile.open(fileobj=io.BytesIO(archive)) as files:
            files.extractall(source, filter="data")
        if variant == "fixed":
            for file in (HERE / "overlay").rglob("*"):
                if file.is_file():
                    target = source / file.relative_to(HERE / "overlay")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file, target)
        shutil.copytree(HERE / "repro", work / "repro")
        hashes = {str(f.relative_to(source)): hashlib.sha256(f.read_bytes()).hexdigest()
                  for f in sorted(source.rglob("*")) if f.is_file()}
        (work / "source-files.json").write_text(json.dumps(hashes, indent=2) + "\n")
        docker = ["docker", "--context", "colima-avelino-verify", "run", "--rm",
                  "--ulimit", "core=0", "-v", str(work) + ":/replay", "-w", "/replay",
                  "--env", "QT_QPA_PLATFORM=offscreen", "--env", "QT_QUICK_BACKEND=software",
                  "--env", "XDG_RUNTIME_DIR=/tmp/avelino-media-lifetime", IMAGE]
        steps = [
            ("configure", ["cmake", "-S", "source", "-B", "build", "-G", "Ninja",
                           "-DCMAKE_BUILD_TYPE=Debug", "-DBUILD_TESTING=OFF"]),
            ("build", ["cmake", "--build", "build", "--target", "Avelino", "--parallel", "2"]),
            ("repro-configure", ["cmake", "-S", "repro", "-B", "repro-build", "-G", "Ninja",
                                 "-DAVELINO_SOURCE=/replay/source",
                                 "-DAVELINO_LIBRARY=/replay/build/src/Avelino/libAvelino.so"]),
            ("repro-build", ["cmake", "--build", "repro-build", "--parallel", "2"]),
            ("repro", ["./repro-build/Repro"]),
        ]
        for name, command in steps:
            with (work / (name + ".log")).open("wb") as log:
                result = subprocess.run(docker + command, stdout=log, stderr=subprocess.STDOUT)
            commands.append(dict(variant=variant, step=name, command=docker + command,
                                 exitCode=result.returncode))
            (output / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
            print(variant, name, result.returncode, flush=True)
            wanted = expected if name == "repro" else 0
            if result.returncode != wanted:
                raise SystemExit(f"{variant}/{name}: expected {wanted}, got {result.returncode}")
    (output / "result.json").write_text(json.dumps(dict(
        accepted=False, baselineExpectedExitCode=133, fixedExpectedExitCode=0,
        replayPassed=True, baseGit=BASE), indent=2) + "\n")


if __name__ == "__main__":
    main()
