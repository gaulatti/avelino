#!/usr/bin/env python3
"""Verify dense SDK path diagnostics while keeping the rejected prototype unapplied."""
import base64
import hashlib
import json
import math
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/surface-stroke-dense-20261016'
METHODS = ['analytic-native-stroke', 'analytic-Qt-stroke-native-centerline',
           'analytic-Qt-stroke-Linux-centerline', 'Qt-contains-native-stroke',
           'Qt-contains-Qt-stroke-Linux-centerline']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mask(value, count):
    raw = base64.b64decode(value, validate=True)
    assert len(raw) == (count + 7) // 8
    if count % 8:
        assert raw[-1] >> (count % 8) == 0
    return raw


def differences(left, right):
    assert len(left) == len(right)
    return sum((a ^ b).bit_count() for a, b in zip(left, right))


def validate_rows(native, linux):
    assert len(native) == len(linux) == 32
    assert len({r['fixture'] for r in native}) == 32
    dense = [0] * 5
    critical = [0] * 5
    generic = core_graphics = samples = queries = 0
    for source, actual in zip(native, linux):
        assert source['fixture'] == actual['fixture']
        assert all(source[key] == actual[key] for key in ['width', 'height', 'radius'])
        width, height = source['width'], source['height']
        grid = source['grid']
        assert grid['step'] == 0.125 and grid['corners'] == 4
        nx, ny = int(min(width / 2, 40) * 8) + 1, int(min(height / 2, 40) * 8) + 1
        assert grid['nx'] == nx and grid['ny'] == ny
        count = nx * ny * 4
        assert grid['samples'] == actual['samples'] == count
        truth = mask(grid['swiftUI'], count)
        generic += differences(truth, mask(grid['generic'], count))
        core_graphics += differences(truth, mask(grid['coreGraphics'], count))
        samples += count
        queries += len(source['queries'])
        assert [r['mode'] for r in actual['methods']] == list(range(5))
        for method in actual['methods']:
            mode = method['mode']
            observed = mask(method['mask'], count)
            difference_count = differences(truth, observed)
            assert difference_count == method['denseMismatches']
            first = []
            for byte_index, (a, b) in enumerate(zip(truth, observed)):
                changed = a ^ b
                if not changed:
                    continue
                for bit in range(8):
                    if not (changed >> bit) & 1:
                        continue
                    index = byte_index * 8 + bit
                    corner, local = divmod(index, nx * ny)
                    xi, yi = divmod(local, ny)
                    x, y = xi / 8, yi / 8
                    first.append(dict(index=index, x=width - x if corner & 1 else x,
                                      y=height - y if corner & 2 else y,
                                      candidate=bool((b >> bit) & 1), swiftUI=bool((a >> bit) & 1)))
                    if len(first) == 256:
                        break
                if len(first) == 256:
                    break
            assert first == method['firstDenseDifferences']
            assert method['queryCount'] == len(source['queries'])
            observed_queries = mask(method['queryMask'], len(source['queries']))
            query_differences = []
            for i, query in enumerate(source['queries']):
                value = bool((observed_queries[i // 8] >> (i % 8)) & 1)
                assert query['genericPathContains'] is query['swiftUIContains']
                if value != query['swiftUIContains']:
                    query_differences.append(dict(index=i, point=[query['x'], query['y']],
                                                  candidate=value, swiftUI=query['swiftUIContains']))
            assert query_differences == method['queryDifferences']
            dense[mode] += difference_count
            critical[mode] += len(query_differences)
    return dict(profiles=32, denseSamples=samples, criticalQueries=queries, methodNames=METHODS,
                denseDifferences=dense, criticalDifferences=critical,
                genericNativePathDifferences=generic, coreGraphicsDifferences=core_graphics)


def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read('investigation.json')
    assert report['accepted'] is False and report['status'] == 'diagnostic-only'
    assert report['implementationApplied'] is False and report['prototypeRejected'] is True
    assert report['expectedImagesChanged'] is False
    assert report['approvedExceptions'] == [] and report['tolerance'] == 'none'
    assert report['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert set(report['files']) == {str(p.relative_to(directory)) for p in directory.rglob('*')
                                   if p.is_file() and p.name not in ['investigation.json', 'README.md']}
    for name, checksum in report['files'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert digest(directory / name) == checksum, name
    native = read('native-paths.json')
    linux = read('linux-results.json')
    assert native['accepted'] is False and linux['accepted'] is False
    assert linux['qt'] == report['qt'] == '6.8.3'
    assert linux['platform'] == report['platform'] == 'offscreen'
    configs = read('geometries.json')
    assert [r['fixture'] for r in native['rows']] == [r['fixture'] for r in configs]
    preserved = 0
    old = json.loads((ROOT / 'evidence/development/surface-supplement-20261016/sdk/v1/paths.json').read_text())['rows']
    old = {r['fixture']: r for r in old}
    for config, row in zip(configs, native['rows']):
        for key in ['width', 'height', 'radius']:
            assert config[key] == row[key]
        queries = [dict(point) for point in config['queries']]
        w, h = config['width'], config['height']
        for x, y in [(0, h / 2), (1, h / 2), (w / 2, 0), (w / 2, 1),
                     (w / 2, h - 1), (w - 1, h / 2), (w, h / 2), (w / 2, h)]:
            for a in [math.nextafter(x, -math.inf), x, math.nextafter(x, math.inf)]:
                for b in [math.nextafter(y, -math.inf), y, math.nextafter(y, math.inf)]:
                    queries.append(dict(x=a, y=b))
        assert [{'x': r['x'], 'y': r['y']} for r in row['queries']] == queries
        if row['fixture'] in old:
            before = old[row['fixture']]
            assert row['centerline'] == before['centerline'] and row['stroke'] == before['stroke']
            assert len(config['queries']) == len(before['queries'])
            for a, b in zip(before['queries'], row['queries']):
                assert all(a[k] == b[k] for k in ['x', 'y', 'swiftUIContains'])
                preserved += 1
    summary = validate_rows(native['rows'], linux['rows'])
    summary['originalSparseQueriesPreserved'] = preserved
    assert summary == report['summary']
    assert (summary['denseSamples'], summary['criticalQueries'], preserved) == (6355228, 3299, 995)
    assert summary['denseDifferences'] == [38308, 37666, 37666, 38318, 37670]
    assert summary['criticalDifferences'] == [641, 724, 724, 652, 726]
    assert summary['genericNativePathDifferences'] == 0 and summary['coreGraphicsDifferences'] == 60063
    replay = read('sdk-replay-comparison.json')
    assert replay['accepted'] is False and replay['identical'] is True
    assert replay['source'] == replay['replay'] == digest(directory / 'native-paths.json')
    assert report['sourceOnlyReplayIdentical'] is True and report['linuxDenseMasksReproduced'] is True
    for name in ['sdk-commands.json', 'sdk-replay/commands.json']:
        commands = read(name)
        assert len(commands) == 2 and all(r['exitCode'] == 0 for r in commands)
        assert commands[0]['command'][:2] == ['xcrun', 'swiftc']
        assert '-I' not in commands[0]['command']
    assert read('linux-result.json')['exitCode'] == 0
    assert read('linux-dense-replay-comparison.json')['completeDenseMasksUnchanged'] is True
    manifest = read('first-linux-attempt-manifest.json')
    with tarfile.open(directory / 'first-linux-attempt.tar.gz') as stream:
        members = stream.getmembers()
        assert {m.name for m in members} == set(manifest) and len(members) == len(manifest)
        for member in members:
            assert member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
            data = stream.extractfile(member).read()
            assert hashlib.sha256(data).hexdigest() == manifest[member.name]['sha256']
            assert len(data) == manifest[member.name]['bytes']
        previous = json.loads(stream.extractfile('qt-results.json').read())['rows']
        assert len(previous) == 32
        for before, after in zip(previous, linux['rows']):
            assert before['fixture'] == after['fixture']
            assert all(a['mask'] == b['mask'] for a, b in zip(before['methods'], after['methods']))
    return summary


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
