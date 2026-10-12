# Avelino

Avelino is the Linux implementation of the Bleecker design system, using Qt Quick.
For this port, Sabella's rendered desktop and television fixtures are the mirror
references. Bleecker, Sabella, Orchard, and Avelino are peer implementations.

**Status: implementation started; desktop and television acceptance are pending.**
No visual exceptions have been approved. A registered component or passing build
does not establish mirror acceptance.

- [Implementation plan](docs/plan.md)
- [Reference reproduction](docs/references.md)
- [Visual acceptance](docs/visual-acceptance.md)
- [Parity inventory](docs/parity-inventory.json)
- [Platform mappings and pending decisions](docs/platform-mappings.md)

## Verify preserved references

```sh
python3 scripts/verify-references.py
python3 scripts/discover-reference.py --check
```

These commands use only the source artifacts in this repository. No Sabella
checkout, GitHub fetch, Apple font redistribution, or expected-image regeneration
is required. Reference capture tools require the recorded Apple OS and SDK.

See [Linux build and catalog checks](docs/development.md) and
[installed-package verification](docs/packaging.md). The initial button, spinner,
and text-field implementations remain verification-pending.
The GitHub wiki has not been initialized; documentation currently lives here.
