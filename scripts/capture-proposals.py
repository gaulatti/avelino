#!/usr/bin/env python3
"""Capture implemented Linux cases against review-only native fixture definitions."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
import os
import shutil
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture(catalog, reference, output, apis=None, jobs=4):
    reference, output, catalog = Path(reference).resolve(), Path(output).resolve(), Path(catalog).resolve()
    assert not output.is_relative_to(ROOT / "reference") and output != reference
    assert jobs > 0 and catalog.is_file()
    spec = importlib.util.spec_from_file_location("verify_proposals", ROOT / "scripts/verify-proposals.py")
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    verifier.verify(reference)
    proposal = json.loads((reference / "proposal.json").read_text())
    manifest = json.loads((reference / "captures.json").read_text())
    available = {case["api"] for case in manifest["captures"]} - {"MonospaceProbe"}
    selected = set(apis) if apis else available
    assert selected and selected <= available, "Requested API has no implemented fixture"
    cases = [c for c in manifest["captures"] if c["api"] in selected]
    failure_root=ROOT/"artifacts/linux/capture-failures"
    assert not failure_root.is_relative_to(output), "Capture output cannot contain its failure archive"
    output.mkdir(parents=True, exist_ok=False)

    def command(*args):
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()

    git = ["git", "-c", f"safe.directory={ROOT}"]
    inputs = sorted([ROOT / "CMakeLists.txt", ROOT / "CMakePresets.json"] +
        [p for directory in ["src", "samples", "assets", "tokens", "tests", "scripts", "cmake", "tools", "evidence/geometry"]
         for p in (ROOT / directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts])
    environment = {"sourceRevision": command(*git, "rev-parse", "HEAD"),
        "uncommittedChanges": bool(command(*git, "status", "--porcelain")),
        "compiler": command("c++", "--version"), "qt": command("qmake", "-query", "QT_VERSION"),
        "cmake": command("cmake", "--version"), "installedPackages": command("dpkg-query", "-W"),
        "catalogSha256": digest(catalog), "referenceProposalSha256": digest(reference / "proposal.json"),
        "caseDefinitionsSha256": digest(reference / "fixtures.json"),
        "qmlImportPath": os.environ.get("QML_IMPORT_PATH", ""),
        "sourceInputs": {str(p.relative_to(ROOT)): digest(p) for p in inputs},
        "captureMethod": "offscreen QQuickWindow::grabWindow; no compositor or input/session acceptance"}
    (output / "environment.json").write_text(json.dumps(environment, indent=2) + "\n")

    def one(case):
        name = Path(case["path"])
        assert str(name) == name.name and name.suffix == ".png"
        args = [str(catalog), "--fixture", "reference-case", "--case", case["fixture"],
            "--case-definitions", str(reference / "fixtures.json"), "--text-scale", str(case["textScale"]),
            "--capture", str(output / name)]
        if case["appearance"] == "dark": args.append("--dark")
        with tempfile.TemporaryDirectory(prefix="avelino-capture-") as runtime:
            env = dict(os.environ, QT_QPA_PLATFORM="offscreen", QT_QUICK_BACKEND="software",
                QT_SCALE_FACTOR=str(case["dpr"]), XDG_RUNTIME_DIR=runtime, LANG="C.UTF-8")
            timed_out=False
            try:
                result = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, timeout=30)
            except subprocess.TimeoutExpired as error:
                timed_out=True
                result=subprocess.CompletedProcess(args,124,error.stdout or b"",(error.stderr or b"")+b"\nCapture exceeded the unchanged 30-second deadline\n")
        (output / (str(name) + ".stderr.txt")).write_bytes(result.stdout + result.stderr)
        row = {"path": str(name), "api": case["api"], "fixture": case["fixture"], "exitCode": result.returncode,
            "referenceSha256": case["sha256"], "referenceStatus": "proposed; no baseline approval", "timedOut":timed_out}
        diagnostics = (result.stdout + result.stderr).decode(errors="replace")
        row["runtimeErrors"] = [line for line in diagnostics.splitlines()
            if any(marker in line for marker in ["Binding loop detected", "ReferenceError:", "TypeError:", "Capture exceeded the unchanged 30-second deadline"])]
        if result.returncode == 0:
            row["sha256"] = digest(output / name)
            row["metadataSha256"] = digest(output / (str(name) + ".json"))
        return row

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        results = list(pool.map(one, cases))
    report = {"schemaVersion": 1, "referenceRevision": proposal["referenceRevision"],
        "referenceStatus": proposal["status"], "expectedImagesChanged": False,
        "selectedApis": sorted(selected), "results": results,
        "excludedApis": [{"api": "MonospaceProbe", "reason": "Unresolved Linux font candidate; no asset substitution approved"}],
        "status": "captured" if all(row["exitCode"] == 0 and not row["runtimeErrors"] for row in results) else "failed",
        "limitations": ["Offscreen diagnostic capture only", "No matched native animation phase", "Reference baseline approval pending"]}
    failure=None
    if report["status"]!="captured":
        failure_root.mkdir(parents=True,exist_ok=True)
        failure=Path(tempfile.mkdtemp(prefix=output.name+"-",dir=failure_root))
        report["failureArtifact"]=str(failure/"captures")
    (output / "capture-results.json").write_text(json.dumps(report, indent=2) + "\n")
    if failure is not None:
        shutil.copytree(output,failure/"captures")
        print(f"Failed capture attempt preserved at {failure/'captures'}")
    print(f"{report['status']}: {len(results)} cases across {len(selected)} APIs")
    return 0 if report["status"] == "captured" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--api", action="append")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    raise SystemExit(capture(args.catalog, args.reference, args.output, args.api, args.jobs))
