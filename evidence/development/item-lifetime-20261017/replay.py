#!/usr/bin/env python3
"""Build the frozen lifetime correction from Git history without build caches."""
import argparse
import io
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
BASE = "a411c51b58810bf7df84eb72ae3271637c1274ab"
IMAGE = "avelino-toolchain:data-metrics-qt6.8.3"
IMAGE_ID = "sha256:48d88f958d93310bf887e4318b27713b7ecbb8b9f6a7d276087e599c9b6383d8"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
    spec = importlib.util.spec_from_file_location("lifetime_record", root / "scripts/verify-item-lifetime.py")
    record = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(record)
    record.verify()
    actual = subprocess.check_output(["docker", "--context", "colima-avelino-verify", "image",
                                      "inspect", IMAGE, "--format", "{{.Id}}"], text=True).strip()
    if actual != IMAGE_ID:
        raise SystemExit(f"Recorded toolchain changed: {actual}")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    source = output / "source"
    source.mkdir()
    data = subprocess.check_output(["git", "archive", BASE, "CMakeLists.txt", "src", "samples", "tests", "assets", "cmake"], cwd=root)
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        archive.extractall(source, filter="data")
    for file in (HERE / "overlay").rglob("*"):
        if file.is_file():
            target = source / file.relative_to(HERE / "overlay")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, target)
    docker = ["docker", "--context", "colima-avelino-verify", "run", "--rm", "--ulimit", "core=0",
              "-v", str(output) + ":/replay", "-w", "/replay", "--env", "QT_QPA_PLATFORM=offscreen",
              "--env", "QT_QUICK_BACKEND=software", IMAGE]
    steps = []
    for name, command in [
        ("configure", ["cmake", "-S", "source", "-B", "build", "-G", "Ninja", "-DCMAKE_BUILD_TYPE=Debug", "-DBUILD_TESTING=ON"]),
        ("build", ["cmake", "--build", "build", "--target", "AvelinoItemLifetimeTests", "Avelinoplugin", "--parallel", "2"]),
        ("tests", ["ctest", "--test-dir", "build", "-R", "^item-lifetime(-dpr2)?$", "--output-on-failure"]),
    ]:
        with (output / (name + ".log")).open("wb") as log:
            result = subprocess.run(docker + command, stdout=log, stderr=subprocess.STDOUT)
        steps.append(dict(name=name, command=docker + command, exitCode=result.returncode))
        (output / "commands.json").write_text(json.dumps(steps, indent=2) + "\n")
        print(name, result.returncode, flush=True)
        if result.returncode:
            raise SystemExit(result.returncode)
    (output / "result.json").write_text(json.dumps(dict(accepted=False, sourceBuildReplayPassed=True), indent=2) + "\n")


if __name__ == "__main__":
    main()
