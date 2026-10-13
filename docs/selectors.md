# Selector candidate

`BleeckerSelect` implements the desktop source's closed button, ordered options,
disabled options and scrollable selection popup. It remains verification-pending.
No native selector capture, symbol equivalence, OS popover presentation or visual
exception has been accepted.

The [checksummed candidate evidence](../evidence/development/selection/candidate.json)
preserves four gallery captures, 512 passing Qt checks and 32 installed-package
window/full-output pairs, including eight with the selector popup open. The
selected row, disabled final row and scrollbar are explicitly in view. Basic,
Fusion and default-style gallery PNGs are byte-identical. All 980 existing desktop
and composition regression PNGs and their comparison metadata are unchanged.
These checks establish candidate behavior and presentation ownership; native
selector appearance and complete acceptance remain pending.

The acceptance cases are: caller-owned selection survives reopening and external
changes; unknown values display the source placeholder; disabled options cannot
activate through pointer or keyboard; the popup scrolls within its 288-unit bound;
Escape/outside dismissal preserves selection; activation restores focus; empty and
changed option collections do not select a default; narrow/scaled labels elide;
and the installed package exercises and captures the open popup on X11 and Wayland.
Complete native comparisons, screen-reader output and physical input remain gates.

The Qt interface has required `selection`, ordered `options` containing `value`,
`label` and optional `disabled`, `placeholder` defaulting to `Select…`, and an
optional `leading` component slot. Values retain their types and identity. The
caller updates its authoritative value in response to `activated(value)`:

```qml
BleeckerSelect {
    selection: editor.edition
    options: [{value: "morning", label: "Morning"},
              {value: "evening", label: "Evening"}]
    onActivated: value => editor.edition = value
}
```

The component emits an activation request and never silently replaces an unknown,
removed or disabled selection. Qt Button, Popup, ItemDelegate and ScrollBar
templates own input and focus mechanisms; Avelino supplies every visible delegate.
The popup uses `Popup.Item` explicitly so the host cannot select a native popup
style. Keyboard movement skips disabled rows and commits only on activation.
Model changes keep an open popup visible and refresh its keyboard position.

The closed surface uses card/border colors, radius 7, horizontal padding 14 and a
minimum height of 40. Options use primary 14 typography, horizontal padding 12,
minimum height 36, spacing 2 and popup padding 4. The candidate popup is at least
220 wide and has a maximum height of 288. Its placement prefers above the button;
Qt constrains it to the window. Exact width allocation, edge placement, native
popover arrow/material/shadow, hover/focus presentation, RTL, transitions and
focus preservation through reordered collections remain unverified.

`SelectionGlyph.qml` contains original geometric chevron/checkmark candidates.
Their [provenance](../assets/selection-symbols.json) records the source SF Symbol
roles without copying Apple asset bytes. Geometry, weight, alignment and sizing
still require comparison; these are not approved substitutes. The leading slot
lets the caller supply its Linux-owned icon presentation without guessing an SF
Symbol mapping.

The owned text renderer's optional `elideWidth` shapes a single elided line at
font design-unit precision. Its default `-1` keeps existing typography unchanged.
The selector gives it the allocated width directly, avoiding an implicit-size
feedback loop. Accents and a multi-code-point emoji appear in the narrow-label
regression; rendering equivalence remains a separate visual gate.

`AvelinoCatalog --fixture selection` shows the open long-list popup and closed,
disabled, empty and constrained selectors. `InstalledConsumer --selection` checks
pointer/keyboard activation, disabled options, external value changes, dismissal,
focus and scrolling, then leaves the popup open for window and full-session
capture. The session harness runs this fourth fixture independently in each of
eight configurations. Offscreen and virtual-session evidence cannot establish
physical input, hardware acceleration, separate-window overlays or accessibility.

Reference: `Sources/Sabella/Controls.swift` at
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`. Framework contracts:
[Qt 6.8 control customization](https://doc.qt.io/qt-6.8/qtquickcontrols-customize.html),
[Popup](https://doc.qt.io/qt-6.8/qml-qtquick-controls-popup.html), and
[QFontMetricsF](https://doc.qt.io/qt-6.8/qfontmetricsf.html).
