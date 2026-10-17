# Media library

The pinned desktop `BleeckerMediaLibrary` takes identifiable items, a minimum tile
width (default 160) and a caller-supplied tile view. Its body is a vertical lazy
grid with one adaptive column specification and 16-point horizontal and vertical
gaps. It adds no scroll view, tile presentation, selection, background or clipping.
Those belong to its caller. A Linux candidate uses retained caller components and
viewport-driven creation. Native mirror acceptance remains pending.

Library teardown disconnects window and owned-caller geometry observers before
the derived library state is destroyed. Qt's base-item teardown can emit those
signals while detaching the visual tree; they must not reenter library methods
after its destructor has run. Caller actions may remove their own tiles, and an
attached grid may be destroyed with live tiles. Both paths have Qt regression
coverage. Caller contexts continue to outlive their tiles during deferred removal.

The QML API takes an `items` array and a required `tile: Component`. Each item
normally has an `id`; `itemIdentity: value => value.key` can supply the identity
for another data shape. Identities are typed primitives, with canonical Unicode
string equality using the library's pinned normalization facts. Duplicate keys,
unsupported identifier shapes and callback failures fail explicitly. Changing
the array updates existing tiles by identity, while removing an item destroys
its retained state. Mutate data by assigning a new array.

Caller tiles receive `tileData`, `tileIndex` and `tileActive` through their
creation context. They may declare these as required properties. `tileActive`
tracks viewport participation; it does not override the caller's own `visible`
property. `itemAt(index)` returns a previously created tile or null, and the
read-only `itemCount`, `instantiatedCount` and `activeCount` distinguish data,
creation and visibility. `contentHeight`, `columns` and `columnWidth` describe
the current layout. The caller owns any surrounding `Flickable` and its clipping.
Content-height changes notify the caller before viewport activity is updated.
If an auto-height caller recenters the grid, activity waits for its settled
viewport. A visible tile therefore retains its appearance count during reflow.

```qml
Flickable {
    width: 460; height: 100; clip: true
    contentWidth: width; contentHeight: library.contentHeight
    BleeckerMediaLibrary {
        id: library
        width: parent.width
        items: [{id: "first", title: "First edition"}]
        tile: Component {
            BleeckerText { required property var tileData; text: tileData.title }
        }
    }
}
```

The minimum tile width defaults to 160 and the gaps remain 16. A caller's fixed
width can overflow its column. Flexible tiles can use
`BleeckerLayout.minimumWidth`, `idealWidth` and `fillsWidth`; composed text tiles
can forward `BleeckerLayout.proposedWidth` to a nested label with
`label.BleeckerLayout.propose(width)`. Width and height measurements must be
finite and nonnegative. Invalid public data is rejected separately from the
captured native numeric edge cases. The candidate preserves the observed
single-column result for nonfinite minima and explicitly fails at minimum -16.

`AvelinoCatalog --fixture media-library` exposes four caller tile types, edits,
reordering, empty/reset, adaptive widths, the caller viewport, RTL, theme, text
scale and disabled state. Isolated source definitions use `libraryWidth` and
`libraryHeight` to keep caller proposals separate from the 640 by 400 capture
window. The installed consumer's `--media-library` mode fails strict acceptance
while sizing remains unobserved; `--media-library-observe` records differences
while still failing structural errors. `scripts/capture-media-library.py` keeps
all 496 closed contexts, 104 successful edges, eight isolated fatal edges and
all 1,008 retained-history steps. The strict comparator adds no tolerance.

The [formatted-text correction record](../evidence/development/media-library-caption-20261017/candidate.json)
compares all 1,608 observed pairs: 1,008 match pixels, frames and lifecycle together;
1,168 match pixels, 1,288 match frames and all 1,608 match native lifecycle. All 48
offscreen restore observations reproduce their initial candidate pixels. No
previously passing pixel, frame, lifecycle, state or retained-raster observation
regressed from the [earlier candidate](../evidence/development/media-library-20261017/candidate.json),
which had 864 complete matches and 1,488 matching native lifecycle observations. The
7,440 direct public sizing queries remain unobserved on Linux. No complete
component acceptance follows from these capture matches.

Historical producer verification uses the frozen build manifest, immutable Git
objects and archived source overlays. Generated Python bytecode present during
capture remains preserved as input provenance; replay verifies those archived
bytes independently of the checkout's generated files.

The candidate evidence keeps failures as well as successful checks. Fractional
column geometry, text measurement and lazy height estimates still differ from
the source. Actual gallery input exercises 14 controls and 23 XTest clicks through
24 states; every caller viewport now matches its fresh isolated candidate.
The [earlier reflow record](../evidence/development/media-library-reflow-20261017/candidate.json)
keeps the four failed RTL states (`width460`, `minimum160`, `light`,
`scale-restored`) and their original pixels. Earlier inactive-painter warnings
also remain preserved; the current eight capture contexts contain none.

A Qt 6.8.3 trace found a retained line width of `101 + 1/3` after the item grew to 103 and
222. Its [width-growth shortcut](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quick/items/qquicktext.cpp#L2489)
reuses the earlier layout and translates its glyphs. Wrapped `BleeckerText`
now invokes the public [forceLayout method](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quick/items/qquicktext.cpp#L3167)
when its width changes. The regression reproduces two pixel failures against the
earlier module, in right-aligned `Tile 2` and centered `Tile 5`, and passes all
14 text/alignment rows at DPR 1 and 2 with the correction. Native sizing, complete
raster, font, physical display/input and reader acceptance remain pending.

The catalog and independent consumer use the same fixture-only `MediaTileFill`
for caller fill and button backgrounds. It preserves logical item geometry and
snaps the two scene-space edges independently at the effective display scale,
including fills narrower than one pixel. An alpha-capable texture avoids the
fractional-edge background gap observed under virtual Wayland software rendering.
The grid still supplies no tile styling. A painted-item trial lost subpixel-width
fills and a texture ownership trial crashed; both failed attempts and their input
bytes remain in the correction record. Qt's [exact 6.8.3 painted-item implementation](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quick/items/qquickpainteditem.cpp)
and [texture-node ownership implementation](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quick/scenegraph/util/qsgsimpletexturenode.cpp)
are recorded as investigation sources.

All eight current virtual X11/Wayland profiles preserve the six retained restore
cases, including `width-337`, for 48 exact restore observations. They use software
rendering, including the OpenGL profiles, and do not establish physical display,
hardware acceleration, real input or reader acceptance. Fifteen focused checks
pass at each DPR, including the native-backed reflow regression; all 33 Qt targets,
34 installed modes and 139 catalog captures pass. All 139 previous catalog images
and complete metadata remain byte-identical.

The [native source record](../evidence/reference-investigations/media-library-20261017/investigation.json)
uses the unchanged public component, a transparent geometry probe and the literal
pinned grid expression. Its 62 definitions cover empty and populated data, exact
column thresholds and fractional widths, minimum widths including zero, variable
row heights, fixed tiles wider than columns, text and button tiles, long labels,
caller font/color/disabled state, RTL and enclosing scroll views. All 496 closed
contexts span light/dark appearance, Bleecker text scales 1/1.5 and requested
bitmap/display scales 1/2. The actual native window backing scale remains two.
All 1,488 closed PNGs agree across the public/probed/literal branches, as do the
496 geometry and lifecycle witnesses.

The measured grid begins its second column at width 336 with the default
160-point minimum and 16-point gap. Rows center shorter tiles vertically within
the tallest tile. Fixed-width caller tiles center in a column and may overflow it.
RTL reverses column placement. The offered width, including widths narrower than
the minimum, remains distinct from the width of an individual tile.

At zero offered width the grid reports zero height and has no active tile views.
Returning to a positive width retains previously created tile state. Updating
values or reordering the same identifiers also retains state; removing all items
and restoring them creates new tile state. The probes observe caller wrapper
state, not SwiftUI's internal view storage. String identifiers include canonical
Unicode equivalents and distinct `ss`/`ß` values; broader generic identity contexts
remain pending.

An enclosing scroll view changes which rows are created. The native grid estimates
the height of rows it has not measured, and that estimate can change after
scrolling or waiting without a data change. The source traces keep the actual
visible item sets, row frames, wrapper state, callbacks and height estimates.
A Linux implementation must preserve lazy behavior and retained identities; an
eager repeater with a column-count formula does not establish this contract.
Apple documents the distinction between a [lazy grid and an eager grid](https://developer.apple.com/documentation/swiftui/lazyvgrid).

Direct layout queries omit the caller's fixed frame and scroll wrapper. Fifteen
zero, unspecified, finite, mixed and infinite proposals run in each context and
each branch, for 22,320 queries. Responses include lazy height estimates and are
not interchangeable with the final laid-out frame. Of 496 query contexts, 495
agree across all three branches. In `text-red`, light/text1/DPR1, the public
unspecified-width height is 208 while the two witnesses return 264. All three
responses remain preserved. This is an unresolved sizing witness difference,
not an accepted replacement for the public result. See Apple's
[proposal contract](https://developer.apple.com/documentation/swiftui/proposedviewsize).

Six retained definitions exercise 21 steps in each context: value edits, Unicode
identifier representation, reorder, insertion/removal, minimum width, size,
appearance, text scale, direction, disabled input, empty/reset, zero width,
programmatic scrolling, controlled waits and actual pointer delivery. The two
waits add 0.2 and 1.0 seconds in the scrolling case. The button caller records
actual callbacks; disabled input is kept separate from successful activation.
Native keyboard focus, animation timing, physical input and actual reader
behavior remain unverified.

Fourteen negative or nonfinite minimum-width/caller-frame inputs run in 112
isolated processes. A minimum of exactly -16 traps with signal 5 in all eight
contexts. The other 104 processes complete and retain their framework warnings,
images and geometry. Minimum NaN and either infinity produce one column rather
than the default minimum's two columns at width 460. Negative caller width
collapses the grid, while NaN/positive-infinite caller width uses the parent
offer. Invalid caller height can leave the grid drawing beyond a zero-height
outer frame. These are recorded native outcomes, not an approved Linux input
policy or permission to replace invalid values with the default minimum.

The capture tools and source-only build inputs stay outside the Linux tree.
The first full capture uses a previously source-built module. A fresh extraction
and build of all 89 unchanged pinned source files reproduces every one of the
4,931 image/metadata outputs exactly, including the sizing disagreement. All 112
edge-process outcomes repeat, including the eight native traps. The final
source-only artifact contains ten input files and no compiled library; earlier
pilot helper versions are preserved in a separate checksummed artifact. Their
download and independent-machine replay remain pending.

Source pins, expected images and tolerances remain unchanged; no exception or
mirror baseline is approved. Run `python3 scripts/verify-media-library-source.py`
to recompute the source evidence. A native reference investigation is not an
accepted Linux component.
Run `python3 scripts/verify-media-library-caption.py` to recompute the current
media comparisons, all 3,768 font/pill pairs, archived restore images and
historical regression guards. The font/pill native pixels remain byte-identical
to their earlier candidates; existing native mismatches remain failed.


The corrected package also exercises eight virtual font and eight virtual pill
profiles across X11/Wayland, software/OpenGL and standard/scaled settings. These
profiles preserve the separate physical display, input, acceleration and reader
gates. Auxiliary captures and metadata are stored in the formatted-observations
archives with `font-captures/` and `pill-captures/` member prefixes.
