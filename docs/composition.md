# Desktop composition candidates

Seven additional APIs have Linux candidates. They remain verification-pending:
complete visual and behavior cases and accessibility acceptance have not been
established. These add implementation coverage, not
accepted mirror completion.

The [checksummed development evidence](../evidence/development/composition/candidate.json)
preserves four catalog images, 498 passing Qt checks and twenty-four installed
window/full-output pairs. At that checkpoint, desktop coverage was 32 of 80 APIs started (40%), with
zero accepted components. The previous 25-API diagnostic comparison remains at
514 geometry matches and 40 exact matches of 724 cases. Its fresh raw comparison
outputs are local; the previous complete comparison artifacts remain committed.

The [composition source proposal](../evidence/reference-proposals/composition-20261012-v1/proposal.json)
adds 256 native captures covering 32 definitions: the seven APIs below and an
unchanged button anchor, each in both appearances, text scales and DPRs.
The [first strict comparison](../evidence/development/composition-native-before/candidate.json)
records 184 geometry matches and 60 exact matches. Every component remains pending.
The grid's empty definition has a measured zero-height component inside a nonempty
capture frame; the verifier permits this specific case without permitting missing
components or other blank captures.

The checksummed external native-tool artifact was extracted into a separate clean
directory. Helper recompilation and replay reproduced all 256 PNGs and the capture
manifest byte for byte. It links preserved owned Sabella object/module inputs from
the prior verified pinned-source build; this is not a new full source compilation.
Apple source and capture tooling remain outside Avelino. These images are proposed;
the existing expected baseline has not changed.

Measured open differences include intrinsic feed-content centering, progress-stack
capsule extent, wrapped-title line spacing and present-empty subtitle/footer line
heights. The first progress renderer clipped at the allocated control width;
the source capsule instead follows the sum of segment widths and gaps and can
paint beyond that allocation. The source's present-empty 12-point secondary line
occupies 14 logical units. These are implementation corrections, with no approved
exceptions or tolerance changes.

The [repaired candidate](../evidence/development/composition-repair/candidate.json)
preserves a fresh 256-case matrix: geometry matches increase from 184 to 240,
while exact image-and-geometry matches remain 60. Every section-header,
dashboard-section and feed case now matches the proposed source dimensions.
The button anchor's fractional width and the empty-footer line height still
differ; typography, semantic colors and capsule-edge rasterization also remain
open. All 724 PNGs in the original desktop matrix reproduce the prior repaired
candidate byte for byte. No component or reference baseline is accepted here.

A later [footer source investigation](../evidence/reference-investigations/footer-slots-20261019/investigation.json)
records 15 content cases across light/dark, text scale 1/1.5 and DPR 1/2.
All 120 transparent measurement pairs retain identical PNG bytes, and the 24
overlapping text, empty-text and block renders reproduce the original proposed
references byte for byte. The helper reuses a source-verified pinned Sabella
library object; it does not constitute another independent library rebuild or
clean replay. Native window/input observations remain pending.

Those measurements expose a public footer layout error that the catalog's
manually centered Loader concealed. The footer now lays out flattened content
children with the shared proposal column. Each child is horizontally centered
and receives 20 units above and below; padding is applied per child. An absent
slot or empty group leaves only the one-unit separator. A present zero-size
child produces height 41, while a present empty text line produces height 55.
Hidden content retains its layout allocation. Multiple children stack in source
order, and text wraps at the supplied width. The source footer retains its fixed
12-point Libre Franklin font in both recorded text-scale contexts.

The catalog uses the shared `FooterCase.qml` fixture with `BleeckerText` for the
source Text cases and leaves centering to the public control. Component tests
compare the footer and child frames against all 120 native measurements. The
installed composition consumer also constructs empty and two-child public
footers directly, checking heights 1/131 and the measured child positions without
the catalog fixture. The [compiled checkpoint](../evidence/development/footer-layout-20261019/result.json)
passes all 120 layouts, both existing composition suites, eight source-free
consumer contexts, and eight virtual X11/Wayland display contexts. All 120
catalog PNGs reproduce the earlier public-slot prototype byte for byte; 44 match
native pixels exactly. The build reuses a verified COW build cache and rebuilds
the affected targets. The consumer fixture was rebuilt after correcting an
invalid `Component.objectName` declaration; the failed attempt is retained.

Against the 24 earlier catalog captures, 12 pixel comparisons improve and two
light/DPR1 nonempty text comparisons increase from 491 to 495 changed pixels
when the fixture uses the source Text counterpart. No existing exact image pass
is lost. The remaining text raster and dark separator color differences remain
open. `python3 scripts/verify-footer-candidate.py` decodes these comparisons and
checks the retained code, native frames, component logs, package contexts, and
display captures. Strict pixels, native window/input, readers, and physical
display acceptance remain pending; the footer is still verification-pending.

The fresh Linux build and 498 Qt checks pass at DPR 1 and 2. A package-only
container passes the three consumer fixtures and all 24 virtual X11/Wayland
window/full-output checks, split across software/OpenGL and standard/scaled
configurations. The progress regression additionally verifies that a clipping
parent hides overflow while the unclipped control paints beyond its allocation.
Capture input hashes retain the pre-addition test file; the final regression
test and its separate successful run are preserved with the repaired evidence.

The runtime harness was enlarged after the verified build to fit the complete
1680 × 1120 scaled composition client. Original build input hashes are retained;
the exact replacement harness and its SHA are recorded separately in runtime
provenance. New captures use X11 1920 × 1400 and nested Wayland 1760 × 1280.

| Reference API | Linux interface and source behavior |
| --- | --- |
| `BleeckerSectionHeader` | Required `title`, optional `subtitle` with explicit `hasSubtitle` for present-empty versus omitted, and an `actions` component slot. Encode Sans 17 semibold title, Libre Franklin 12 subtitle, gap 3; trailing actions remain independently focusable. |
| `BleeckerDashboardSection` | Required `title`, subtitle/action properties and a default content slot, separated from the section header by 16. Content-height changes update the section's intrinsic height. |
| `BleeckerDashboardGrid` | Ordered `tiles` and required `tile` component. The delegate context exposes `tileData` and `tileIndex`. Defaults: minimum column width 260, spacing 16. Column count adapts to the offered width, cells share the available width, each row accommodates its tallest tile. |
| `BleeckerAppShell` | Required `sidebar`, `header` and `content` component slots. Sidebar content width defaults to 240 plus 16 padding on all sides; its intrinsic block is vertically centered, and a vertical separator precedes the main area. Header minimum height 64 with 24 horizontal padding; main content has 24 padding and a header separator. |
| `BleeckerFooter` | Default content slot and one-unit separator. Each flattened child receives 20 vertical padding and horizontal centering; no children leaves the separator alone. Inherited Libre Franklin 12 and secondary text color. Template labels inherit font/palette; `BleeckerText` supplies the measured source Text layout. |
| `BleeckerFeedItem` | Required author/timestamp and a default content slot. Small avatar 32, gap 12, body spacing 6 and vertical padding 8. Author is Encode Sans 13 semibold; timestamp Libre Franklin 11. |
| `BleeckerProgressStack` | Ordered segments with `id`, `value` and `color`, height default 8. Segment widths are `max(0, offeredWidth × value)`, with 2 between segments. Values are not normalized. The capsule covers the sum of those widths and gaps; its painted extent can exceed the allocated control width. |

The interfaces use native QML factories and content slots; generic Swift types
are not Linux requirements. The current dashboard-grid layout instantiates its
tile delegates eagerly. Large-grid virtualization, scrolling presentation and
equivalence with the rendered lazy source remain pending. This is an unfinished
case, not an approved platform exception.

Tile placement is explicitly controlled so fractional logical widths are retained
instead of rounded by Qt's layout engine. Changing the column count moves existing
tile delegates; it preserves the focused tile and its input state.

Source `.secondary` in the feed timestamp is a platform semantic color. The
candidate currently uses the shared secondary token; native capture must resolve
the actual rendered color before acceptance. No substitution or exception is
approved by this implementation. Measured native line boxes are 22 for each
section-title line, 16 for each feed-author line and 14 for the section's
present-empty subtitle. The text renderer exposes an optional logical `lineHeight`
for these measured cases; its default retains existing metrics.

The stacked-progress capsule is painted and clipped explicitly on both software
and OpenGL backends. Its renderer retains gaps after zero-width segments, negative
values clamp to zero, and overflowing values paint within the segment-sized capsule
beyond the offered control width. Empty segments paint no track. Rasterization
still requires comparison against Sabella.

`AvelinoCatalog --fixture composition` shows the seven candidates together.
`InstalledConsumer --composition` exercises the same composition through an
installed QML package. It invokes an action with pointer and keyboard input,
resizes through a two-to-one-column breakpoint and back, and checks that focus
survives reflow. The session harness captures this third independent window in
each X11/Wayland, software/OpenGL and scaling configuration. Input is synthetic;
physical-display and screen-reader checks remain separate.

The component suite also covers optional/present-empty subtitles, title wrapping,
action slots, ordered variable-height rows, collection mutation/empty state,
feed slot resizing, inherited footer typography/palette, shell allocation changes,
and rendered progress gaps/negative/overflow/parent-clipping/reset states at DPR 1 and 2.

References are `Layout.swift`, `Navigation.swift` and `Extended.swift` at the
pinned desktop revision `fe8a1d462fbd793d883fb92086a16aa2947e32c9`.
The original references and expected images are unchanged. Framework mechanisms:
[Qt 6.8 Repeater](https://doc.qt.io/qt-6.8/qml-qtquick-repeater.html)
and [Canvas](https://doc.qt.io/qt-6.8/qml-qtquick-canvas.html).
