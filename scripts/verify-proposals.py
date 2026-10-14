#!/usr/bin/env python3
"""Verify proposed native captures without adopting them as expected images."""
import hashlib
import itertools
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_AXES = {
    "BleeckerCard": {"variant": "BleeckerCardVariant", "size": "BleeckerCardPadding"},
    "BleeckerProgress": {"variant": "BleeckerProgressVariant", "size": "BleeckerProgressSize"},
    "BleeckerAvatar": {"size": "BleeckerAvatarSize"},
    "BleeckerLoadingSpinner": {"size": "BleeckerLoadingSize"},
    "BleeckerTextField": {"size": "BleeckerControlSize"},
    "BleeckerStatusBadge": {"variant": "BleeckerStatusBadgeVariant"},
    "BleeckerToggleStyle": {"variant": "BleeckerToggleVariant"},
}
COMPOSITION_APIS = {"BleeckerButton", "BleeckerSectionHeader", "BleeckerDashboardSection",
    "BleeckerDashboardGrid", "BleeckerAppShell", "BleeckerFooter", "BleeckerFeedItem", "BleeckerProgressStack"}
SCOPED_APIS = {"desktop-composition": COMPOSITION_APIS,
    "desktop-selectors": {"BleeckerButton", "BleeckerSelect"},
    "desktop-checkbox": {"BleeckerButton", "BleeckerCheckbox"},
    "desktop-secure-field": {"BleeckerButton", "BleeckerSecureField"},
    "desktop-search-field": {"BleeckerButton", "BleeckerTextField", "BleeckerSearchField"},
    "desktop-collection-filters": {"BleeckerButton", "BleeckerFilterChip", "BleeckerCollectionFilters"}}

SCOPED_CONTRACT_AXES = {"desktop-checkbox": {"BleeckerCheckbox": {"size": "BleeckerControlSize"}}}


def verify(directory):
    directory = Path(directory)
    proposal = json.loads((directory / "proposal.json").read_text())
    assert proposal["accepted"] is False, "A proposal cannot self-approve a reference baseline"
    assert proposal["existingExpectedImagesChanged"] is False
    reference = json.loads((ROOT / "reference/source-manifest.json").read_text())["references"]["desktop"]
    assert proposal["referenceRevision"] == reference["revision"]
    expected_files = set(proposal["files"])
    actual_files = {str(p.relative_to(directory)) for p in directory.rglob("*") if p.is_file()}
    assert actual_files == expected_files | {"proposal.json"}, "Missing or extra proposal files"
    for name, checksum in proposal["files"].items():
        path = Path(name)
        assert not path.is_absolute() and ".." not in path.parts, "Unsafe proposal path"
        assert hashlib.sha256((directory / path).read_bytes()).hexdigest() == checksum, name
    manifest = json.loads((directory / "captures.json").read_text())
    fixtures = json.loads((directory / "fixtures.json").read_text())["fixtures"]
    definitions = {f["fixture"]: f for f in fixtures}
    assert len(definitions) == len(fixtures) == proposal["fixtureDefinitions"]
    captures = manifest["captures"]
    assert len(captures) == proposal["captures"] and not manifest["unrenderedCases"]
    scoped = proposal.get("scope")
    if scoped:
        assert scoped in SCOPED_APIS and manifest.get("scope") == scoped
        message = {"desktop-composition": "Missing composition API", "desktop-selectors": "Missing selector API",
            "desktop-checkbox": "Missing checkbox API", "desktop-secure-field": "Missing secure-field API",
            "desktop-search-field": "Missing search-field API", "desktop-collection-filters": "Missing collection-filter API"}[scoped]
        assert {case["api"] for case in captures} == SCOPED_APIS[scoped], message
    keys = set()
    for case in captures:
        assert case["source"] == reference["revision"]
        assert case["status"] == "proposed reference candidate; no baseline approval"
        assert case["environmentDisplayScale"] == case["dpr"]
        definition = definitions[case["fixture"]]
        assert all(case[key] == value for key, value in definition.items()), case["fixture"]
        key = (case["fixture"], case["appearance"], case["textScale"], case["dpr"], case["captureMethod"])
        assert key not in keys, "Duplicate capture case"
        keys.add(key)
        data = (directory / case["path"]).read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR"
        assert struct.unpack(">II", data[16:24]) == (case["width"] * case["dpr"], case["height"] * case["dpr"])
        assert hashlib.sha256(data).hexdigest() == case["sha256"]
        if case.get("expectedEmpty", False):
            assert scoped == "desktop-composition" and case["api"] == "BleeckerDashboardGrid" and case["variant"] == "empty", "Invalid empty fixture"
            assert case["componentSize"]["width"] > 0 and case["componentSize"]["height"] == 0, "Invalid empty fixture geometry"
        else:
            assert case["componentSize"]["width"] > 0 and case["componentSize"]["height"] > 0
    for fixture in definitions:
        rows = [c for c in captures if c["fixture"] == fixture]
        assert {(c["appearance"], c["textScale"]) for c in rows} == set(itertools.product(["light", "dark"], [1, 1.5]))
        expected_dprs = {1, 2} if rows[0]["captureMethod"] == "SwiftUI.ImageRenderer/CoreGraphics" else {2}
        assert {(c["appearance"], c["textScale"], c["dpr"]) for c in rows} == set(itertools.product(["light", "dark"], [1, 1.5], expected_dprs))
    if scoped == "desktop-secure-field":
        required = {f"{mode}-{state}" for mode in ["masked", "revealed"]
                    for state in ["empty", "filled", "long", "disabled", "narrow"]}
        assert required <= {f["variant"] for f in fixtures if f["api"] == "BleeckerSecureField"}, "Missing secure-field state combinations"
        for case in captures:
            if case["api"] != "BleeckerSecureField": continue
            revealed = case["variant"].startswith("revealed-")
            assert case.get("revealed") is revealed and case.get("sourceValuePreserved") is True, "Invalid source reveal/value state"
            fonts = case["nativeControlFonts"]
            assert len(fonts) == 1 and fonts[0]["secure"] is not revealed, "Invalid native secure/plain editor"
            assert fonts[0]["pointSize"] == 14 and fonts[0]["fontName"] == "EncodeSans-Regular", "Invalid native secure-field font"
            assert fonts[0]["enabled"] is not case["flag"], "Invalid native disabled state"
    if scoped == "desktop-search-field":
        for api in ["BleeckerSearchField", "BleeckerTextField"]:
            required = {"empty", "filled", "long", "disabled", "narrow", "cleared"} | ({"error"} if api == "BleeckerTextField" else set())
            sizes = ["sm", "md", "lg"] if api == "BleeckerTextField" else ["md"]
            assert {(size, state) for size in sizes for state in required} <= {(f["size"], f["variant"]) for f in fixtures if f["api"] == api}, "Missing search-field state combinations"
        for case in captures:
            if case["api"] == "BleeckerButton": continue
            cleared = case["variant"] == "cleared"
            assert case.get("clearButtonActivated") is cleared and case.get("sourceBindingChecked") is True, "Invalid source clear state"
            assert case.get("sourceValueAfterAction") == ("" if cleared else case["text"]), "Invalid source clear value"
            fonts = case["nativeControlFonts"]
            assert len(fonts) == 1 and fonts[0]["secure"] is False and fonts[0]["enabled"] is not case["flag"], "Invalid native search editor"
            assert fonts[0]["pointSize"] == (12 if case["size"] == "sm" else 14) * case["textScale"] and fonts[0]["fontName"] == "EncodeSans-Regular", "Invalid native search font"
    if scoped == "desktop-collection-filters":
        chip_variants = {"plain", "removable", "disabled", "removable-disabled", "empty", "removable-empty", "narrow", "removable-narrow"}
        assert {(variant, flag) for variant in chip_variants for flag in [False, True]} <= {(f["variant"], f["flag"]) for f in fixtures if f["api"] == "BleeckerFilterChip"}, "Missing filter-chip state combinations"
        required = {"empty", "chip", "selected", "filled", "disabled", "narrow", "long", "cleared", "removed", "activated", "tall"}
        assert required <= {f["variant"] for f in fixtures if f["api"] == "BleeckerCollectionFilters"}, "Missing collection-filter state combinations"
        for case in captures:
            if case["api"] == "BleeckerFilterChip":
                font = case["resolvedLabelFonts"]["chipExpression"]
                assert font["pointSize"] == 12 and font["postScriptName"] == "EncodeSans-Md", "Invalid fixed chip font"
            if case["api"] != "BleeckerCollectionFilters": continue
            variant = case["variant"]
            assert case.get("sourceQueryAfterAction") == ("" if variant == "cleared" else case["text"]), "Invalid collection query state"
            assert case.get("sourceContentAfterAction") is (variant not in {"empty", "removed"}), "Invalid collection content state"
            assert case.get("sourceSelectedAfterAction") is (variant in {"selected", "activated"}), "Invalid collection selected state"
            assert case.get("sourceActionCounts") == {"activations": int(variant == "activated"), "removals": int(variant == "removed")}, "Invalid collection action counts"
            fonts = case["nativeControlFonts"]
            assert len(fonts) == 1 and fonts[0]["pointSize"] == 14*case["textScale"] and fonts[0]["fontName"] == "EncodeSans-Regular", "Invalid collection editor font"
            assert fonts[0]["enabled"] is not case["flag"], "Invalid collection disabled state"
    discovery = json.loads((ROOT / "reference/api-discovery.json").read_text())["desktop"]
    declarations = {d["name"]: d for d in discovery["declarations"]}
    for api, axes in {**CONTRACT_AXES, **SCOPED_CONTRACT_AXES.get(scoped, {})}.items():
        if scoped and api not in SCOPED_APIS[scoped]: continue
        values = []
        for contract in axes.values():
            names = [name.strip().strip("`") for row in declarations[contract]["enumCases"] for name in row.split(",")]
            assert all(re.fullmatch(r"\w+", name) for name in names), contract
            values.append(names)
        actual = {tuple(f[key] for key in axes) for f in fixtures if f["api"] == api}
        assert set(itertools.product(*values)) <= actual, f"Missing discovered contract combinations for {api}"
    index = json.loads((directory / "api-index.json").read_text())
    assert set(index) == {c["api"] for c in captures}
    for api, entry in index.items():
        assert set(entry["captures"]) == {c["path"] for c in captures if c["api"] == api}
        assert set(entry["fixtures"]) == {c["fixture"] for c in captures if c["api"] == api}
    tooling = json.loads((directory / "tooling-provenance.json").read_text())
    assert tooling["referenceArchiveSha256"] == reference["sha256"]
    assert tooling["toolArtifact"]["sha256"] == proposal["sourceToolArtifact"]
    for comparison in json.loads((directory / "anchor-comparison.json").read_text()):
        assert hashlib.sha256((ROOT / comparison["reference"]).read_bytes()).hexdigest() == comparison["referenceSha256"]
    return len(captures)


if __name__ == "__main__":
    for directory in sorted((ROOT / "evidence/reference-proposals").iterdir()):
        if (directory / "proposal.json").is_file():
            count = verify(directory)
            print(f"{directory.name}: {count} proposed captures verified; baseline approval and external tool replay remain separate")
