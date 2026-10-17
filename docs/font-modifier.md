# Caller font defaults

`BleeckerFont` supplies a default font to retained caller content. Set required
`family` (`primary`, `secondary` or `mono`) and `size`; `weight` defaults to
`regular`. The nine weight names are `ultraLight`, `thin`, `light`, `regular`,
`medium`, `semibold`, `bold`, `heavy` and `black`. The scope reads the nearest
ancestor `bleeckerTextScale`, or `BleeckerTheme.textScale`; its own `textScale`
can be set explicitly. Size and scale must be finite in this candidate.

```qml
BleeckerFont {
    family: "primary"
    size: 14
    BleeckerText { text: "Keep edition" }
}
```

Caller fonts, bold/italic traits, paint and input remain caller-owned. Nested
scopes read their own scale without multiplying an already resolved font again.
`ProposalRow`, `ProposalColumn` and `ProposalOverlay` flatten the font scope's
emitted views; an explicit caller stack remains one view. The scope adds no
padding, background or input target. `BleeckerText` provides the owned renderer
and first-baseline guide for ordinary text in these scopes. Standard Qt text
has its own point-size quantization, including the half-point rounding in
[Qt 6.8.3 QQuickText::setFont](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quick/items/qquicktext.cpp#L1776).

## Linux candidate

Open `AvelinoCatalog --fixture font-modifier` to change family, size, weight,
caller structure, baseline parent, text scale and theme. The independent installed
consumer runs with `--font-modifier`. Its actual X11 toolbar checks deliver eight
XTest clicks across six controls and match nine complete caller viewports against
separately captured Qt fixtures. Whole window images remain available in the
[operator record](../evidence/development/font-modifier/operator-ui/result.json).

The [candidate](../evidence/development/font-modifier/candidate.json) preserves all
1,656 closed contexts: 864 caller cases, 720 first-baseline cases and 72 finite
negative-size cases. Strict comparison records **76 exact pixel/frame matches**,
1,168 frame matches, 1,440 baseline maps and all 1,656 matching produced states.
All 488 frame differences and 216 baseline differences remain in the report;
monospaced/system font mapping, noncustom line boxes, attributed runs, Unicode,
bidi and exact glyph/raster behavior remain open. No case is excluded and no
font mapping, tolerance or exception is approved.

All 382 host and 382 Linux contracts pass. The full Qt suite passes all 25 targets,
including 5,172 component checks at DPR
one and 5,400 at DPR two. The new kernel contributes 487 checks at each DPR.
A fresh independent package passes 28 modes and 123 gallery captures; all 119
prior PNGs and full metadata are byte-identical. Eight compiled-only virtual
X11/Wayland profiles exercise software/OpenGL rendering, standard/scaled displays,
caller identity, live/restored font pixels, pointer/keyboard and Qt accessibility.
Each profile measures 207 contexts, 146 exact frame sets and 180 baseline maps.
These virtual checks leave physical displays, actual readers and complete native
framework contexts pending. At this font checkpoint, desktop candidate coverage
reached 64/80, with 16 pending
and zero accepted; all 46 TV entries remain pending.

The corrected candidate reproduces every original v4 PNG byte for byte while
removing its warnings. Its shared library differs only in GNU build ID and a
generated qmldir timestamp. Original prototypes, the tiny-font metadata crash,
pending-polish observations and warning-bearing captures are preserved in the
candidate's diagnostics. An outer package wrapper invoked an already completed
gallery checker twice; its overwrite refusal and terminal exit one are retained
separately from the successful required package check.

Run `python3 scripts/verify-font-modifier-candidate.py` and
`python3 scripts/generate-font-modifier-witnesses.py --check` to audit the saved
candidate and native consumer projection. For a fresh capture, run
`python3 scripts/capture-font-modifier-cases.py <installed-catalog> <new-directory>`;
then use `scripts/compare-font-modifier-captures.py` for the complete strict
comparison. Comparison exit one preserves the unresolved native differences.

## Native source contract

`View.bleeckerFont` sets the default font for caller content. Its pinned source is
`Sources/Sabella/Tokens.swift:93–114` at
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`. It reads Bleecker text scale,
multiplies the requested size by that scale and chooses primary, secondary or
system monospaced typography. Weight defaults to regular. SwiftUI's
[font environment](https://developer.apple.com/documentation/swiftui/view/font%28_%3A%29)
supplies defaults down the caller hierarchy; individual views can override them.

The [native source record](../evidence/reference-investigations/font-modifier-20261016/investigation.json)
contains 108 fixtures across light/dark appearance, Bleecker text scales one/1.5
and requested bitmap/environment DPR one/two. All 864 public images match both
their geometry-probed and independent source-expression witness images byte for
byte. Probe and witness state collections match too. Twenty-four retained
update histories add seven steps each. This source checkpoint leaves Linux
implementation pending and changes no accepted component count.

The measured caller behavior defines these implementation criteria:

- Apply font defaults without adding padding, paint, an input target or a layout
  participant around flat content. Flat siblings keep independent allocations in
  the surrounding row, column or overlay. An explicit caller stack stays one
  participant.
- Preserve explicit inner fonts and attributed runs. A fixed caller font stays
  fixed while the modifier's scale changes. An inner scaled font reads its own
  environment. An outer system font or outer font modifier leaves the nearer
  modifier in effect.
- Keep requested size distinct from platform font resolution. The custom
  families round to whole points; zero and requests that round to zero resolve
  to 12. The measured system monospaced face preserves positive fractional
  sizes and resolves zero to 12. These are source observations, not a general
  invalid-size policy or approval of a Linux system font.
- Preserve caller identity across changes to scale, family, size and weight,
  then restore the original pixels when those inputs are restored. EmptyView,
  a zero-size view and empty Text remain distinct.

The matrix exercises all nine declared weights in all three families and fifteen
size boundaries per family. It also covers fixed inner fonts, explicit nil font,
bold/italic Text, mixed attributed runs, nested scaled fonts, a local scale below
the modifier, a separately scaled inner subtree, hidden content, rectangles,
explicit stacks, flat siblings, multiline/long/Unicode/bidi text, RTL and six
outer width offers.

At light appearance, text scale one and requested DPR one, primary regular 14
`Keep edition` measures 77 by 17 points. At scale 1.5 it measures 116 by 27.
The fixed secondary bold 13 caller remains 79 by 16 at both scales. Explicit
`Text.font(nil)` resolves through the platform default and remains 76 by 16;
it does not resume the modifier's font. Ambient-font observations still report
the surrounding primary font in both cases. They are not the resolved glyph
fonts of explicit Text-level or attributed runs.

A flat `First child` and 72-by-44 rectangle occupy separate positions. With a
40-by-12 leading rectangle, a 30-by-20 trailing rectangle and spacing 11, the
parent HStack measures 235 by 44; the VStack measures 72 by 126. At text scale
1.5 those parents measure 265 by 44 and 90 by 136. Root/styled arrays retain
both emitted frames. At width offer zero, the default Text's zero-width box is
187 points tall. At offer 40 the outer frame is 40 by 51 and the fitted Text is
35 by 51. No extra wrapper width is inferred from the font modifier.

Each update history retains one caller instance, one appearance and no
disappearance. Public, probed and witness pixels match at every step. A fixed
inner font keeps identical pixels through all updates. An inner scaled font
responds to Bleecker scale while ignoring changes to the outer modifier's font.
These are programmatic hosted updates with animation disabled, not physical
input or animation timing acceptance.

Both runs compile all 89 unchanged pinned Sabella files and build the helper
from source. A fresh extraction of the external source-only archive reproduces
all 2,761 output files, including complete metadata, byte for byte. The archive
SHA-256 is
`a4c4723f86124a6231c0e64fedf9eccdd014f038fd1af030200644fd4e65d5ce`.
Its locator and input hashes are in the
[tooling provenance](../evidence/reference-investigations/font-modifier-20261016/tooling-provenance.json).
Swift sources, native resources, executables and the archive remain external.
Independent-machine archive availability remains pending.

The recorded host has actual backing DPR two. Requested DPR one changes the
bitmap/environment request; it does not prove a physical DPR-one display.
The centered layouts never request the first-baseline alignment guide, so all
baseline maps are empty and untrusted. The separate
[typography probes](typography.md) retain their narrower baseline evidence;
this corpus does not extend it. First-baseline participation, dynamic type,
legibility settings, nonfinite Text layout, native accessibility, screen
readers and physical display/input remain pending. Monospaced Linux font mapping
and exact glyph/raster equivalence remain pending without an approved exception.

Run `python3 scripts/verify-font-modifier-source.py` to check the complete matrix,
source input hashes, untouched library build, transparent probe/witness pixels,
font environment, flat layout, font precedence, caller retention and clean
replay. References CI runs the verifier and its negative contracts. Reference
pins, expected images, tolerances and exceptions are unchanged.

## First-baseline parent supplement

The separate [baseline source record](../evidence/reference-investigations/font-baseline-20261016/investigation.json)
places the public modifier in an HStack that requests first-text-baseline
alignment. A three-by-30 rectangle supplies a reference baseline at 30. Ninety
fixtures cover all three families, all nine weights, the fifteen size boundaries,
explicit fonts, nil font, nested/scaled fonts, attributed runs, explicit stacks,
empty/zero/rectangle content and selected multiline/Unicode/bidi text. The same
eight requested appearance/scale/DPR profiles produce 720 groups.

All 720 probed images match their unprobed public images byte for byte. The
independent source-expression witness matches all measured frames and baselines,
but only 717 public images. Three strict raster failures remain: primary and
secondary ultraLight at light appearance, text scale one and requested DPR one;
and primary size 48 at light appearance, text scale 1.5 and requested DPR two.
Every original/probed/witness image remains in the matrix. The differences are
reproducible; no tolerance, excluded region or exception is added.

Primary regular 14 `Keep edition` has first baseline 14 within its 77-by-17 view.
Its parent measures 91 by 33, with both children reaching the same absolute
baseline. Fixed secondary bold 13 has baseline 13; explicit system bold 32 has
baseline 31. The background font probe still observes primary 14 for that system
Text, so ambient metrics cannot replace the actual Text baseline. Empty Text
retains a zero-by-14 view and baseline 11, while EmptyView emits no label or extra
spacing. Explicit stack baselines and child positions remain separately recorded.

The ImageRenderer run and a fresh source-only extraction both compile all 89
unchanged source files. All 2,161 raw outputs, including the three witness
differences and complete metadata, replay byte for byte. The external archive
SHA-256 is
`a1838774f37f3ec4b7d825d20ec3242293dd997761bf66e785c6754abf6739ab`.
Source-only inputs and toolchain provenance remain separate from hosted-window
and physical-display evidence. This supplement supplies first-baseline source
measurements without accepting Linux fonts, rasterization, native accessibility,
physical input, readers or complete framework contexts.

Run `python3 scripts/verify-font-baseline-source.py` to audit transparent public
probes, baseline propagation into the actual parent, complete contexts, preserved
strict witness failures and fresh source replay. References CI runs this verifier
and its negative contracts too. The centered corpus above remains unchanged.

## Finite negative-size supplement

The [finite-negative source record](../evidence/reference-investigations/font-edges-20261016/investigation.json)
measures sizes -14, -0.5 and -0.11 in each family at regular weight across all
eight appearance/scale/DPR profiles. All 72 public/probed/witness groups match
the corresponding unchanged zero-size case: each resolves to 12 points while
retaining its family. All 216 PNGs are byte-identical to those original zero-size
images. A fresh source-only extraction and full 89-file library rebuild reproduce
all 217 outputs exactly. The external replay archive SHA-256 is
`e6c15e72d08a9cb5193b83ff9e0d0200d3c10bfc8f57b814ba37b9b7811fa8f2`.

Run `python3 scripts/verify-font-edges-source.py` to verify this bounded result.
Other weight combinations, nonfinite Text layout, hosted/physical behavior,
readers and Linux acceptance remain pending. Centered baseline maps remain empty;
this supplement adds no baseline claim. Pins, expected images and tolerances are
unchanged. Linux catalog and independent-consumer integration remain pending.


Earlier full Linux CI runs on x64 and ARM64 fail Tooltip retained-popup pixels
in scaled Wayland after the preceding session sequence. Its isolated local
eight-profile replay passes, so that separate runtime issue remains open. The
font evidence above verifies the font matrix and does not claim whole-workflow
CI success. The [CI note](../evidence/development/font-modifier/diagnostics/prior-ci-status.json)
retains the exact failed step and follow-up scope.
