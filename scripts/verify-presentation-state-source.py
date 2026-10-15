#!/usr/bin/env python3
"""Validate source investigation evidence without approving or starting Linux APIs."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "evidence/reference-investigations/presentation-states-20261014"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(directory=DIRECTORY):
    directory = Path(directory)
    report = json.loads((directory / "investigation.json").read_text())
    assert report["accepted"] is False, "Source investigation cannot self-approve acceptance"
    assert report["linuxImplementationStarted"] is False, "Source evidence cannot start Linux coverage"
    assert report["existingExpectedImagesChanged"] is False
    reference = json.loads((ROOT / "reference/source-manifest.json").read_text())["references"]["desktop"]
    assert report["reference"] == reference["revision"]
    actual = {str(p.relative_to(directory)) for p in directory.rglob("*") if p.is_file()}
    assert actual == set(report["files"]) | {"investigation.json"}, "Missing or extra investigation files"
    for name, expected in report["files"].items():
        path = Path(name)
        assert not path.is_absolute() and ".." not in path.parts, "Unsafe investigation path"
        assert digest(directory / path) == expected, f"Changed investigation file: {name}"
    manifest = json.loads((directory / "captures.json").read_text())
    assert manifest["reference"] == reference["revision"]
    assert manifest["sourceKeyboardStatus"].startswith("pending;"), "Source keyboard acceptance remains pending"
    captures = manifest["captures"]
    assert len(captures) == report["sourceCaptureCount"] == 304
    apis = {"BleeckerButton", "BleeckerEmptyState", "BleeckerErrorState", "BleeckerLoadingOverlay"}
    assert {c["api"] for c in captures} == apis, "Missing source presentation API"
    states = {"default", "normal", "empty-actions", "zero-actions", "two-actions", "empty-title", "empty-message",
              "empty-both", "long", "multiline", "narrow", "intrinsic", "rtl", "disabled"}
    for api in ("BleeckerEmptyState", "BleeckerErrorState"):
        assert states <= {c["variant"] for c in captures if c["api"] == api}, "Missing source action/layout states"
    assert {"default", "normal", "empty-message", "long", "multiline", "narrow", "intrinsic", "rtl"} <= {
        c["variant"] for c in captures if c["api"] == "BleeckerLoadingOverlay"}, "Missing source loading states"
    assert any(c["api"] == "BleeckerEmptyState" and c["variant"] == "custom-icon" for c in captures)
    matrix = set(itertools.product(["light", "dark"], [1, 1.5], [1, 2]))
    fixtures = {c["fixture"] for c in captures}
    for fixture in fixtures:
        rows = [c for c in captures if c["fixture"] == fixture]
        assert len(rows) == 8 and {(c["appearance"], c["textScale"], c["dpr"]) for c in rows} == matrix, "Incomplete source capture matrix"
    for c in captures:
        assert c["source"] == reference["revision"] and c["environmentDisplayScale"] == c["dpr"]
        assert c["status"] == "proposed reference candidate; no baseline approval"
        assert c["captureMethod"] == "SwiftUI.ImageRenderer/CoreGraphics"
        name = Path(c["path"])
        assert name.name == str(name) and name.suffix == ".png"
        data = (directory / name).read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR"
        assert struct.unpack(">II", data[16:24]) == (c["width"] * c["dpr"], c["height"] * c["dpr"])
        assert all(math.isfinite(c["componentSize"][k]) and c["componentSize"][k] > 0 for k in ("width", "height"))
        if c["api"] == "BleeckerButton":
            assert (c["width"], c["height"]) == (240, 96), "Source anchor canvas changed"
            continue
        if c["variant"] == "default" and c["api"] == "BleeckerErrorState":
            assert c["title"] == "Something went wrong", "Source error initializer default changed"
        if c["variant"] == "default" and c["api"] == "BleeckerLoadingOverlay":
            assert c["text"] == "Loading…", "Source loading initializer default changed"
        for key, family, size in [("title", "EncodeSans-SmBold", 17), ("message", "LibreFranklin-Regular", 13), ("loading", "EncodeSans-Md", 14)]:
            font = c["resolvedLabelFonts"][key]
            assert (font["postScriptName"], font["pointSize"]) == (family, size), "Source fixed typography changed"
    for api in ("BleeckerEmptyState", "BleeckerErrorState"):
        for appearance, scale, dpr in matrix:
            rows = {c["variant"]: c for c in captures if (c["api"], c["appearance"], c["textScale"], c["dpr"]) == (api, appearance, scale, dpr)}
            assert rows["zero-actions"]["componentSize"]["height"] - rows["empty-actions"]["componentSize"]["height"] == 12, "Source EmptyView/zero-view spacing changed"
    behavior = manifest["behavior"]
    assert len(behavior) == report["sourceBehaviorCases"] == 68, "Missing source pointer/lifecycle matrix"
    expected_actions = {"BleeckerEmptyState": {"activate", "producer-update", "disabled-click", "outside-release", "remove", "reopen"},
                        "BleeckerErrorState": {"activate", "producer-update", "disabled-click", "outside-release", "remove", "reopen"},
                        "BleeckerLoadingOverlay": {"center", "edge", "outside", "removed", "producer-update"}}
    expected = {(api, action, appearance, scale) for api, actions in expected_actions.items()
                for action, appearance, scale in itertools.product(actions, ["light", "dark"], [1, 1.5])}
    assert len(behavior) == len(expected) and {(b["api"], b["action"], b["appearance"], b["textScale"]) for b in behavior} == expected, "Missing source pointer/lifecycle matrix"
    for b in behavior:
        action = b["action"]
        assert b["dpr"] == 2, "Native source pointer DPR changed"
        if b["api"] == "BleeckerLoadingOverlay":
            assert b["underlyingPositiveControl"] == 1, "Missing successful underlying-input positive control"
            assert b["underlying"] == int(action in {"outside", "removed"}), "Invalid source overlay hit behavior"
            assert b["overlayAfterAction"] is (action != "removed")
            assert b["messageAfterAction"] == ("Updated loading message" if action == "producer-update" else "Create an edition to get started.")
        else:
            assert b["counter"] == int(action in {"activate", "producer-update", "remove"}), "Invalid source action counter"
            lifetime = (2, 1) if action == "reopen" else (1, 1) if action == "remove" else (1, 0)
            assert (b["mounts"], b["unmounts"]) == lifetime, "Invalid source action subtree lifecycle"
            assert b["presentAfterAction"] is (action != "remove"), "Invalid source presentation removal"
            assert b["titleAfterAction"] == ("Updated title" if action == "producer-update" else "No editions yet")
            assert b["messageAfterAction"] == ("Updated message" if action == "producer-update" else "Create an edition to get started.")
    lines = manifest["centeredTextLines"]
    assert len(lines) == report["centeredTextWitnesses"]
    assert len(lines) == 63 and {p["id"] for p in lines} == {f"lines-{i}" for i in range(63)}, "Invalid text witness identifiers"
    assert {(p["dpr"], p["offeredWidth"], p["text"]) for p in lines} == set(itertools.product(
        [1, 1.25, 1.5, 1.75, 2, 2.5, 3], [116, 180, 256],
        ["First line\nShort\nA longer final line", "Create an edition and invite the team to prepare its articles for publication.", "Trailing space \nShort "])), "Incomplete centered-text witnesses"
    for p in lines:
        original, probe = [directory / f"{p['id']}-{suffix}.png" for suffix in ("original", "probe")]
        same = original.read_bytes() == probe.read_bytes()
        assert same is p["probePngByteIdentical"], "False text-probe identity claim"
        if p["dpr"] in {1, 2}:
            assert same, "Integer-DPR text instrumentation changed source pixels"
        assert p["lines"] and all(math.isfinite(line[key]) for line in p["lines"] for key in ("x", "y", "width", "ascent", "descent"))
    assert sum(p["probePngByteIdentical"] for p in lines) == report["byteIdenticalTextWitnesses"]
    symbols = manifest["sourceSymbols"]
    assert len(symbols) == 21 and {(s["symbol"], s["dpr"]) for s in symbols} == set(itertools.product(
        ["tray", "exclamationmark.triangle", "archivebox"], [1, 1.25, 1.5, 1.75, 2, 2.5, 3]))
    provenance = json.loads((directory / "tooling-provenance.json").read_text())
    assert provenance["referenceRevision"] == reference["revision"] and provenance["referenceArchiveSha256"] == reference["sha256"]
    assert provenance["toolArtifact"]["sha256"] == report["sourceToolArtifact"]
    replay = provenance["cleanReplay"]
    assert replay["changedFiles"] == [] and replay["filesCompared"] == replay["byteIdenticalFiles"] == len(captures) + 2 * len(lines) + 1, "Native clean replay changed outputs"
    anchors = json.loads((directory / "anchor-comparison.json").read_text())
    assert len(anchors) == 2 and {a["appearance"] for a in anchors} == {"light", "dark"}
    for anchor in anchors:
        path = f"reference/captures/desktop/buttons/button-{anchor['appearance']}-primary-md-enabled.png"
        assert anchor["reference"] == path and digest(ROOT / path) == anchor["referenceSha256"], "Changed preserved source anchor"
        assert anchor["accepted"] is False
    return {"captures": len(captures), "behaviorCases": len(behavior), "lineWitnesses": len(lines),
            "byteIdenticalLineWitnesses": sum(p["probePngByteIdentical"] for p in lines), "accepted": False}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
