#!/usr/bin/env python3
"""Carry unchanged native admin geometry and binding observations to consumers."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/reference-investigations/admin-shell-pinned-matrix-20261020'
BOUNDARIES = ROOT / 'evidence/reference-investigations/admin-divider-boundaries-20261020'
TARGET = ROOT / 'tests/consumer/native-admin-shell-witnesses.json'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'


def generate():
    source = json.loads((SOURCE / 'measurements.json').read_text())
    fixtures = {r['id']: r for r in json.loads((SOURCE / 'fixtures.json').read_text())}
    boundaries = json.loads((BOUNDARIES / 'boundaries.json').read_text())
    assert source['reference'] == boundaries['reference'] == REFERENCE
    assert source['accepted'] is boundaries['accepted'] is False
    assert boundaries['freshWindowPerPosition'] and boundaries['mechanism'] == 'NSSplitView.setPosition'
    files = json.loads((BOUNDARIES / 'files.json').read_text())
    assert set(files) == {str(f.relative_to(BOUNDARIES)) for f in BOUNDARIES.rglob('*') if f.is_file() and f.name != 'files.json'}
    assert all(hashlib.sha256((BOUNDARIES / n).read_bytes()).hexdigest() == h for n, h in files.items())
    inputs = json.loads((BOUNDARIES / 'inputs.json').read_text())
    assert inputs['reference'] == REFERENCE and inputs['pinnedSourceFiles'] == 53
    assert inputs['libraryObjectSha256'] == '0d98b215928f864cb6874be5426360db0861eb44a049af40e556aca9e319c025'
    assert inputs['reusedLibraryObject'] and not inputs['independentLibraryRebuild']
    assert all(json.loads((BOUNDARIES / n).read_text())['exitCode'] == 0
               for n in ['compile-command.json', 'capture-command.json', 'result.json'])

    def state(row):
        return dict(step=row['step'], navigation=row['navigation'], requests=row['requests'], pending=row['pending'],
                    displayedNavigation=not row['arrangedSubviews'][0]['collapsed'],
                    columnWidth=row['arrangedSubviews'][0]['frame']['width'], frames=row['bodyFramesFromGlobal'])

    profiles = []
    for row in source['profiles']:
        if not row['measured']:
            continue
        observed = row['state']
        definition = dict(fixtures[row['case']], width=observed['contentFrame']['width'], height=observed['contentFrame']['height'])
        profiles.append(dict(name=f"{row['case']}-{'dark' if row['dark'] else 'light'}-{row['initial']}",
                             definition=definition, initial=row['initial'], dark=row['dark'], state=state(observed),
                             sourceCapture=observed['before']['path']))
    histories = [dict(owner=r['owner'], initial=r['initial'], definition=fixtures['standard'],
                      states=[state(s) for s in r['states']]) for r in source['histories'] if r['measured']]
    assert len(profiles) == 80 and len(histories) == 6 and sum(len(r['states']) for r in histories) == 160
    assert len(boundaries['rows']) == 168
    return json.dumps(dict(reference=REFERENCE, profiles=profiles, histories=histories, boundaries=boundaries['rows'],
                           sourceFiles={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                        for p in [SOURCE / 'measurements.json', SOURCE / 'fixtures.json', BOUNDARIES / 'boundaries.json']},
                           physicalInput=False, toolbarActionsObserved=False, accepted=False), indent=2, sort_keys=True) + '\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    content = generate()
    if args.check:
        assert TARGET.read_text() == content, 'Admin shell witnesses differ from the retained native observations'
        relative = BOUNDARIES.relative_to(ROOT)
        expected = {str(f.relative_to(ROOT)) for f in BOUNDARIES.rglob('*') if f.is_file()}
        staged = set(subprocess.check_output(['git', 'ls-files', '-z', '--', str(relative)], cwd=ROOT).decode().strip('\0').split('\0'))
        assert staged == expected, 'Every native divider capsule member must be in the Git index'
        for name in staged:
            assert subprocess.check_output(['git', 'show', ':' + name], cwd=ROOT) == (ROOT / name).read_bytes(), name
    else:
        TARGET.write_text(content)
