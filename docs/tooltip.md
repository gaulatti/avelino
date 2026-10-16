# Tooltip source contract

The pinned `BleeckerTooltip` returns caller content with `.help(text)` and
`.accessibilityHint(text)`. It supplies no authored bubble, padding, font,
background, open state, timer, input handler or animation.
The [source investigation](../evidence/reference-investigations/tooltip-20261016/investigation.json)
preserves the closed wrapper and a real native help panel separately. Linux
implementation and complete mirror acceptance remain pending.

The closed corpus covers 21 fixtures in light/dark, text scale one/1.5 and
requested bitmap/display DPR one/two. Every one of the 168 groups has four
byte-identical images: public wrapper, separately probed wrapper, direct
`.help().accessibilityHint()` witness and unwrapped caller. The probe and witness
also have identical recorded geometry and state. Hint values include empty,
long, multiline, Unicode and bidi strings. Caller content includes controls,
empty and zero-sized views, hidden, oversized, inherited text, flat children,
explicit stacks, disabled and RTL contexts, parent font and foreground.

The wrapper introduces no closed-state layout or pixel change in these cases.
Two flat caller children overlap at the center of the test's ZStack, just as the
unwrapped children do; explicit horizontal and vertical stacks retain their own
layout. Empty content has no measured frame. Zero-size content retains a zero
frame. Hidden 200-by-80 content retains that size. An 800-point child and an
828-point button overflow the 640-point canvas without acquiring a wrapper clip.
These facts describe the measured parent context, rather than a new stack policy
for arbitrary callers.

A normal active test application exposes `Publish 0` with its help string in an
external accessibility inspection. An actual AX click advances its local caller
counter to one. Updating the hint changes the external AX Help value and retains
that caller at one, with one recorded mount and no disappearance. Before and
after body PNG files remain byte-identical. The helper's own
`NSAccessibilityProtocol` traversal exposes only a root group; it cannot establish
the absence of accessible children or reader acceptance.

A second test application initially places its own window beneath the actual
pointer. It receives genuine native mouse-enter events and presents an
`NSToolTipPanel`, without moving or synthesizing pointer events. The panel is
171 by 21 logical points, at actual backing DPR two, with a 342-by-42 captured
body. Its content view is `NSVisualEffectView`, containing
`NSCustomToolTipDrawView`; it is visible at window level 103 and is neither key
nor main. The popup reads “Publishes the selected edition.” Changing the source
hint to “Reviews the published edition” leaves this already shown panel's
pixels and size unchanged during the preserved observation. Accessibility hint
updates and the currently visible help panel therefore need separate handling.
This observation does not establish the next hover's text or a dismissal policy.

The public AppKit tooltip font query resolves `.AppleSystemUIFont` at 11 points;
its measured default line height is 13. This is measurement evidence, with no
font redistribution or substitution approval. Panel captures use
`NSView.cacheDisplay` on the body and theme frame. They establish neither full
compositor shadow/vibrancy nor physical-display equivalence. An
`NSLocalWindowSharingWindow` created by app screenshot inspection is an OS
sharing indicator, and is excluded from Tooltip identification.

Two expanded popup-harness attempts remain under `diagnostics/`. The first
preserves a missing-resource startup failure and an incomplete re-entry run.
The corrected run completes its planned stages but remains inactive throughout,
with no genuine mouse events and no native popup. Those observations cannot
establish empty-hint, disabled, dark, scale, re-entry or removal behavior.
The earlier actual popup capture remains the positive native evidence. Timing,
dismissal, keyboard behavior, full shown-popup configuration coverage and readers
remain pending.

The closed capture archive contains four source inputs and `inputs.json`, with
SHA-256 `25e65515bd19c88f9ba5b1546a5e3d2ac1cdfd59e726af00d2322c25ea645a39`.
A clean extraction rebuilds the unchanged 89-source library and reproduces all
673 output files byte for byte. A separate active-probe archive has SHA-256
`810513e431df9bd8d0a22f74c13857bdd912d694c2516c0fb20fc9501afcdd66`.
Its clean extraction builds both active helpers from the same unchanged source;
it makes no automatic live-popup pixel-replay claim. Archive locators, source
hashes and toolchain are in
[provenance](../evidence/reference-investigations/tooltip-20261016/tooling-provenance.json).
All Swift sources, native helpers and source archives remain external to this
Linux repository. Independent-machine archive availability is pending.

Run `python3 scripts/verify-tooltip-source.py` to audit complete closed coverage,
pixel identity, geometry, state retention, the actual panel, source-only inputs
and explicit diagnostic exclusions. Negative contracts run in References CI.
The reference pins, approved exceptions, expected images and zero-pixel
tolerance remain unchanged. The public repository's wiki remote is unavailable;
this contract is maintained in the repository.
