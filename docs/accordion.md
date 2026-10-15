# Accordion candidate contract

The reference is `BleeckerAccordion` in `Sources/Sabella/Navigation.swift:190` at
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`. It owns its expansion state after
initialization and inserts/removes its caller-provided content conditionally.
The Linux candidate remains verification-pending.

The observable criteria cover initial closed/open states; subsequent changes to
the initializer value without replacing internal state; title and content updates;
empty, zero-size, single and multiple content rows; content destruction and state
reset on reopening; header title/spacer/chevron pointer hit regions; held/canceled
presses; disabled input; keyboard and real Qt accessibility actions; focus during
content removal; ordinary/narrow/intrinsic/RTL layout; light/dark appearance;
text/display scaling; motion/reduced-motion behavior; owned clipping and border;
and independently installed catalog/consumer runtime in separate X11/Wayland
software/Mesa sessions. Source keyboard, exact pixels/assets, physical input and
actual screen-reader acceptance remain separate gates.

The QML adapter uses `title`, `initiallyExpanded` and a nullable Component
`content` slot. `expanded` is inspectable and read-only. The initializer is read
once when the control is created. A null content slot means source `EmptyView`;
a zero-size Item remains an explicit view and retains the source stack gap.
A Loader creates the slot when expanded and destroys it when collapsed; a
caller-owned component factory supplies each new subtree. Multiple source content
rows are represented by a caller Column with the measured source stack spacing.
The control owns the complete header/button, chevron candidate, background,
border, clipping, transition and native Qt input/focus/accessibility mechanics.
No system symbol equivalent, raster tolerance or exception is approved.

```qml
BleeckerAccordion {
    width: 320
    title: "Edition details"
    initiallyExpanded: true
    content: Column {
        width: parent.availableWidth
        spacing: 10
        BleeckerTextField { width: parent.width; placeholderText: "Edition name" }
    }
}
```

The field above is private to each expansion and resets on reopening. Bind it to
caller-owned state when that state should survive removal. Changing
`initiallyExpanded` afterward does not control the existing accordion's state.

The factory parent exposes `availableWidth`, the content width proposed by the
accordion. A factory root can bind its width or text wrapping to that value;
unconstrained roots retain their own size. The source gap is ten units, padding
is fourteen and radius is the existing UI token (seven). The header uses fixed
14-unit primary semibold text, independent of the custom text-scale environment.

Measured plain-header opacity is 0.5 when disabled and 0.75 when held. The inherited
symbol font resolves to the native system face at 13 units; the original rotated
chevron remains unaccepted. Source image-frame probes cover DPR 1 through 3,
including fractional scales. The source default rounded contour agrees with the
existing continuous-surface geometry. The Linux keyboard cue uses the existing
ring/radius tokens; source focus presentation remains pending. Source animation
phases are not established by settled captures; the Linux transition uses the
source 200 ms ease-out duration and the existing reduced-motion theme.

The [native source proposal](../evidence/reference-proposals/accordion-20261014/proposal.json)
contains 184 accordion cases plus eight button anchors. All 193 output files
replay byte-for-byte. The [Linux candidate](../evidence/development/accordion/candidate.json)
records 192/192 source root bounds and 0/192 exact images. Every post-action expansion, mount/unmount count, private
counter value and subsequent title/initializer/content value matches separately
from pixels. Both source and Qt reject the blank header spacer, accept the title
and chevron, preserve constructor ownership and reset private content on reopen.

All 3,214 Qt checks, 64 contracts, eight pagination and three slider invalid-startup
refusals pass. Thirteen installed offscreen modes, 104 package-only virtual-session
pairs and 63 installed-catalog captures pass. The accordion's eight virtual pairs
check actual Qt accessibility actions, disabled rejection, focus restoration,
normal inside/outside editing, private-state reset and later producer updates.
An existing pagination resize check was repaired to await exact frame geometry
with a bounded failure instead of a fixed 20 ms delay; the full 104-pair matrix
was rerun. Numeric expectations and tolerances are unchanged. A temporary-package negative
control rejected a deliberately wrong width with status 160.
Basic/Fusion/default gallery PNGs match; all 2,782 preceding PNG/full metadata pairs
are unchanged. Scope is 43/80 desktop APIs started, with none accepted. Source pins,
accepted captures, tolerances and exceptions are unchanged. Exact symbols/pixels,
source keyboard/focus/motion/touch, broader generic composition/font/script
contexts, physical input/display and actual readers remain pending.

The existing rounded-content renderer is reused. Its software path's rectangular
clipping and the full GPU/physical clipping boundary remain pending acceptance;
root bounds and interior-slot cases do not close arbitrary overflow/corner cases.
This is a native-only control; no backend, metrics, configuration or TV changes.
