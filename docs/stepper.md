# Stepper source contract

The pinned desktop `BleeckerStepper` has a preserved native source investigation;
its Linux candidate is being verified separately. The
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

Exact fonts and symbols, full frame/raster comparison, held/animated paint,
physical displays/input, native keyboard/focus/accessibility and actual reader
behavior remain pending. The proposed monospaced font exception is
still unapproved. At that checkpoint desktop coverage was 57/80 started, zero fully accepted;
TV is a separate later phase.

## Installed Linux reader observations at 899f3e8

The [2026-10-24 evidence](../evidence/development/stepper-reader-20261024/README.md)
binds two 13-phase runs to the installed package from `899f3e8`: XCB/software/light
at DPR 1 and nested Wayland/OpenGL/dark at DPR 2 with text scale 1.5. The normal
caller accepts assistive button requests, rejects disabled bound actions and
updates its accessible value; focused Space activation works in both directions.
Focus then moves to the outside field, which receives keyboard text. The complete
package prefix is hash-bound to its original producer; no source/build tree was
mounted and no new Qt suite execution or product change is claimed.

Orca and Speech Dispatcher name both focused buttons, but changed numeric values
are not announced in the measured action windows. Qt also logs `ValueChanged
event and no ValueInterface or ComboBox`. Static value updates and named focus
therefore do not establish complete reader usability. Numeric feedback and the
native keyboard/reader comparison remain unresolved. Audio uses a controlled null
device; physical input/display and independent-machine acceptance stay open.

The first observer run remains a failure: it expected a fresh named utterance
while the same button was already focused. The successful runs explicitly focus
the outside field before probing each button; deadlines and speech assertions
are unchanged. `python3 scripts/verify-stepper-reader.py` rechecks the retained
trees, state changes, named speech windows, absence of numeric speech in bounded
action windows, original package inputs and preserved acceptance fields. It does
not rerun the application. Desktop candidate coverage is 78/80, with zero fully
accepted; TV remains a separate phase.

## Native action names

The [pinned native accessibility caller](../evidence/reference-investigations/stepper-accessibility-20261024/README.md)
exposes `Remove` and `Add`, with the label and value as separate text elements.
Actual clicks update the binding from 2 to 3 to 2 to 1, where Remove becomes
disabled. The caller uses the unchanged 89-file pinned source; original CUA
responses, paired actions and owner receipts are preserved. Its wrapper resource
placement failure is retained separately. Native VoiceOver speech and native
button keyboard activation were not measured.

The [Linux repair](../evidence/development/stepper-native-action-names-20261024/README.md)
changes only the two accessible button names to those observed English names.
The prior names included the caller label. Both old-name failures are retained;
the repaired source passes 159 Stepper checks at each DPR 1/2. Two installed
catalog sessions complete 13 reader phases each with actual Remove/Add speech.
The independent consumer also verifies the names after its caller label changes,
and passes 25 native action traces, 126 formatter witnesses, binding and focus
checks in both X11 profiles. Its updated header is frozen separately from the
library snapshot; no later library build or full 58-group rerun is claimed.

The original consumer observer timed out after the application assertions passed
because it omitted the capture acknowledgement. The corrected observer captures
the full Xvfb session before acknowledging and receives exit zero. The timeout
and all capture outputs remain in the evidence.

Before/after Linux images match exactly in 14/26 full-session pairs. Eleven
Wayland frames differ by one pixel; outside-focused differs by 32,010 pixels and
shows the software keyboard at a different vertical position. These observations
grant no visual exception. Numeric speech, native reader/raster and full parity
remain pending. Audit retained evidence with
`python3 scripts/verify-stepper-native-names.py`; use `--current` before publication
to additionally require the candidate's runtime inputs to match the tested files.

The Qt candidate exposes `label`, `value`, `lowerBound`, `upperBound`, `step` and
`displayOffset`, with `valueRequested(string)` preserving caller ownership:

```qml
BleeckerStepper {
    label: "Copies"
    value: model.copies
    lowerBound: "1"
    upperBound: "9223372036854775807"
    onValueRequested: requested => model.copies = requested
}
```

Use canonical decimal strings outside JavaScript's safe integer range. All five
integer inputs reject fractions, booleans, non-finite numbers, noncanonical
strings and values beyond Int64. The C++ adapter checks addition/subtraction
without negating `Int.min`, then applies the source's one-sided action clamp.
Requests are calculated only on activation. Display formatting uses ICU's
`formatInt`, preserving all 64 bits; process-locale changes refresh the label.
The control's inherited `locale` does not own this string.
Keep each separately observed Qt property update's range and display sum valid.
Native transaction equivalence for broader composed producer updates is still
open; independent native test fixtures are not one continuous producer session.

`decrementInput` and `incrementInput` expose the owned Qt template buttons. They
retain their small glyph-sized input rectangles, disable repetition, and use the
normal Qt release, keyboard and accessibility paths. The English Remove/Add
names follow the bounded native accessibility observation above. Qt keyboard and
complete reader behavior remain candidates until native equivalence is
established. Template behavior is documented in
[Qt AbstractButton](https://doc.qt.io/qt-6.8/qml-qtquick-controls-abstractbutton.html).
The measured primary label and fixed monospaced value sizes remain independent
of custom text scale. The system fixed font and original plus/minus strokes are
unapproved candidates, with provenance in
[the presentation manifest](../assets/stepper-presentation.json).

`AvelinoCatalog --fixture stepper` and `InstalledConsumer --stepper` expose the
full fixture. Isolated catalog cases share `StepperCase.qml` with the consumer.
The generated installed witnesses contain all 25 source action traces and 126
integer strings; `python3 scripts/generate-stepper-witnesses.py --check` audits
their projection against preserved raw source inputs. Tests wait for row layout
before pointer events after a wide value shrinks; they do not change production
input behavior or weaken expected results. This follows Qt's explicit
[layout-polish test boundary](https://doc.qt.io/qt-6.8/qml-qttest-testcase.html#waitForPolish-method).

The [sealed Linux candidate](../evidence/development/stepper/candidate.json) records
7,356 passing Qt checks across both DPRs, nine CTest targets and 135 Python
contracts on macOS and Linux ARM64. All 25 native action traces and 126 native
integer strings match through the installed consumer. The existing 49,448 numeric
formatter witnesses also remain exact. A container with only the installed
package mounted, networking disabled and no ICU development headers passes all
21 consumer modes and all 95 catalog captures. The 91 previous catalog PNG/full
metadata pairs remain byte-identical.

Eight source-free X11/Wayland, software/OpenGL and standard/scaled configurations
pass with separate window and full-output captures. They are virtual sessions,
with no physical-display, hardware-acceleration or actual-reader acceptance.
The first X11 held-input check failed after a wide value shrank. The driver now
settles the owned row before sampling and processes release events before the
assertion, preserving the small native target and expected single request. The
initial log did not record which timing boundary caused the miss.
First attempts, diagnostics and source
headers are retained. A separate setup correction clears a previous fixture's
display offset before constructing the next independent extreme-value case.
Neither correction changes production arithmetic, control state or hit regions.

The strict hosted-source comparison covers 344 images, including eight button
anchors. It records 336/336 matching Stepper values, strings and enabled states,
132/344 matching root bounds, 508 matching and 2,516 failing mapped child frames,
and zero exact RGBA images. These failures remain visible. Raw Qt text frames
include OwnedText's paint-alignment transform, while the native background probes
do not expose glyph-run paint origins; quarter-point frame differences need
further interpretation before claiming a source layout defect. The unresolved
system monospace line box, normalized original symbol geometry, inherited font
and requested-DPR behavior are separate from the passing numeric/action contract.

`capture-stepper-cases.py` uses the installed catalog with source/build QML import
overrides unset. Failed attempts remain available. `compare-stepper-captures.py`
validates the original source evidence, projects its preserved hashes/geometry
without writing native manifests, then applies the existing strict pixel engine
plus observed state and child-frame checks. CI collects these 344 cases and
reports Stepper diagnostics independently on x64 and ARM64. No tolerance,
expected image, source pin or exception approval changes. No backend, metrics or
application-configuration changes are needed by this control.
