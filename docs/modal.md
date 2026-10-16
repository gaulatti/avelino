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
