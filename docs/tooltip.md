# Tooltip source contract

The pinned `BleeckerTooltip` returns caller content with `.help(text)` and
`.accessibilityHint(text)`. It supplies no authored bubble, padding, font,
background, open state, timer, input handler or animation.
The [source investigation](../evidence/reference-investigations/tooltip-20261016/investigation.json)
preserves the closed wrapper and a real native help panel separately. The Linux
candidate described below remains verification-pending.

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

## Linux adapter acceptance

The Linux adapter attaches to an existing Qt Quick item. It must leave that
item's geometry, parent, local state, focus and input delivery intact. Its hint
must reach the existing accessible descendants, update independently of any
already shown popup, and restore their descriptions when the adapter detaches.
Dynamic caller content must receive the hint without recreating the caller.

The presentation must use an owned Qt template, plain text, a separate tooltip
window and no focus grab. Only one adapter may present help at a time. Hover
departure, target removal and presentation-owner destruction must release the
popup without leaving window or accessibility state behind. These Linux
integration checks do not establish the corresponding unmeasured native
dismissal, timing or reader policies.

The first candidate uses the Qt template's default delay and timeout, and the
repository's bundled primary font at the measured 11-point logical size. The
source has an unresolved native system font. Light-body color measurements may
inform the candidate; unmeasured dark/vibrancy behavior and strict original-size
popup comparison must remain pending. No candidate choice approves a source
substitution, changes reference images or closes a native behavior gate.

## Linux candidate API

Attach help to the caller item without introducing a layout container:

```qml
BleeckerButton {
    id: publish
    text: "Publish"
    onClicked: controller.publish()
}
BleeckerTooltip {
    target: publish
    text: "Publishes the selected edition"
}
```

Both `target` and `text` are required. A null target detaches help. Empty text
does not open a popup. `visible` reports whether this adapter owns the currently
shown help. `presentation` exposes the shared implementation popup for runtime
inspection. One `TooltipHost` singleton owns a plain-text
`QtQuick.Templates.ToolTip` with `Popup.Window`, an owned background and no focus
grab. Caller hover, input, focus, layout and local state remain with the caller.
The shown text is retained until the next presentation; editing the hint updates
the accessible description independently.

`TooltipAccess` supplies the hint through the actual Qt accessible interface. A
read-only metadata layer overlays description reads while leaving native
description fields, writes, bindings, Action proxies and Behaviors intact. On
detach, reads return the current producer description. Dynamic native text and
control descendants are discovered without recreating them; ignored accessible
items are excluded. Competing help owners on one accessible element are rejected.
The integration uses private Qt metadata APIs and refuses compilation against a
version other than the pinned 6.8.3. The package evidence records private-header
and runtime-library hashes. A Qt upgrade needs explicit revalidation.

The regression checks query actual `QAccessibleInterface` names, roles and
descriptions. They cover native Action replacement and repeated attachment,
same-value explicit writes, description bindings and animated descriptions,
native Button/Text/TextInput/TextEdit, caller clicks, retargeting, removal and
owner-window hide/close. These are Qt integration results; screen reader output
remains a separate pending gate.

Run `InstalledConsumer --tooltip` from a separately built installed consumer,
or `AvelinoCatalog --fixture tooltip` from the installed catalog. The closed
reference adapters use `scripts/capture-tooltip-cases.py`; compare their original
physical pixels, caller geometry and state with
`scripts/compare-tooltip-captures.py`. The comparison never resizes images or
changes tolerance. The standard Linux/package/display-session scripts include
the Tooltip fixture. Complete shown-popup coverage, native font, timing,
dismissal, dark appearance, vibrancy, physical input and reader acceptance remain
pending.

## Candidate evidence

The [sealed candidate](../evidence/development/tooltip/candidate.json) records 168
closed attached/bare pairs across the eight source profiles. Every pair is
byte-identical, and all 336 PNGs retain the preliminary candidate's pixels after
the accessibility integration correction. Strict native comparison matches 40
closed bodies exactly, 144 caller-frame sets and all 168 initial states. The
three frame-mismatch groups use unresolved inherited system fonts. These closed
body results do not accept the help popup.

A fresh installed package passes 26 independent consumer modes and 115 catalog
captures; all 111 preceding gallery PNGs and complete metadata remain byte-identical.
The runtime-only image has the same 119 installed files and five checked Qt
private-header/library inputs as the producer, with producer source/build trees
absent. All eight Tooltip virtual X11/Wayland, software/OpenGL and standard/scaled
profiles pass. Their separate popup, retained shown pixels, caller state, focus,
actual Qt accessibility interface and typed hint binding are recorded alongside
whole-output captures. Physical displays, input and readers remain pending.

Later CI exposed interference between QTest's synthetic pointer and the idle
native compositor cursor. The [preserved diagnosis](../evidence/development/tooltip-pointer-isolation-20261016/README.md)
reproduces a native Wayland Leave when the tooltip maps beneath that other
cursor, despite the synthetic pointer remaining over the caller. The display
harness now retains Xvfb state, parks and checks the native cursor outside the
clients, and records its position. Thirty repeated processes using the actual
failed CI installation pass the original retained-pixel assertion after this
isolation. The complete 224-session matrix and eight executable-only Tooltip
profiles also pass. This does not establish native dismissal or physical-input
parity.

A separate light DPR-two/text-scale-one profile captures the default popup body
at 314 by 42 physical pixels. The native body is 342 by 42. The
[body comparison](../evidence/development/tooltip/popup-comparison/comparison.json)
refuses resizing and remains failed. The primary-font substitution, body width,
glyph/radius raster and full compositor appearance are unapproved.

The earlier setter-based accessibility prototype damaged native Action proxies.
An interceptor-only revision then rejected existing animated-description
metadata. Both failures are preserved; the final read-only VME layer passes
native Action, same-value write, binding and Behavior regressions at both DPRs.
A separate Wayland/OpenGL scaled fixture failure caught initial palette
animation: the fixture now disables motion before changing the palette. Raw
before/after images remain preserved, and the final matrix passes the same
pixel-equality check. No expected image, pixel tolerance, pin or approved
exception changed.
