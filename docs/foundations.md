# Surfaces and layout candidates

This batch implements seven pinned desktop APIs. Every entry remains
verification-pending; native reference images and complete visual, accessibility,
scaling, and runtime acceptance are still required.

| Component | Linux interface and behavior |
| --- | --- |
| `BleeckerSeparator` | `vertical`; one logical pixel on the narrow axis, palette border color; caller supplies the long axis |
| `BleeckerSkeleton` | Caller supplies dimensions; `radius` defaults to 7; muted fill pulses between opacity 0.9 and 0.45 over two 900 ms legs |
| `BleeckerBauhausBackground` | Fills its allocated rectangle; clipped circle and band use the pinned proportional geometry and opacity 0.16 |
| `BleeckerProgress` | `value`, `size` (`sm`, `md`, `lg`), `variant` (`default`, `success`, `warning`, `destructive`), `accessibleName`; heights 4/7/10, clamped fill, leading alignment, 200 ms value transition |
| `BleeckerButtonGroup` | Default content slot, `spacing` defaults to 8; vertically centered children retain Qt layout and input behavior |
| `BleeckerHeader` | Required `leading`, `center`, `trailing` QML components; two flexible spacers; minimum height 56 |
| `BleeckerPanelLayout` | Required `leading`, `content`, `trailing` QML components; side widths default to 240/300; two separators and a flexible center |

The progress presentation owns both capsules and their colors through an internal
Qt Quick `ProgressBar` template. Qt supplies progress semantics, clamping, and
mirroring. No host style supplies its visual delegates. QML component slots are
the Linux composition interface; Swift view-builder API shapes are not required.
Panel slots receive their allocated width and height. Header slots retain their
implicit dimensions; the container grows for tall content.

Skeleton motion stops when hidden. The reduced-motion/capture setting freezes its
initial opacity of 0.9 and disables progress transitions. Native motion timing,
hide/show behavior, reduced-motion correspondence, RTL, constrained compositions,
and each visual state still need source/session evidence before acceptance.

The token generator now constructs Qt color values for canonical CSS `rgba()`
colors. Qt does not parse that CSS string syntax as a color. The neutral JSON
and pinned Bleecker source stay unchanged; border/input alpha remains 0.08 rather
than being rounded to an eight-bit hexadecimal alpha in the generator.

`tests/components/tst_foundations.qml` covers both themes, both separator axes,
all twelve progress size/variant combinations with boundary values and resizing,
RTL fill, value transitions, skeleton visibility/motion, background proportions,
group spacing/alignment, header slot replacement, and panel resizing. These tests
run at DPR 1 and 2. They establish implementation behavior, not image parity.

Run the gallery with `AvelinoCatalog --fixture foundations`, optionally `--dark`
or `--text-scale 1.5`. `scripts/check-linux.sh` captures its light/dark appearance
at DPR 1 and 2 alongside the existing button matrix. The independent installed
consumer exercises all seven components, grouped keyboard activation/tab order,
and returns focus to editing before its window/session captures. The display
harness records these checks separately from visual and accessibility acceptance.

Sources: pinned `Sources/Sabella/Surfaces.swift`, `Feedback.swift`, `Buttons.swift`,
and `Layout.swift`, linked per entry in [the parity inventory](parity-inventory.json).
Framework mechanisms: [Qt ProgressBar](https://doc.qt.io/qt-6.8/qml-qtquick-controls-progressbar.html)
and [Qt RowLayout](https://doc.qt.io/qt-6.8/qml-qtquick-layouts-rowlayout.html).

The [button group slot investigation](button-group-layout.md) now covers 23
source cases across 184 contexts. Groups retain hidden-child allocation, flatten
content slots, preserve fractional widths and center the fitted row in a caller
proposal. Negative spacing can place later children outside the fitted extent.
The focused geometry check does not close strict pixel, physical or reader gates.
