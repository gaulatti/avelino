#!/usr/bin/env python3
"""Prepare review-only native evidence; never write accepted reference images."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def prepare(source, tooling, output, scope=None):
    source, tooling, output = Path(source), Path(tooling), Path(output).resolve()
    assert not output.is_relative_to(ROOT / "reference"), "Accepted reference locations are forbidden"
    output.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((source / "captures.json").read_text())
    provenance = json.loads(tooling.read_text())
    expected = json.loads((ROOT / "reference/source-manifest.json").read_text())["references"]["desktop"]
    assert manifest["reference"] == provenance["referenceRevision"] == expected["revision"]
    assert provenance["referenceArchiveSha256"] == expected["sha256"]
    if scope is not None:
        assert scope == "desktop-composition", "Unknown reference proposal scope"
        assert {c["api"] for c in manifest["captures"]} == {
            "BleeckerButton", "BleeckerSectionHeader", "BleeckerDashboardSection", "BleeckerDashboardGrid",
            "BleeckerAppShell", "BleeckerFooter", "BleeckerFeedItem", "BleeckerProgressStack"}
        manifest["scope"] = scope
    blanks, fixtures, intentional_empty = [], {}, set()
    for case in manifest["captures"]:
        name = Path(case["path"])
        assert name.name == str(name) and name.suffix == ".png", "Only named PNG captures can be copied"
        file = source / name
        image = Image.open(file).convert("RGBA")
        assert image.size == (case["width"] * case["dpr"], case["height"] * case["dpr"])
        assert case["environmentDisplayScale"] == case["dpr"]
        empty = case.get("expectedEmpty", False)
        if empty:
            assert scope == "desktop-composition" and case["api"] == "BleeckerDashboardGrid" and case["variant"] == "empty"
            assert case["componentSize"]["width"] > 0 and case["componentSize"]["height"] == 0
            intentional_empty.add(case["fixture"])
        else:
            assert case["componentSize"]["width"] > 0 and case["componentSize"]["height"] > 0
        uniform = ImageChops.difference(image, Image.new("RGBA", image.size, image.getpixel((0, 0)))).getbbox(alpha_only=False) is None
        assert not empty or uniform, "An expected-empty grid must render only its background"
        if uniform and not empty:
            blanks.append(case["fixture"])
        case["sha256"] = sha(file)
        profile = Image.open(file).info.get("icc_profile")
        case["pngIccProfileSha256"] = hashlib.sha256(profile).hexdigest() if profile else None
        shutil.copyfile(file, output / name)
        fixtures[case["fixture"]] = {key: case[key] for key in ["fixture", "api", "width", "height", "variant", "size", "value", "flag", "text"]}
        if "expectedEmpty" in case: fixtures[case["fixture"]]["expectedEmpty"] = empty
    assert not blanks, f"Blank native captures: {blanks}"
    manifest["unrenderedCases"] = blanks
    manifest["captureValidation"] = {"dimensions": "passed", "environmentDpr": "passed", "componentDimensions": "passed", "blankImages": blanks}
    if intentional_empty: manifest["expectedEmptyCases"] = sorted(intentional_empty)
    write(output / "captures.json", manifest)
    shutil.copyfile(tooling, output / "tooling-provenance.json")
    definitions = {"schemaVersion": 1, "status": "proposed supplemental fixture definitions; baseline approval pending",
        "fixtures": list(fixtures.values()), "sourceToolArtifact": provenance["toolArtifact"]["sha256"],
        "wrapper": "Component centered in a fixed logical frame; palette background, requested color scheme/text scale, en_US locale; no root font or foreground override. Explicit inherited-toggle and Encode Sans toggle cases are separate."}
    write(output / "fixtures.json", definitions)
    comparisons = []
    for appearance in ["light", "dark"]:
        candidate = output / f"button-anchor-{appearance}-text1.0-offscreen-dpr2.0.png"
        reference = ROOT / f"reference/captures/desktop/buttons/button-{appearance}-primary-md-enabled.png"
        a, b = Image.open(candidate).convert("RGBA"), Image.open(reference).convert("RGBA")
        assert a.size == b.size
        pixels = list(ImageChops.difference(a, b).get_flattened_data())
        comparisons.append({"appearance": appearance, "changedPixels": sum(any(p) for p in pixels),
            "maxChannelDifference": max(max(p) for p in pixels), "candidate": candidate.name,
            "reference": str(reference.relative_to(ROOT)), "referenceSha256": sha(reference),
            "status": "diagnostic difference; no baseline update or tolerance approval"})
    write(output / "anchor-comparison.json", comparisons)
    index = {api: {"fixtures": sorted({c["fixture"] for c in manifest["captures"] if c["api"] == api}),
        "captures": [c["path"] for c in manifest["captures"] if c["api"] == api],
        "status": "proposed; not accepted reference"} for api in sorted({c["api"] for c in manifest["captures"]})}
    write(output / "api-index.json", index)
    mono = [{"fixture": c["path"], "size": c["value"], "weight": c["variant"],
        "font": c["resolvedLabelFonts"]["sourceMonospaceExpression"],
        "status": "resolved source expression; Linux counterpart, glyph fallback and affected component fixture checks pending"}
        for c in manifest["captures"] if c["api"] == "MonospaceProbe" and c["appearance"] == "light" and c["textScale"] == 1 and c["dpr"] == 2]
    write(output / "monospace-resolution.json", {"reference": manifest["reference"], "fontFilesRedistributed": False, "probes": mono})
    proposal = {"schemaVersion": 1, "status": "proposed; no reference baseline approval", "referenceRevision": manifest["reference"],
        "captures": len(manifest["captures"]), "fixtureDefinitions": len(fixtures), "startedDesktopApisCovered": len(index) - ("MonospaceProbe" in index),
        "extraProbeApi": "MonospaceProbe" if "MonospaceProbe" in index else None, "nativeDescendantCaptures": sum("NSHostingView" in c["captureMethod"] for c in manifest["captures"]),
        "sourceToolArtifact": provenance["toolArtifact"]["sha256"], "accepted": False, "existingExpectedImagesChanged": False,
        "postprocessor": {"path": "scripts/prepare-proposal.py", "sha256": sha(Path(__file__))},
        "limitations": ["Offscreen rendering and native view caching are separate from actual display-session and overlay acceptance.",
            "Native windows have measured DPR 2; native DPR 1 session evidence is missing.",
            "Loading/skeleton animation timing is diagnostic, not deterministic phase acceptance.",
            "System-font substitutions and emoji glyph fallback remain unresolved.",
            "Tool source is in the immutable external workspace artifact; no public download endpoint.",
            "Linux matching isolated fixtures/comparisons and complete behavior cases remain pending."],
        "files": {str(p.relative_to(output)): sha(p) for p in sorted(output.rglob("*")) if p.is_file()}}
    if scope is not None: proposal["scope"] = scope
    write(output / "proposal.json", proposal)
    return len(manifest["captures"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--captures", required=True)
    parser.add_argument("--tooling", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--scope", choices=["desktop-composition"])
    args = parser.parse_args()
    print(f"Prepared {prepare(args.captures, args.tooling, args.output, args.scope)} review candidates; expected images unchanged")
