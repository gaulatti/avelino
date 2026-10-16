#!/usr/bin/env python3
"""Prove Stepper fails at the native construction/action/display boundary."""
from pathlib import Path
import resource
import subprocess
import sys
import tempfile

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
runner, imports = sys.argv[1:]
minimum, maximum = '-9223372036854775808', '9223372036854775807'


def run(name, declaration, message, action=None, request=None):
    with tempfile.TemporaryDirectory(prefix='avelino-invalid-stepper-') as directory:
        fixture = Path(directory) / 'tst_invalid.qml'
        fixture.write_text('import QtQuick\nimport QtTest\nimport Avelino\nItem { width: 800; height: 180\n'
            + 'BleeckerStepper { id: stepper; label: "Copies"; ' + declaration
            + '; onValueRequested: value => { console.log("binding-request:"+value); stepper.value=value } }\n'
            + 'TestCase { when: windowShown; function test_refusal() { console.log("constructed"); '
            + (('stepper.' + action + 'Input.click(); ') if action else '')
            + 'wait(50); fail("Invalid Stepper configuration/action was accepted") } }\n}')
        result = subprocess.run([runner, '-import', imports, '-input', str(fixture)], capture_output=True, timeout=20)
        output = result.stdout + result.stderr
        assert result.returncode < 0 and message.encode() in output, (name, result.returncode, output.decode(errors='replace'))
        assert (b'constructed' in output) == bool(action), name
        assert (b'binding-request:' in output) == bool(request), name
        if request:
            assert ('binding-request:' + request).encode() in output, name


wide = f'lowerBound: "{minimum}"; upperBound: "{maximum}"'
cases = [
    ('display-overflow', f'value: "{maximum}"; {wide}; displayOffset: 1', 'Stepper display overflow', None, None),
    ('display-underflow', f'value: "{minimum}"; {wide}; displayOffset: -1', 'Stepper display overflow', None, None),
    ('decrement-overflow', f'value: "-9223372036854775807"; {wide}; step: 2', 'Stepper decrement overflow', 'decrement', None),
    ('increment-overflow', f'value: "9223372036854775806"; {wide}; step: 2', 'Stepper increment overflow', 'increment', None),
    ('negative-step-decrement-overflow', f'value: 0; lowerBound: -1; upperBound: 1; step: "{minimum}"', 'Stepper decrement overflow', 'decrement', None),
    ('negative-step-increment-underflow', f'value: -1; lowerBound: -2; upperBound: 1; step: "{minimum}"', 'Stepper increment overflow', 'increment', None),
    ('display-after-increment', f'value: "9223372036854775806"; {wide}; displayOffset: 1', 'Stepper display overflow', 'increment', maximum),
    ('display-after-decrement', f'value: "-9223372036854775807"; {wide}; displayOffset: -1', 'Stepper display overflow', 'decrement', minimum),
    ('invalid-range', 'value: 2; lowerBound: 10; upperBound: 1', 'Stepper requires an ascending closed range', None, None),
]
for case in cases:
    run(*case)
for value in ['9007199254740992', '1.25', 'Number.NaN', 'Number.POSITIVE_INFINITY', 'true', 'null', '"9223372036854775808"', '"-9223372036854775809"', '"01"', '"-0"', '" 8"']:
    run('invalid-value-' + value, f'value: {value}; {wide}', 'Stepper requires signed 64-bit integers')
for key in ['lowerBound', 'upperBound', 'step', 'displayOffset']:
    declaration = 'value: 2; lowerBound: 1; upperBound: 10; step: 1; displayOffset: 0'
    defaults = {'lowerBound': '1', 'upperBound': '10', 'step': '1', 'displayOffset': '0'}
    declaration = declaration.replace(key + ': ' + defaults[key], key + ': true')
    run('invalid-' + key, declaration, 'Stepper requires signed 64-bit integers')
print('Stepper: 9 native fail-fast phases and 15 invalid integer inputs refused; enabled action overflows occur only on activation')
