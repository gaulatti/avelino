#!/usr/bin/env python3
"""Verify preserved native FileInput panel observations without accepting parity."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "evidence/reference-investigations/file-input-panel-20261017"
REFERENCE = "fe8a1d462fbd793d883fb92086a16aa2947e32c9"


def validate(report):
    assert report["reference"] == REFERENCE
    assert report["accepted"] is False
    assert report["expectedImagesChanged"] is False
    assert report["tolerance"] == "none" and report["approvedExceptions"] == []
    assert report["physicalInputAcceptance"] == "pending"
    assert report["readerAcceptance"] == "pending"
    assert report["independentBehaviorSourceReplay"] == "pending"
    assert report["nativeOpenPanelRaster"] == "observed three lossy CUA states; lossless comparison acceptance pending"
    assert report["losslessPanelCaptureAcceptance"] == "pending"
    assert len(report["presentationGaps"]) == 6
    assert len(report["screenshots"]) == 3
    assert report["selectionResult"]["kind"] == "success"
    assert report["selectionResult"]["panelVisibleAtCallback"] is True
    assert [url.rsplit("/", 1)[1] for url in report["selectionResult"]["urls"]] == ["one.txt", "two.txt"]


def verify():
    report = json.loads((DIRECTORY / "investigation.json").read_text())
    validate(report)
    files = json.loads((DIRECTORY / "files.json").read_text())
    actual = {str(f.relative_to(DIRECTORY)): hashlib.sha256(f.read_bytes()).hexdigest()
              for f in DIRECTORY.rglob("*") if f.is_file() and f.name != "files.json"}
    assert actual == files, "Native panel evidence changed or is incomplete"
    frame = report["windowFrame"]
    assert (frame["width"], frame["height"]) == (880, 448)
    for image in report["screenshots"]:
        data = (DIRECTORY / image["path"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == image["sha256"]
        assert image["format"] == "JPEG" and image["lossless"] is False
        with Image.open(DIRECTORY / image["path"]) as raster:
            assert raster.format == "JPEG"
            assert raster.size == (image["pixelWidth"], image["pixelHeight"]) == (1760, 896)
    flags = report["panelFlags"]
    assert flags["visible"] and flags["directoryIsControlled"] and flags["allowsMultipleSelection"]
    assert flags["canChooseFiles"] and not flags["canChooseDirectories"]
    assert flags["allowedContentTypes"] == ["public.plain-text"]
    trace = json.loads((DIRECTORY / "output/ui-trace.json").read_text())
    assert trace["reference"] == REFERENCE and trace["accepted"] is False
    assert trace["steps"][-1]["results"] == [report["selectionResult"]]
    helper = json.loads((DIRECTORY / "helper-inputs.json").read_text())
    earlier = json.loads((DIRECTORY.parent / "file-input-types-20261017/inputs.json").read_text())
    assert helper == earlier, "Panel observation must bind the recorded source-built helper"
    print("FileInput panel: three raw native states and multiple-selection callback; strict acceptance pending")


if __name__ == "__main__":
    verify()
