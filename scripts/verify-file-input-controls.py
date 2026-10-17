#!/usr/bin/env python3
"""Audit scoped native panel controls; leave Linux and raster acceptance open."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "evidence/reference-investigations/file-input-controls-20261017"


def verify():
    read = lambda name: json.loads((DIRECTORY / name).read_text())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    report = read("investigation.json")
    assert report["accepted"] is False
    assert report["reference"] == "fe8a1d462fbd793d883fb92086a16aa2947e32c9"
    assert report["physicalInput"] is False and report["independentBehaviorSourceReplay"] is False
    for gate in ["physicalDisplayAcceptance", "nativeReaderAcceptance", "strictRasterAcceptance", "completeContextCoverage"]:
        assert report[gate] == "pending"
    assert report["expectedImagesChanged"] is False and report["tolerance"] == "none" and report["approvedExceptions"] == []
    files = read("files.json")
    assert set(files) == {str(f.relative_to(DIRECTORY)) for f in DIRECTORY.rglob("*") if f.is_file() and f.name != "files.json"}
    for name, row in files.items():
        path = DIRECTORY / name
        assert path.stat().st_size == row["bytes"] and digest(path) == row["sha256"], name
    for name, row in report["images"].items():
        path = DIRECTORY / name
        assert digest(path) == row["sourceSha256"]
        assert row["resized"] is row["cropped"] is row["masked"] is row["menuArtworkVerified"] is False
        with Image.open(path) as image:
            assert image.format == "JPEG" and list(image.size) == row["pixels"]
    assert report["images"]["history/new-folder-existing-default.jpg"]["pixels"] == [640, 316]
    assert report["images"]["history/duplicate-folder-error.jpg"]["pixels"] == [640, 364]
    for label in ["controls", "history", "history-selection"]:
        trace = read(label + "/ui-trace.json")
        assert trace["reference"] == report["reference"] and trace["accepted"] is False
        assert all(step["results"] == [] for step in trace["steps"])
        assert trace["steps"][-1]["phase"] == "finished"
        assert read(label + "/result.json")["exitCode"] == 0
        assert read(label + "/launch.json")["executableSha256"] == report["helperSha256"]
    observed = report["observations"]
    assert observed["views"] == ["Icons", "List", "Columns"]
    assert observed["groupMenu"] == ["None", "Name", "Kind", "Application", "Date Last Opened", "Date Added", "Date Modified", "Date Created", "Size", "Tags"]
    assert observed["optionSortMenu"] == ["Name", "Kind", "Date Last Opened", "Date Added", "Date Modified", "Date Created", "Size", "Tags"]
    assert observed["newFolderDefault"] == "untitled folder" and observed["newFolderExistingDefault"] == "untitled folder 2"
    assert observed["newFolderAndHistoryOwnerResults"] == [] and observed["positiveSearchResultsExercised"] is False
    checks = {
        "controls/new-folder-empty.ax.txt": ["button (disabled) Create"],
        "history/new-folder-existing-default.ax.txt": ["untitled folder 2"],
        "history/duplicate-folder-error.ax.txt": ["This name is already taken.", "button (disabled) Create"],
        "history/duplicate-file-error.ax.txt": ["one.txt", "This name is already taken.", "button (disabled) Create"],
        "history/created-folder-navigation.ax.txt": ["Where:, Value: untitled folder 2", "button (disabled) Open"],
        "history/back-to-parent.ax.txt": ["Where:, Value: fixtures", "button forward"],
        "history/forward-to-created.ax.txt": ["Where:, Value: untitled folder 2", "button (disabled) forward"],
        "history/new-folder-keyboard-shortcut.ax.txt": ["New Folder Name of new folder inside “untitled folder 2”", "untitled folder"],
        "history/nested-escape-keeps-chooser.ax.txt": ["Description: open, ID: open-panel", "Where:, Value: untitled folder 2"],
    }
    for name, phrases in checks.items():
        text = (DIRECTORY / name).read_text()
        assert all(phrase in text for phrase in phrases), name
    filesystem = read("history/filesystem-observations.json")
    assert filesystem["created"] == "untitled folder 2" and filesystem["createdDirectoryEmpty"] is True
    assert filesystem["nestedEscapeCreatedNothing"] is True and filesystem["ownerResults"] == []
    assert observed['historyBackClearsFileSelection'] is observed['historyForwardClearsChildSelection'] is True
    assert observed['postBackShiftCSelectedFiles'] == ['a.txt', 'b.txt', 'c.txt']
    for name in ['back-after-a-b.ax.txt', 'back-after-b.ax.txt']:
        text = (DIRECTORY / 'history-selection' / name).read_text()
        assert 'button (disabled) Open' in text
        assert not any('text field (selected,' in line and '/fixtures/' in line and '.txt' in line for line in text.splitlines())
    text = (DIRECTORY / 'history-selection/shift-c-after-back-from-b.ax.txt').read_text()
    for name in ['a.txt', 'b.txt', 'c.txt']:
        assert any('text field (selected,' in line and '/fixtures/' + name in line for line in text.splitlines())
    text = (DIRECTORY / 'history-selection/forward-clears-child-selection.ax.txt').read_text()
    assert 'button (disabled) Open' in text and not any('text field (selected,' in line and 'child.txt' in line for line in text.splitlines())
    print("FileInput controls: native views/menus, name validation, folder creation and actual Back/Forward; strict acceptance pending")


if __name__ == "__main__":
    verify()
