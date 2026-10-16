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
    "desktop-collection-filters": {"BleeckerButton", "BleeckerFilterChip", "BleeckerCollectionFilters"},
    "desktop-slider": {"BleeckerButton", "BleeckerSlider"},
    "desktop-tabs": {"BleeckerButton", "BleeckerSegmentedControl", "BleeckerTabs"},
    "desktop-pagination": {"BleeckerButton", "BleeckerIconButton", "BleeckerPagination"},
    "desktop-pagination-integers": {"BleeckerButton", "BleeckerPagination"},
    "desktop-accordion": {"BleeckerButton", "BleeckerAccordion"},
    "desktop-presentation-states": {"BleeckerButton", "BleeckerEmptyState", "BleeckerErrorState", "BleeckerLoadingOverlay"},
    "desktop-alert":{"BleeckerButton","BleeckerAlert"},
    "desktop-navigation-layout":{"BleeckerButton","BleeckerPageHeader","BleeckerBreadcrumb"},
    "desktop-sidebar-brand":{"BleeckerButton","BleeckerSidebarItem","BleeckerBrandMark","BleeckerBrandLockup"},
    "desktop-data-metrics":{"BleeckerButton","BleeckerIconBadge","BleeckerMetric","BleeckerStatCard","BleeckerKbd"}}

SCOPED_CONTRACT_AXES = {"desktop-data-metrics":{"BleeckerIconBadge":{"size":"BleeckerIconBadgeSize","variant":"BleeckerIconBadgeVariant"},"BleeckerMetric":{"format":"BleeckerMetricFormat"},"BleeckerStatCard":{"format":"BleeckerMetricFormat"}},"desktop-alert":{"BleeckerAlert":{"alertType":"BleeckerAlertType"}},"desktop-pagination": {"BleeckerIconButton": {"size":"BleeckerIconButtonSize", "variant":"BleeckerIconButtonVariant"}}, "desktop-checkbox": {"BleeckerCheckbox": {"size": "BleeckerControlSize"}}}


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
            "desktop-search-field": "Missing search-field API", "desktop-collection-filters": "Missing collection-filter API", "desktop-slider": "Missing slider API", "desktop-tabs": "Missing tabs API", "desktop-pagination": "Missing pagination API", "desktop-pagination-integers": "Missing exact pagination API", "desktop-accordion": "Missing accordion API", "desktop-presentation-states": "Missing presentation-state API", "desktop-alert":"Missing alert API", "desktop-navigation-layout":"Missing navigation layout API", "desktop-sidebar-brand":"Missing sidebar/brand API", "desktop-data-metrics":"Missing data-display API"}[scoped]
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
            if scoped=="desktop-sidebar-brand":
                edge=float(case["size"])
                assert case["api"]=="BleeckerBrandMark" and edge in {0,1}, "Invalid uniform brand case"
                assert case["componentSize"]=={"width":edge,"height":edge}, "Invalid uniform brand geometry"
            elif scoped=="desktop-navigation-layout":
                assert (case["api"],case["variant"]) in {("BleeckerPageHeader","empty-labels"),("BleeckerBreadcrumb","empty"),("BleeckerBreadcrumb","single-empty")}, "Invalid navigation empty fixture"
                assert case["componentSize"]==({"width":0,"height":0} if case["variant"]=="empty" else {"width":0,"height":14} if case["variant"]=="single-empty" else {"width":560,"height":50}), "Invalid navigation empty geometry"
            else:
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
    if scoped == "desktop-slider":
        required = {"continuous", "lower", "upper", "disabled", "narrow", "stepped", "off-grid", "signed", "shifted", "clicked-upper", "clicked-lower", "external", "clicked-disabled", "dense", "dense-narrow", "tiny", "odd", "clicked-odd-upper", "clicked-decimal-upper", "clicked-odd2-upper", "dragged"}
        assert required <= {f["variant"] for f in fixtures if f["api"] == "BleeckerSlider"}, "Missing slider state combinations"
        assert manifest.get("sourceKeyboardStatus", "").startswith("pending;"), "Source keyboard gate cannot be self-approved"
        assert set(manifest.get("unverifiedInputCases", [])) == {"slider-key-right", "slider-key-left", "slider-key-step", "slider-key-signed", "slider-key-disabled", "slider-key-upper"}, "Missing unverified source keyboard cases"
        for case in captures:
            if case["api"] != "BleeckerSlider": continue
            size, variant = case["size"], case["variant"]
            minimum, maximum = {"signed": (-5, 5), "shifted": (10, 22), "decimal": (0, 0.3)}.get(size, (0, 1))
            step = {"unit":0,"signed":0.5,"shifted":3,"quarter":0.25,"dense":0.01,"tiny":0.000001,"odd":0.3,"odd2":0.26,"decimal":0.1}[size]
            assert (case.get("sourceMinimum"), case.get("sourceMaximum"), case.get("sourceStep")) == (minimum, maximum, step), "Invalid source slider range"
            expected = {"clicked-upper":1,"clicked-lower":0,"external":0.8,"clicked-odd-upper":0.8999999999999999,"clicked-decimal-upper":0.30000000000000004,"clicked-odd2-upper":0.78,"dragged":0.75}.get(variant, float(case["text"]))
            assert case.get("sourceValueAfterAction") == expected, "Invalid source slider value"
            updated = (variant.startswith("clicked-") and not case["flag"]) or variant == "dragged"
            assert case.get("sourceBindingUpdated") is updated and (case.get("sourceUserEdits",0) > 0) is updated, "Invalid source slider binding update"
            if variant != "dragged":
                assert case.get("sourceUserEdits") == int(updated), "Invalid source slider callback count"
            assert case.get("sourceControlActiveState") == "active", "Missing explicit native slider active context"
    if scoped == "desktop-tabs":
        required = {"normal", "selected", "selected-disabled", "unmatched", "empty", "disabled", "all-disabled", "long", "multiline", "narrow", "wide", "rtl", "activated", "reselected", "disabled-click", "disabled-group-action", "external"}
        for api in ["BleeckerSegmentedControl", "BleeckerTabs"]:
            assert required <= {f["variant"] for f in fixtures if f["api"] == api}, "Missing tabs state combinations"
        for case in captures:
            if case["api"] == "BleeckerButton": continue
            variant = case["variant"]
            expected = {"activated":"c", "reselected":"c", "external":"a"}.get(variant, case["text"])
            assert case.get("sourceSelectionAfterAction") == expected, "Invalid source tab selection"
            assert case.get("sourceActivations") == int(variant in {"activated", "reselected", "external"}), "Invalid source tab activation count"
            assert case["resolvedLabelFonts"]["segmentExpression"]["postScriptName"] == "EncodeSans-Md", "Invalid source tab font"
    if scoped == "desktop-pagination":
        assert manifest.get("sourceKeyboardStatus", "").startswith("pending;"), "Source pagination keyboard gate cannot be self-approved"
        icons = [c for c in captures if c["api"] == "BleeckerIconButton"]
        for size, variant in itertools.product(["sm", "md", "lg"], ["default", "subtle", "ghost"]):
            rows = [c for c in icons if c["size"] == size and c["variant"] == variant]
            assert {(symbol, flag) for symbol in ["chevron.left", "chevron.right"] for flag in [False, True]} <= {(c["text"], c["flag"]) for c in rows if c["sourceAction"] == "none"}, "Missing icon state combinations"
            assert {"clicked", "disabled-click", "pressed"} <= {c["sourceAction"] for c in rows}, "Missing icon action cases"
        required = {"first", "middle", "last", "single", "zero-count", "negative-count", "below-first", "above-last", "empty-count", "long", "narrow", "wide", "rtl", "disabled", "previous", "next", "lower-bound", "upper-bound", "disabled-action", "no-handler", "external", "shrink-count", "below-first-next", "above-last-prev"}
        assert required <= {f["variant"] for f in fixtures if f["api"] == "BleeckerPagination"}, "Missing pagination state combinations"
        for case in captures:
            if case["api"] == "BleeckerButton": continue
            action = case["sourceAction"]
            if case["api"] == "BleeckerIconButton":
                assert action in {"none", "clicked", "disabled-click", "pressed"}, "Unknown icon action"
                assert case["sourceActivations"] == int(action == "clicked"), "Invalid source icon callback count"
                assert case["flag"] is (action == "disabled-click") or action == "none", "Invalid disabled icon action"
                width,height = {"sm":(32,28),"md":(44,36),"lg":(56,40)}[case["size"]]
                assert case["componentSize"] == {"width":width,"height":height}, "Invalid source icon bounds"
                continue
            page,count = int(case["text"]),int(case["value"])
            rejected = action in {"none", "lower-bound", "upper-bound", "disabled-action"}
            previous = action in {"previous", "lower-bound", "above-last-prev"}
            request = None if rejected else max(1,page-1) if previous else min(count,page+1)
            expected = 7 if action == "external" else page if rejected or action == "no-handler" else request
            assert case.get("sourceActivations") == int(not rejected), "Invalid source page callback count"
            assert case.get("sourceRequestedPage") == request, "Invalid source requested page"
            assert case.get("sourcePageAfterAction") == expected, "Invalid source caller page"
            assert case.get("sourcePageCountAfterAction") == (3 if action == "shrink-count" else count), "Invalid source page count"
            assert case["resolvedLabelFonts"]["sourceExpression"]["pointSize"] == 12, "Invalid source pagination label font"
    if scoped == "desktop-pagination-integers":
        required = {"int32", "int32-after", "safe-limit", "beyond-safe", "upper-before", "upper", "minimum", "lower-equal", "negative-count", "above-count", "wide-count", "negative-middle", "rtl", "narrow", "disabled", "next-i32", "next-safe", "next-beyond", "previous-beyond", "next-upper", "previous-upper", "disabled-upper", "next-min", "disabled-min", "previous-negative-count", "no-handler", "external", "shrink-count", "disabled-group"}
        assert required <= {f["variant"] for f in fixtures if f["api"] == "BleeckerPagination"}, "Missing full integer pagination cases"
        assert manifest.get("sourceKeyboardStatus", "").startswith("pending;"), "Source exact pagination keyboard gate cannot be self-approved"
        lower,upper = -(2**63),2**63-1
        def decimal(value):
            assert isinstance(value,str) and str(int(value)) == value and lower <= int(value) <= upper, "Invalid exact integer representation"
            return int(value)
        for case in captures:
            if case["api"] != "BleeckerPagination": continue
            page,count = decimal(case["text"]),decimal(case["size"])
            action = case["sourceAction"]
            rejected = action in {"none", "disabled-upper", "disabled-min", "disabled-group"}
            request = None if rejected else str(max(1,page-1) if action.startswith("previous-") else min(count,page+1))
            expected = str(upper-2) if action == "external" else str(page) if rejected or action == "no-handler" else request
            assert case["sourceActivations"] == int(not rejected), "Invalid exact pagination callback count"
            assert case["sourceRequestedPageDecimal"] == request, "Invalid exact requested page"
            assert case["sourcePageAfterActionDecimal"] == expected, "Invalid exact caller page"
            assert case["sourcePageCountAfterActionDecimal"] == (str(lower) if action == "shrink-count" else str(count)), "Invalid exact page count"
    if scoped == "desktop-accordion":
        static_variants={"closed","open","empty-content","zero-content","two-rows","counter","empty-title","empty-title-open","long-title","long-title-open","multiline","wide","intrinsic","rtl","disabled","disabled-open","long-body"}
        action_variants={"open-title","open-spacer","open-glyph","close","reopen","initial-update","retitle","disabled","disabled-open","pressed","outside-release","body-update"}
        assert static_variants <= {f["variant"] for f in fixtures if f["api"] == "BleeckerAccordion" and not f["fixture"].startswith("accordion-action-")}, "Missing accordion state/content/input cases"
        assert action_variants <= {f["variant"] for f in fixtures if f["api"] == "BleeckerAccordion" and f["fixture"].startswith("accordion-action-")}, "Missing accordion action cases"
        assert manifest.get("sourceKeyboardStatus", "").startswith("pending;"), "Source accordion keyboard gate cannot be self-approved"
        for case in captures:
            if case["api"] != "BleeckerAccordion": continue
            action=case["sourceAction"];initial=case["value"] == 1
            assert action == (case["variant"] if case["fixture"].startswith("accordion-action-") else "none"), "Invalid accordion action classification"
            assert case["captureMethod"].startswith("NSHostingView.cacheDisplay" if action != "none" else "SwiftUI.ImageRenderer"), "Invalid accordion input capture method"
            expanded=initial if action == "none" else action in {"open-title","open-glyph","reopen","retitle","body-update","disabled-open"}
            mounts=int(initial and case["variant"] != "empty-content") if action == "none" else 2 if action == "reopen" else int(initial or action in {"open-title","open-glyph"})
            assert case["sourceExpandedAfterAction"] == expanded, "Invalid source accordion expanded state"
            assert case["sourceMounts"] == mounts and case["sourceUnmounts"] == int(action in {"close","reopen"}), "Invalid source accordion content lifecycle"
            assert case["sourceCounterValue"] == int(action == "retitle"), "Invalid source accordion child state"
            assert case["sourceInitialAfterAction"] == (initial or action == "initial-update"), "Invalid source accordion initializer update"
            assert case["sourceTitleAfterAction"] == ("Updated title" if action == "retitle" else case["text"]), "Invalid source accordion title update"
            body="Updated body copy" if action == "body-update" else "Keep selected editions available for review" if case["variant"] == "long-body" else "Body copy"
            assert case["sourceContentTextAfterAction"] == body, "Invalid source accordion content update"
            font=case["resolvedLabelFonts"]["title"]
            assert font["pointSize"] == 14 and font["postScriptName"] == "EncodeSans-SmBold", "Invalid source accordion title font"
    if scoped == "desktop-presentation-states":
        source = ROOT / "evidence/reference-investigations/presentation-states-20261014"
        sealed = json.loads((source / "captures.json").read_text())
        sealed_files = json.loads((source / "investigation.json").read_text())["files"]
        hosted_directory=ROOT / "evidence/reference-investigations/loading-native-20261015"
        hosted=json.loads((hosted_directory / "captures.json").read_text())
        hosted_files=json.loads((hosted_directory / "investigation.json").read_text())["files"]
        assert not any(c["api"]=="BleeckerLoadingOverlay" and not c["captureMethod"].startswith("NSHostingView.cacheDisplay") for c in captures), "ImageRenderer native progress placeholders cannot be visual references"
        expected = {c["path"]: c for c in sealed["captures"] if c["api"]!="BleeckerLoadingOverlay"}
        expected.update({c["path"]:c for c in hosted["captures"]})
        sealed_files={**sealed_files,**hosted_files}
        assert set(expected) == {c["path"] for c in captures}, "Missing sealed presentation-state capture"
        for case in captures:
            assert all(case.get(key) == value for key, value in expected[case["path"]].items()), "Source presentation capture differs from sealed investigation"
            assert case["sha256"] == sealed_files[case["path"]], "Source presentation pixels differ from sealed investigation"
        assert manifest["behavior"] == sealed["behavior"], "Source presentation behavior differs from sealed investigation"
        assert manifest["centeredTextLines"] == sealed["centeredTextLines"] and manifest["sourceSymbols"] == sealed["sourceSymbols"], "Source presentation expression witnesses differ"
    if scoped=="desktop-alert":
        source=ROOT/"evidence/reference-investigations/alert-20261015"
        sealed=json.loads((source/"captures.json").read_text());sealedFiles=json.loads((source/"investigation.json").read_text())["files"]
        expected={c["path"]:c for c in sealed["captures"]}
        assert set(expected)=={c["path"] for c in captures},"Missing sealed alert capture"
        for c in captures:
            assert all(c.get(k)==v for k,v in expected[c["path"]].items()),"Alert source metadata differs from sealed investigation"
            assert c["sha256"]==sealedFiles[c["path"]],"Alert source pixels differ from sealed investigation"
        assert manifest["behavior"]==sealed["behavior"] and manifest["sourceSymbols"]==sealed["sourceSymbols"],"Alert source state/symbol witnesses differ"
    if scoped=="desktop-navigation-layout":
        source=ROOT/"evidence/reference-investigations/navigation-layout-20261015"
        sealed=json.loads((source/"captures.json").read_text());sealed_files=json.loads((source/"investigation.json").read_text())["files"]
        expected={c["path"]:c for c in sealed["captures"]}
        assert set(expected)=={c["path"] for c in captures}, "Missing sealed navigation capture"
        for case in captures:
            assert all(case.get(k)==v for k,v in expected[case["path"]].items()), "Navigation source metadata differs from sealed investigation"
            assert case["sha256"]==sealed_files[case["path"]], "Navigation source pixels differ from sealed investigation"
        assert manifest["behavior"]==sealed["behavior"] and manifest["expressions"]==sealed["expressions"], "Navigation source witnesses differ"
    if scoped=="desktop-data-metrics":
        source=ROOT/"evidence/reference-investigations/data-metrics-20261015"
        sealed=json.loads((source/"captures.json").read_text());hashes=json.loads((source/"investigation.json").read_text())["files"]
        expected={c["path"]:c for c in sealed["captures"]}
        inputs=json.loads((ROOT/"evidence/reference-investigations/data-metrics-inputs-20261015/fixture-inputs.json").read_text())
        widths={c["fixture"]:c["proposalWidth"] for c in inputs["fixtures"]}
        assert set(expected)=={c["path"] for c in captures}
        assert manifest["formatting"]==sealed["formatting"],"Data-display source formatter differs"
        for case in captures:
            assert all(case.get(k)==v for k,v in expected[case["path"]].items() if k!="status"),"Data-display source metadata differs"
            assert case["sha256"]==hashes[case["path"]],"Data-display source image differs"
            assert case["proposalWidth"]==widths[case["fixture"]],"Data-display source proposal differs"

    if scoped=="desktop-sidebar-brand":
        source=ROOT/"evidence/reference-investigations/sidebar-brand-20261015"
        sealed=json.loads((source/"captures.json").read_text());checksums=json.loads((source/"investigation.json").read_text())["files"]
        expected={c["path"]:c for c in sealed["captures"]}
        assert set(expected)=={c["path"] for c in captures}, "Missing sealed sidebar/brand capture"
        for case in captures:
            assert all(case.get(k)==v for k,v in expected[case["path"]].items()), "Sidebar/brand source metadata differs"
            assert case["sha256"]==checksums[case["path"]], "Sidebar/brand source pixels differ"
        assert manifest["behavior"]==sealed["behavior"], "Sidebar/brand source actions differ"
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
    if scoped == "desktop-presentation-states":
        primary=json.loads((ROOT / "evidence/reference-investigations/loading-native-20261015/investigation.json").read_text())["sourceToolArtifact"]
        static=json.loads((ROOT / "evidence/reference-investigations/presentation-states-20261014/investigation.json").read_text())["sourceToolArtifact"]
        assert tooling["toolArtifact"]["sha256"]==primary
        assert [a["sha256"] for a in tooling["additionalToolArtifacts"]]==[static], "Missing static source tool provenance"
        assert tooling["captureToolAssignments"]=={api:primary if api=="BleeckerLoadingOverlay" else static for api in SCOPED_APIS[scoped]}, "Invalid source capture tool assignments"
    for comparison in json.loads((directory / "anchor-comparison.json").read_text()):
        assert hashlib.sha256((ROOT / comparison["reference"]).read_bytes()).hexdigest() == comparison["referenceSha256"]
    return len(captures)


if __name__ == "__main__":
    for directory in sorted((ROOT / "evidence/reference-proposals").iterdir()):
        if (directory / "proposal.json").is_file():
            count = verify(directory)
            print(f"{directory.name}: {count} proposed captures verified; baseline approval and external tool replay remain separate")
