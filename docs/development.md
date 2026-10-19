# Linux development

Qt is pinned to **6.8.3**; the version must match exactly. The checked-in Dockerfile
uses an immutable Ubuntu 24.04 base image and official Qt archives via aqt 3.3.0.
It supports separate ARM64 and x86_64 builds. ICU is included from Qt's archive,
since the prebuilt Qt binaries require its matching version. Metric formatting
also uses Ubuntu system ICU **74.2** (`libicu-dev` to build, `libicu74` at runtime).
Versioned library lookup and a configure-time ABI link probe prevent mixing its
headers with Qt's separate ICU73 libraries. The software content
mask also builds against Qt QuickPrivate; the image provides `libxkbcommon-dev`
for its private dependency graph. Installed consumers use public dependencies.
See [content clipping](content-clipping.md) before changing the Qt pin.

System-font date editors require CJK glyph coverage for Chinese lunar labels and
Korean leap-month labels. On Ubuntu 24.04, install `fonts-noto-cjk` and
`fontconfig`; the checked-in toolchain installs both. Glyph-run regression checks
reject missing-glyph boxes in all 72 Chinese source endpoint strings. This
coverage check is separate from native font metrics and raster acceptance.

Keep the tracked tree Linux-only. `.gitignore` excludes Swift/Apple project files
and the reference source cache. Before committing, run
`python3 scripts/check-linux-boundary.py`; the References CI job also rejects
Apple source or projects hidden in tracked archives. Reference discovery reads
verified historical artifacts from the ignored cache; Apple capture tools are
external, as described in [reference reproduction](references.md).

```sh
docker build -t avelino-toolchain:qt6.8.3 -f tools/Dockerfile .
docker run --rm -v "$PWD:/work" avelino-toolchain:qt6.8.3 bash scripts/check-linux.sh
```

The check compiles the module and catalog, exercises Qt Quick pointer/keyboard
and editing tests, installs a package into a clean temporary prefix, builds and
runs a separately copied consumer, and saves light/dark PNGs with capture metadata.
The consumer verifies actions, disabled state, text selection/replacement, and
bundled font registration. Loading suppression must hold even when a consumer
explicitly sets `enabled: true`; an internal native Button template enforces it.
It currently has no accepted overlay implementation.

The [chart matrix](charts.md#linux-candidate) adds all five public families and
their complete closed/edge/history corpus. `--fixture charts` opens the installed
gallery. Package checks run `--charts --charts-observe`, preserve source geometry
failures and check real Qt data-row interfaces and read-only pointer/keyboard
behavior. All 1,744 native/candidate image pairs are compared separately by
`scripts/compare-chart-captures.py`; its strict failures remain visible in CI.
The [supplemental geometry matrix](charts.md#geometry-correction) adds 125
requested-scale, tiny-frame, RTL-category and long-legend inputs through the
installed catalog. Its separate strict CI comparison retains native fractional
font/layout/raster differences; actual native backing scale stays two.

The [AppTabBar candidate](app-tabs.md#linux-candidate-api) adds the 35th installed
consumer mode and `--fixture app-tabs`. Its 1,208 closed/history comparisons keep
all native differences visible. The gallery exercises caller-owned selection,
delayed acknowledgement, reorder, empty/restore, widths, badges, disabled state,
RTL, appearance and text scale. Eight focused virtual profiles are recorded
separately from physical displays and readers. The subsequent badge correction
makes all 28 retained gallery states match fresh processes at DPR 1 and 2.
`app-tabs-retained-raster` and `app-tabs-retained-raster-dpr2` also require visible
badge pixels, independently of fresh-versus-retained equality. The original
disabled failures and discarded ordinary-layer attempts remain preserved.

The [command spotlight source investigation](command-spotlight.md) precedes its
Linux implementation. It records fixed sizing, caller query ownership, local
field events, measured clear-button targets and retained row state. Run
`python3 scripts/verify-command-spotlight-source.py` to audit the native record;
these observations do not increment candidate coverage or close Linux gates.

Every Linux capture links an environment record with source revision, dirty-tree
state, exact source/resource hashes, compiler, Qt, CMake, and installed package
versions. The image metadata also records the actual renderer API and resolved
label metrics. A dirty local capture remains distinguishable from a CI commit.
The container's read-only Git queries trust only the mounted checkout for that
invocation; they do not change the host or global Git configuration.

The installed consumer also runs on an Xvfb X11 server and a Weston Wayland
compositor nested on that server. Both exercise Qt's software and OpenGL renderers
with Mesa software rendering, at DPR 1 and 2; the second configuration uses dark
appearance and text scale 1.5. Whole-output screenshots accompany single-window
captures, renderer logs, dimensions, checksums, and environment metadata. These
are virtual display-session checks with synthetic in-process input. They do not
close physical input, hardware acceleration, accessibility, or overlay acceptance.
The default Weston input-method keyboard appears when the text field receives
focus; the whole-output capture preserves it as session evidence.
[Weston's backend documentation](https://wayland.pages.freedesktop.org/weston/toc/running-weston.html)
describes how its X11 backend composites Wayland surfaces into the parent output.
The toolchain builds Weston 13.0.4 from a checksummed upstream release using
`tools/install-weston.sh`. Ubuntu 24.04's original Weston 13.0.0 crashes in its
desktop-shell child-focus walk when another application activates while a
non-grabbing popup is visible. A standalone stock Qt tooltip reproduces the
failure without loading Avelino; the same executable survives on 13.0.4. Qt
remains pinned to 6.8.3. The compositor build provides X11, nested Wayland and
headless backends for verification; physical display and DRM acceptance remain
separate gates.
The Docker context explicitly includes both `tools/Dockerfile` and
`tools/install-weston.sh`; repository sources and evidence remain excluded.
Each configuration runs the base fixture, `--controls`, `--composition`,
`--selection`, `--checkbox`, `--secure-field`, `--search-field`, `--collection-filters`, `--slider`, `--tabs`, `--pagination`, `--pagination-integers`, `--accordion`, `--presentation-states`, `--spinner`, `--alert`, `--clipping`, `--navigation`, `--sidebar-brand` and
`--data-metrics`, `--stepper`, `--radio-group`, `--otp-input`, `--activity-item`,
`--modal`, `--tooltip`, `--button-style`, `--font-modifier`, `--surface-modifier`,
`--surface-baseline`, `--surface-input`, `--pill-modifier`, `--charts`,
`--media-library` and `--app-tabs` independently. The configured matrix has 280
parent-window/full-output pairs; Modal and Tooltip also record their separate
popup windows in each configuration. The harness reports live producers every
30 seconds while waiting for their evidence; it does not kill them after a fixed
poll count. Producer exit without metadata still reports the actual exit status
and fails. Consumer assertions and the CI runner's job deadline remain in effect.
The catalog galleries are `--fixture foundations`, `surfaces`, `data-display`,
`controls`, `composition`, `selection`, `checkbox`, `secure-field`, `search-field`, `collection-filters`, `slider`, `tabs`, `pagination`, `pagination-integers`, `accordion`, `presentation-states`, `spinner`, `alert`, `clipping`, `navigation`, `sidebar-brand`, `data-metrics`, `stepper`, `radio-group`, `otp-input`, `activity-item`, `modal`, `tooltip`, `button-style`, `font-modifier`, `surface-modifier`,
`pill-modifier`, `charts`, `media-library` and `app-tabs`; their native
comparisons remain pending.

The [ActivityItem fixture](activity-item.md#linux-candidate) checks caller-owned
actions, field updates, fixed typography, dense proposals and resize histories.
`--fixture activity-item` opens its gallery; `InstalledConsumer --activity-item`
replays the 13 source pointer/lifecycle traces. Producer updates wait for an
actual completed frame before sending the next synthetic click. Qt interface
queries and virtual displays remain separate from real reader/physical acceptance.

The [Modal fixture](modal.md#linux-candidate) replays 80 preserved state snapshots,
clipped input and measured Close hit regions, then uses the gallery button to
open an editor, type through its caller binding and reopen it. Separate source
trace windows are destroyed immediately between traces to release their renderers;
retained-window state is kept throughout its own reopening trace. The final popup
remains visible for the full-output capture. Native focused keyboard/IME and
reader acceptance remain separate.

The selector's open `Popup.Item` and scrollbars remain
inside the captured client, with explicit bounds checks. Native selector/popover
and symbol comparisons, separate-window overlays and screen-reader acceptance
remain pending. See [the selector contract](selectors.md).
The [checkbox contract](checkbox.md) adds bound-state/input checks and real Qt
accessibility interface queries. Its native font/glyph, full behavior and
screen-reader acceptance remain pending.
The [secure-field contract](secure-field.md) adds masking/reveal, clipboard,
caller-model and native Qt password/action interface checks.
The [search-field contract](search-field.md) adds conditional clear actions,
caller updates, fixed glyph slots and native Qt editor/action queries.
The [collection-filter contract](collection-filters.md) adds composed query binding,
independent chip callbacks, caller selection/removal, wrapping and slot sizing.

In the package-only container, run `bash check-installed.sh` followed by
`bash check-display-sessions.sh`. The latter refuses an existing output directory;
pass a new absolute directory as its first argument for another candidate run.

These are implementation checks. The first Qt button, spinner, and text-field
presentations are **verification-pending**: the SwiftUI comparisons, shadow and
continuous-corner geometry, loading indicator, platform focus, selection treatment,
actual X11/Wayland sessions, accessibility, and scaling matrices are unfinished.
Do not interpret software-rendered PNGs as accepted mirror baselines.

The button surface now draws explicit continuous cubic contours, including the
half-width inset border, through an internal Qt Quick Shape. Narrow surfaces
adjust each axis independently. Native point measurements and the geometry test
cover normal, fractional, narrow, square, and radius-clamped surfaces. Qt uses
its raster path renderer in software sessions and the requested curve renderer
in RHI sessions; capture metadata records the actual renderer and both paths.
The installed consumer checks that the owned surface is present too.
[Qt Shape rendering](https://doc.qt.io/qt-6.8/qml-qtquick-shapes-shape.html)
describes these backend implementations. These geometry checks do not establish
glyph, custom-content clipping, focus, transition, or complete button acceptance.

Button backgrounds and label baselines now align their painted origins to the
window's physical pixel grid. Logical widths, positions, and padding remain
fractional. The label line box rounds upward to a physical pixel before vertical
centering. A native helper reads the window's effective DPR and refreshes before
scene-graph synchronization, including ancestor motion and window reparenting.
The helper's target excludes the painted item's own translation to avoid feedback.
The default loading/label composition uses an explicitly positioned content item;
this prevents positioner/anchor updates from displacing short link-button labels.
[Qt window rendering signals](https://doc.qt.io/qt-6.8/qquickwindow.html#afterAnimating)
document the GUI-thread synchronization point.

The component suite runs at DPR 1 and 2. Its button fixtures exercise fractional
placement, translated/scaled/rotated ancestors, reparenting between displayed
windows, unchanged logical dimensions, and pointer activation after movement.
All four link sizes also verify that their label remains vertically centered.
The rotated-coordinate assertions allow two Float32 rounding units for scene
matrices; the image comparator still allows zero changed pixels. The installed
consumer uses fractional parent coordinates and checks the owned background and
loading-label baseline in each display configuration. These checks establish
the rendering mechanism, not source-image or transition acceptance.

The [surfaces and layout batch](foundations.md) adds seven owned presentation and
composition candidates. Its gallery is available through `--fixture foundations`;
the build check captures both themes at both DPRs. The installed consumer includes
every component and checks group keyboard navigation, progress geometry, separator
alpha, frozen skeleton motion, and header/panel composition. Native source images
and full component acceptance remain pending.

Default button labels use an owned `ButtonLabel` painted item. Qt shapes at
font design-unit precision; the two bundled families now resolve sizes, line
boxes and intrinsic view bounds using [measured native typography](typography.md).
The requested logical size remains separate from the source-resolved glyph size.
Shaping for the two bundled families uses typographic line metrics, including
their fallback runs. This keeps CJK coverage from enlarging the native line box:
the captured Unicode page header remains 68 points high with Noto CJK installed.
Glyph size and fallback coverage remain separate from native raster acceptance.
For example, a source custom-font request of 19.5 resolves to 20, with a 25-unit
line box and baseline 21. This corrects the earlier assumption that preserving
the fractional request as the rendered size reproduced the source.

The control's font remains available to consumers, including explicit pixel-size
overrides. Glyph runs carry value data across synchronization; the painting thread
creates its own `QRawFont`, as required by
[Qt's thread-local font contract](https://doc.qt.io/qt-6.8/qrawfont.html).

The typography suite checks all 2,160 measured source cases at their matching DPR,
all four button sizes at four text scales, consumer font-size overrides, literal
markup, explicit line heights and wrapping. The installed consumer verifies both
requested/resolved sizes and source line metrics. Existing catalog fixtures record
the same fields. Exact rasterization, system/fallback fonts, custom content,
screen-reader output and complete component acceptance remain pending.
Text-field and text-area editing still use Qt's native font path; fractional-size
editing typography requires separate source comparison.

The catalog is a native Qt application; this repository has no browser frontend
or application server. Application-backend Compose requirements do not apply.

`AvelinoCatalog --fixture composition` exercises the dashboard, shell, footer,
feed and stacked-progress candidates. See [their contract and pending cases](composition.md).

Official framework references:
[Qt control customization](https://doc.qt.io/qt-6.8/qtquickcontrols-customize.html),
[QML modules](https://doc.qt.io/qt-6.8/qt-add-qml-module.html), and
[Qt Quick Test](https://doc.qt.io/qt-6.8/qtquicktest-index.html).

The [slider contract](slider.md) adds retained numeric bindings, native template
input/value interfaces, partial intervals, decimal endpoints and bounded dense
ticks. Source keyboard equivalence remains explicitly pending.

The [Tabs fixture](tabs.md) checks shared caller selection, later external updates, disabled traversal and typed IDs. `--fixture tabs` renders the gallery; `InstalledConsumer --tabs` exercises the installed module. Proposed source captures remain separate from accepted references.

The [pagination and icon-button contract](pagination.md) adds `--fixture pagination` and an independent `--pagination` consumer. It preserves caller requests, external page/count updates and localized integer grouping. The source's inherited primary color is measured; symbols remain original pending equivalents.

The catalog links Qt 6.8.3 Test for held pointer captures. It verifies the pressed
state before capture and one activation after release. This is a catalog/tooling
dependency; the Avelino library does not link Qt Test.

The installed catalog discovers its packaged QML module without a build-tree
import override. `scripts/check-installed-catalog.sh` is copied into each fresh
package and verifies all gallery startup paths and missing-module refusal.

The [exact pagination integer contract](pagination-integers.md) uses native arithmetic over the complete signed 64-bit range. Large inputs and all requests use decimal strings; `pageRequested` now has a string signature. The `pagination-integers` gallery and consumer cover the precision and overflow boundaries.

The [source wrapping contract](wrapping.md) adds 120 measured text cases and
full-range pagination resize checks. Source ink bounds and trailing whitespace
remain distinct from shaped advances and exact pixel acceptance.

The [accordion contract](accordion.md) adds a conditional content factory and
initializer-owned state. The installed consumer checks header hit regions,
creation/destruction and reset, normal form editing/actions, Qt accessibility
and focus restoration through repeated collapses and later producer updates.

The [presentation-state contract](presentation-states.md) covers empty/error action
factories and the loading overlay. The native evidence matrix is copied unchanged
to `evidence/geometry/native-presentation-states.json` for component tests; its
verifier checks exact identity with the sealed source investigation. Centered label
origins use fitted source widths and trimmed advances, with all DPR 1/2 witnesses
checked separately from rasterization. Button `maximumWidth` supplies a label
layout proposal; the default `-1` retains intrinsic behavior. Invalid proposals
and unsupported alignment fail real QML startup. All preceding captures/metadata
must be checked for regression before publishing a checkpoint.

The [shared spinner](spinner.md) has its own installed consumer and gallery. Its
public native animation-model witnesses and 112 loading-button geometry/input
cases remain separate from exact raster, physical motion and reader acceptance.

The [alert fixture](alert.md) exercises its fitted presentation and generic content
factory. The source matrix and inherited-font prose cases remain distinct from
exact symbol/raster, software rounded-overflow and physical/reader acceptance.

The [navigation gallery](navigation-layout.md) is shared with the installed
consumer: `AvelinoCatalog --fixture navigation` and
`InstalledConsumer --navigation`. It exercises PageHeader caller actions and
Breadcrumb's logical-index requests through native Qt Templates. The proposal
pipeline captures all 392 isolated source contexts and CI compares the alert and
navigation groups alongside the preceding groups. Geometry/input checks remain
separate from exact pixels, unresolved Japanese glyph fallback, physical input
and actual reader output.

The [sidebar/branding gallery](sidebar-brand.md) shares its real fixture with the
installed `--sidebar-brand` consumer. The three source APIs cover selected and
disabled input, empty/wrapped/narrow/RTL titles, tiny/fractional logo sizes,
template tint and caller updates. The fixed source mask bytes ship embedded and
as an installed provenance asset. The 416-case strict native comparison remains
separate from input, package and virtual display checks.

The [data metrics gallery](data-metrics.md) shares its real fixture with the
installed `--data-metrics` workflow. Process-locale metric strings and inherited
control-locale deltas are checked separately. `--format-diagnostics PATH` writes
the strict 1,330-case native string report and exits 244 when differences remain;
other nonzero results are runtime failures. CI keeps this comparison as a separate
failing gate. The normal runtime/package checks do not imply string or pixel
acceptance.

Capture subprocesses retain the existing 30-second deadline. A timeout is recorded
as exit 124 with partial stdout/stderr and a failed manifest; the failed attempt
is copied under `artifacts/linux/capture-failures/` before temporary staging is
removed. CI still fails that capture. There is no automatic retry or deadline
extension.

RadioGroup uses the pinned Qt 6.8.3 `QuickTemplates2Private` font adapter in the
library build. Consumers use the installed QML module and shared library. Run
`python3 scripts/generate-radio-witnesses.py --check` to audit generated Unicode
facts and the independent consumer witnesses against the preserved source.


The [ButtonStyle candidate](button-style.md#candidate-evidence) adds the 27th
consumer mode, four gallery images and a strict 704-case matrix. Local virtual
evidence covers eight focused ButtonStyle profiles; that checkpoint configured
216 parent-window/full-output pairs in CI. The consumer checks that actual
paint grows and shrinks with text scale, beyond metadata and input assertions.
`RoundedContent.clipsInput` defaults to true; ButtonStyle separates rounded paint
from its rectangular input. Both continuous background and clipping shapes use
asynchronous curve processing to retain queued layout edits in Qt 6.8.3.

After runtime assertions, the ButtonStyle consumer waits for explicit capture
acknowledgment; the runner owns deadlines/cancellation. The isolated local CTest
run keeps source/build inputs read-only and mounts separate writable Testing and
artifacts directories, including OTP trace reports.
