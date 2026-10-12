#!/usr/bin/env python3
"""Initialize licensed fonts and brand assets from the verified desktop artifact."""
import hashlib
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[1]
record = json.loads((ROOT / "reference/source-manifest.json").read_text())["references"]["desktop"]
destination = ROOT / "assets/provenance.json"
if destination.exists():
    raise SystemExit("Assets already initialized; preserve provenance through reviewed changes.")
assert hashlib.sha256((ROOT / record["artifact"]).read_bytes()).hexdigest() == record["sha256"]
assets = []
with tarfile.open(ROOT / record["artifact"]) as archive:
    for member in archive.getmembers():
        if not member.isfile():
            continue
        if "/Resources/Fonts/" in member.name:
            name = f"assets/fonts/{Path(member.name).name}"
            license_path = "assets/fonts/OFL-EncodeSans.txt" if "EncodeSans" in member.name else "assets/fonts/OFL-LibreFranklin.txt"
            upstream = "https://github.com/thundernixon/Encode-Sans/tree/6407de854a4dc3bfbe2160a11c5b57f5a1baf3bc/fonts/EncodeSans/static" if "EncodeSans" in member.name else "https://github.com/googlefonts/Libre-Franklin/tree/310b7eef1f7b7ba82322295e0034675ea68040b0/fonts/ttf"
        elif member.name.endswith("BleeckerLogo.png"):
            name, license_path, upstream = "assets/brand/BleeckerLogo.png", None, "Gaulatti-owned Bleecker brand artwork"
        else:
            continue
        data = archive.extractfile(member).read()
        output = ROOT / name
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
        assets.append({"path": name, "referencePath": member.name,
            "referenceRevision": record["revision"], "sha256": hashlib.sha256(data).hexdigest(),
            "upstream": upstream, "license": license_path})
destination.write_text(json.dumps({"assets": assets, "appleSystemFontsRedistributed": False,
    "systemSymbolsRedistributed": False}, indent=2) + "\n")
