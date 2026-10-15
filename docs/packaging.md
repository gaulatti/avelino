# Installed package checks

The core ships a shared library, QML plugin, qmldir/type metadata, QML source,
embedded static font resources, font license notices, and asset provenance.
`find_package(Avelino 0.1 REQUIRED)` exposes `Avelino::Avelino` and
`Avelino_QML_IMPORT_PATH`. Set the engine's import path to that installed directory.
Desktop has no media-decoder dependency.

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
The harness runs eleven independent windows in each configuration: the base library
fixture, `InstalledConsumer --controls`, `InstalledConsumer --composition` and
`InstalledConsumer --selection`, `InstalledConsumer --checkbox` and
`InstalledConsumer --secure-field`, `InstalledConsumer --search-field` and
`InstalledConsumer --collection-filters`, `InstalledConsumer --slider`, `InstalledConsumer --tabs` and `InstalledConsumer --pagination`.
Their eighty-eight capture pairs keep
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
is supported only by the CurveRenderer; software clipping remains pending.
Screen-reader output remains a separate unaccepted gate.
Context menus and separate-window overlays
remain unimplemented and cannot pass their gate through these captures.
The composition fixture checks ordered adaptive-grid reflow and focus through
window resizing, plus section/action, shell, footer, feed and progress slots.
These runtime checks do not close their native visual comparisons.
The package includes the original selection/checkbox/secure-field/search-field-symbol candidates' provenance records;
their source equivalence and distribution acceptance remain pending.
The X11 output is 1920 × 1400 and the nested Wayland output 1760 × 1280.
The harness checks that each complete scaled client fits with room for decorations;
the composition fixture's 1680 × 1120 client must not be cropped by the compositor.
If a consumer exits before producing capture metadata, the harness reports its
actual exit status and log rather than only a missing process.

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
probe currently fails with `module "Avelino" is not installed`: the executable
does not add its installed QML import directory. Catalog relocation/startup
remains an open packaging gate despite the passing library consumer. The
[pagination evidence](../evidence/development/pagination/candidate.json) retains
that failed probe; the next packaging change must verify source/build trees and
`QML_IMPORT_PATH` are absent while launching the installed catalog.
