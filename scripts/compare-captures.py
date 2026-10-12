#!/usr/bin/env python3
"""Strict candidate comparison. Never rewrites expectations, resizes, or masks pixels."""
import argparse
import hashlib
import html
import json
from pathlib import Path
from PIL import Image, ImageChops


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare(reference, candidate, output):
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((reference / "captures.json").read_text())
    results, rows = [], []
    for fixture in manifest["captures"]:
        name = fixture["path"]
        expected_path, actual_path = reference / name, candidate / name
        result = {"fixture": name, "reference": str(expected_path), "candidate": str(actual_path),
                  "status": "failed", "tolerance": "none; glyph-edge policy has not been calibrated or approved",
                  "referenceRevision": fixture["source"]}
        if not actual_path.is_file() or not (candidate / (name + ".json")).is_file():
            result["error"] = "Missing candidate image or capture metadata"
            results.append(result)
            continue
        metadata = json.loads((candidate / (name + ".json")).read_text())
        for key in ["width", "height", "dpr", "appearance", "variant", "size", "state"]:
            if fixture[key] != metadata.get(key):
                result["error"] = f"Incompatible fixture metadata: {key}"
                break
        expected, actual = Image.open(expected_path), Image.open(actual_path)
        result.update(referenceSHA256=digest(expected_path), candidateSHA256=digest(actual_path),
                      referenceColorMetadata={k: str(v) for k, v in expected.info.items() if k in ["srgb", "gamma", "chromaticity"]},
                      candidateColorMetadata={k: str(v) for k, v in actual.info.items() if k in ["srgb", "gamma", "chromaticity"]})
        if expected.size != actual.size:
            result["error"] = "Physical pixel dimensions differ; comparison refuses resizing"
        if "icc_profile" in expected.info or "icc_profile" in actual.info:
            result["error"] = "ICC-managed captures require an explicitly reviewed color-space conversion"
        if "error" in result:
            results.append(result)
            continue
        # RGB avoids Pillow's RGBA alpha-only bbox rule; alpha is compared separately.
        delta = ImageChops.difference(expected.convert("RGB"), actual.convert("RGB"))
        alpha_delta = ImageChops.difference(expected.convert("RGBA").getchannel("A"), actual.convert("RGBA").getchannel("A"))
        pixels = list(delta.get_flattened_data())
        result.update(changedPixels=sum(any(channel != 0 for channel in pixel) for pixel in pixels),
                      maximumChannelError=max(max(pixel) for pixel in pixels),
                      differenceBounds=delta.getbbox(), alphaDifferenceBounds=alpha_delta.getbbox())
        result["status"] = "passed" if not delta.getbbox() and not alpha_delta.getbbox() else "failed"
        stem = Path(name).stem
        delta.save(output / f"{stem}-diff.png")
        overlay = Image.blend(expected.convert("RGB"), actual.convert("RGB"), 0.5)
        overlay.save(output / f"{stem}-overlay.png")
        side = Image.new("RGB", (expected.width * 2, expected.height))
        side.paste(expected.convert("RGB"), (0, 0)); side.paste(actual.convert("RGB"), (expected.width, 0))
        side.save(output / f"{stem}-pair.png")
        rows.append(f'<article><h2>{html.escape(name)}</h2><p>{result["status"]}: {result["changedPixels"]} changed pixels; maximum channel error {result["maximumChannelError"]}</p><img src="{stem}-pair.png" alt="Reference left, candidate right"><img src="{stem}-overlay.png" alt="Overlay"><img src="{stem}-diff.png" alt="Raw difference"></article>')
        results.append(result)
    report = {"status": "passed" if results and all(r["status"] == "passed" for r in results) else "failed",
              "acceptance": "comparison only; runtime, asset, state, session, and accessibility gates remain independent",
              "results": results}
    (output / "comparison.json").write_text(json.dumps(report, indent=2) + "\n")
    (output / "index.html").write_text('<!doctype html><meta charset="utf-8"><title>Avelino mirror comparison</title><style>body{font:16px sans-serif;margin:24px;background:#f6f6f6}article{background:white;padding:16px;margin:20px 0}img{display:block;max-width:100%;margin:12px 0}</style><h1>Reference and Linux candidate comparison</h1><p>No resizing, ignored regions, or visual exceptions. Raw differences remain open.</p>' + ''.join(rows))
    print(f"{report['status']}: {len(results)} fixture comparisons; report {output / 'index.html'}")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(compare(args.reference, args.candidate, args.output))
