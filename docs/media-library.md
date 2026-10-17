# Media library

The pinned desktop `BleeckerMediaLibrary` takes identifiable items, a minimum tile
width (default 160) and a caller-supplied tile view. Its body is a vertical lazy
grid with one adaptive column specification and 16-point horizontal and vertical
gaps. It adds no scroll view, tile presentation, selection, background or clipping.
Those belong to its caller. A Linux candidate uses retained caller components and
viewport-driven creation. Native mirror acceptance remains pending.

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

The [sealed candidate record](../evidence/development/media-library-20261017/candidate.json)
compares all 1,608 observed pairs: 864 match pixels, frames and lifecycle together;
992 match pixels, 1,288 match frames and 1,488 match native lifecycle. All 48
offscreen restore observations reproduce their initial candidate pixels. The
7,440 direct public sizing queries remain unobserved on Linux. No complete
component acceptance follows from these capture matches.

The candidate evidence keeps failures as well as successful checks. Fractional
column geometry, text measurement and lazy height estimates still differ from
the source. Actual gallery input exercises 14 controls through 24 states;
19 caller viewports match fresh isolated candidates, while five retained RTL
caption states differ. Virtual Wayland software window grabs also differ after restoring the
fractional-width fill case (`width-337`) at both standard and scaled settings. Observation mode saves those failed frames and
continues; strict comparison remains failed. Raw Qt inactive-painter warnings
remain preserved with their origin unresolved. These are open acceptance gates.

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
