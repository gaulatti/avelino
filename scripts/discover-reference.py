#!/usr/bin/env python3
"""Discover pinned Swift API/asset surfaces; check inventory drift without rewriting it."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tarfile

ROOT = Path(__file__).resolve().parents[1]
VISUAL_PROTOCOLS = {"View", "ViewModifier", "ButtonStyle", "ToggleStyle", "UIViewRepresentable"}
TYPE = re.compile(r"\bpublic\s+(struct|enum|class|protocol)\s+(\w+)([^\n{]*)\{")
EXTENSION = re.compile(r"\bpublic\s+extension\s+(\w+)[^{]*\{")


def closing_brace(text, opening):
    """Balance Swift braces, ignoring quoted strings and line/block comments."""
    depth, i = 1, opening + 1
    while i < len(text):
        if text.startswith("//", i):
            end = text.find("\n", i)
            i = len(text) if end < 0 else end
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            if end < 0:
                raise ValueError("Unterminated comment")
            i = end + 2
        elif text[i] == '"':
            i += 1
            while i < len(text) and text[i] != '"':
                i += 2 if text[i] == "\\" else 1
            i += 1
        else:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    return i
            i += 1
    raise ValueError("Unbalanced declaration")


def location(text, offset, path):
    return {"path": path, "line": text.count("\n", 0, offset) + 1}


def discover(kind, record):
    declarations, modifiers, symbols, adapters, mono = [], [], [], [], []
    with tarfile.open(ROOT / record["artifact"]) as archive:
        sources = {m.name: archive.extractfile(m).read().decode() for m in archive.getmembers()
                   if m.isfile() and m.name.endswith(".swift")}
    for path, text in sorted(sources.items()):
        if not path.startswith("Sources/Sabella/"):
            continue
        for match in TYPE.finditer(text):
            end = closing_brace(text, match.end() - 1)
            body = text[match.start():end + 1]
            name, signature = match[2], match[3]
            television = name.startswith("SabellaTV")
            if (kind == "television") != television:
                continue
            inherited = signature.rsplit(":", 1)[-1]
            visual = bool(set(re.findall(r"\w+", inherited)) & VISUAL_PROTOCOLS)
            declarations.append({"name": name, "kind": match[1], "visual": visual,
                "signature": text[match.start():match.end()].strip(),
                "source": location(text, match.start(), path),
                "sha256": hashlib.sha256(body.encode()).hexdigest(),
                "publicMembers": re.findall(r"\bpublic\s+(?:init|(?:static\s+)?(?:let|var|func))[^\n{]*", body),
                "bindings": re.findall(r"@Binding\s+(?:public\s+)?var\s+(\w+)", body),
                "compositionSlots": re.findall(r"@ViewBuilder[^\n]*", body),
                "contractTypes": sorted(set(re.findall(r"\bBleecker\w+(?:Variant|Size|Type|Orientation)\b", body))),
                "enumCases": re.findall(r"\bcase\s+([^\n}]+)", body) if match[1] == "enum" else [],
                "stateInputs": re.findall(r"@(?:State|FocusState|Environment)[^\n]*", body)})
        if kind == "desktop":
            for match in EXTENSION.finditer(text):
                end = closing_brace(text, match.end() - 1)
                body = text[match.end():end]
                for function in re.finditer(r"\bfunc\s+(bleecker\w+)[^{]*", body):
                    modifiers.append({"name": f"{match[1]}.{function[1]}",
                        "signature": function[0].strip(),
                        "source": location(text, match.end() + function.start(), path)})
        television_file = "/Television" in path
        if (kind == "television") != television_file:
            continue
        for match in re.finditer(r"\b(systemName|systemImage)\s*:\s*([^\n]+)", text):
            symbols.append({"input": match[1], "expression": match[2].strip(),
                "source": location(text, match.start(), path),
                "resolution": "pending", "replacement": None, "provenance": None,
                "comparison": None, "exception": None})
        for match in re.finditer(r"\b(?:ProgressView|DatePicker|TextEditor|Picker|Divider)\s*\(|\.(?:help|popover|fileImporter|menuStyle|textFieldStyle|buttonStyle)\s*\(", text):
            adapters.append({"expression": match[0], "source": location(text, match.start(), path)})
        for match in re.finditer(r"BleeckerTypography\.mono\([^\n]*|\.system\([^\n]*\.monospaced[^\n]*", text):
            mono.append({"expression": match[0], "source": location(text, match.start(), path),
                "resolvedFace": None, "fixtureEvidence": None, "status": "pending"})
    catalog = sources["Sources/SabellaCatalogSupport/CatalogCoverage.swift"]
    registry = "registeredTelevisionComponents" if kind == "television" else "registeredComponents"
    registry_body = re.search(rf"{registry}:\s*Set<String>\s*=\s*\[(.*?)\]", catalog, re.S)[1]
    registered = sorted(re.findall(r'"(\w+)"', registry_body))
    visual_names = {d["name"] for d in declarations if d["visual"]}
    unknown = set(registered) - visual_names
    if unknown:
        raise ValueError(f"Catalog names absent from public visual discovery: {unknown}")
    return {"reference": record["revision"], "registered": registered, "declarations": declarations,
            "modifiers": modifiers, "symbolInputs": symbols, "platformAdapters": adapters,
            "monospaceUses": mono,
            "unregisteredVisualAPIs": sorted(visual_names - set(registered)),
            "caseDiscovery": "pending: extracted API inputs require explicit fixture matrices; counts do not establish coverage"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--initialize", action="store_true")
    args = parser.parse_args()
    if args.check == args.initialize:
        parser.error("Choose --check or --initialize; ordinary verification never updates expectations")
    manifest = json.loads((ROOT / "reference/source-manifest.json").read_text())
    output = {kind: discover(kind, manifest["references"][kind]) for kind in ["desktop", "television"]}
    target = ROOT / "reference/api-discovery.json"
    if args.check:
        assert json.loads(target.read_text()) == output, "Pinned API discovery drift; review explicitly"
        inventory = json.loads((ROOT / "docs/parity-inventory.json").read_text())
        for kind, discovery in output.items():
            expected = {d["name"] for d in discovery["declarations"] if d["visual"]}
            expected.update(m["name"] for m in discovery["modifiers"])
            actual = [entry["id"] for entry in inventory[kind]["entries"]]
            assert len(actual) == len(set(actual)) and set(actual) == expected, kind
            for entry in inventory[kind]["entries"]:
                if entry["status"] == "complete":
                    assert entry["caseDiscovery"] == "complete" and entry["cases"], entry["id"]
                    assert entry["implementation"] and entry["tests"] and entry["captures"] and entry["comparisonResults"], entry["id"]
                    assert all(gate["status"] == "passed" and gate["evidence"] for gate in entry["runtimeGates"].values()), entry["id"]
                    assert all(case["status"] == "passed" and case["evidence"] for case in entry["cases"]), entry["id"]
        print("API discovery and parity inventory reconciled; unfinished entries remain pending")
    else:
        if target.exists():
            raise SystemExit("Discovery already exists; updates require review, not initialization.")
        target.write_text(json.dumps(output, indent=2) + "\n")
        gates = ["offscreen", "x11", "wayland", "keyboardPointer", "focusAccessibility", "displayTextScaling", "installedConsumer"]
        inventory = {"schemaVersion": 1, "exceptions": {"proposed": [], "approved": []}}
        for kind, discovery in output.items():
            entries = []
            items = [d for d in discovery["declarations"] if d["visual"]] + discovery["modifiers"]
            for item in sorted(items, key=lambda d: d["name"]):
                entries.append({"id": item["name"], "status": "pending",
                    "reference": {"revision": discovery["reference"], **item["source"]},
                    "implementation": [], "caseDiscovery": "pending", "cases": [], "tests": [],
                    "captures": [], "comparisonResults": [], "exceptions": [],
                    "runtimeGates": {g: {"status": "pending", "evidence": []} for g in
                                     gates + (["physicalRemote", "sustainedPlayback", "targetHardware"] if kind == "television" else [])}})
            inventory[kind] = {"acceptance": "pending", "registeredCount": len(discovery["registered"]), "entries": entries}
        (ROOT / "docs/parity-inventory.json").write_text(json.dumps(inventory, indent=2) + "\n")
        print("Initial discovery written; every implementation and acceptance gate is pending")


if __name__ == "__main__":
    main()
