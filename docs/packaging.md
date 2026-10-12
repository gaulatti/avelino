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
The harness runs three independent windows in each configuration: the base library
fixture, `InstalledConsumer --controls` and `InstalledConsumer --composition`.
Their twenty-four capture pairs keep
form editing, scrolling, switch/toggle actions, disabled segmented options and
focus restoration separate from the base composition checks. The controls fixture
exercises the multiline editor's owned scrollbar. Context menus and other overlays
remain unimplemented and cannot pass their gate through these captures.
The composition fixture checks ordered adaptive-grid reflow and focus through
window resizing, plus section/action, shell, footer, feed and progress slots.
These runtime checks do not close their native visual comparisons.
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
