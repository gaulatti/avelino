# RadioGroup source contract

The pinned desktop `BleeckerRadioGroup` has a preserved native source investigation.
The [record](../evidence/reference-investigations/radio-20261016/investigation.json)
covers 432 public RadioGroup captures, eight button anchors, 24 binding/input
traces, eight finite pointer grids, 11 pointer phase traces and 13,762 native
String identity pairs. A clean source-only extraction rebuilds the unchanged
89-file Sabella tree and the native helpers, then reproduces all 1,358 image and
metadata outputs byte for byte. This checkpoint adds source evidence; the Linux
control and its runtime/package/visual acceptance remain pending. Desktop coverage
stays at 57/80 started and zero fully accepted.

`Sources/Sabella/Controls.swift:219` accepts caller-owned `Binding<Value>`, an array
of `BleeckerSelectOption<Value>` and an orientation defaulting to vertical.
`Value` is `Hashable`. Options identify themselves by their value and carry a label
and `disabled` flag. The source makes one plain button per option, containing a
SwiftUI `Label` with `largecircle.fill.circle` when selected and `circle` otherwise.
Vertical layout uses a leading-aligned stack with spacing ten; horizontal layout
uses spacing 16. There is no explicit font, foreground, radio input, checked
accessibility trait, auto-exclusive group or arrow-key selection policy in this
implementation. Actual native keyboard and reader semantics still require testing.

Every enabled release invokes the binding setter with the original option value,
including a click on the already selected option. Empty string values are valid.
The owner may reject writes; the control must continue displaying the owner's
selection. Selections outside the option array are retained. External selection,
option labels/order/values/disabled flags, orientation and inherited font updates
emit no request. The raw traces exercise those updates on the same public control.

The native selected-value fixture starts with decomposed `e` plus combining acute,
while its first option carries precomposed `é`. It renders selected, and clicking
it requests the option's original precomposed spelling. Swift String identity uses
canonical equivalence. Case folding, compatibility ligatures, fullwidth characters,
nonbreaking spaces and zero-width joiners do not become equal through that rule.
The measured macOS runtime uses ICU 78.1 and Unicode 17. All 13,253 raw canonical
mappings compare equal in native Swift; 500 deterministic combining-mark pairs
and nine explicit string pairs retain positive and negative witnesses. Fourteen
separate `AnyHashable` probes record numeric, Boolean, optional and string type
boundaries; these do not imply that every generic `Value` has one portable encoding.

The [Linux diagnostic](../evidence/reference-investigations/radio-20261016/qt-string-identity.json)
normalizes the same strings with Qt 6.8.3's Unicode 16 data. It disagrees on 17
combining-mark ordering pairs. A plain `QString.normalized()` call cannot establish
native String identity across this corpus. The probe's C++/CMake sources, build
logs, image identity and native inputs are preserved alongside the report. No
production identity adapter is added by this source checkpoint.

At requested display scale two, the default vertical group is 72 by 68 points;
the horizontal group is 224 by 16. The default SF 13 title line is 16 points high,
with 15-point image frames and an eight-point icon/title gap. Parent Encode Sans
20 produces a 23-point icon and a 25.1-point row; bold 20 produces a 24-point icon
and a 25.6-point row. Requested primary size 0.3 resolves the title to size 12
while the image frame collapses to zero. Custom `bleeckerTextScale` one/1.5 leaves
all RadioGroup captures identical; explicit inherited font settings do affect them.
Base font probes do not establish actual fallback glyph runs or portable assets.

The icon's vertical position follows the title's cap region in the measured cases.
This relationship is inferred from preserved frames and Core Text cap metrics;
an earlier alignment-guide probe never queried its baseline closures. There is no
direct baseline measurement to claim. Empty titles retain line-layout space and
an icon/title gap. Empty option arrays have a measured zero-by-zero root. A
100-point horizontal proposal produces a 101-by-112 group: zero-width titles keep
five/six/seven line heights while their icons stay near the first line. The Linux
candidate must preserve wrapping and overflow behavior without inventing truncation
or a fixed row height.

Synthetic NSEvents reach the actual public control in an isolated borderless
window. The finite grids show active icon content and title rectangles with an
inactive gap. The unselected hollow icon responds at its center and at interior
rectangle corners outside the circle curve. A circular alpha/path hit test and a
whole-row rectangular hit test would both change these observed targets. Exact
sampled coordinates, font-dependent edges and hits/misses remain in the raw grids;
these samples do not define every unsampled edge.

Pointer-down and a 1.2-second hold emit no request; release emits one. Dragging
outside cancels it. Disabling the group or option, removing the pressed option,
reordering options under the stationary pointer, or changing orientation during
the press produces no release request in the measured traces. An external
selection change during the hold still permits the original enabled button's
release action. The before/down/up PNGs preserve paint separately from callbacks.

All 440 public captures match both the reconstructed button witness and the
instrumented `LabelStyle` witness byte for byte. The eight hosted public button
anchors also match the previously preserved Stepper anchors exactly, including
PNG bytes and component bounds. Existing expected images, source pins, tolerances
and exception approvals are unchanged. Native symbol artwork remains reference
evidence and is not installed as a Linux asset.

Captures use `NSHostingView.cacheDisplay` into explicit bitmap dimensions without
resizing. Windows are inactive, non-key and non-main, with actual backing scale
two. Requested SwiftUI display scale and bitmap DPR one/two are recorded separately;
physical DPR one is unverified. The accessibility diagnostic in six contexts
exposes only an `AXGroup` hosting view with no control children. It establishes
no individual-control role, checked trait, focus order or reader acceptance.

Run `python3 scripts/verify-radio-source.py` to audit raw hashes, complete capture
coverage, canonical identity, original payload spelling, binding ownership,
release/cancellation, finite grids, anchors and clean replay. Negative contracts
also run in References CI. Native source and tooling stay external to this Linux
repository. The source-only archive SHA-256 is
`99924f3161fe21b7883bbf01c5a95e1b425081881ac2cd9440af682b7453635a`;
its machine-local locator and individual source hashes are in
[tooling provenance](../evidence/reference-investigations/radio-20261016/tooling-provenance.json).
Independent-machine download remains pending. Exact fonts, symbols, frames, raster,
physical displays/input, keyboard/focus, actual reader behavior, Linux sessions and
the installed consumer remain acceptance work.
