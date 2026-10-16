# RadioGroup source contract

The pinned desktop `BleeckerRadioGroup` has a preserved native source investigation.
The [record](../evidence/reference-investigations/radio-20261016/investigation.json)
covers 432 public RadioGroup captures, eight button anchors, 24 binding/input
traces, eight finite pointer grids, 11 pointer phase traces and 13,762 native
String identity pairs. A clean source-only extraction rebuilds the unchanged
89-file Sabella tree and the native helpers, then reproduces all 1,358 image and
metadata outputs byte for byte. The Linux
candidate now has library, catalog and independent-consumer coverage; complete
mirror acceptance remains pending. Desktop coverage is 58/80 started and zero
fully accepted.

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

## Linux candidate API

`BleeckerRadioGroup` exposes `selection`, `options`, `orientation`, `maximumWidth`
and `selectionRequested(var)`. The owner accepts or rejects each request:

```qml
Item {
    id: owner
    property string frequency: "daily"
    BleeckerRadioGroup {
        selection: owner.frequency
        options: [{value: "daily", label: "Daily"},
                  {value: "weekly", label: "Weekly", disabled: true}]
        onSelectionRequested: value => owner.frequency = value
    }
}
```

Replace an options array to publish a new snapshot. A keyed `QAbstractListModel`
keeps buttons alive when their value identities survive label/disabled/order
updates. Changing orientation recreates the layout branch. An enabled click on
the selected option still requests its original value; there is no internal
selection write, automatic checking or arrow-key selection policy.

The default value encoding distinguishes strings, Boolean values, Double numbers
and null. Strings compare through pinned Unicode 17 canonical NFD. Signed zeros
compare equal; NaN remains unselected. Distinct, stable option identities are
required; duplicate IDs have no defined source `ForEach` behavior. A `valueIdentity`
function supplies the equality key for custom values, such as
`valueIdentity: value => value.editionId`. It must return equal primitive keys for
equal values and distinct keys for unequal values. The original value, including
an object payload or a string's scalar spelling, is passed through the request.
Use explicit typed values/keys for concrete numeric, optional or custom types that
JavaScript's default representations cannot distinguish. Preserve exact decimal
strings or typed payloads for integers beyond its safe range.

The NFD adapter recursively decomposes canonical mappings, decomposes Hangul
algorithmically, and stably orders combining classes. It follows
[Unicode 17 UAX #15](https://www.unicode.org/reports/tr15/tr15-57.html) without
compatibility folding. All 2,081 non-Hangul canonical mappings and 968 nonzero
combining classes match the official Unicode 17 data and the native ICU profile.
The generator and [Unicode provenance/license](../assets/unicode/provenance.json)
retain their hashes. Product data contains Unicode facts, with no native font or
symbol artwork. The original 17 Qt normalization disagreements remain preserved
as source diagnostics; ordinary verification does not replace that record.

An adapter over the pinned Qt 6.8.3 control template supplies the default font
while respecting ancestor and caller font fields. The default Encode Sans 13
remains a candidate for the source's SF 13. Explicit inherited fonts, fractional
point sizes and palette `windowText` changes propagate. A direct `foreground`
property can override that color. Custom `bleeckerTextScale` does not change this
control's font. `OwnedText` now exposes its design-space cap height without
changing its existing layout or painting; the RadioGroup positions icons relative
to that cap region. Empty and zero-width titles keep their measured line layout.
Vertical leading alignment and horizontal order follow `LayoutMirroring`.

The original circle drawing and its size/weight fit are unapproved candidates,
identified in [presentation provenance](../assets/radio-presentation.json).
Each Qt template button uses a
[containment mask](https://doc.qt.io/qt-6.8/qml-qtquick-item.html#containmentMask-prop)
covering its icon-content and title rectangles, with an inactive gap. The template
retains release/cancel handling and native Qt keyboard/accessibility input; those
Qt paths do not establish native keyboard or actual reader equivalence. Arbitrary
inherited font/symbol geometry, exact paint and all strict comparison gates remain
pending.

`AvelinoCatalog --fixture radio-group` and `InstalledConsumer --radio-group`
exercise the complete fixture. The isolated `RadioGroupCase.qml` is shared by the
catalog and independent consumer. `generate-radio-witnesses.py --check` audits
the consumer's source-derived binding and String identity witnesses and the
production normalization facts. `capture-radio-cases.py` preserves a new installed
catalog attempt; `compare-radio-captures.py` checks actual state, frames and strict
pixels against the unchanged hosted source corpus.

The candidate passes 7,384 Qt checks across DPR one/two, 11 CTest targets and
153 Python contracts on macOS and Linux ARM64. A network-disabled container with
only the installed package mounted and no ICU development headers passes all
22 consumer modes and 99 catalog captures. The previous 95 gallery PNG/full
metadata pairs remain byte-identical. Eight focused virtual X11/Wayland,
software/OpenGL and standard/scaled configurations pass their Qt input/interface
assertions. Their initial full-output captures can catch the compositor keyboard
partly below the output. A separate timed Wayland/OpenGL/scaled diagnostic shows
all four keyboard rows after 500 ms; its 500 ms and two-second full-output PNGs
are byte-identical. The one-second frame differs by 108 pixels at the text caret.
The initial cropping is consistent with the entrance transition; a persistent
layout defect is not established. This one settled virtual profile does not close
complete keyboard/overlay, physical input/displays, native keyboard or reader gates.

The first installed trace exposed a demo overlapping the last icon of a tall
narrow group. Moving that demo preserved the public hit targets and restored all
24 native action traces. Additional tests keep a renamed button pressed, cancel
on disable/remove/orientation changes, and verify stable horizontal reorder and
RTL leading alignment. Template font attributes now match the title's resolved
font fields, including the default family and fractional point-size requests.

The catalog's first full matrix reached the 0.3-point fixture, wrote its PNG and
then crashed while collecting font metadata. GDB locates the crash in
`QRawFont::familyName()`. A probe returned `isValid() == true` with `pixelSize() == -1`;
the pinned implementation then accesses an empty family list. The collector
now requires a positive raw pixel size before querying that identity. It records
the owned text renderer's reported family/style where available and explicitly
unavailable metadata for templates that do not draw their text. It does not
substitute a font. A real catalog regression covers empty groups, both subpixel
and fractional font cases, both DPRs, and refusal of a forged empty contract.
Raw failures and their partial captures remain preserved.

The nested layout Loader initially shifted odd and fractional groups by up to
half a logical pixel, even though its own `alignWhenCentered` was false. The
control's center anchor was still rounded. Disabling center rounding on the
control preserves the real parent center; a regression measures the presentation
through the complete Loader/control wrapper at sizes 0.3, 13, 13.5, 20 and 30.
The failing pre-fix trace and complete earlier comparison remain preserved.

The first post-fix capture attempt timed out while writing an image. Its original
partial files and controller log remain available; the final run uses a fresh
output directory. The timeout stays at 30 seconds. The collector now records a
machine-readable timeout failure as well as the raw log. An injected subprocess
timeout checks that diagnostic boundary without claiming GUI acceptance.

The final pointer audit also reproduced a native cancellation difference during
reordering: Qt moved the button correctly but retained its pressed state, then
triggered its action at release. An index change now releases that button's mouse
grab through the Qt template's cancellation path. Renaming a stable option and
external selection changes keep the valid press. Both DPR component tests cover
reversal while held, and the installed consumer replays all 11 preserved native
pointer-phase traces, including the 1.2-second hold and each mutation. These
callback checks remain separate from held/animated paint and native keyboard.

The [sealed Linux candidate](../evidence/development/radio/candidate.json) retains
440 captures, the strict comparison, raw first failures, frozen source/package
hashes, all eight virtual profiles and the timed keyboard diagnostic. Its 339
frozen product/validation inputs match the final files. The
[comparison](../evidence/development/radio/comparison/comparison.json) matches all
432 RadioGroup states, 200/440 root rectangles and 1,292/4,864 child rectangles.
Only the 16 empty-group cases pass the complete pixel/geometry comparison.
Before the centering fix, 124 root and 708 child rectangles matched. No source
pin, expected image, tolerance or font/symbol exception changed. These results
leave the component verification-pending and fully accepted desktop coverage at
zero.

The [timed full-output analysis](../evidence/development/radio/keyboard-settlement/settlement-analysis.json)
preserves the entrance snapshot and the nominal 500 ms, one-second and two-second
outputs. It diagnoses one virtual compositor capture phase, with no product,
focus, viewport or expected-image changes. It does not establish source keyboard,
physical display/input or actual reader equivalence.
