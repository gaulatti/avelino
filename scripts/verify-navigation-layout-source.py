#!/usr/bin/env python3
"""Verify measured public PageHeader/Breadcrumb source; never approve parity."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "evidence/reference-investigations/navigation-layout-20261015"
PAGE_VARIANTS = {
    "normal", "intrinsic", "narrow", "very-narrow", "long", "empty-eyebrow",
    "empty-title", "empty-description", "empty-labels", "multiline", "unicode",
    "rtl", "disabled", "zero", "rect", "two", "tall", "overflow", "button",
    "buttons", "text", "custom-font", "parent-font20", "narrow-button",
    "very-narrow-button", "narrow-buttons", "narrow-two", "intrinsic-two",
    "intrinsic-button",
}
BREADCRUMB_VARIANTS = {
    "normal", "intrinsic", "narrow", "very-narrow", "empty", "single",
    "no-icons", "all-icons", "empty-labels", "multiline", "long", "rtl",
    "disabled", "nil-handler", "parent-font20", "single-empty",
    "single-empty-icon", "zero-labels-no-icons", "rtl-narrow",
}
ACTIONS = {"activate", "producer-update", "disabled-click", "outside-release",
           "replace", "reopen", "rtl", "nil-handler"}
TEXT_WIDTHS = {0, 1, 9, 30, 31, 32, 60, 64, 120, 180, 240, 320}
FONTS = {
    "eyebrow": (10, "EncodeSans-Bold"),
    "title": (25, "EncodeSans-SmBold"),
    "description": (13, "LibreFranklin-Regular"),
    "breadcrumb": (12, "EncodeSans-Regular"),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def named(directory, name):
    path = Path(name)
    assert path.name == name and path.suffix == ".png", "Unsafe native PNG name"
    return directory / path


def rectangle(value):
    assert set(value) == {"x", "y", "width", "height"}
    assert all(isinstance(n, (int, float)) and math.isfinite(n) for n in value.values())
    assert value["width"] >= 0 and value["height"] >= 0


def font(value, key):
    size, name = FONTS[key]
    assert value == {"pointSize": size, "postScriptName": name}, "Source navigation font changed"


def verify(directory=DIRECTORY):
    directory = Path(directory)
    report = json.loads((directory / "investigation.json").read_text())
    reference = json.loads((ROOT / "reference/source-manifest.json").read_text())["references"]["desktop"]
    assert report["accepted"] is False and report["existingExpectedImagesChanged"] is False
    assert report["reference"] == reference["revision"]
    actual = {str(p.relative_to(directory)) for p in directory.rglob("*") if p.is_file()}
    assert actual == set(report["files"]) | {"investigation.json"}, "Missing or extra native evidence"
    for name, checksum in report["files"].items():
        path = Path(name)
        assert not path.is_absolute() and ".." not in path.parts
        assert digest(directory / path) == checksum, name
    data = json.loads((directory / "captures.json").read_text())
    assert data["reference"] == reference["revision"]
    captures = data["captures"]
    assert len(captures) == 392, "Missing source navigation capture"
    axes = set(itertools.product(["light", "dark"], [1, 1.5], [1, 2]))
    for api, variants in [("BleeckerPageHeader", PAGE_VARIANTS),
                          ("BleeckerBreadcrumb", BREADCRUMB_VARIANTS),
                          ("BleeckerButton", {"default"})]:
        observed = [(c["variant"], c["appearance"], c["textScale"], c["dpr"])
                    for c in captures if c["api"] == api]
        assert len(observed) == len(set(observed)) == len(variants) * len(axes)
        assert set(observed) == {(v, *a) for v in variants for a in axes}, "Incomplete navigation source matrix"
    assert {c["api"] for c in captures} == {"BleeckerPageHeader", "BleeckerBreadcrumb", "BleeckerButton"}
    for c in captures:
        assert c["source"] == reference["revision"]
        assert c["captureMethod"] == "SwiftUI.ImageRenderer/CoreGraphics"
        assert c["status"] == "proposed reference candidate; no baseline approval"
        assert c["environmentDisplayScale"] == c["dpr"]
        original = named(directory, c["path"]).read_bytes()
        assert c["instrumentedPngByteIdentical"] is True and original == named(directory, c["instrumentedPath"]).read_bytes(), "Native instrumentation identity failed"
        assert c["layoutWitnessPngByteIdentical"] is True and original == named(directory, c["layoutWitnessPath"]).read_bytes(), "Native layout witness identity failed"
        frame = (240, 96) if c["api"] == "BleeckerButton" else (720, 800)
        assert (c["width"], c["height"]) == frame
        assert original[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", original[16:24]) == tuple(v * c["dpr"] for v in frame)
        rectangle(c["componentRect"])
        assert c["componentSize"] == {k: c["componentRect"][k] for k in ["width", "height"]}
        for r in c["layoutWitnessRects"].values():
            rectangle(r)
        blank = (c["api"] == "BleeckerPageHeader" and c["variant"] == "empty-labels") or (
            c["api"] == "BleeckerBreadcrumb" and c["variant"] in {"empty", "single-empty"})
        assert c["expectedEmpty"] is blank, "Invalid intentional empty source case"
        with Image.open(directory / c["path"]) as image:
            image = image.convert("RGBA")
            uniform = ImageChops.difference(image, Image.new("RGBA", image.size, image.getpixel((0, 0)))).getbbox(alpha_only=False) is None
        assert uniform is blank, "Unexpected blank/nonblank source output"
        if c["api"] == "BleeckerPageHeader":
            rects, fonts = c["layoutWitnessRects"], c["layoutWitnessFonts"]
            assert set(rects) == {"labels", "eyebrow", "title", "description", "spacer", "actions"}
            for key in ["eyebrow", "title", "description"]:
                font(fonts[key], key)
            assert rects["title"]["y"] == rects["eyebrow"]["y"] + rects["eyebrow"]["height"] + 4
            assert rects["description"]["y"] == rects["title"]["y"] + rects["title"]["height"] + 4
            assert rects["labels"]["height"] == sum(rects[k]["height"] for k in ["eyebrow", "title", "description"]) + 8
            for key, text in [("eyebrow", c["eyebrow"]), ("title", c["title"]), ("description", c["text"])]:
                if text == "":
                    assert (rects[key]["width"], rects[key]["height"]) == (0, 14), "Empty source label line box changed"
            for key in ["labels", "actions", "spacer"]:
                assert rects[key]["y"] + rects[key]["height"] / 2 == c["componentRect"]["y"] + c["componentRect"]["height"] / 2
            visual = ["actions", "spacer", "labels"] if c["rtl"] else ["labels", "spacer", "actions"]
            for left, right in zip(visual, visual[1:]):
                assert rects[right]["x"] - rects[left]["x"] - rects[left]["width"] == 24, "Source header group spacing changed"
            assert rects["spacer"]["width"] >= 8
            for key in ["eyebrow", "title", "description"]:
                label = rects[key]
                assert label["x"] + (label["width"] if c["rtl"] else 0) == rects["labels"]["x"] + (rects["labels"]["width"] if c["rtl"] else 0), "Source header leading alignment changed"
        elif c["api"] == "BleeckerBreadcrumb":
            count = len(c["titles"])
            rects, fonts = c["layoutWitnessRects"], c["layoutWitnessFonts"]
            assert {k for k in rects if k.startswith("button-")} == {f"button-{i}" for i in range(count)}
            assert {k for k in rects if k.startswith("separator-")} == {f"separator-{i}" for i in range(1, count)}
            for i in range(count):
                font(fonts[f"text-{i}"], "breadcrumb")
                button, label = rects[f"button-{i}"], rects[f"text-{i}"]
                if i < len(c["icons"]) and c["icons"][i]:
                    icon = rects[f"icon-{i}"]
                    left, right = (label, icon) if c["rtl"] else (icon, label)
                    assert right["x"] - left["x"] - left["width"] == 5, "Source breadcrumb icon spacing changed"
                    assert button["width"] == label["width"] + icon["width"] + 5
                else:
                    assert button["width"] == label["width"]
                if i:
                    previous, separator = rects[f"button-{i-1}"], rects[f"separator-{i}"]
                    visual = [button, separator, previous] if c["rtl"] else [previous, separator, button]
                    for left, right in zip(visual, visual[1:]):
                        assert right["x"] - left["x"] - left["width"] == 8, "Source breadcrumb separator spacing changed"
            if c["variant"] == "empty":
                assert c["componentSize"] == {"width": 0, "height": 0}, "Empty source breadcrumb geometry changed"
            if c["variant"] == "single-empty":
                assert c["componentSize"] == {"width": 0, "height": 14}, "Empty source breadcrumb label geometry changed"
    behavior = data["behavior"]
    assert len(behavior) == 32 and {(b["api"], b["action"], b["textScale"]) for b in behavior} == set(itertools.product(["BleeckerPageHeader", "BleeckerBreadcrumb"], ACTIONS, [1, 1.5]))
    for b in behavior:
        assert b["nativeDpr"] == 2 and set(b["nativeWindowState"]) == {"key", "main", "applicationActive"}
        action = b["action"]
        if b["api"] == "BleeckerPageHeader":
            reset = action in {"replace", "reopen"}
            empty = action == "nil-handler"  # Helper branch supplies EmptyView actions.
            expected = (int(action in {"activate", "producer-update", "rtl"}), 0 if empty else 2 if reset else 1, int(reset))
            assert (b["counter"], b["mounts"], b["unmounts"]) == expected, "Native header lifecycle changed"
            assert b["titleAfterAction"] == ("Updated title" if action == "producer-update" else "Editions")
        else:
            disabled = action in {"disabled-click", "nil-handler"}
            expected = [] if disabled or action == "outside-release" else [0, 0] if action == "replace" else [2, 2]
            assert b["selected"] == expected, "Native breadcrumb index callback changed"
            expected_hits = set() if disabled else {"0"} if action == "replace" else {"0", "1", "2"}
            assert set(b["buttonHitXs"]) == expected_hits, "Native breadcrumb hit scan changed"
            assert all(xs and all(math.isfinite(x) for x in xs) for xs in b["buttonHitXs"].values())
    expressions = data["expressions"]
    assert len(expressions) == 30 and {(e["key"], e["variant"], e["dpr"]) for e in expressions} == set(itertools.product(["eyebrow", "title", "description", "separator", "icon"], ["normal", "empty", "parent-font20"], [1, 2]))
    for e in expressions:
        rectangle(e["rect"])
        assert named(directory, e["path"]).is_file()
    text = json.loads((directory / "text-layout/measurements.json").read_text())
    assert len(text) == 104 and {(r["key"], r["text"] == "", r["offeredWidth"], r["dpr"]) for r in text} == {
        (key, empty, width, dpr) for key in FONTS for empty, width in [(False, w) for w in TEXT_WIDTHS] + [(True, 180)] for dpr in [1, 2]}
    untrusted = []
    for r in text:
        path = named(directory / "text-layout", r["path"])
        same = path.read_bytes() == path.with_name(path.stem + "-probed.png").read_bytes()
        bounds_same = (r["componentWidth"], r["componentHeight"]) == (r["probedWidth"], r["probedHeight"])
        assert r["probeByteIdentical"] is same
        assert r["lineEvidenceTrusted"] is (same and bounds_same), "Untrusted text renderer cannot supply accepted line evidence"
        font(r["font"], r["key"])
        if not r["lineEvidenceTrusted"]:
            untrusted.append(r["path"])
        elif r["text"]:
            assert r["lines"] and all(set(line) == {"x", "y", "width", "ascent", "descent"} for line in r["lines"])
        else:
            assert r["componentWidth"] == 0 and r["componentHeight"] == 14 and r["lines"] == []
    assert len(untrusted) == 22 and sorted(untrusted) == report["untrustedTextWitnesses"], "Untrusted text renderer list changed"
    provenance = json.loads((directory / "tooling-provenance.json").read_text())
    assert provenance["referenceRevision"] == reference["revision"] and provenance["referenceArchiveSha256"] == reference["sha256"]
    assert provenance["toolArtifact"]["sha256"] == report["sourceToolArtifact"] and len(provenance["toolArtifact"]["files"]) == 37
    replay = json.loads((directory / "clean-replay.json").read_text())
    assert replay["inputHashesVerified"] == 37 and replay["filesCompared"] == replay["byteIdenticalFiles"] == 1416 and replay["changedFiles"] == [], "Native navigation replay changed"
    assert len(replay["results"]) == 1416
    for row in replay["results"]:
        path = Path(row["path"])
        assert path.parts[0] in {"captures", "text-layout"} and ".." not in path.parts
        preserved = directory / (Path(*path.parts[1:]) if path.parts[0] == "captures" else path)
        assert row["byteIdentical"] is True and row["sha256"] == row["replaySha256"] == digest(preserved), "Native navigation replay file mismatch"
    return {"captures": 392, "publicComponentInstrumentationIdentity": 392,
            "layoutWitnessIdentity": 392, "sourcePointerLifecycleCases": 32,
            "isolatedTextCases": 104, "trustedTextLineWitnesses": 82,
            "untrustedTextLineWitnesses": 22, "byteIdenticalReplayFiles": 1416,
            "linuxImplementation": "pending", "accepted": False}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
