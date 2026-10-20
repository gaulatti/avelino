#!/usr/bin/env python3
"""Decode diagnostic glyph evidence; do not promote a raster model or accept APIs."""
import hashlib
import io
import itertools
import json
from pathlib import Path
import struct
import zipfile

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / "evidence/development/font-raster-investigation-20261019"
TAGS = {"head", "hhea", "hmtx", "maxp", "OS/2", "cmap", "loca", "glyf", "name", "GPOS", "GSUB"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(name):
    return json.loads((CAPSULE / name).read_text())


def pixels(data):
    with Image.open(io.BytesIO(data)) as image:
        return image.convert("RGBA")


def difference(a, b):
    assert a.size == b.size
    delta = ImageChops.difference(a, b)
    mask = delta.getchannel("R")
    for channel in ["G", "B", "A"]:
        mask = ImageChops.lighter(mask, delta.getchannel(channel))
    histogram = mask.histogram()
    return a.width * a.height - histogram[0], max(i for i, n in enumerate(histogram) if n)


def font_tables(path):
    data = path.read_bytes()
    count = struct.unpack_from(">H", data, 4)[0]
    tables = {}
    for i in range(count):
        tag, _, offset, length = struct.unpack_from(">4sIII", data, 12 + 16 * i)
        name = tag.decode("ascii")
        assert offset + length <= len(data)
        if name in TAGS:
            tables[name] = sha(data[offset:offset + length])
    assert set(tables) == TAGS
    return tables


def verify():
    manifest = read("files.json")["files"]
    assert set(manifest) == {str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob("*")
                             if p.is_file() and p != CAPSULE / "files.json"}
    for name, checksum in manifest.items():
        assert not Path(name).is_absolute() and ".." not in Path(name).parts
        assert sha((CAPSULE / name).read_bytes()) == checksum, name
    result = read("result.json")
    for key in ["productImplementationChanged", "sourcePinsChanged", "expectedImagesChanged",
                "tolerancesChanged", "exceptionsChanged", "modelPromoted", "physicalDisplay",
                "readerAcceptance", "accepted", "fullMirrorAccepted"]:
        assert result[key] is False
    provenance = read("provenance.json")
    for key in ["independentLibraryRebuild", "independentMachineReplay", "physicalInput",
                "windowSessionObserved", "accepted", "fullMirrorAccepted"]:
        assert provenance[key] is False
    assert provenance["reusedPinnedLibraryObject"] is True
    assert provenance["sourceRevision"] == result["sourceRevision"] == "86334226962e67d2a102b6bed720fe723a7eaae3"
    for name, checksum in read("implementation-inputs.json").items():
        assert sha((CAPSULE / "implementation-inputs" / name).read_bytes()) == checksum

    reference = json.loads((ROOT / "reference/source-manifest.json").read_text())["references"]["desktop"]
    assert read("native-v1/result.json")["exitCode"] == 1
    assert "noOptions" in (CAPSULE / "native-v1/compile.log").read_text()
    expected = set(itertools.product(["primary", "secondary"], ["regular", "medium", "bold"],
                                     [12, 15, 18, 23], ["Short", "Tall", "Keep edition"],
                                     [False, True], [1, 2]))
    previous = None
    base_rows = None
    summaries = {}
    zero_controls = []
    png_count = 0
    measurement_pairs = 0
    for version, modes in [(2, set(range(-1, 8))), (3, set(range(-1, 19))),
                           (4, set(range(-1, 21))), (5, {17, 19, 20})]:
        inputs = read(f"native-v{version}/inputs.json")
        native_result = read(f"native-v{version}/result.json")
        run = next(r for r in provenance["nativeRuns"] if r["version"] == version)
        assert inputs["reference"] == native_result["reference"] == reference["revision"]
        assert inputs["sourceArchiveSha256"] == reference["sha256"]
        assert inputs["pinnedSourceFiles"] == len(reference["files"]) == 53
        assert inputs["libraryObjectSha256"] == "0d98b215928f864cb6874be5426360db0861eb44a049af40e556aca9e319c025"
        assert inputs["reusedLibraryObject"] is True and inputs["independentLibraryRebuild"] is False
        assert inputs["helperSha256"] == native_result["helperSha256"] == run["helperSha256"]
        assert run["appleToolingIncluded"] is native_result["accepted"] is False
        assert native_result["exitCode"] == 0
        for name, checksum in inputs["resourceFiles"].items():
            if "/Fonts/" in name:
                assert sha((ROOT / "assets/fonts" / Path(name).name).read_bytes()) == checksum
        with zipfile.ZipFile(CAPSULE / f"native-v{version}/captures.zip") as archive:
            names = archive.namelist()
            assert len(names) == len(set(names))
            assert all(Path(n).name == n and n.endswith((".png", ".json")) for n in names)
            raw = {name: archive.read(name) for name in names}
        data = json.loads(raw.pop("measurements.json"))
        assert data["reference"] == reference["revision"] and data["accepted"] is False
        rows = data["profiles"]
        keys = {(r["family"], r["weight"], r["requestedSize"], r["text"], r["dark"], r["dpr"],
                 r.get("xOffset", 0)) for r in rows}
        offsets = [-.75, -.5, -.25, 0, .25, .5, .75] if version == 5 else [0]
        assert keys == {(*key, offset) for key in expected for offset in offsets}
        assert len(rows) == len(keys) == 288 * len(offsets)
        declared = set()
        stats = {str(mode): {"profiles": 0, "exact": 0, "changedPixels": 0,
                             "maxChannelError": 0, "maxErrorAtMostTwo": 0} for mode in modes}
        for row in rows:
            assert row["resolvedSize"] == row["requestedSize"]
            assert set(row["fontTables"]) == TAGS
            assert raw[row["bare"]] == raw[row["measured"]]
            assert sha(raw[row["bare"]]) == row["sourceSha256"]
            measurement_pairs += 1
            declared.update([row["bare"], row["measured"]])
            source = pixels(raw[row["bare"]])
            assert source.size == (240 * row["dpr"], 80 * row["dpr"])
            assert source.getchannel("A").getextrema() == (255, 255)
            if version == 5 and row["xOffset"] == 0:
                changed, maximum = difference(source, pixels(previous[row["bare"]]))
                zero_controls.append((row["name"], raw[row["bare"]] == previous[row["bare"]], changed, maximum))
            assert {r["mode"] for r in row["coreText"]} == modes
            for variant in row["coreText"]:
                declared.add(variant["path"])
                assert sha(raw[variant["path"]]) == variant["sha256"]
                candidate = pixels(raw[variant["path"]])
                assert candidate.getpixel((0, 0)) == source.getpixel((0, 0))
                changed, maximum = difference(source, candidate)
                stats[str(variant["mode"])]["profiles"] += 1
                stats[str(variant["mode"])]["exact"] += changed == 0
                stats[str(variant["mode"])]["changedPixels"] += changed
                stats[str(variant["mode"])]["maxChannelError"] = max(stats[str(variant["mode"])]["maxChannelError"], maximum)
                stats[str(variant["mode"])]["maxErrorAtMostTwo"] += maximum <= 2
        assert set(raw) == declared
        assert len(raw) == native_result["captures"] == run["pngCaptures"]
        if previous is not None and version < 5:
            assert all(raw[name] == value for name, value in previous.items())
        assert all(r["exact"] == 0 for r in stats.values())
        png_count += len(raw)
        summaries[str(version)] = stats
        previous = raw
        if version == 2:
            base_rows = rows
    assert png_count == result["nativeProbePngCaptures"] == 26496
    assert measurement_pairs == 2880
    assert len(zero_controls) == 288 and sum(r[1] for r in zero_controls) == 286
    assert all(r[3] <= 1 for r in zero_controls)
    for version, audit in [(2, "font-raster-source-audit-v1"), (3, "font-raster-source-audit-v2"),
                            (5, "font-raster-source-audit-v5")]:
        for mode, record in read(audit + "/result.json")["summary"].items():
            assert record["changedPixels"] == summaries[str(version)][mode]["changedPixels"]
            assert record["exact"] == summaries[str(version)][mode]["exact"]
    assert summaries["4"]["19"]["maxChannelError"] == 2
    assert summaries["5"]["19"]["maxChannelError"] == 212
    assert summaries["5"]["19"]["maxErrorAtMostTwo"] == 1728
    assert read("font-raster-source-audit-v4/command.json")["exitCode"] == 1

    faces = read("font-face-audit-v1/font-faces.json")
    face_result = read("font-face-audit-v1/result.json")
    assert face_result["exitCode"] == 0 and face_result["productSourceChanged"] is False
    assert face_result["imageId"] == "sha256:e29f85ab0df39f3ae46c4d5ddcc075517701fc05359a230c8647b1174e862dd3"
    assert all(r["exitCode"] == 0 for r in read("font-face-audit-v1/commands.json"))
    assert faces["qt"] == "6.8.3" and len(faces["records"]) == result["fontFaceProfiles"] == 72
    for row in faces["records"]:
        native = [r for r in base_rows if (r["family"], r["weight"], r["requestedSize"], r["text"]) ==
                  (row["family"], row["weight"], row["size"], row["text"])]
        assert len(native) == 4
        prefix = "EncodeSans" if row["family"] == "primary" else "LibreFranklin"
        bundled = font_tables(ROOT / "assets/fonts" / (prefix + "-" + row["weight"].title() + ".ttf"))
        for source in native:
            assert source["fontTables"] == bundled
            assert len(source["glyphRuns"]) == len(row["glyphRuns"])
            for a, b in zip(source["glyphRuns"], row["glyphRuns"]):
                assert a["glyphs"] == b["glyphs"]
                assert b["shapeTables"] == b["paintTables"] == bundled
                assert len(a["positions"]) == len(b["positions"]) == len(a["glyphs"])
                for x, y in zip(a["positions"], b["positions"]):
                    assert abs(x["x"] - y["x"]) < 1e-10 and abs(x["y"] - y["y"]) < 1e-10

    assert read("button-glyph-hinting-v1/result.json")["exitCode"] == 1
    assert all(r["exitCode"] == 0 for r in read("button-glyph-hinting-v2/commands.json"))
    hint_rows = read("button-glyph-hinting-v2/comparison.json")["rows"]
    assert len(hint_rows) == result["hintingProfiles"] == 32
    hint_summary = {name: 0 for name in ["default", "none", "vertical", "full"]}
    for row in hint_rows:
        capture = CAPSULE / "button-glyph-hinting-v2/output" / row["capture"]
        source = ROOT / "evidence/reference-investigations/button-group-slots-20261019/canonical" / row["source"]
        assert sha(capture.read_bytes()) == row["sha256"]
        assert sha(source.read_bytes()) == row["sourceSha256"]
        changed, maximum = difference(pixels(capture.read_bytes()), pixels(source.read_bytes()))
        assert changed == row["changedPixels"] > 0 and maximum == row["maxChannelError"]
        assert row["geometryPassed"] is True and all(row["geometry"].values())
        hint_summary[row["hintName"]] += changed
        if row["hint"] == 0:
            control = CAPSULE / "compiled-catalog-controls" / (row["context"] + ".png")
            historical = ROOT / "evidence/development/button-group-layout-20261019/legacy-after" / control.name
            assert capture.read_bytes() == control.read_bytes() == historical.read_bytes()
    assert hint_summary == {"default": 7584, "none": 7551, "vertical": 7584, "full": 7339}
    return {"physicalFontAndGlyphProfiles": 72, "nativeProbePngCaptures": png_count,
            "measurementIdentityPairs": measurement_pairs, "offsetWrapperControlsIdentical": 286,
            "offsetWrapperControlsChanged": 2, "hintingProfiles": 32,
            "globalSnappingModelPromoted": False, "productImplementationChanged": False,
            "accepted": False}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
