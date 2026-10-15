# Alert mirror contract

The pinned `BleeckerAlert` in `Sources/Sabella/Feedback.swift` accepts a title,
four alert types and generic caller content. Its title uses primary semibold 14;
content inherits secondary 13 and the palette text color while retaining explicit
child overrides. The icon is a source system symbol. Avelino must own its Linux
presentation, with exact symbol and physical/reader acceptance kept pending.

Before implementation, the observable acceptance criteria cover:

- Default info and success/error/warning colors, alpha fill/border, rounded
  clipping, title/body alignment, fixed fonts, 14-unit padding and 12/4 gaps.
- Source intrinsic/fitted/narrow sizing, long and multiline text, empty title,
  empty text versus absent/zero content, RTL and explicit inherited icon fonts.
- Generic text, explicitly styled text, tall content and real child controls.
  Propagate the source content font/color through the documented Linux slot
  interface; keep child overrides and factory identity across producer updates.
- Caller title/type changes preserve child state. Replacing/removing factories
  destroys the previous child, and recreation starts new private state.
  Disabled descendants reject input; pointer release outside does not activate.
- Independently installed consumer/catalog startup, actual Qt accessibility and
  keyboard/pointer behavior, continued outside editing, host-style isolation and
  separate X11/Wayland software/Mesa evidence at both scale profiles.
- Immutable pinned-source captures and geometry/state witnesses, clean external
  helper replay, strict source comparisons and all preceding capture regressions.

No source pin, expected capture, tolerance or exception may change. Backend,
authentication, metrics and TV are outside this native desktop change. The public
wiki is unavailable; this repository owns the current documentation.

The Linux content slot is a stable Component factory. It receives `availableWidth`,
`font` and `foregroundColor`; caller-owned labels bind those values and may
explicitly override them. `maximumWidth` supplies a finite source-style proposal;
`-1` requests intrinsic sizing, following the existing button proposal interface.
Outer `width`/`height` reserve a caller frame around the centered fitted alert.
This separates intrinsic measurement from the finite proposal and avoids a
circular dependency through a wrapping generic child's implicit width.
The default type icon uses original Linux artwork at measured source frames;
a caller-owned `icon` Component can supply a resolved asset/context. Broader
font/symbol-context equivalence remains pending.

The source investigation preserves 248 alert captures and eight button anchors,
96 actual native pointer/lifecycle records, 16 separate icon expressions and 96
isolated text-layout cases. All 256 component and 96 text instrumented renders
are byte-identical to their untouched counterparts. Clean extraction of 37
verified inputs, helper recompilation and replay reproduce all 722 raw files
exactly. Pointer records report actual native DPR 2 and inactive window/application
state; static ImageRenderer cases cover DPR 1/2. These are separate evidence paths.
The helper links preserved pinned-source objects; fresh full source compilation
and public helper distribution remain pending.

The default original `AlertGlyph` uses measured native frames: 15×15 for the three
circles; the error triangle is 16×15 at DPR 1 and 16.5×14.5 at DPR 2. The source
20-point parent-font context is represented by a caller-owned icon Component
with its measured 24/23-unit circle frames. No SF Symbol resolver or Apple asset
is installed. Arbitrary symbol/font/fractional-scale contexts and exact artwork
remain unaccepted.

The owned fill and border use separate rounded rectangles so the 9% fill remains
under the 24% inset border, including translucent compositing. Both use the
source circular 7-unit radius. Circular generic-content clipping uses the Qt
curve renderer in RHI sessions and the [shared software adapter](content-clipping.md)
in software sessions. Both consume the same circular path. Strict native overflow
and complete clipping acceptance remain pending; no visual exception is approved.

Run `AvelinoCatalog --fixture alert` for the four types, generic editable content,
explicit text styling and hide/show lifecycle. The independent `--alert` consumer
checks real pointer/keyboard/accessibility activation, disabled guards, title/type
updates without replacing the child or losing editing focus, replacement/removal
and fresh private state, narrow fitting and continued outside editing. The
component tests additionally replay all 96 source lifecycle transitions at both
Qt DPRs. Source keyboard equivalence and actual reader output remain pending.

The custom 18-point body exposed a shared wrapping difference. The
[prose measurements](../evidence/geometry/native-alert-text-layout.json) establish
that the native two-line examples keep a final token of at most ten measured
ASCII characters with its predecessor when both fit. Longer final tokens and
longer paragraphs retain their prior breaks. Short numeric tokens follow the
same measured rule; the full-range numeric labels remain unchanged. The
shared renderer is checked against the new 96-case matrix and the existing
numeric/centered-text metrics; no label string or alert-specific width is used
in its implementation. Broader language, script and line-breaking contexts remain
pending. See [wrapping](wrapping.md) and [source investigation](../evidence/reference-investigations/alert-20261015/investigation.json).

The first shared-rule run exposed four loading-message pixel regressions in the
full old-image audit. It is preserved as a diagnostic and is not substituted for
the corrected run. The [boundary investigation](../evidence/reference-investigations/prose-boundaries-20261015/investigation.json)
adds explicit 10/11-character and narrow/wide-glyph controls, short numeric
controls, both font families and independent ImageRenderer/native-host contexts.
A clean 37-input replay reproduces all 179 output files. Its 84 trusted Qt cases
exclude a hosted primary18 TextRenderer witness that changes source pixels;
that raw witness remains diagnostic. Broader Unicode/grapheme segmentation is
unaccepted. This boundary is measured behavior, not an alert-specific string or
font-family exception.

Opaque source Color.red samples also differ from Qt's named red. The reference
content uses measured native light/dark values through `BleeckerTheme.nativeRed`;
`alert-symbols.json` records the exact source image/pixel witness. Bleecker's
separate destructive palette tokens are unchanged.

The corrected checkpoint passes 4,552 Qt checks, 84
contract tests and 20 actual invalid-startup refusals.
All 16 installed consumer modes pass offscreen. A fresh
relocated package passes 128 virtual window/output
pairs and 75 catalog captures; Basic/Fusion gallery
images are byte-identical. These runs use all 239 recorded source inputs and
do not substitute the preserved first pass.

All 3,258 preceding PNG/full-metadata pairs were audited:
3,258 are byte-identical and 0 changed.
The new 256 source comparisons match all 256
root bounds; 0 pass exact images. The case-by-case audit records
zero lost geometry or exact-image passes, without a tolerance, source-pin or
expected-image change. Complete glyph/raster, software rounded overflow,
broader font/script/composition and physical/reader acceptance remain pending.

Coverage is 47/80 desktop APIs started, with none fully accepted. TV is unchanged.
The prior main checkpoint's x64 and ARM build/runtime/package jobs passed; its
strict image jobs failed and References passed. These remote CI results remain
separate from this checkpoint's fresh local evidence. See
[the complete record](../evidence/development/alert/candidate.json).
