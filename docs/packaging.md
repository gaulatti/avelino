# Installed package checks

The core ships a shared library, QML plugin, qmldir/type metadata, QML source,
embedded static font resources, font license notices, and asset provenance.
`find_package(Avelino 0.1 REQUIRED)` exposes `Avelino::Avelino` and
`Avelino_QML_IMPORT_PATH`. Set the engine's import path to that installed directory.
Desktop has no media-decoder dependency. Metric formatting requires Ubuntu
`libicu74` (74.2); its development headers are required only for library builds.
The formatter links versioned system ICU libraries independently from Qt's ICU73.
Installed consumers need public Qt development files and the runtime library;
Avelino's private ICU and Qt QuickPrivate headers are not exported.

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
for software/OpenGL rendering at two display/text scales. Source and build trees
remain absent. Metadata explicitly identifies virtual displays, Mesa software
rendering, synthetic input, and the still-pending overlay/accessibility checks.
The harness runs twenty-seven independent fixtures in each configuration: the base library
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
`InstalledConsumer --tooltip` and `InstalledConsumer --button-style`.
Their configured 216 capture pairs keep
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

`check-installed-catalog.sh` exercises all twenty-nine galleries at both appearances
and DPRs, both action galleries, and the default button: 119 images with physical
size/metadata checks. Both QML import environment variables are unset. A copied
executable without its module must fail with the missing-module error. The full
Linux check runs this against the staged install, then the package-only check
repeats it after relocation. CI preserves both capture sets. `catalog-evidence`
refuses existing output; rerun against a fresh package copy. These startup checks
do not close compositor, physical input, screen-reader or strict visual gates.

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
