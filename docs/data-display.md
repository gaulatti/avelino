# Data display and surface candidates

The initial data-display batch added four desktop candidates. Their complete
comparisons, behavior cases and runtime acceptance remain pending. Current
coverage is recorded in the [parity inventory](parity-inventory.json).

| Reference API | Linux interface and behavior |
| --- | --- |
| `BleeckerAvatar` | Required `name`, optional image `source`, sizes xs/sm/md/lg/xl = 24/32/40/52/72; first grapheme of the first two literal-space-separated words, uppercased; semibold Encode Sans at edge × 0.32; centered image cover crop inside a circle; muted background and one-pixel border |
| `BleeckerDataList` | `rows` in authoritative array order; required `rowContent` QML component; slot context exposes `row` and `rowIndex`; padding 10 above/below each row, separator after each row except the final one; Qt ListView delegates retain lazy creation in a finite viewport |
| `BleeckerTimelineItem` | Required `title` and `date`, `last`, default content slot; dot 9, connector 1, horizontal gap 12, body gap 4, bottom padding 18 except final item; title Encode Sans 14 semibold, date Libre Franklin 11, inherited content Libre Franklin 13 |
| `View.bleeckerSurface` | `BleeckerSurface` wraps a content slot without padding; continuous radius defaults to 12, configurable `radius`, card background/border, light-only deep-sea shadow opacity 0.055/radius 14/offset 5 |

The Linux composition interface uses QML components and slots. Timeline content
implemented with Qt control templates such as `QtQuick.Templates.Label` inherits
its font and palette. Raw QtQuick Text requires explicit font/color bindings.
Data-list callers supply an ordered array of row values and a component using
the documented slot context. The default list expands to its content height and
leaves interaction to an enclosing scroll view; a finite viewport can enable
ListView interaction. Other Qt model adapters and full scrolling presentation
remain pending rather than being inferred from this array fixture.

The painted text helper now exposes `wrapWidth` and `unwrappedWidth`. A negative
one wrap width preserves explicit lines; a nonnegative width enables Qt word
wrapping with grapheme-safe emergency breaks. Panel and timeline titles use their
allocated width and preserve their unwrapped intrinsic size for layout. Native
line breaks, bidi behavior, baselines and fallback faces still require comparisons.

DPR 2 rendering exposed a double-scaling defect: Canvas.Image already maps logical
coordinates to the window DPR. Applying another DPR transform enlarged the avatar
image and shared surface shadow. Both now paint in logical coordinates. The avatar
test compares the displayed corner to the unchanged background, asserts the exact
centered crop color, and verifies the original view returns when its image is removed,
at DPR 1 and 2. It does not assume that a software window snapshot has a transparent
background. The original CC0 `tests/consumer/avatar-wide.ppm` fixture has red/blue/green
stripes so a correct centered square crop contains only blue.

Emoji initials retain their Unicode grapheme sequence, but the current toolchain
renders missing glyph boxes for this fixture. Emoji/fallback assets remain
verification-pending; no font substitution is approved. Surface shadow calibration,
software rounded-content clipping, GPU masks and opaque/interactive slot geometry
also remain pending. Native avatar images and every size/theme/scale/font case are
still required before acceptance.

The component tests cover ten avatar size/theme combinations, eight Unicode/name
boundaries, image crop/reset, row order/mutation/empty state, lazy delegates,
interactive row content, inherited timeline typography, title wrapping, final-entry
connector/padding, panel wrapping and four surface radius/theme cases. The installed
consumer exercises these four candidates alongside the previous sixteen, including
pointer/keyboard row actions, tab order, and return to field editing. Its wider
fixture is captured on correspondingly larger virtual outputs to keep the complete
window visible at DPR 2.

Run `AvelinoCatalog --fixture data-display`. The check script captures both themes
at DPR 1 and 2. [The inventory](parity-inventory.json) keeps all cases and runtime
gates pending. Pinned sources are `Sources/Sabella/DataDisplay.swift` and
`Tokens.swift` at `fe8a1d462fbd793d883fb92086a16aa2947e32c9`.
Mechanisms: [Qt grapheme boundaries](https://doc.qt.io/qt-6.8/qtextboundaryfinder.html),
[ListView](https://doc.qt.io/qt-6.8/qml-qtquick-listview.html), and
[Canvas logical coordinates](https://doc.qt.io/qt-6.8/qml-qtquick-canvas.html#canvasSize-prop).

The remaining icon badge, metric, stat card and key-label APIs now have a
[separate native source investigation](data-metrics.md). Their Qt implementations
remain pending; native evidence does not increase candidate or accepted counts.
