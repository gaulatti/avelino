# Linux development

Qt is pinned to **6.8.3**; the version must match exactly. The checked-in Dockerfile
uses an immutable Ubuntu 24.04 base image and official Qt archives via aqt 3.3.0.
It supports separate ARM64 and x86_64 builds. ICU is included from Qt's archive,
since the prebuilt Qt binaries require its matching version.

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
Each configuration runs the base fixture, `--controls`, `--composition`,
`--selection`, `--checkbox`, `--secure-field`, `--search-field`, `--collection-filters`, `--slider`, `--tabs` and `--pagination` independently; eighty-eight
window/full-output pairs cover them.
The catalog galleries are `--fixture foundations`, `surfaces`, `data-display`,
`controls`, `composition`, `selection`, `checkbox`, `secure-field`, `search-field`, `collection-filters`, `slider`, `tabs` and `pagination`; their native
comparisons remain pending.

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
