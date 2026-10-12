# Desktop composition candidates

Seven additional APIs have Linux candidates. They remain verification-pending:
native fixtures, visual comparisons, complete behavior cases and accessibility
acceptance have not been established. These add implementation coverage, not
accepted mirror completion.

The [checksummed development evidence](../evidence/development/composition/candidate.json)
preserves four catalog images, 498 passing Qt checks and twenty-four installed
window/full-output pairs. Desktop coverage is 32 of 80 APIs started (40%), with
zero accepted components. The previous 25-API diagnostic comparison remains at
514 geometry matches and 40 exact matches of 724 cases. Its fresh raw comparison
outputs are local; the previous complete comparison artifacts remain committed.

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
| `BleeckerFooter` | Default content slot, separator, 20 vertical padding, inherited Libre Franklin 12 and secondary text color. Template labels inherit the control font/palette; raw QtQuick text binds them explicitly. |
| `BleeckerFeedItem` | Required author/timestamp and a default content slot. Small avatar 32, gap 12, body spacing 6 and vertical padding 8. Author is Encode Sans 13 semibold; timestamp Libre Franklin 11. |
| `BleeckerProgressStack` | Ordered segments with `id`, `value` and `color`, height default 8. Segment widths are `max(0, offeredWidth × value)`, with 2 between segments. Values are not normalized; overflow is clipped by the capsule. |

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
the actual rendered color before acceptance. The section header's present-empty
subtitle also needs measured native line-height evidence. No substitution or
exception is approved by this implementation.

The stacked-progress capsule is painted and clipped explicitly on both software
and OpenGL backends. Its renderer retains gaps after zero-width segments, negative
values clamp to zero, and overflowing values remain visible only inside the
capsule. Rasterization still requires comparison against Sabella.

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
and rendered progress gaps/negative/overflow/reset states at DPR 1 and 2.

References are `Layout.swift`, `Navigation.swift` and `Extended.swift` at the
pinned desktop revision `fe8a1d462fbd793d883fb92086a16aa2947e32c9`.
The original references and expected images are unchanged. Framework mechanisms:
[Qt 6.8 Repeater](https://doc.qt.io/qt-6.8/qml-qtquick-repeater.html)
and [Canvas](https://doc.qt.io/qt-6.8/qml-qtquick-canvas.html).
