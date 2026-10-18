# HeroCarousel Linux mirror

Implementation and acceptance are pending. The pinned desktop reference is
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`, `Sources/Sabella/Extended.swift:90–94`.
See the [native investigation](../evidence/reference-investigations/hero-carousel-20261018/README.md)
for raw captures, sizing queries, source-rebuild receipts and input limitations.

The reference takes identifiable items and arbitrary caller-supplied slides. Its
horizontal lazy stack allocates viewport width per slide with a 16-point gap,
hides scroll indicators and aligns scrolling to one view at a time. Fixed-width
content remains centered within its allocation. Preserve caller identity,
appearance, font, foreground and disabled state; add no autoplay or navigation UI.

The first native investigation covers 160 closed contexts and 7,200 direct sizing
queries. Public/probed/literal witness images, geometry and caller lifecycle
agree. An additional 1,080 queries distinguish prior-placement dependence from
window-width dependence. Ideal width after layout can reflect the complete
document extent rather than a constant or the current parent width. Linux must
account for this history instead of hardcoding the observed 632-point result.

Accessible scroll-to-end and scroll-to-start work in the native probe. Its first
slide's state survives disappearance/reappearance. No wheel event was delivered
by the available page-scroll request, so native wheel/momentum/settling and
reader behavior remain unproven. The source-only package replay is byte-exact on
the current machine; independent-machine availability is still pending.

Next implement the library, catalog fixture and independent installed consumer,
then verify owned Qt presentation, identity, input/focus/accessibility, scaling,
offscreen and X11/Wayland behavior, packaging and strict visual comparisons.
Keep each acceptance gate pending until its own evidence proves it.
