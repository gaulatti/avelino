# Search-field candidate

`BleeckerSearchField` mirrors the pinned search wrapper and its shared text-field
path. It provides a fixed magnifier and a clear button only while text is nonempty.
It remains verification-pending for exact images, glyphs, native editing/focus,
context menus, input methods, RTL, physical input and screen-reader output.

The observable criteria are caller-model editing and external updates, pointer
and keyboard clearing exactly once, restored editor focus, removal of the empty
clear action and padding, disabled/read-only enforcement, Return acceptance,
disabled tab traversal, constrained scrolling, source sizes/scales and installed
consumption through X11/Wayland and both renderers.

```qml
BleeckerSearchField {
    width: 300
    placeholderText: "Search editions"
    text: search.query
    onTextEdited: search.query = text
    onAccepted: search.submit()
}
```

Applications own searching, persistence and requests. The library owns editing
and the clear action. Qt's `clear()` changes text without emitting `textEdited`;
the user-facing action emits that signal once after clearing so the normal caller
binding stays synchronized. It returns focus to the editor. `readOnly` is the Qt
editor extension and also disables clearing.

`BleeckerTextField` now has `leading` and `trailing` Component slots, following the
existing selector slot convention. Their measured widths reserve a ten-unit gap;
removal restores the original padding and height even when a Loader retains its
previous dimensions. Source horizontal padding is 12/14/16 and minimum height
36/40/44, multiplied by text scale. Default editor typography is primary regular,
12 for small and 14 otherwise, with text scaling; explicit caller fonts remain
available. The regular default overrides a bold ancestor, matching the source.

The search companion supplies the source magnifier/clear behavior through these
slots. Use it for the source `systemImage: "magnifyingglass"` presentation. Other
Linux artwork can be supplied through slots without interpreting arbitrary Apple
system-symbol names. The search wrapper inherits the text-field size/error APIs;
the source search wrapper uses the default medium field. The native matrix also
exercises the source text field's search presentation at all three sizes and its
error state. Linux captures use the public search companion for this shared path.

The fixed magnifier allocation is 16.5 units; the clear action is 18.5 with four
units of internal padding and radius four. These allocations follow native editor
frame differences, including AppKit's two-unit alignment inset. They do not scale
with text. Original Canvas magnifier/xmark candidates and their
[provenance](../assets/search-field-symbols.json) remain unaccepted for exact
system-symbol equivalence. Editor colors and the existing field surface stay on
the established shared path; native cached ink/rasterization remain unresolved.

The [native proposal](../evidence/reference-proposals/search-field-20261014/proposal.json)
contains 108 native search/text-field cases and eight button anchors: empty,
filled, long, disabled, constrained and post-clear states, both appearances/text
scales, all three shared field sizes, and field error cases. Clear is triggered
through the helper's own button and its actual binding value is checked. Captures
are defocused native view caches at measured DPR 2. Native DPR 1 and compositor
acceptance remain separate. The comparison rejects an incorrect post-action value
even with otherwise identical images.

Clean extraction, input hash verification and helper recompilation reproduce all
108 search/text-field PNGs and capture data byte for byte. One scaled DPR 1 button
anchor varies by three pixels at channel level one, retained without a tolerance
or expected-image update. Recompilation links preserved source-verified objects;
it is not a fresh full Sabella build. Native tooling stays external at
`../avelino-reference-vault/candidates/search-field-20261014-02ac648/native-capture-replay.tar.gz`
(SHA-256 `a6b1a63877b3ef4df90acd2ae51d9a56ca6f933c9ca01422cf80d76304c065c7`).
Run `tool/build-capture.py` and `tool/NativeCapture` in a clean extraction with a
new output directory. The scoped verifier rejects API, state, size, font and
post-clear binding omissions even after coherent checksum changes.

Use `AvelinoCatalog --fixture search-field` for the gallery and
`InstalledConsumer --search-field` for editing, pointer/keyboard clear, caller
binding, Return, traversal, fixed slots and actual Qt editor/action interfaces.
The explicit `Clear search` Button role/name is a Linux semantic mapping;
interface queries do not establish native or screen-reader equivalence.

Reference: `Sources/Sabella/Controls.swift:35-95` at
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`. The pinned
[Qt 6.8.3 TextInput clear implementation](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quick/items/qquicktextinput.cpp)
defines the programmatic-edit signal boundary.

The [checksummed candidate](../evidence/development/search-field/candidate.json)
preserves all 116 strict comparisons: 116/116 matching root component bounds and 0/116 exact images.
All 2,846 Qt checks and 41 contract checks pass. Fifty-six fresh package-only
virtual-session pairs include eight for search editing, caller updates,
pointer/keyboard clear, Return, focus, disabled traversal and actual Qt interfaces.
Default/Basic/Fusion gallery PNGs at DPR 2 are byte-identical. All 1,390 preceding
PNGs and complete metadata are unchanged. The slot-removal test guards retained
Loader dimensions; the font test guards source regular weight under a bold host.
No expected image, reference pin, tolerance or approved exception changes.
