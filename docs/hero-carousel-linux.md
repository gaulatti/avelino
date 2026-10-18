# HeroCarousel Linux mirror

Implementation and acceptance are pending. The pinned desktop reference is
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

Next implement the library, catalog fixture and independent installed consumer,
then verify owned Qt presentation, identity, input/focus/accessibility, scaling,
offscreen and X11/Wayland behavior, packaging and strict visual comparisons.
Keep each acceptance gate pending until its own evidence proves it.
