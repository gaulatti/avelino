# HeroCarousel Linux mirror

The Linux candidate supplies a horizontal scrolling viewport with retained caller
slides. Mirror acceptance remains pending. The pinned desktop reference is
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`, `Sources/Sabella/Extended.swift:90–94`.
See the [native investigation](../evidence/reference-investigations/hero-carousel-20261018/README.md)
for raw captures, sizing queries, source-rebuild receipts and input limitations.

The reference takes identifiable items and arbitrary caller-supplied slides. Its
horizontal lazy stack allocates viewport width per slide with a 16-point gap,
hides scroll indicators and uses view-aligned scrolling with `.always` limit
behavior. The exact per-interaction limit remains pending; Apple's
[single-view guarantee](https://developer.apple.com/documentation/swiftui/viewalignedscrolltargetbehavior/limitbehavior/alwaysbyone)
belongs to `.alwaysByOne`, which the pinned source does not use. Fixed-width
content remains centered within its allocation. Preserve caller identity,
appearance, font, foreground and disabled state; add no autoplay or navigation UI.

The [history supplement](../evidence/reference-investigations/hero-carousel-history-20261018/README.md)
records a safe runtime value observation on macOS 27.0 build 26A428: `.always`
reflects the same value as `.alwaysByOne`, while `.alwaysByFew` differs. That
host-specific result supports investigating Qt's `SnapOneItem`; it does not
prove identical gestures or change the pinned source's `.always` spelling.

The first native investigation covers 160 closed contexts and 7,200 direct sizing
queries. Public/probed/literal witness images, geometry and caller lifecycle
agree. An additional 1,080 queries distinguish prior-placement dependence from
window-width dependence. Ideal width after layout can reflect the complete
document extent rather than a constant or the current parent width. Linux must
account for this history instead of hardcoding the observed 632-point result.

Accessible scroll-to-end and scroll-to-start work in the native probe. Its first
slide's state survives disappearance/reappearance. No wheel event was delivered
by the original page-scroll request. A later coordinate-based horizontal
request delivered zero-delta wheel events; vertical wheel events did not move
the horizontal viewport. Native wheel/momentum/settling and
reader behavior remain unproven. The source-only package replay is byte-exact on
the current machine; independent-machine availability is still pending.

Two additional typed, animation-suppressed native histories cover 32 steps at
light appearance, text scale 1 and DPR 1. Caller instance 1 survives scrolling,
reordering, removal, empty data, consecutive 1-second and 3-second idle intervals,
restoration and subsequent scrolling. Fitted height follows the logical first
slide, remaining 80 after visiting or enlarging a later slide, then becoming 200
when that enlarged slide moves to index zero. Empty data fits to zero. This does
not establish retention under memory pressure or other lazy timing histories.

The native geometry preferences retain stale frames for hidden/removed slides.
The portable consumer witnesses preserve those raw maps and explicitly label
the active-frame projection; the history helper did not measure the caller
wrapper frame. Full geometry cannot be accepted from that projection. The native
history helper's independent source availability also remains pending.

Validate the supplementary evidence and exact portable projection with:

```sh
python3 scripts/verify-hero-carousel-history.py
python3 scripts/generate-hero-carousel-witnesses.py --check
```

The public QML API takes `items` and a required `slide: Component`. Items normally
have an `id`; `itemIdentity: value => value.key` supports other data shapes.
Identities use the shared typed-primitive and pinned Unicode normalization
contract. Duplicate identities, unsupported shapes and callback failures fail
explicitly. Assign a new array to update data. Caller objects receive
`slideData`, `slideIndex` and `slideActive`, which may be declared as required
properties. `slideAt(index)` returns a previously created caller or null.

```qml
BleeckerHeroCarousel {
    width: 337; height: 180
    items: [{id: "first", title: "First slide"}]
    slide: Component {
        Rectangle {
            required property var slideData
            implicitWidth: 10; implicitHeight: 80
            BleeckerLayout.minimumWidth: 0
            BleeckerLayout.idealWidth: 10
            BleeckerLayout.fillsWidth: true
            color: BleeckerTheme.palette.sea
        }
    }
}
```

Supply a finite viewport width. An explicit height bounds the viewport; otherwise
`implicitHeight` follows the logical first slide's measured height. Flexible
callers use `BleeckerLayout.minimumWidth`, `idealWidth` and `fillsWidth`; fixed
content remains centered. Allocations align their scene origin to device pixels
before caller centering, preserving fractional caller sizes and offsets.
`documentWidth` reports the full extent, and the attached layout exposes it as
the current ideal width. Complete direct native proposal replay is still pending.

`itemCount`, `instantiatedCount` and `activeCount` distinguish data, caller creation
and viewport activity. Created callers survive offscreen movement and removed
identifiers remain retained until the slide factory or control is destroyed.
This follows the measured removal/restore histories; native retention under
memory pressure and complete lazy timing remain unverified. The presenter
disconnects geometry/window observers before destruction. Layout also preserves
its pixel ratio while a caller callback detaches the owner; the earlier null-window
teardown failure is retained in the development evidence.

Qt owns dragging, velocity and `SnapOneItem` targets through the horizontal
`ListView`; the presenter owns the actual caller objects. RTL reverses physical
placement while preserving logical identities and target indices. Arrow keys do
not change carousel selection. Caller buttons retain their own Qt keyboard,
pointer and accessibility behavior. No navigation buttons or autoplay are added.

`AvelinoCatalog --fixture hero-carousel` exposes four caller slots, data edits,
reorder, empty/restore, width, RTL, theme, scale and disabled operators. Isolated
definitions use `carouselWidth`/`carouselHeight` beside the 640 by 400 capture
canvas. The installed consumer's `--hero-carousel` command refuses strict
acceptance; `--hero-carousel-observe` records differences while structural
failures remain fatal. Add `--hero-carousel-gallery` and a fresh
`--hero-carousel-report` prefix to exercise the actual operators and caller input.

The [Linux development evidence](../evidence/development/hero-carousel-20261018/README.md)
preserves seven source attempts, including the failed teardown attempt, a fresh
independent installed consumer, eight offscreen contexts and eight virtual
X11/Wayland software/OpenGL profiles. Eight gallery contexts each pass 17 operator
clicks and 21 observed states, actual caller Tab/Space activation, arrow-key
non-navigation, and disabled pointer/Tab exclusion. The installed catalog and
consumer render their initial gallery identically. These checks use synthetic Qt
input; reader and physical input acceptance remain separate.

All 192 full images and observed frame/lifecycle pairs remain in strict comparison:
108 images, 184 active-frame sets and 168 lifecycle records match; 84 match all
three together. The 32 history images and active-frame sets all agree, but only
eight history lifecycle records agree. Native SwiftUI transiently realizes an
additional slide during width changes; no artificial lifecycle events hide that
difference. Eight inherited system-font frame sets differ. Full history geometry,
font/raster, sizing, lazy and gesture timing, readers, physical displays/input,
and independent-machine acceptance remain pending. No mask, resizing, tolerance
or exception is used.
