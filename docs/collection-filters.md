# Collection filters and filter chips

`BleeckerCollectionFilters` and `BleeckerFilterChip` are desktop candidates from
`Extended.swift:78` and `DataDisplay.swift:53` at the pinned Sabella revision.
The observable criteria are a bound editable query, one clear notification,
Return forwarding, independent label/removal callbacks, caller-owned selection
and removal, disabled input, keyboard traversal, natural/wrapped chip sizing,
content resizing/removal, and installed consumption through both Linux sessions
and renderers. Exact images and full platform acceptance remain pending.

```qml
BleeckerCollectionFilters {
    width: 620
    query: model.query
    onQueryEdited: model.query = query
    onAccepted: model.search()
    content: model.hasEdition ? editionChip : null
}
Component {
    id: editionChip
    BleeckerFilterChip {
        text: "Edition"
        selected: model.editionSelected
        removable: true
        onClicked: model.editionSelected = !model.editionSelected
        onRemoveRequested: model.hasEdition = false
    }
}
```

The query aliases the normal search editor. `queryEdited` forwards its user edit
signal; clearing follows the same caller update path and restores editor focus.
`accepted` forwards Return. The caller supplies a `Component` through `content`;
a single root can contain multiple controls. Its natural width plus a 10-point
gap is reserved beside the expanding search field. With no content, the search
uses the full width. Height is the maximum of 40, the search's scaled height,
and the content height. Taller content vertically centers the search. Natural
slot height uses the Loader implicit dimension, with positioning on a separate
parent so replacement cannot feed position changes back into Loader sizing.
The regression exercises replacing tall content with a chip. The sizing
contract follows the [pinned Qt 6.8.3 Loader implementation](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quick/items/qquickloader.cpp).

A chip has separate Qt template buttons for the label and optional removal.
`clicked` and `removeRequested` only notify: neither changes `selected` nor hides
the chip. Its source typography is fixed Encode Sans medium at 12 logical pixels,
independent of text scale. Horizontal padding is 10, the removal gap is 6 and
its measured allocation is 10. Minimum height is 28. A constrained label wraps
and increases height; empty labels retain padding. Selected and unselected
backgrounds use the shared palette. Disabled descendants reject input.

The capsule clips through the owned CurveRenderer path in RHI sessions and the
[shared software adapter](content-clipping.md) in software sessions. Both use the
same capsule path; complete native clipping equivalence remains pending. Keyboard focus indicators, role/name queries
and synthetic input checks do not establish source-to-platform accessibility
or actual screen-reader acceptance. The removal icon is original Linux Canvas
geometry, tracked in `assets/filter-chip-symbols.json`; Apple artwork is not
redistributed. Glyph/distribution acceptance remains pending.

The [native proposal](../evidence/reference-proposals/collection-filters-20261014/proposal.json)
contains 180 captures: 128 chip cases, 44 collection cases and eight anchors.
Chip cases cover selection, removal, disabled, empty and constrained labels at
both appearances, text scales and DPRs. Collection cases cover empty content,
chips, selected/filled/disabled/narrow/long queries, actual clear/removal/activation
callbacks, and tall content at native measured DPR 2. The comparator checks query,
content, selected state and callback counts independently of pixels.

A clean external helper extraction/recompile/replay reproduced 170 of 181 files
byte-for-byte. Eleven images vary by at most one channel level; those differences
remain recorded without changing expected images or tolerances. The helper links
preserved source-verified objects and is not a fresh full Sabella compilation.
The archive retains the original preserved-reference toolchain record; the
separate tooling provenance records this helper preparation at `b8cb7db`. Current
macOS 27.0 (26A428), Xcode 27.0 and SDK 27.0 were verified. Apple source and
tooling remain outside this Linux-only repository.

`AvelinoCatalog --fixture collection-filters` provides the composed gallery;
`InstalledConsumer --collection-filters` exercises real caller updates, separate
actions, removal, disabled traversal, tall slots and Qt accessibility interfaces.
Physical input, real desktop compositor/display, native cache/color matching,
complete editing/RTL/input methods, custom-font wrapping and screen readers
remain pending. TV remains separate and requires a selected hardware target.
This UI library change has no backend, metrics or application configuration impact.

The [checksummed Linux candidate](../evidence/development/collection-filters/candidate.json)
preserves 180/180 matching root bounds and 0/180 exact images. All 2,888 Qt checks and 45 contract
checks pass, together with eight installed offscreen modes and 64 fresh
package-only virtual-session pairs. Eight session pairs exercise the new workflow.
Default/Basic/Fusion gallery PNGs at DPR 2 are byte-identical in both appearances.
All 1,510 preceding PNGs and complete metadata remain unchanged. No reference
pin, accepted image, tolerance or approved exception changes.
