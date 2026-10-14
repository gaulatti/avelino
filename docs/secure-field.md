# Secure-field candidate

`BleeckerSecureField` implements the pinned desktop control's masked editor and
eye/eye-slash visibility action. It remains verification-pending for exact images,
native password glyphs, focus/caret/selection presentations, context menus, input
methods, full RTL behavior, physical input and screen-reader output.

The observable criteria are: text entered by the user reaches the caller model;
masked text stays masked immediately, including during entry and clipboard copy;
the reveal action preserves the value and switches to normal editing; hiding
restores masking; disabled controls refuse input; tab traversal reaches the reveal
button and subsequent editor while skipping disabled controls; external values
remain synchronized; and installed consumers preserve these behaviors across
display/text scales, X11/Wayland and both renderers. Actual Qt accessibility
interfaces must reflect the editor's password state and visibility action.

Use normal Qt text ownership:

```qml
BleeckerSecureField {
    width: 300
    placeholderText: "Passphrase"
    text: editor.passphrase
    onTextEdited: editor.passphrase = text
}
```

The control derives from the Qt TextField template. It retains native editing,
selection, `readOnly`, focus and keyboard behavior. `revealed` is read-only; use the
button to keep its checked state, glyph, accessible action and echo mode in sync.
The default Qt allocation is 240 units wide; source comparisons supply the same
explicit 300/160-unit allocations as the native fixtures. Unconstrained source
sizing remains a separate case.

The source fixes Encode Sans Regular at 14 and minimum height 40 without a text
scale multiplier. Horizontal padding is 14. The candidate reserves 22 for the
visibility action and eight for its gap. It reuses `BleeckerSurface` with radius
seven, border and source shadow. The source native editor resolves text opacity
216/255, placeholder 127/255 in light and 140/255 in dark, and disabled text 63/255,
using black/white respectively. These measured native control properties live
centrally in `BleeckerTheme`, independently of platform-neutral Bleecker tokens.
CoreText and Qt produce different rendered ink from these values; the raw image
comparisons retain that unresolved rasterization/color difference.

Masking uses Qt Password mode, a candidate U+2022 bullet and zero echo delay.
Revealing uses Normal mode. Qt supplies clipboard and accessible-value behavior;
the installed test queries the real interfaces and checks both masked and revealed
copy paths. No real credentials are used in fixtures or evidence. These checks
establish neither a general application security boundary nor native glyph or
screen-reader equivalence.

The [native proposal](../evidence/reference-proposals/secure-field-20261014/proposal.json)
contains 40 secure-field images plus eight button anchors: masked/revealed,
empty/filled/long/disabled/constrained text, both appearances and text scales.
Native descendants require own-window caches at measured DPR 2; native DPR 1 and
whole-output/compositor evidence remain pending. Reveal is exercised through the
helper's own button, then captures are defocused to exclude caret timing.
Font, native editor frame, disabled state and preserved caller value are recorded.

Clean extraction, input checksum verification and helper recompilation reproduce
all 40 secure-field PNGs byte for byte, with identical capture data. One scaled
DPR 1 button anchor varies by three pixels at one channel level. That raw variation
is recorded in the tooling provenance and remains unaccepted; expected images and
tolerances are unchanged. Recompilation links preserved source-verified objects
and is not a fresh full Sabella compilation. Apple tools and objects remain external
at `../avelino-reference-vault/candidates/secure-field-20261014-b31551b/native-capture-replay.tar.gz`
(SHA-256 `353b3cc21d5decc8528a299379cf8cd94fb47f5e8a1529bfc5e28dec365593cd`).
Run `tool/build-capture.py` and `tool/NativeCapture` from a clean extraction into a
new output directory. The scoped verifier rejects missing visibility/disabled
combinations and false native reveal/value/font metadata even after checksum updates.

`SecureEyeGlyph` is original candidate geometry, with provenance in
[the symbol record](../assets/secure-field-symbols.json). Exact system-symbol
equivalence remains open. `AvelinoCatalog --fixture secure-field` shows the
interactive gallery; `InstalledConsumer --secure-field` exercises editing,
visibility, clipboard, disabled input, focus and Qt interfaces.

Reference: `Sources/Sabella/Controls.swift:74` at
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`. The implementation uses the pinned
[Qt 6.8.3 TextInput echo modes](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quick/items/qquicktextinput.cpp)
and [accessible value mapping](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quick/accessible/qaccessiblequickitem.cpp).

The [checksummed candidate](../evidence/development/secure-field/candidate.json)
preserves all 48 strict comparisons, four default galleries, four Basic/Fusion
galleries and 48 fresh installed-package window/full-output pairs. All 40 secure
component bounds and eight button anchors match; exact images remain 0/48.
All 2,784 Qt checks and 37 contract checks pass. The eight secure-field session
pairs exercise masking/reveal, editing, disabled input, clipboard, focus and actual
Qt password/value/action interfaces. Default/Basic/Fusion gallery PNGs are
byte-identical. All 1,338 previous PNGs and their full metadata are unchanged;
the regression report links their existing immutable evidence rather than copying
it. The checkable reveal action explicitly retains the Button accessibility role.
Native cached ink, symbol geometry, focus/caret/context-menu/input-method/RTL,
physical input and real screen-reader acceptance remain pending.
