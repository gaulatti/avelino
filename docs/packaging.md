# Installed package checks

The core ships a shared library, QML plugin, qmldir/type metadata, QML source,
embedded static font resources, font license notices, and asset provenance.
`find_package(Avelino 0.1 REQUIRED)` exposes `Avelino::Avelino` and
`Avelino_QML_IMPORT_PATH`. Set the engine's import path to that installed directory.
The desktop library has no playback backend. Metric formatting requires Ubuntu
`libicu74` (74.2); its development headers are required only for library builds.
The formatter links versioned system ICU libraries independently from Qt's ICU73.
Installed consumers need public Qt development files and the runtime library;
Avelino's private ICU, Tracker and Qt QuickPrivate headers are not exported.
FileInput indexed search links Ubuntu24.04 Tracker SPARQL3.7.1 and requires its
filesystem miner/extractors on the session bus. It uses the existing index policy
and reports an unavailable service in the chooser. The build requires pkg-config
and `libtracker-sparql-3.0-dev`; the toolchain includes the runtime service and
extractors. This adds system indexed search, with TV/playback still separate.
See [file-input-search.md](file-input-search.md).
The package also carries `run-file-search.py` and
`check-display-sessions-file-search.sh`. CI runs this separate eight-profile
search matrix through the real private index and the normal installed module,
including a selected chooser held for full compositor capture.

The five [chart candidates](charts.md#linux-candidate) add an owned QPainter-based
renderer to the same library, with no Qt Charts dependency. The package-only
`--charts --charts-observe` mode exercises all 170 closed/edge inputs and six
retained histories in each selected context, including per-row Qt accessibility
and read-only synthetic input. Default `--charts` keeps native geometry failures
strict; observation mode does not accept them. The display harness includes charts
in all eight X11/Wayland, renderer and display/text-scale profiles.

The independent consumer is copied outside the repository and built against a
temporary installation. Its public import comes from the installed package;
it does not use a source QML directory or build-tree module import. CI then builds
and runs it again in a fresh container whose only mount contains the installed
package and the independent consumer fixture. The original product source and
build trees are absent. This also checks relocating the CMake/QML package prefix.
Open overlays and internal controls will be required as those APIs are implemented.

Each local run replaces the generated `artifacts/package/` directory with the
already-verified fresh temporary installation and consumer source. This removes
obsolete installed files and prevents nested copies from retaining old consumer
code. CI deliberately seeds stale source and install files, then verifies their
replacement before building the package-only consumer. Previous generated package
outputs are temporary and are removed by the check script.

The package-only consumer's display harness starts an Xvfb X11 server and a
Weston Wayland compositor nested on it. It saves whole-output and window captures
for software/OpenGL rendering at two display/text scales. The producer's source
and build trees remain absent. Metadata explicitly identifies virtual displays, Mesa software
rendering, synthetic input, and the still-pending overlay/accessibility checks.
Xvfb retains its state between clients, and the native cursor is parked at
2559,1919, outside all clients and the nested compositor. The checked position is
saved in `native-pointer.txt` and identified in each capture's metadata. Otherwise,
mapping a tooltip beneath the idle native cursor can inject a genuine Wayland
Leave while the consumer's synthetic Qt pointer is still over its caller.
This separates the synthetic-input run from the physical-input acceptance gate.
The base consumer also waits for asynchronous Shape processing and two displayed
frames with unchanged ready path/geometry observations after changing loading
content. Its metadata records `asyncShapeFrameChecks`, which the display harness
requires. A [delayed-worker regression](../evidence/development/surface-border-20261016/README.md#async-shape-readiness)
shows that the former fixed 50 ms wait could capture an earlier button width
while its live properties already described the new width. The current barrier
reaches Shape Ready before capture under the same delay. Existing assertions and
strict comparison tolerances remain intact.
The [pointer-isolation checkpoint](../evidence/development/tooltip-pointer-isolation-20261016/README.md)
passes the complete 224-session matrix, eight executable-only Tooltip profiles,
and 30 repeated processes using the original failed CI installation. Failed
attempts, the native Wayland event trace and the startup position guard remain
preserved. These checks leave strict native and physical acceptance pending.
The harness runs thirty-three independent fixtures in each configuration: the base library
fixture, `InstalledConsumer --controls`, `InstalledConsumer --composition` and
`InstalledConsumer --selection`, `InstalledConsumer --checkbox` and
`InstalledConsumer --secure-field`, `InstalledConsumer --search-field` and
`InstalledConsumer --collection-filters`, `InstalledConsumer --slider`, `InstalledConsumer --tabs`, `InstalledConsumer --pagination`, `InstalledConsumer --pagination-integers`, `InstalledConsumer --accordion`,
`InstalledConsumer --presentation-states`, `InstalledConsumer --spinner` and
`InstalledConsumer --alert`, `InstalledConsumer --clipping` and
`InstalledConsumer --navigation`, `InstalledConsumer --sidebar-brand` and
`InstalledConsumer --data-metrics`, `InstalledConsumer --stepper`,
`InstalledConsumer --radio-group`, `InstalledConsumer --otp-input` and
`InstalledConsumer --activity-item`, `InstalledConsumer --modal` and
`InstalledConsumer --tooltip`, `InstalledConsumer --button-style` and
`InstalledConsumer --font-modifier`, `--surface-modifier`, `--surface-baseline`,
`--surface-input`, `--pill-modifier` and `--charts`.
Their configured 264 capture pairs keep
form editing, scrolling, switch/toggle actions, disabled segmented options and
focus restoration separate from the base composition checks. The controls fixture
exercises the multiline editor's owned scrollbar. The selector fixture exercises
its open owned item popup, checkmark and scrollbar. Popup type, visible bounds,
disabled rows, scrolling, dismissal and restored focus are checked independently.
The checkbox fixture checks caller-model updates, disabled input, tab traversal,
wrapping and the real Qt accessibility role/name/checked-state interface.
The secure-field fixture checks immediate masking, caller-model editing,
reveal/hide, disabled input, clipboard behavior, keyboard traversal and the actual
Qt password/value/action interfaces. Screen-reader output remains separate.
The search fixture checks caller editing, pointer/keyboard clear, empty-action
removal, disabled traversal, Return, fixed slots and actual Qt interfaces.
The collection fixture checks composed query/clear/Return, independent caller
actions, removal and reclaimed width, tall content, disabled traversal, wrapped
chips and actual Qt grouping/editor/button interfaces. Its curved content clip
is implemented through both the CurveRenderer and the shared software adapter;
strict native clipping acceptance remains pending.
Screen-reader output remains a separate unaccepted gate.
Context menus remain unimplemented. Modal and Tooltip candidates preserve their
separate windows independently; full native presentation acceptance stays open.
The composition fixture checks ordered adaptive-grid reflow and focus through
window resizing, plus section/action, shell, footer, feed and progress slots.
These runtime checks do not close their native visual comparisons.
The package includes the original selection/checkbox/secure-field/search-field-symbol candidates' provenance records;
their source equivalence and distribution acceptance remain pending.
The X11 output is 2560 × 1920 and the nested Wayland output 2400 × 1800.
These outputs contain the 1100-by-850 Modal gallery at DPR two, including room
for window decorations. Client capture dimensions are checked against the output;
the harness does not resize client pixels to make them fit.

The [Modal package candidate](modal.md#linux-candidate) runs 25 consumer modes and
111 catalog captures without the implementation source/build tree mounted. The
eight focused display profiles also preserve a separate popup image. Its gallery
button opens the editor; typed text crosses the caller binding and survives a
close/reopen cycle. Source trace windows are deleted between traces to release
their renderers, and the parent must regain activation before a new sheet opens.
All 116 installed files match the package used for the 288 native-case captures.
Exact visible pixels, native keyboard/IME, physical input and readers stay open.
The harness checks that each complete scaled client fits with room for decorations;
the composition fixture's 1680 × 1120 client must not be cropped by the compositor.
If a consumer exits before producing capture metadata, the harness reports its
actual exit status and log rather than only a missing process.
It waits while the producer is alive and reports that state every 30 seconds.
A fixed observation interval does not terminate the consumer. Existing consumer
frame/input assertions, the runner's job deadline and explicit cancellation
remain in effect. Missing metadata after producer exit still fails immediately.

The [Tooltip package candidate](tooltip.md#candidate-evidence) runs 26 modes and
115 catalog captures, with 119 installed files checked against the producer.
Its eight focused profiles retain the parent, separate tooltip and whole output,
plus default/updated-hint bodies. Actual Qt accessibility descriptions and typed
caller bindings are checked without accepting native fonts, timing or readers.

The installed fixture places its controls at fractional parent coordinates. It
checks the button's owned surface and the label baseline after loading changes
the content composition, and records their painted coordinates at the window DPR.
The session harness verifies those coordinates independently of the catalog.
These are package/runtime checks; they do not accept the loading appearance.

No package release or complete mirror acceptance is claimed by these checkpoints.
Release acceptance requires every desktop gate in the parity inventory to pass.

The slider fixture checks retained caller bindings through pointer/drag, Qt
keyboard and actual value/action interfaces; disabled writes, partial/decimal
intervals, dense ticks and continued editing are included. Native source keyboard,
inactive presentation and real screen-reader acceptance remain separate.

The Tabs fixture verifies shared caller bindings across both wrappers after pointer, keyboard and Qt accessibility actions; disabled options/groups, numeric IDs, RTL, wrapping and continued editing are exercised. Screen-reader output and source keyboard equivalence remain pending.

The pagination window checks real Qt names/actions for both navigation buttons, disabled rejection, caller-owned requests, external updates, locale grouping, narrow/RTL layout and continued editing. Icon slots remain caller-owned; the package installs `navigation-symbols.json` with the original-chevron provenance.

The independent library consumer and the installed catalog have separate startup
boundaries. A package-only `install/bin/AvelinoCatalog --fixture pagination`
probe at `eed9aac` failed with `module "Avelino" is not installed`: the executable
does not add its installed QML import directory. That checkpoint left catalog relocation/startup open despite the passing library consumer. The
[pagination evidence](../evidence/development/pagination/candidate.json) retains
that failed probe; the relocation regression checks verify source/build trees and
`QML_IMPORT_PATH` are absent while launching the installed catalog.

The catalog now derives its QML import directory relative to the executable,
using the same GNU install directories as the exported CMake package. Launch
`install/bin/AvelinoCatalog` directly from a relocated installation; no
`QML_IMPORT_PATH` override is required. The Qt 6.8.3 runtime remains a prerequisite.
The source-build catalog continues to use the documented build-tree import path.

`check-installed-catalog.sh` exercises all thirty-nine galleries at both appearances
and DPRs, both action galleries, and the default button: 159 images with physical
size/metadata checks. It derives the complete expected filename set from the
gallery list, rejecting missing and unexpected captures. Both QML import environment variables are unset. A copied
executable without its module must fail with the missing-module error. The full
Linux check runs this against the staged install, then the package-only check
repeats it after relocation. CI preserves both capture sets. `catalog-evidence`
refuses existing output; rerun against a fresh package copy. These startup checks
do not close compositor, physical input, screen-reader or strict visual gates.

The FileInput display-session contract includes the current 49 images, 30
owner/input phases, 62 synthetic pointer deliveries and 164 synthetic key
deliveries. Native comparison and physical/reader gates remain pending. CI makes
only generated evidence trees readable to the host artifact uploader, including
after a failed check: Qt's temporary evidence directories otherwise retain root's
0700 mode from the verification container. This changes artifact readability,
not application behavior, reference images or acceptance rules.

The exact-pagination window verifies full Int64 labels and string requests across pointer, keyboard, actual accessibility actions and later caller updates. Unsafe numeric input and malformed/out-of-range string values are refused. Its virtual-session evidence remains separate from real reader/physical acceptance.

The accordion window preserves initializer-owned expansion, rejects spacer and
disabled input, destroys/recreates conditional forms, resets private child state
and preserves later title/body producer bindings. Real Qt accessibility presses,
keyboard traversal and focus restoration precede continued inside/outside editing.
Its physical/source-reader and motion acceptance remains separate.

The presentation-state consumer exercises both empty/error action factories,
producer updates without replacing child state, destruction/recreation, actual Qt
accessibility and disabled actions, normal keyboard input and outside editing.
Loading input checks first activate the underlying button without the overlay,
then prove inside blocking, outside activation and input restoration after removal.
The installed catalog includes `presentation-states` in both appearances/DPRs.
Source keyboard trapping, exact progress/symbol rendering, physical input and
actual screen-reader behavior remain separate acceptance work.

The spinner package installs `spinner-presentation.json` alongside its owned
QML/JavaScript presentation. The spinner consumer verifies 16/32/32 sizes, fixed
inner glyph bounds, phase progression, hidden/stopped/reduced-motion behavior,
explicit color and loading-button callback guards through real Qt interfaces.
Its eight virtual window/output pairs are implementation evidence; physical
animation timing, actual readers and complete image equivalence remain pending.

The alert package installs its original symbol provenance in `alert-symbols.json`.
The `--alert` window keeps input, focus, accessibility and factory lifecycle
evidence separate from native exact symbols and generic rounded-overflow clipping.
Its software/Mesa and standard/scaled captures do not establish physical input
or actual reader output.

The clipping fixture separately verifies all three outline kinds against a
patterned background, live source and path changes, resize, empty-source removal,
hide/show, and pointer/keyboard/editing/Qt accessibility actions inside the real
masked control tree. Its software adapter uses private Qt 6.8.3 interfaces only
inside the library; package consumers do not need private headers. See
[generic content clipping](content-clipping.md) for the source/input boundary.

The navigation mode checks action-state and focused-field preservation through
header producer updates, disabled and canceled actions, logical breadcrumb
indices through C++ array replacement, explicit factory replacement and header
remounting. It invokes the real Qt button accessibility actions. Its eight
virtual display configurations remain separate from native keyboard/focus,
Japanese glyph fallback, exact symbols/pixels and actual screen readers.

The sidebar/branding mode verifies the embedded pinned mask checksum, updates
the mark through one-point and fractional sizes inside an explicit caller frame,
and retains the lockup's fixed font through text-scale changes. Sidebar requests
do not overwrite caller selection; producer changes preserve editing/focus and
update actual Qt accessibility metadata. The installed package also includes
the unchanged source PNG and brand/symbol provenance. These checks do not approve
native icon artwork, interpolation/tint/raster or actual reader output.

The data-metrics workflow checks caller updates without remounting labels,
process/control locale ownership, absent/zero/signed deltas, fixed badge frames,
RTL rows, key-label updates, normal button actions and continued outside editing.
Its actual Qt static-text interfaces must reflect updated number/key strings.
The separate formatter diagnostic embeds all 1,330 sealed source witnesses in the
independent consumer, so it needs no source checkout at runtime. Complete native
font/symbol/locale/raster/motion and physical/reader acceptance stays pending.

The `radio-group` installed mode adds the source-derived selection and Unicode
identity witnesses. Its virtual-session checks use the same software/OpenGL and
standard/scaled profiles; native keyboard and actual-reader acceptance stay open.

The `activity-item` mode preserves caller actions and replays 94 native state
snapshots in 13 pointer/lifecycle traces. It verifies Qt Tab/Backtab and actual
static-text/button interfaces. Producer updates await layout synchronization and
a completed frame before further synthetic input; the session record reports
38 completed producer updates. The final package passes all 24 consumer modes,
107 gallery captures and eight focused ActivityItem configurations. All 112
installed files are byte-identical to its separate 552-case capture package.
The [candidate evidence](../evidence/development/activity/candidate.json) keeps
the first failed display attempt, diagnostics, exact comparisons and remaining
font/symbol/RTL/raster, physical and reader gates separate.


The [ButtonStyle package candidate](button-style.md#candidate-evidence) runs 27
modes and 119 gallery captures from a 121-file install. Its compiled consumer
passes eight virtual profiles with consumer sources and the producer build
absent. Every profile includes live curve-paint growth/shrink checks. All 115
previous gallery images and their full metadata remain byte-identical; all
installed files and five Qt private-integration files match. Native font/raster,
focused keyboard/timing, physical input and readers remain pending.


## Caller-font package checkpoint

The [font candidate](../evidence/development/font-modifier/candidate.json) adds
`BleeckerFont` and `BleeckerText` to the installed module. All 123 installed files
match across the build, independent package and compiled-only runtime copies.
The package's 28 modes and 123 gallery captures pass; all 119 prior PNGs and
full metadata remain byte-identical. Seven source files include Qt private
headers for the exact 6.8.3 integration; none is exported as a package header.

Eight virtual X11/Wayland profiles verify retained callers, actual Qt input and
accessibility, and live/restored font paint. A separate XTest operator run checks
six toolbar controls through nine exact complete Qt caller viewports. Source and
consumer checkouts are absent from those runtime containers. Native strict
comparison still fails, with 76/1,656 exact cases. Physical displays/readers and
complete framework contexts remain pending.

The original outer package wrapper ran the completed gallery check twice. Its
second call refused the existing directory and exited one; the required
`check-installed.sh` had already passed all modes, galleries and missing-module
refusal. The [receipt](../evidence/development/font-modifier/package-validation.json)
retains that control-flow evidence and the failed outer result separately.

## Generic surface adapter checkpoint

`InstalledConsumer --surface-modifier` exercises independent flat caller surfaces,
an explicit stack, inherited fonts, live/restored radius paint and retained button
state, focus, pointer/keyboard actions and actual Qt accessible names. The package
now runs 29 modes. Its 125 installed files match the executable-only runtime copy;
all 123 existing catalog PNGs and their metadata remain byte-identical to the
previous surface-paint checkpoint, as does the catalog relocation record.

The [development evidence](../evidence/development/surface-modifier-kernel-20261016/validation.json)
retains the initial font-unit assertion failure. A point-based QFont reports raw
pixel size -1 while retaining the correct family and 24-point size. The corrected
consumer compares the exact installed pixel-to-point conversion; all eight
virtual profiles pass and preserve these measurements in their logs. This check
does not approve a native font mapping. The later complete matrix below keeps
strict native comparison, first-baseline and physical/reader acceptance open.

The [complete surface candidate](../evidence/development/surface-modifier/candidate.json)
extends that mode with all 52 closed contexts and five retained histories per
profile. Eight surface and eight base profiles pass with consumer sources and
producer sources/builds absent. The package still has 125 installed files and
29 modes; the catalog now has 127 captures. All 123 prior PNGs and metadata are
unchanged. Its 96 module files match the published kernel exactly. Ten actual
XTest toolbar clicks produce eleven exact Qt caller viewports. These checks do
not accept native pixels, first-baseline/hit tests or physical/reader behavior.

The [surface guide/input candidate](../evidence/development/surface-supplement-20261016/candidate.json)
adds two installed modes, for 31 total, and keeps 127 catalog captures. The
default baseline/input modes fail strictly on native differences. Package and
display readiness use the explicit `--surface-supplement-observe` switch while
recording all failures; CI compares the complete native corpus independently.
All 125 installed files match producer, independent package and executable-only
runtime copies. The final consumer was compiled from separately frozen inputs.
Its post-run package digest matches the pre-run runtime digest; the capture
driver itself did not hash the executable at start.

All 32 focused virtual profiles pass structural checks. Native comparison still
has 112 activation differences, 16 guide and 40 baseline-frame failures, and
758 nonmatching images. Two catalog PNGs change; all other PNGs and all catalog
metadata remain identical. Physical display/input, hardware acceleration and
readers remain pending.


## Pill package checkpoint

The [pill candidate](pill-modifier.md#linux-candidate) adds `BleeckerPill` and its
internal decorator to a 127-file installation. The standalone consumer has 32
modes; the catalog has 131 captures. `--pill-modifier` fails on native frame/guide
differences; `--pill-observe` records every difference with structural failures
still fatal. The separate strict image job retains all 2,112 public/bare/history
comparisons. Native fonts, symbols, pixels, complete formatting, input timing and
physical/reader acceptance remain open.

Nine library source/header files include exact-version Qt private interfaces.
The new text resource bridge prepares explicitly sized inline images on the GUI
thread before the threaded scene graph can request them. Private headers stay
inside the library. GPU capsule tessellation is asynchronous and capture waits
for ready geometry and stable displayed pixels. Source-measured sharp rectangles
snap their paint while retaining fractional layout frames; the fixture's
alpha-capable painted texture clears adjacent software-rendered pixels correctly.

All 127 previous gallery PNGs and metadata are checked against the published
surface checkpoint. The executable-only virtual runtime uses the same compiled
consumer and installed module bytes as the independent package. Exact inputs,
failed attempts, source overlays and remaining gates are recorded in the
[sealed evidence](../evidence/development/pill-modifier-20261017/candidate.json).
