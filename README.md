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
Seventy-six of the 80 discovered desktop entries have Linux candidates;
no component has passed its complete mirror gate.
The public GitHub wiki remote is unavailable; documentation currently lives here.

The [Stepper source investigation](docs/stepper.md) preserves hosted native
captures, exact integer/binding behavior and a fresh source-only replay. The Qt
candidate adds catalog and independent installed-consumer coverage; complete
font, symbol, frame, raster, physical and reader acceptance remains pending.

The [RadioGroup source investigation](docs/radio-group.md) preserves inherited
layout, controlled selection, precise pointer behavior and native Unicode identity.
Its Linux candidate adds catalog and independent package coverage; complete
font, symbol, frame, raster, keyboard and reader acceptance remain pending.

The [OTP source investigation](docs/otp-input.md) records numeric-character
filtering, raw editing versus caller state, composition and large input. Its
Linux candidate adds controlled editing, catalog and independent package
fixtures; native lifecycle, font, raster, physical and reader acceptance remain
pending.

The [ActivityItem source investigation](docs/activity-item.md) preserves action-slot
composition, dense width proposals, fixed label typography and native action
lifecycle traces. Its Linux candidate adds fixed-font labels, caller-owned action
content, catalog captures and an independent package consumer; complete native
font, symbol, frame, raster, physical and reader acceptance remains pending.

Generic child clipping now has a [software renderer candidate](docs/content-clipping.md)
sharing the existing continuous/circular/capsule paths; strict native acceptance
remains pending.

The [Modal source investigation](docs/modal.md) records fixed-width layout,
per-child padding and contextual sheet dismissal, with a clean source-only replay.
Its Linux candidate adds caller content, separate-window presentation, catalog
captures and an independent consumer. Exact pixels, native focused input,
physical presentations and reader acceptance remain pending.

The [Tooltip source investigation](docs/tooltip.md) preserves 168 closed wrapper
cases, a byte-identical source-only replay, accessibility hint updates and an
actual native help panel. The Linux candidate attaches to caller items, retains
their layout/input/state, supplies Qt accessibility hints and owns a separate
tooltip window. Native font, popup appearance/timing, physical input and reader
acceptance remain pending.

The [ButtonStyle source investigation](docs/button-style.md) preserves 704 closed
groups and an exact source-only replay. Flat label parts participate separately
in parent layout while sharing pressed visuals. CUA checks in an active/key
window confirm distinct targets, cross-target cancellation and rectangular input
beyond rounded paint. The Linux candidate preserves separate label parts, shared
action/press and caller identity, with catalog, independent package and eight
virtual profiles. Exact native pixels, focused keyboard/timing, physical input
and readers remain pending.

The [caller-font candidate](docs/font-modifier.md) supplies inherited defaults,
retained caller views, local scaling and first-baseline participation. All 1,656
closed source contexts remain in strict comparison: 76 exact pixel/frame matches,
1,168 frame matches and all produced states matching. Full Qt tests, independent
packaging, eight virtual display profiles and actual gallery toolbar input pass.
Native fonts/raster, complete contexts, physical displays and readers remain open.
That checkpoint recorded desktop candidate coverage of 75/80; none were accepted.

The [pill candidate](docs/pill-modifier.md) retains a single text caller, fixed mono 9
font and 7/4 capsule padding, caller formatting and baseline guides. All 2,112
public/bare/history captures remain in strict comparison: 224 exact cases, all
bare. Native fonts, symbols, pixels, complete formatting, physical input and
reader acceptance remain pending.

The [native chart investigation](docs/charts.md) covers all five chart families,
120 closed fixtures, 45 non-finite inputs and five finite controls. Ordinary
source outputs reproduce exactly; NaN-bar replay differences remain failed and
preserved. The five Linux chart candidates retain every closed/edge input and
history step in 1,744 strict comparisons. The geometry correction raises complete
native metric matches from 120 to 624 of 1,344; 40 complete cases match, all empty
charts. Another 125 scale/size/category/legend pairs remain strict. Native fonts,
fractional layout, geometry/raster, intrinsic proposals, non-finite behavior,
physical input and readers remain pending.

The [MediaLibrary candidate](docs/media-library.md) supplies an adaptive lazy grid
with retained caller tiles and generic primitive identities. Its complete 1,608
pixel/frame/lifecycle comparisons have 1,008 exact observed pairs and all 1,608
native lifecycle observations match; eight isolated
fatal inputs remain preserved. The formatted-text correction makes all 24 actual
gallery states match fresh callers exactly. Strict acceptance still fails.
The native record also preserves 7,440 public sizing queries and one witness
difference; Linux direct sizing remains unobserved. Fractional/text geometry,
lazy height estimates, fonts/raster, native input timing,
physical displays and readers remain pending; no mirror acceptance is claimed.

The [HeroCarousel candidate](docs/hero-carousel-linux.md) supplies an owned
horizontal viewport and retained caller slides, with catalog, independent
package and eight virtual display profiles. All 192 observations remain strict:
108 images, 184 active-frame sets and 168 lifecycle records match; 84 match all
three together. Eight gallery contexts pass actual operator clicks and caller
Tab/Space/disabled checks. Native sizing, complete geometry, lazy/gesture timing,
font/raster, reader, physical and independent-machine acceptance remain pending.

The [DateRangePicker reference investigation](docs/date-range-picker.md) preserves
384 closed contexts, 17,280 sizing queries and 17 matching typed history steps.
Its source-only rebuild replays all 1,206 files exactly on this machine. A native
input supplement retains 82 OS events and 21 milestones, including identical
ignore/delay images across three source variants, exact range clamping and
graphical preview/Space-commit differences. The owned Qt editors now run in the
catalog and independent consumer. Eight source-absent package/gallery profiles
match all 384 native model/displayed-date observations; complete geometry matches
in 8, and all 384 strict raster comparisons fail. Eight virtual display profiles
pass structural/input checks. All 17 typed caller-history steps now match model,
editor identity, calendar and environment observations. Complete native input,
geometry/raster, reader and physical acceptance remain pending. Desktop candidate coverage remains 76/80,
with zero accepted APIs.

The [desktop app tab bar candidate](docs/app-tabs.md) preserves caller-owned
selection requests, retained typed identities, integer badges and narrow overflow.
All 1,208 native state observations agree; 940 frame sets and 56 images match.
The [badge raster correction](docs/app-tabs.md#retained-badge-raster-correction)
brings the installed gallery to 28/28 exact operator states and preserves visible
badges at both pixel ratios. Native symbols, label fitting, sizing, keyboard timing,
accessibility, physical displays and readers remain pending.

The [dropdown menu candidate](docs/dropdown-menu.md) preserves all 256 native
closed contexts and 3,840 public sizing proposals. Every closed state agrees;
zero complete frame sets or pixels match, with 48 body/caller-only frame matches.
The installed package, eight virtual display profiles and 24 exact gallery caller
states pass. Native label/update timing, fonts/symbols/raster, popup presentation,
sizing, accessibility, physical displays and readers remain pending. Desktop
candidate coverage is 76/80 with zero accepted APIs.

The [file input source investigation](docs/file-input.md) records 256 native
closed contexts, 11,520 sizing responses and scoped chooser selection/cancel
diagnostics. FileInput's Linux chooser and full type/input/visual acceptance
remain pending, so desktop candidate coverage stays 75/80 with zero accepted.

The [command spotlight candidate](docs/command-spotlight.md) preserves its
fixed 520 by 380 surface, caller-owned query and lazy rows. Its public, probed and
literal witnesses agree at 256 closed contexts and 1,536 retained steps. The
source-only replay reproduces all 5,381 outputs. The Linux candidate retains all
1,792 strict native comparisons and caller-owned query/row state. All 23 actual
gallery states pass, and all 143 prior catalog PNGs and metadata stay unchanged.
Native fonts/raster, builder and callback timing, lazy eviction, sizing, physical
input and readers remain pending. Desktop candidate coverage is 75/80 with zero
accepted APIs.

The [surface modifier](docs/surface-modifier.md) decorates flat callers separately
and explicit stacks as one caller, preserving caller state, font inheritance and
input. Its complete 416-context comparison has 36 exact pixel/frame matches, 376
matching frame sets and all caller states matching. Eight surface virtual profiles,
five retained histories per profile and all ten actual gallery toolbar controls
pass. Native raster/shadow, system fonts/button, first-baseline/hit tests, physical
displays/input and readers remain pending.

The [page header and breadcrumb candidates](docs/navigation-layout.md) use measured
source layout, fixed typography, caller action content and logical-index
callbacks. Full font/symbol/raster and physical/reader acceptance remains pending.

[Sidebar items and branding](docs/sidebar-brand.md) add caller-owned selection and
the pinned template logo/lockup. Their full native visual and runtime acceptance
remains pending.

The [data-display candidates](docs/data-metrics.md) add icon badges, metrics,
stat cards and key labels with native layout/locale evidence. Complete mirror
acceptance remains pending.
