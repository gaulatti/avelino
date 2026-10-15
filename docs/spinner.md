# Shared loading spinner contract

The pinned desktop `BleeckerLoadingSpinner` in `Sources/Sabella/Feedback.swift`
uses the platform indeterminate ProgressView with small, regular or large control
size. The actual hosted source fixtures measure 16×16 for `sm` and 32×32 for both
`md` and `lg`. Avelino now uses those intrinsic sizes and eight original capsule spokes. The
preceding 20×20 medium and single sea-colored arc remain in historical evidence.

The acceptance criteria for this shared primitive cover:

- Source small/medium/large intrinsic bounds, the default size and explicit outer
  frames; reject unknown size strings through actual QML startup.
- Measured native shape and tint in light/dark, inherited/active/inactive,
  disabled and foreground/tint contexts. Keep caller color overrides explicit.
- Loading buttons in all variants and sizes, with both text scales, plus the
  loading overlay and catalog. Verify button callback suppression while loading,
  restoration afterward, disabled behavior and actual Qt accessibility state.
- Owned Qt presentation and accessible noninteractive semantics, with no focus or
  pointer interception. Visibility and reduced-motion handling must remain
  usable; source animation timing/phase needs its own evidence.
- Independent installed consumer/catalog startup and X11/Wayland software/Mesa
  sessions at standard/scaled settings. Audit every changed preceding capture
  against source; do not replace expected images or accept a visual exception.

All source captures must render actual NSProgressIndicator descendants. The
historical ImageRenderer unsupported-view markers remain preserved diagnostics
and cannot become visual references. Native DPR 1, active-window/display,
motion phase, physical input and real reader acceptance remain separate gates.
This is native-only work with no backend, metrics, authentication or TV changes.

The hosted native investigation contains 186 context captures, including all
112 loading-button size/variant/text-scale/appearance combinations, and 144
controlled model-frame captures. The public native animation has 24 discrete
`contentsRect` values over 0.8 seconds. Applying phase zero to the native layer
reproduces the uninstrumented PNG exactly in all six size/appearance cases;
clean extraction, compilation and replay reproduce all 335 raw files exactly.
The tool links preserved source-verified objects. A fresh complete Sabella build
and a public helper download endpoint remain pending.

Avelino uses `QtQuick.Templates.BusyIndicator` for native control semantics and
owns every visual spoke. Measured native light-mode bar-center intensities drive
24 opacity patterns; the shape is original Qt capsule geometry. No native bitmap
or vector is installed. The default foreground is black in light mode and white
in dark mode; explicit caller color overrides remain supported. Native inherited,
active/inactive, disabled, foreground-style and tint probes do not change the
source pixels. The 16/32-pixel glyph stays centered inside narrower or wider caller
frames, including overflow. Unknown sizes fail actual QML startup.

Visibility and reduced motion stop animation and reset to phase zero. Explicit
`running: false` hides the content. Reduced motion keeps the loading state visible.
These are Linux behavior checks; native reduced-motion equivalence remains open.
The source snapshots expose a static model frame even after elapsed-time waits;
they do not prove physical animation cadence or synchronized phase. The hosted
dark bitmap also has a different background color pipeline from the canonical Qt
tokens. No expected image normalization or global palette change is introduced.

Run the gallery with `AvelinoCatalog --fixture spinner` and the installed consumer
with `InstalledConsumer --spinner`. The gallery includes all sizes, an explicit
color, three loading-button variants and an interactive loading overlay. The
consumer checks actual Qt progress/action interfaces, live phase changes, fixed
inner bounds, stopped/hidden/reduced-motion states, callback suppression while
loading, restoration through pointer/keyboard/accessibility actions and continued
outside editing. Actual screen-reader output and physical input remain pending.
See [source evidence](../evidence/reference-investigations/spinner-20261015/investigation.json),
[asset provenance](../assets/spinner-presentation.json) and
[the implementation checkpoint](../evidence/development/spinner/candidate.json).

The implementation checkpoint passes 3,922 Qt checks at DPR 1/2, 80 contract
tests and 16 actual invalid-startup refusals. All 15 independently installed
consumer modes pass offscreen; a fresh relocated package passes 120 virtual
window/full-output pairs and 71 catalog captures without source/build imports.
Basic and Fusion host-style captures are byte-identical.

The complete preceding 3,254 image/full-metadata pairs were audited: 3,204 remain
byte-identical. The 50 changed pairs comprise 12 spinner cases, 32 loading-overlay
cases and six gallery images. Against the same immutable native inputs, all 44
component cases have fewer differing pixels; source root geometry improves from
40/44 to 44/44. Exact image matches remain 0/44. No geometry or exact-image pass
was lost. The six gallery captures preserve full metadata and limit pixel changes
to the indicator. The whole-output Wayland scaled capture also preserves a
Weston virtual keyboard clipped at the compositor boundary; OS presentation
acceptance remains open. No mask, resize, palette normalization, source-pin or
expected-image change, tolerance or approved exception is introduced.

Coverage remains 46/80 desktop APIs started, with none fully accepted. TV is
unchanged. The public wiki is unavailable; documentation remains in this tree.
The previous checkpoint's Linux x64 and ARM build/runtime/package jobs passed,
while its strict image jobs failed; its References workflow passed. These CI
results are separate from the fresh local implementation checks above.
