#!/usr/bin/env python3
"""Verify immutable reference artifacts in separate clean extraction directories."""
import hashlib
import json
from pathlib import Path
import tarfile
import tempfile
from reference_sources import resolve_reference

ROOT = Path(__file__).resolve().parents[1]


def verify_reference(record, directory):
    artifact = resolve_reference(record)
    assert hashlib.sha256(artifact.read_bytes()).hexdigest() == record["sha256"], artifact
    expected = {entry["path"]: entry for entry in record["files"]}
    with tarfile.open(artifact, "r:gz") as archive:
        members = archive.getmembers()
        assert all(member.isdir() or member.isfile() for member in members), "Unexpected symlink/member"
        actual = {member.name for member in members if member.isfile()}
        assert actual == set(expected), "Artifact scope mismatch"
        archive.extractall(directory, filter="data")
    for name, entry in expected.items():
        data = (directory / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == entry["sha256"], name
        blob = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        assert blob == entry["gitBlob"], name
    assert json.loads((directory / "Package.resolved").read_text()) == record["dependencies"]


def main():
    manifest = json.loads((ROOT / "reference/source-manifest.json").read_text())
    for kind in ["desktop", "television"]:
        with tempfile.TemporaryDirectory(prefix=f"avelino-{kind}-verify-") as clean:
            verify_reference(manifest["references"][kind], Path(clean))
        print(f"{kind}: clean extraction verified ({manifest['references'][kind]['revision']})")
    token = manifest["references"]["bleecker"]
    assert hashlib.sha256((ROOT / token["artifact"]).read_bytes()).hexdigest() == token["sha256"]
    print("bleecker: canonical token source verified")
    lock = manifest["captureDependencyRecord"]
    assert hashlib.sha256((ROOT / lock["artifact"]).read_bytes()).hexdigest() == lock["sha256"]
    print("capture dependencies: original lock bytes preserved as JSON provenance")
    asset_manifest = ROOT / "assets/provenance.json"
    if asset_manifest.exists():
        assets = json.loads(asset_manifest.read_text())
        assert not assets["appleSystemFontsRedistributed"] and not assets["systemSymbolsRedistributed"]
        source_files = {f["path"]: f for f in manifest["references"]["desktop"]["files"]}
        for asset in assets["assets"]:
            assert hashlib.sha256((ROOT / asset["path"]).read_bytes()).hexdigest() == asset["sha256"], asset["path"]
            assert source_files[asset["referencePath"]]["sha256"] == asset["sha256"], asset["path"]
            if asset["path"].endswith(".ttf"):
                assert asset["license"] and (ROOT / asset["license"]).is_file(), asset["path"]
        assert len([asset for asset in assets["assets"] if asset["path"].endswith(".ttf")]) == 18
        print("assets: all 18 licensed static font faces and brand inputs verified against the desktop artifact")
    capture_directory = ROOT / "reference/captures/desktop/buttons"
    if capture_directory.exists():
        captures = json.loads((capture_directory / "captures.json").read_text())
        assert captures["reference"] == manifest["references"]["desktop"]["revision"]
        expected = {case["path"] for case in captures["captures"]}
        assert len(expected) == len(captures["captures"]) == 112
        assert {path.name for path in capture_directory.glob("*.png")} == expected
        for case in captures["captures"]:
            assert hashlib.sha256((capture_directory / case["path"]).read_bytes()).hexdigest() == case["sha256"], case["path"]
            assert case["source"] == captures["reference"] and case["dpr"] == 2
            assert case["resolvedFont"]["postScriptName"] == "EncodeSans-Md", case["path"]
        print("captures: 112 immutable source button images verified; Linux comparison acceptance remains separate")
        source_cases = {case['path']: case for case in captures['captures']}
        for checkpoint_path in sorted((ROOT / 'evidence/checkpoints').glob('*/checkpoint.json')):
            checkpoint = json.loads(checkpoint_path.read_text())
            assert checkpoint['referenceRevision'] == captures['reference'], checkpoint_path
            for name, checksum in checkpoint['files'].items():
                assert Path(name).name == name, name
                assert hashlib.sha256((checkpoint_path.parent / name).read_bytes()).hexdigest() == checksum, name
            environment = json.loads((checkpoint_path.parent / 'environment.json').read_text())
            assert environment['sourceRevision'] == checkpoint['sourceRevision'] and not environment['uncommittedChanges']
            reports = []
            for arch in ['x64', 'arm64']:
                report = json.loads((checkpoint_path.parent / f'button-comparison-{arch}.json').read_text())
                assert len(report['results']) == checkpoint['cases']
                assert sum(case['status'] == 'passed' for case in report['results']) == checkpoint['passed']
                assert {case['fixture'] for case in report['results']} == set(source_cases)
                for case in report['results']:
                    assert case['referenceSHA256'] == source_cases[case['fixture']]['sha256'], case['fixture']
                    if (checkpoint_path.parent / case['fixture']).exists():
                        assert hashlib.sha256((checkpoint_path.parent / case['fixture']).read_bytes()).hexdigest() == case['candidateSHA256']
                reports.append({case['fixture']: case['candidateSHA256'] for case in report['results']})
            assert checkpoint['candidatePixelsIdenticalAcrossArchitectures'] == (reports[0] == reports[1])
            change_path = checkpoint_path.parent / 'geometry-change.json'
            if change_path.exists():
                change = json.loads(change_path.read_text())
                previous = json.loads((checkpoint_path.parent.parent / change['beforeCheckpoint'] / 'button-comparison-x64.json').read_text())
                old_cases = {case['fixture']: case for case in previous['results']}
                new_report = json.loads((checkpoint_path.parent / 'button-comparison-x64.json').read_text())
                new_cases = {case['fixture']: case for case in new_report['results']}
                assert len(change['cases']) == len(new_cases) and {case['fixture'] for case in change['cases']} == set(new_cases)
                counts = {'improved': 0, 'unchanged': 0, 'worse': 0}
                for case in change['cases']:
                    old, new = old_cases[case['fixture']], new_cases[case['fixture']]
                    assert case['beforeSHA256'] == old['candidateSHA256'] and case['afterSHA256'] == new['candidateSHA256']
                    assert case['beforeChangedPixels'] == old['changedPixels'] and case['afterChangedPixels'] == new['changedPixels']
                    direction = 'improved' if new['changedPixels'] < old['changedPixels'] else 'worse' if new['changedPixels'] > old['changedPixels'] else 'unchanged'
                    counts[direction] += 1
                assert change['changedPixelCounts'] == counts
                for key in ['beforeRGBAbsoluteError', 'afterRGBAbsoluteError']:
                    assert change[key] == sum(case[key] for case in change['cases'])
            if checkpoint.get('sessionEvidence'):
                for protocol in ['xcb', 'wayland']:
                    for backend in ['software', 'opengl']:
                        for configuration in ['standard', 'scaled']:
                            name = f'{protocol}-{backend}-{configuration}'
                            session = json.loads((checkpoint_path.parent / f'{name}.json').read_text())
                            assert session['platform'] == protocol
                            assert session['graphicsApi'] == (1 if backend == 'software' else 3)
                            assert session['buttonSurfaceRendererType'] == (3 if backend == 'software' else 4)
                            assert session['buttonSurfaceRadius'] == 7 and session['buttonSurfaceOuterPath']
                            assert session['dpr'] == (1 if configuration == 'standard' else 2)
                            assert session['textScale'] == (1 if configuration == 'standard' else 1.5)
                            assert session['appearance'] == ('light' if configuration == 'standard' else 'dark')
                            assert not session['physicalDisplay'] and not session['hardwareAcceleration']
                            assert session['inputMethod'].startswith('QTest synthetic')
                            for suffix, key in [('.png', 'windowCaptureSha256'), ('-session.png', 'sessionCaptureSha256')]:
                                image = checkpoint_path.parent / (name + suffix)
                                if image.exists():
                                    assert hashlib.sha256(image.read_bytes()).hexdigest() == session[key], image
            print(f"checkpoint: checksummed candidate evidence verified ({checkpoint['sourceRevision']}); visual acceptance is {checkpoint['acceptance']}")


if __name__ == "__main__":
    main()
