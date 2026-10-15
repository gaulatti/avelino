# Form control candidates

Five more desktop APIs have candidates. All remain verification-pending. Native
captures are preserved as proposed references; full behavior cases, accessibility
output and strict visual acceptance remain open. The [selector](selectors.md)
has a separate candidate with an owned open popup.
The [checkbox](checkbox.md) separately covers boolean selection and all three sizes.
The [secure field](secure-field.md) separately covers masked editing and its
visibility action with fixed source typography.
The [search field](search-field.md) covers the magnifier/clear path and the shared
field's leading/trailing slots, including all sizes and error state.

| Reference API | Linux interface and owned presentation |
| --- | --- |
| `BleeckerField` | Required `label`, description/error/optional flags, default content slot; gap 10, first-baseline optional label, primary 13 medium and secondary 11/12 typography with text scaling |
| `BleeckerTextArea` | Text/font/readOnly/selection properties, `minimumHeight` 96, `accessibleName`; editable wrapped viewport with padding 10, card background/radius 7/border, explicit selection colors and scrollbar |
| `BleeckerSwitchStyle` | `BleeckerSwitch` uses Qt Switch input; track 36 × 20, white thumb 16 with padding 2 and light shadow, label gap 12, scaled primary 14 medium, pinned standard-duration transition |
| `BleeckerToggleStyle` | `BleeckerToggleButton` has caller-owned `selected`, default/outline variants, horizontal padding 12 and minimum height 34; selected primary fill, unselected pressed muted fill, radius 7 |
| `BleeckerSegmentedControl` | Required `selection`, ordered `options` with value/label/disabled; caller values retained; gap 2, padding 4, muted opacity 0.65/radius 9/border, segment minimum height 32 and padding 12 |

Qt templates supply editing, selection, focus, disabled behavior and activation.
Avelino supplies the visible content, backgrounds, indicators, colors and transitions.
The multiline viewport uses the template's Flickable integration and an explicitly
painted ScrollBar; its document extent must be supplied through implicitHeight
because a bare template has no default style to do that. Keyboard and pointer
checks exercise the input inside this viewport. The toggle style emits `clicked`
and leaves selection changes to the caller, matching a style's ownership boundary.
Segmented buttons update selection with the option's value and skip disabled options
in the Qt tab sequence.

`hasDescription` and `hasError` distinguish absent optional content from a present
empty string. Field content is a caller-supplied composition root; callers retain
its width, layout and accessible naming. Wrapped title metrics now notify intrinsic
width changes separately from line-layout changes, preventing a switch label's
width/wrapping feedback loop when text scaling changes.

The tests cover twelve field theme/content combinations, eight switch theme/state/
scale combinations, eight toggle theme/state/variant combinations, segmented
ordering/disabled options/keyboard/empty state, and multiline editing/selection/
read-only/scrolling/resizing. The installed consumer's `--controls` fixture
exercises all five, including visible scrollbar internals and focus restoration to
an editable field. The display harness captures this fixture and the existing base
fixture separately in each of eight X11/nested-Wayland configurations.

Run `AvelinoCatalog --fixture controls` for the gallery. The catalog check captures
light/dark at DPR 1 and 2. These captures are Linux candidates, not expected source
images. Focus outlines, thumb shadow rasterization, inherited toggle label fonts,
editing insets, full constrained segment layouts, RTL, transitions, native text
scaling, screen readers, context menus and selection/caret states remain pending.
The scrollbar appearance also needs the native presentation reference and comparison.
Owned labels use the [measured native font metrics](typography.md); editor caret,
selection, native insets and system/fallback-font presentation remain separate gates.
No host theme is used to supply these templates' visual delegates; no visual
exception is approved.

The composed-field fixture exposed two omissions in the existing text field:
its shader-layer background disappeared with software rendering, and the bare
template did not paint placeholder text. The background now uses the shared
continuous surface and Canvas shadow, with the reference's focus-dependent shadow
radius 4/1 and offset 1. An explicit elided placeholder follows the editor's font,
alignment, preedit and empty-text state. A rendered composition check checks border
and placeholder ink; the installed consumer clicks the field before typing.
These fixes preserve Qt editing and do not establish native placeholder/caret parity.

Scaled session capture also exposed wrapping at an exact intrinsic text width.
The owned label now enables automatic wrapping only below its shaped intrinsic
advance; this avoids a fixed-point rounding boundary when converting logical
width back to font design units. Explicit newlines and narrower-width wrapping
remain covered. This numeric boundary fix does not change visual comparison tolerances.

Pinned reference: `Sources/Sabella/Controls.swift` and `Buttons.swift` at
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`; per-case links are in
[the inventory](parity-inventory.json). Native platform APIs are implementation
details rather than Linux API requirements.

The [Tabs and segmented selection checkpoint](tabs.md) adds an `activated(value)` caller boundary that preserves `selection` bindings after input. It also covers disabled-label opacity, constrained wrapping and explicit Qt button accessibility interfaces. Earlier evidence remains historical; the new candidate records changed segmented captures separately.
