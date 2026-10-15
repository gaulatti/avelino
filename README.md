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

These commands recover the exact checksummed source artifacts from an immutable
historical Avelino commit into `.cache/reference-sources/`. A full clone contains
that history; shallow checkouts need the explicit fetch documented in
[reference reproduction](docs/references.md). No Sabella checkout is needed.
The current tracked tree contains Linux code, rendered references, and provenance.
Swift source and Apple capture tooling stay outside it.

`.gitignore` blocks accidental Swift/Apple project additions and local reference
caches. `python3 scripts/check-linux-boundary.py` checks the Git index, including
archive contents, and runs in CI to catch forced additions.

See [Linux build and catalog checks](docs/development.md) and
[installed-package verification](docs/packaging.md). The initial button, spinner,
and text-field implementations remain verification-pending.
Additional candidates and their unresolved acceptance cases are documented in
[foundations](docs/foundations.md), [cards and badges](docs/cards-and-badges.md),
and [data display](docs/data-display.md), alongside [form controls](docs/form-controls.md)
and [desktop composition](docs/composition.md), plus [selectors](docs/selectors.md)
and [checkboxes](docs/checkbox.md), plus [secure fields](docs/secure-field.md)
and [search fields](docs/search-field.md), plus [collection filters](docs/collection-filters.md), [sliders](docs/slider.md), and [tabs](docs/tabs.md), and [pagination/icon buttons](docs/pagination.md), plus [accordions](docs/accordion.md).
The [shared spinner contract](docs/spinner.md) records measured native sizes and
model-frame timing, with visual and physical acceptance still pending.
Shared label sizing follows [measured native typography](docs/typography.md).
The [empty/error/loading source investigation](docs/presentation-states.md)
now has [Linux presentation-state candidates](docs/presentation-states.md); complete mirror acceptance remains pending.
The [alert candidate](docs/alert.md) adds typed feedback with caller-owned content
and native prose-layout evidence.
Forty-seven of the 80 discovered desktop
entries have started; no component has passed its complete mirror gate.
The public GitHub wiki remote is unavailable; documentation currently lives here.

Generic child clipping now has a [software renderer candidate](docs/content-clipping.md)
sharing the existing continuous/circular/capsule paths; strict native acceptance
remains pending.

The [page header and breadcrumb source investigation](docs/navigation-layout.md)
preserves measured layout, fonts and pointer/lifecycle evidence for the next
desktop batch. Both Linux controls remain unimplemented.
