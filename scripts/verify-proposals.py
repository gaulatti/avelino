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
    "desktop-checkbox": {"BleeckerButton", "BleeckerCheckbox"}}

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
            "desktop-checkbox": "Missing checkbox API"}[scoped]
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
