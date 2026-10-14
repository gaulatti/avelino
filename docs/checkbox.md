# Checkbox candidate

`BleeckerCheckbox` mirrors the pinned desktop source's boolean checkbox through a
Qt CheckBox template. The control remains verification-pending. Glyph equivalence,
focus presentation, screen-reader output, physical input and complete visual
acceptance are open; no exception or expected-image change is approved.

The observable acceptance cases are toggling through the indicator or label and
Space, maintaining a bound caller model through external changes, refusing input
when disabled, skipping disabled controls in keyboard traversal, preserving all
three size contracts across appearances and text/DPR scales, and wrapping long
labels without scaling the indicator. An empty label retains the source's gap.
The independent installed consumer must exercise the same path and query the real
Qt accessibility interface before recording virtual X11/Wayland evidence.

The Qt interface uses `text`, boolean `checked`, `enabled`, and `size` (`sm`, `md`,
`lg`). The sizes have indicator edges 14/18/22 and label fonts 11/14/16. Small has a
six-unit label gap; the others use ten. Label typography follows text scaling,
while indicator, gap and the ten-unit checkmark remain fixed. The indicator has
radius four, a one-unit border, card fill when unchecked and primary fill when
checked. Disabled controls use half opacity, measured from the native source.
Natural label width rounds up to the current physical pixel grid. The component
owns its indicator, label and candidate keyboard focus outline; host styles
supply no visible delegates. Qt templates supply focus and input semantics.

For a caller-owned model, use the normal Qt binding/update path:

```qml
BleeckerCheckbox {
    text: "Keep edition"
    checked: editor.keepEdition
    onToggled: editor.keepEdition = checked
}
```

The source exposes a boolean; Qt's inherited tristate/checkState extension has no
source presentation or acceptance. Use the documented boolean interface. The
source's selected trait/value maps to Qt's checkbox role and checked state, plus
`Selected`/`Not selected` description. An accessible interface query proves that
Qt publishes these values, but does not prove a screen reader announces them.

`CheckboxGlyph.qml` is an original geometric candidate for the source's system
checkmark at ten units/bold. No Apple artwork or system font is redistributed.
The [asset provenance](../assets/checkbox-symbols.json) records its pending
comparison and distribution acceptance. Font/icon and OS presentation gates
remain explicit.

The [source proposal](../evidence/reference-proposals/checkbox-20261013/proposal.json)
contains 128 checkbox captures and eight button anchors: both appearances,
text scales 1/1.5 and DPR 1/2, checked/unchecked, enabled/disabled, all sizes,
constrained wrapping and empty labels. ImageRenderer is offscreen evidence.
A clean extraction with verified input checksums, helper recompilation against
preserved pinned-reference objects, and replay reproduces all 136 PNGs and the
capture metadata byte for byte. This is not a new full Sabella compilation.
The native source and capture tooling remain external at
`../avelino-reference-vault/candidates/checkbox-20261013-67e9262/native-capture-replay.tar.gz`
(SHA-256 `6ebd9ec9a2b7dfef5cba08a8a5ed98aded09fd4f7bf68600c53d8f3c43582fbb`).
Run its `tool/build-capture.py` and `tool/NativeCapture`, then
`scripts/prepare-proposal.py --scope desktop-checkbox` with its provenance.

`AvelinoCatalog --fixture checkbox` shows the candidate states. The installed
consumer's `--checkbox` mode checks bound state, pointer/keyboard toggling,
disabled input, focus traversal, label wrapping, subsequent editing and Qt
accessibility role/name/state. Its window and complete virtual output are captured
separately for X11/nested Wayland, software/Mesa OpenGL, and standard/scaled
configurations. These sessions do not prove hardware acceleration, physical
input or screen-reader behavior.

Reference: `Sources/Sabella/Controls.swift` at
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`. The implementation uses the pinned
[Qt 6.8.3 CheckBox contract](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quicktemplates/qquickcheckbox.cpp)
and the [Qt accessibility interface](https://doc.qt.io/qt-6.8/qaccessibleinterface.html).

The [checksummed candidate evidence](../evidence/development/checkbox/candidate.json)
preserves all 136 strict comparisons, four default galleries, eight Basic/Fusion
style galleries and 40 installed-package window/full-output pairs. All default,
Basic and Fusion checkbox gallery PNGs are byte-identical. The Qt suite passes
287 checks per DPR (574 total); 34 contract checks pass. All 1,060 earlier
regression PNGs and component dimensions are unchanged.

Of 128 checkbox captures, 88 component geometries match and zero exact images
match. The forty remaining geometry differences concern small scaled text,
medium scaled height and constrained wrapped-line spacing. Eight anchor widths
also differ. These are recorded failures, with no tolerance or exception.
The source's regular font weight now overrides a bold host font. The Qt template
requires an explicit checkbox accessibility role to expose the correct interface;
the installed consumer verifies role, name, checked state and selected description.
