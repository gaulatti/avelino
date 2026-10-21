#!/usr/bin/env python3
"""Audit scoped search observations without granting FileInput acceptance."""
import hashlib
import json
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "evidence/reference-investigations/file-input-search-20261020"
LINUX = ROOT / "evidence/development/file-input-search-provider-20261020"
TOKEN = ROOT / "evidence/reference-investigations/file-input-search-token-20261020"
REFERENCE = "fe8a1d462fbd793d883fb92086a16aa2947e32c9"
LIBRARY = "61d1e55c6f9c17c841eded420066c72b5611ec51af8c5a4821306f1751ea6514"


def read(path):
    return json.loads(path.read_text())


def manifest(directory):
    files = read(directory / "files.json")
    assert set(files) == {
        str(p.relative_to(directory)) for p in directory.rglob("*")
        if p.is_file() and p != directory / "files.json"
    }
    for name, row in files.items():
        relative = PurePosixPath(name)
        assert str(relative) == name and not relative.is_absolute() and ".." not in relative.parts
        path = directory / name
        assert not path.is_symlink()
        assert path.stat().st_size == row["bytes"], name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"], name


def verify():
    for directory in [NATIVE, LINUX, TOKEN]:
        manifest(directory)
    native = read(NATIVE / "observations.json")
    assert native["reference"] == REFERENCE and native["libraryObjectSha256"] == LIBRARY
    assert "not a raw AX-tree archive" in native["method"]
    for gate in ["independentNativeLibraryRebuild", "queryCompletionVerified",
                 "searchOwnerDeliveryVerified", "broaderMatchingVerified",
                 "nativeRasterAccepted", "physicalInput", "readerAcceptance", "accepted"]:
        assert native[gate] is False, gate
    build = read(NATIVE / "helper-v1/build.json")
    second = read(NATIVE / "helper-v2/build.json")
    for helper in [build, second]:
        assert helper["reference"] == REFERENCE and helper["libraryObjectSha256"] == LIBRARY
        assert helper["exitCode"] == 0 and helper["independentNativeLibraryRebuild"] is False
        assert helper["sourceLibraryChanged"] is helper["accepted"] is False
    controls = read(NATIVE / "content-controls.json")
    fixtures = dict(build["fixtureFiles"], **controls["files"])
    for name, digest in fixtures.items():
        assert hashlib.sha256((NATIVE / "fixtures" / name).read_bytes()).hexdigest() == digest
    token = controls["token"]
    name_match, content_match = token + "-name.txt", "pine-only.txt"
    assert token not in content_match and token in (NATIVE / "fixtures" / content_match).read_text()
    assert token not in (NATIVE / "fixtures" / name_match).read_text()
    sets = native["rowSets"]
    assert sets["single-word-general"] == [name_match, content_match]
    assert sets["single-word-filename"] == [name_match]
    assert "avelino-search-body-20261020.txt" in sets["prefix-general"]
    assert "avelino-search-body-20261020.txt" not in sets["prefix-filename"]
    assert "nested/avelino-search-cedarfield-20261020-child.txt" in sets["prefix-filename"]
    snapshots = {row["id"]: row for row in native["snapshots"]}
    assert snapshots["single-word-raw-query"]["kind"] == "full"
    assert snapshots["single-word-filename-query"]["kind"] == "full"
    scoped = "\n".join(snapshots["folder-filename-query"]["controls"])
    assert "Value: 1" in scoped and "Searching “This Mac”" in scoped
    assert native["outsideScopeControl"]["scopeExclusionVerified"] is False
    assert all(v is None for v in native["outsideScopeControl"]["mdls"].values())
    assert native["freshPlainTextBaseline"]["openEnabled"] is False
    assert native["freshPlainTextBaseline"]["ownerResultObserved"] is False

    token_observation = read(TOKEN / "observations.json")
    assert token_observation["reference"] == REFERENCE and token_observation["libraryObjectSha256"] == LIBRARY
    assert token_observation["tokenLabel"] == "Everything: " + token
    assert token_observation["observedRows"] == [name_match, content_match]
    assert token_observation["escapeClearsSearchAndReturnsToBrowse"] is True
    assert token_observation["forwardEnabledAfterEscape"] is True
    for gate in ["independentNativeLibraryRebuild", "queryCompletionVerified", "ownerDeliveryVerified", "accepted"]:
        assert token_observation[gate] is False
    assert "unrelated recursive entries" in token_observation["forwardDiagnostic"]
    outside_controls = token_observation["indexedOutsideFolderControls"]
    assert outside_controls["observedGlobally"] is True
    assert len(outside_controls["knownIndexedRepositoryCopies"]) == 2
    assert outside_controls["repositoryCopiesObservedInCurrentFolder"] is False
    assert outside_controls["scopeExclusionObservedForTheseCopies"] is True
    assert outside_controls["originalSiblingReadinessVerified"] is False
    assert read(TOKEN / "helper-build.json")["libraryObjectSha256"] == LIBRARY
    assert read(TOKEN / "startup-failure.json")["accepted"] is False

    report = read(LINUX / "validation.json")
    assert report["reference"] == REFERENCE and report["nativeLibraryObjectSha256"] == LIBRARY
    for gate in ["accepted", "expectedImagesChanged", "nativeRawAxArchiveRetained",
                 "nativeQueryCompletionVerified", "nativeSearchOwnerDeliveryVerified",
                 "nativeCrossFolderExclusionVerified", "linuxProductIntegration",
                 "linuxDesktopProviderPolicySelected", "linuxReadinessCancellationAndLifecycleVerified",
                 "installedConsumerVerified", "x86_64Verified", "physicalInputVerified",
                 "readerAcceptance", "strictRasterAcceptance"]:
        assert report[gate] is False, gate
    assert report["approvedExceptions"] == [] and report["tolerance"] == "none"
    first, second, third = [LINUX / ("attempt-" + str(i)) for i in [1, 2, 3]]
    assert read(first / "runtime-result.json")["exitCode"] == 1
    assert "ModuleNotFoundError: No module named 'gi'" in (first / "runtime.log").read_text()
    assert read(second / "build-result.json")["exitCode"] == 0
    assert read(second / "runtime-result.json")["exitCode"] == 1
    assert "Filesystem index did not expose all three controlled files" in (second / "runtime.log").read_text()
    result = read(third / "runtime-result.json")
    assert result["exitCode"] == 0 and result["accepted"] is False
    assert result["imageId"] == report["linuxPrototypeImageId"] == read(second / "image.json")["imageId"]
    command = read(third / "runtime-command.json")
    assert command["probeSha256"] == hashlib.sha256((third / "probe.py").read_bytes()).hexdigest()
    assert not any(arg in command["command"] for arg in ["--privileged", "--security-opt", "--mount", "-v"])
    events = [json.loads(line) for line in (third / "runtime.log").read_text().splitlines() if line.startswith("{")]
    completed = [event for event in events if event.get("phase") == "complete"]
    assert len(completed) == 1 and completed[0]["accepted"] is False
    values = completed[0]["values"]
    assert {key: len(urls) for key, urls in values.items()} == {
        "filename-global": 2, "filename-folder": 1, "content-global": 3, "content-folder": 2}
    urls = values["content-folder"]
    assert all(urlsplit(url).scheme == "file" for url in values["content-global"])
    folder = unquote(urlsplit(urls[0]).path).rsplit("/", 1)[0] + "/"
    assert folder.startswith("/home/avelino-search-provider-") and folder.endswith("/inside/")
    names = lambda rows: {unquote(urlsplit(url).path).rsplit("/", 1)[-1] for url in rows}
    assert names(values["filename-folder"]) == {name_match}
    assert names(urls) == {name_match, content_match}
    outside = token + "-outside.txt"
    assert names(values["filename-global"]) == {name_match, outside}
    assert names(values["content-global"]) == {name_match, content_match, outside}
    assert all(unquote(urlsplit(url).path).startswith(folder) for url in urls)
    assert "File is NOT eligible to be indexed (not an indexed folder)" in (third / "temporary-path-eligibility.jsonl").read_text()
    print("FileInput search: native controlled name/content observations and Linux capability verified; product and native acceptance pending")


if __name__ == "__main__":
    verify()
