# Modal source contract

The pinned desktop `BleeckerModal` is a fixed-width content view that obtains
dismissal from its presentation context. It has no internal open state or
presentation host. The [native investigation](../evidence/reference-investigations/modal-20261016/investigation.json)
records 288 cases, three separately presented sheet fixtures and 14 behavior
traces. Linux implementation and all mirror acceptance gates remain pending.

`Sources/Sabella/Overlays.swift:3` constructs a vertical stack with zero spacing.
The header contains a fixed Encode Sans semibold 18-point title, a spacer and a
ghost IconButton labeled `Close`. Header padding is 20 on each side. The close
button is 44 by 36, including its fixed 16-point symbol frame. The title ignores
the parent font and custom text-scale environment; it inherits the foreground.
Caller content retains its own font, foreground, controls and text scaling.
The separator is one point high and uses the palette border color.

The default width is 480. An outer frame offering zero, 160 or 800 points produces
the same public image as the default fixture. An explicit Modal width remains
fixed even when its children exceed it. At width zero, the header still measures
92 points wide and 293 high; its zero-width title retains 253 points of height.
The public outer frame is zero wide and 414 high. The final rounded clip bounds
the overflowing header and caller content. A 200-point caller rectangle also
overflows a 160-point Modal; an 800-point rectangle remains 800 points wide in the
480-point fixture. A flexible child receives the 440-point interior width.

Padding applies separately to each flattened caller child. Empty content leaves
only the 76-point header and one-point separator: total height 77. A zero-size
child retains 40 points of padding, producing height 117. Hidden 200-by-80 content
retains the ordinary 197-point height. Two flat children, a 16-point text label and
a 44-point rectangle, produce height 217. An explicitly nested vertical stack
with spacing five remains one padded child and produces height 182; the matching
horizontal stack produces height 161. These measurements rule out wrapping all
caller content in one shared padded box.

The background is palette `card`, with a circular rounded rectangle of radius
14. It has no border. Its `deepSea` shadow uses opacity 0.24, radius 32 and vertical
offset 12 in both appearances. This differs from the generic continuous surface
modifier. The hosted canvas images retain the Modal shadow and original physical
dimensions; none is resized or installed as a Linux asset. Sheet captures cover
only their content view bounds. They exclude outer window chrome and shadow and
do not establish complete native sheet appearance.

All 288 public captures match both the separately probed public view and the
reconstructed source layout byte for byte. The 36 fixture groups cover empty,
multiline, long, Unicode and bidi titles; narrow and zero widths; outer offers;
empty, zero, hidden, oversized, flexible, text, editor and grouped caller content;
disabled and RTL layouts; inherited font and foreground. Each group runs in
light/dark, text scale one/1.5 and requested bitmap/display DPR one/two. The hosted
capture windows have actual backing DPR two and remain inactive, non-key and
non-main. Requested DPR one does not establish a physical DPR-one display.
Three sheet fixtures independently preserve the same public/probed/witness image
identity, including disabled and RTL contexts.

The unmodified public component receives synthetic events in separate windows.
Close in a directly hosted Modal hides the containing native window. The retained
hosting view still owns its mounted content, so an unchanged mount count does
not mean the window stays open. The retained view's cached PNG is also unchanged
across Close; `NSWindow.isVisible` establishes that its window is hidden.
In a caller's SwiftUI sheet, Close changes the
caller presentation binding to false, removes the sheet and invokes its dismissal
callback once, while the parent window stays
visible. Disabled Close preserves the sheet and invokes no callback. Each sheet
close target comes from a separately presented witness whose PNG equals the
public sheet before input. A Linux adapter must preserve contextual dismissal:
the hosted-window fixture closes its window, while the presented sheet dismisses
only that presentation and updates its owner. This agrees with Apple's documented
[`DismissAction`](https://developer.apple.com/documentation/swiftui/dismissaction)
presentation scope. The Modal itself supplies no presentation host or open state.

A caller counter keeps its local state through title and width updates. Disabled
input emits nothing; enabling the same child restores activation. Replacing the
counter with empty content or removing the Modal destroys its local state:
observed mount values are zero, zero, zero. A click after each remount invokes
the fresh counter at one. All those inputs run while the containing window is
visible; Close runs last. An earlier attempt put Close before the remounts and
then observed no callbacks because the window was hidden. That complete trace
and its images remain under `diagnostics/post-dismissal-input-attempt/` and are
excluded from remount input acceptance. Holding a pointer produces no callback
before release. Disable or removal during a press cancels activation; the measured
width/title changes still
allow activation on release in these Modal fixtures. These observations are
context-specific and do not replace physical pointer acceptance.

The TextField fixture retains a producer-updated binding through subsequent
layout changes. This is producer/binding evidence, not native typing or IME proof.
Synthetic Escape and parent-window clicks leave the inactive sheet presented;
this does not establish the platform's normal focused keyboard/outside-click
policy. This inactive own-process accessibility traversal returns only the host
group, with no usable button children; its cause is not isolated. Its initial attempt cannot establish Close
behavior or reader acceptance and is preserved under `diagnostics/`.
The traversal uses Apple's documented
[`NSAccessibilityProtocol.accessibilityChildren()`](https://developer.apple.com/documentation/appkit/nsaccessibilityprotocol/accessibilitychildren%28%29).

A clean extraction of five source-only inputs plus their manifest rebuilds the
unchanged 89-file Sabella library and both helpers. It reproduces all 977 capture
and behavior files byte for byte. All 865 original capture files also remain
byte-identical after the additive behavior instrumentation. The external archive
SHA-256 is `0cea0f70a6e2f159f45f3ea32fefb25ca5334c520918fc8c33b4e8da75669416`;
its locator, toolchain and input hashes are in
[tooling provenance](../evidence/reference-investigations/modal-20261016/tooling-provenance.json)
and [replay inputs](../evidence/reference-investigations/modal-20261016/inputs.json).
Swift source, native helpers, resource bundles and the replay archive stay outside
the Linux repository. Independent-machine archive availability remains pending.

Run `python3 scripts/verify-modal-source.py` to check hashes, complete fixture
coverage, image/probe identity, fixed-width and flattened-padding measurements,
presentation/binding/lifecycle observations, preserved harness limits and replay.
Negative contracts run in References CI. This source checkpoint does not start
another Linux API or alter expected images, reference pins, tolerances or approved
exceptions. Exact typography, symbols, shadow/raster, real keyboard/IME, physical
displays/input, complete presentation integration and screen readers stay open.

## Clipped input and reopening

An additive [input investigation](../evidence/reference-investigations/modal-input-20261016/investigation.json)
records 170 clipping queries, 568 precise Close hit queries and three reopening
traces with 20 snapshots. A fresh source-only rebuild repeats every input result
and lifecycle/binding metadata file. It reproduces 65 of 67 output files byte for
byte. Two public TextField reopening images differ within the field body. Both
originals and replay images remain preserved and explicitly quarantined from
pixel acceptance; neither becomes a replacement expected image.

The rounded visual clip does not restrict caller input. An enabled fixed-width
828-by-80 caller button still activates beyond the visible 480-point body. A
disabled caller button does not activate. The clipped zero-width Modal can also
retain an active Close symbol outside its empty visual body. The 44-by-36 Close
layout rectangle includes padding that does not activate its ghost button.
These measurements require separate visual clipping and input containment.

The four measured Close profiles use resolved symbol fonts 13 and 20, each at
requested DPR one/two. Their 142 samples per profile include four boundary searches
and an 81-point grid. All 568 results fit a pixel-aligned square: ceil 0.8 times
the resolved symbol size at the requested DPR, centered with a local pixel round
inside the fixed 16-point frame, then rounded again at its window position. The
measured squares are 11 points at font 13/DPR one, 10.5 at font 13/DPR two, and
16 at font 20. Window position explains the asymmetric half-point offsets.
This is input geometry evidence, not permission to redistribute native symbol
artwork or a claim about unmeasured symbol sizes or physical pointing devices.

Reopening the retained hosting window preserves the caller counter: its next
activation reports two. Reopening the caller's sheet starts the counter at zero,
and its next activation reports one. A caller-owned edition binding survives sheet
reopening and later producer updates. The native sheet counter reports three
appearances and zero disappear callbacks in this inactive harness. Qt object
destruction is a different framework event and must not be reported as an equal
native disappear callback. Focused presentation/lifecycle acceptance remains open.

The TextField's full reconstructed sheet witness changes body pixels. Clearing
native first responders does not make it transparent; the cause is unisolated.
Its first 154 physical header rows remain byte-identical. Only that verified
header supplies the Close target. No TextField body frame from this witness is
used as a regression expectation. The two reopening replay disagreements also
leave that header unchanged. Full field pixels, focus, native typing/IME and
screen readers remain pending.

The five-input source-only archive has SHA-256
`7ecf2f03510770e212135de0c6e33642a4d56785a2bd25049b031820f35c92c7`.
Its [provenance](../evidence/reference-investigations/modal-input-20261016/tooling-provenance.json)
retains the external locator and unchanged 89-source build. All failed helper
attempts, incomplete data, mismatched witnesses and replay differences remain in
the investigation. Run `python3 scripts/verify-modal-input-source.py` to audit the
facts, original capture anchors, precise hit model, source-only input hashes and
explicit exclusions. At that source-only checkpoint, Linux implementation and
all complete mirror gates were pending; the candidate below is recorded separately.

## Linux candidate

`BleeckerModal` requires `title` and accepts caller content through its default
data property. `modalWidth` defaults to 480 and fixes the visible body independently
of the caller's allocated `width`. A zero allocation can contain a 480-point body;
a zero `modalWidth` has no visible body while retaining its measured layout and
input behavior. Negative or nonfinite body widths report explicit errors.

```qml
BleeckerModal {
    title: "Edit edition"
    modalWidth: 480
    BleeckerTextField {
        text: edition.name
        onTextEdited: edition.name = text
        BleeckerLayout.minimumWidth: 0
        BleeckerLayout.idealWidth: implicitWidth
        BleeckerLayout.fillsWidth: true
    }
}
```

The header owns its 18-point semibold title and ghost Close control. Each
flattened caller child receives 20 points of padding. Explicit `ProposalColumn`
or `ProposalRow` content remains one caller child. Layout-transparent conditional
hosts use `BleeckerLayout.flattenChildren` and `participates`; custom content can
describe minimum, ideal and flexible width through `BleeckerLayout`. A fixed wide
child can overflow its proposal. The circular visual mask preserves pointer
delivery outside the visible body, matching the measured source contract.

By default, Close closes the containing Qt window. A presentation owner can
provide `dismissAction` to dismiss its own presentation. The separate
`BleeckerModalDialog` Qt adapter owns a `Popup.Window`, supplies that action and
creates caller content from a `Component` each time it opens. Retained window
content therefore keeps local state; reopened dialog content starts fresh while
its externally owned bindings remain available.

```qml
BleeckerModalDialog {
    id: editor
    title: "Edit edition"
    content: Component {
        BleeckerTextField {
            text: edition.name
            onTextEdited: edition.name = text
            BleeckerLayout.minimumWidth: 0
            BleeckerLayout.idealWidth: implicitWidth
            BleeckerLayout.fillsWidth: true
        }
    }
}
```

The adapter uses no automatic Escape/outside close policy. The preserved native
Escape/outside traces came from an inactive application; they do not establish
active native keyboard policy. Dialog focus, IME, full window chrome, reader
behavior and physical presentations remain pending. Qt destruction counts are
retained separately from native disappear callbacks. The original cross artwork,
inherited platform font candidate and exact shadow/raster remain unapproved.

`AvelinoCatalog --fixture modal` opens the gallery. `InstalledConsumer --modal`
replays all 80 preserved state snapshots, the 170 clipping queries and the 142
Close glyph samples matching its display/text-scale profile. Original lifecycle
and clipping traces run at their recorded text scale one; the glyph profile and
final gallery use the requested scale. Parent activation and displayed frames
are awaited before keyboard traversal. Qt title/button accessibility interfaces
are checked independently from native readers.
The gallery's editor button is also activated through input, text is typed into
the presented field, and its caller binding is checked again after reopening.
That Qt editing check does not establish native keyboard/IME equivalence.

The [parent-focus checkpoint](../evidence/development/modal-parent-focus-20261022/README.md)
preserves the x86 Wayland/software/scaled failure from Linux CI at
`6f16b95`. Both architectures passed58 CTest groups at that revision, and ARM
passed its full workflow; the x86 source-free session step failed at the parent
Close-focus assertion. The failure remains separate from the successful checks.

The replay now waits for `QGuiApplication::focusWindow()` to identify the parent
and for its Quick root to hold active focus. Qt6.8.3's
[`isActive()` implementation](https://github.com/qt/qtbase/blob/v6.8.3/src/gui/kernel/qwindow.cpp#L1218-L1247)
also considers the transient chain active, so it cannot establish that keyboard
precondition. A diagnostic observes an active parent while the hidden popup is
still the focus window. Each presented-sheet check rejects this false parent
readiness state; deliberately restoring the old predicate fails that assertion.
The original Close, Tab and Backtab focus assertions remain in place, and the
five-second readiness bound is unchanged. There is no retry after a failed assertion.

The current consumer passes the offscreen replay, eight scoped source-free
X11/Wayland software/OpenGL profiles and fresh FileInput available, unavailable
and closed flows. These are local ARM observations, not a rerun of the failed
x86 CI job or the full session matrix. All158 installed library/catalog/asset
files are unchanged. The consumer test is the only changed compiled input;
native focus, hierarchy, typing, reader, raster and physical acceptance stay pending.

`scripts/capture-modal-cases.py` captures all 288 original hosted contexts through
the installed catalog, including the unresolved Unicode, bidi and inherited-font
cases. `scripts/compare-modal-captures.py` compares original physical pixels,
body and child frames, actual state and the independently allocated outer frame.
It preserves failures and keeps acceptance false. No expected image, font/symbol
exception or tolerance changes as part of this candidate.

The [candidate evidence](../evidence/development/modal/candidate.json) records
146 Qt results per DPR, 267 contracts on both macOS and Linux, 25 independent
consumer modes, 111 catalog images and eight focused X11/Wayland software/OpenGL
profiles. All 107 prior gallery PNGs and complete metadata files are byte-identical.
All 116 installed catalog/library/asset files used for the 288 source captures
are byte-identical to the final consumed package. Parent activation and a
displayed frame are awaited before opening a separate sheet. Each source trace's
window is destroyed immediately afterward; the observed peak is two windows.

The strict comparison matches all 288 title/width/content-kind/disabled/RTL
observations, 280 root frames and 248 child-frame sets. Its eight complete pixel
matches are the blank zero-width bodies. No visible Modal pixel case passes.
The eight root failures are `parent-font32`; the 40 child-frame failures are the
Unicode, bidi and three inherited-font fixtures. The visible shadow profile,
exact glyph/corner/line raster and symbol remain unresolved. Desktop coverage
is 61/80 candidates, zero accepted; all 46 television entries remain pending.
