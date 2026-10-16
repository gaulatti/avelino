# Stepper source contract

The pinned desktop `BleeckerStepper` has a preserved native source investigation;
its Linux implementation is still pending. The
[record](../evidence/reference-investigations/stepper-20261016/investigation.json)
covers 336 public Stepper captures, eight public button anchors, 25 action traces,
ten pointer phase traces, 126 integer formatter witnesses in seven locales, and
nine native fail-fast cases. A clean extraction rebuilds the unchanged 89-file
Sabella source tree and four helpers, then reproduces all 1,168 output files byte
for byte. This is source evidence, with no mirror acceptance or approved exception.

`Sources/Sabella/Controls.swift:239` defines equivalent unlabeled and labeled
initializers with caller-owned `Binding<Int>`, a closed range, `step` defaulting to
one, and `displayOffset` defaulting to zero. All integer inputs are signed 64-bit.
Preserve exact decimal strings across JavaScript boundaries outside its safe
integer range. The initial value is not clamped; values outside the range still
render. Equal bounds disable both actions only when the value equals that bound.

Decrement is enabled when the value is greater than the lower bound; increment is
enabled when it is less than the upper bound. An enabled decrement evaluates
`value - step` before applying the lower clamp. Increment evaluates `value + step`
before applying the upper clamp. Neither clamps against the opposite bound.
Negative steps can therefore move beyond that opposite bound. Zero steps still
invoke the binding setter. Arithmetic overflow traps before the setter runs,
even when a clamp could otherwise have bounded the result. Avoid precomputing
action requests during construction: the action can overflow only on input.

The displayed value is the checked sum of `value + displayOffset`, formatted by
the process locale. The SwiftUI environment locale does not affect that string.
Overflow traps during initial rendering or after the binding owner accepts a
write. The owner can observe and reject writes: the control emits requests against
the current owner value and never assumes the requested value was accepted.
External label, range, step, offset and value updates produce no action request.

The horizontal stack has zero spacing, a fixed 36-point height, card background,
UI radius, clipping and an overlaid border. The label uses primary Encode Sans
13, secondary text color, ten horizontal padding points and a one-line limit.
The divider is one point wide and 24 high. The value uses system monospaced bold
12 with a minimum 34-point frame. These two fixed fonts ignore the custom
`bleeckerTextScale`. Minus and plus inherit the parent font; default resolution is
SF 13, while parent Encode Sans 20/30 changes their layout. Base font probes do not
establish the actual glyph fallback runs or license portable Linux assets.

At requested display scale two, the normal public control is 132.5 by 36 points.
The padded label is 70.5 wide, the minus button 13.5 by 3.5, the value frame 34 by
15, and the plus button 13.5 by 12.5. A 100-point outer proposal yields a 91-point
control after label elision. Proposals of 60 or 12 yield an 82-point control that
overflows the offer. Parent font 30 increases both buttons to 31.5 points wide;
the label and value fonts remain fixed. The full Int64 display can enlarge the
value frame beyond 34 points.

Synthetic native mouse events reach the real public control in an isolated
window. Requests occur on release, cancellation emits none, and holding the
normal increment for 1.2 seconds produces one release request without repetition.
Four finite half-point hit grids preserve actual observed hits and misses. They
do not establish unsampled edges or license expanding the minus target to the
full 36-point row. Disabled, boundary, zero/negative step, unsafe-JavaScript,
readonly-owner and external-update behavior is retained in raw traces.

The capture path uses `NSHostingView.cacheDisplay` into explicit bitmap dimensions
without resizing. Public, root-instrumented and layout-witness images match byte
for byte in all 344 cases. Windows are isolated offscreen, inactive, non-key and
non-main; their actual backing scale is two. Requested SwiftUI display scale and
bitmap DPR one/two are recorded separately. Physical DPR one remains unverified.
Requested SwiftUI control states do not establish actual keyboard focus.

ImageRenderer produces unsupported placeholder artwork for the native borderless
SF buttons. Its 24 diagnostic captures are retained separately and cannot serve
as Stepper baselines. The eight existing public button anchors retain identical
geometry and alpha across the old and hosted capture methods, but all eight have
RGB differences. The raw images and difference statistics are retained; existing
expected images, source revisions, pixel tolerance and exception approvals are
unchanged. AppKit color constants are measured separately and are not proof of
the control's resolved paint.

The native library and `SabellaCatalog` product both build from the unchanged
pinned source. The catalog executable stayed in its event loop, but the UI
connector found no discoverable window, including with a local app wrapper.
Its UI, keyboard and reader gates remain open. Only the owned test processes were
stopped. No sibling source or Git state changed.

Run `python3 scripts/verify-stepper-source.py` with the pinned visual Python
dependencies to audit the matrix, raw hashes, integer boundaries, action phases,
capture-method differences and clean replay. References CI also runs its negative
integrity contracts. The source-only archive and all native source/tooling remain
external to this Linux repository. Its SHA-256 is
`3da10ba7132de2ca294c718514413cc9f6d4f7ee95217b0b47b4ad0998d3f138`;
the machine-local locator and individual source input hashes are in
[tooling provenance](../evidence/reference-investigations/stepper-20261016/tooling-provenance.json).
Independent-machine download remains pending. The replay preserves full trap
stdout/stderr; current files match, but future ASLR diagnostics are not promised
to be identical. Semantic signal and phase checks remain explicit.

Qt library/catalog/package/input work, exact fonts and symbols, visual comparison,
motion, X11/Wayland and physical displays, native keyboard/focus/accessibility and
actual reader behavior remain pending. The proposed monospaced font exception is
still unapproved. Desktop coverage remains 56/80 started, zero fully accepted;
TV is a separate later phase.
