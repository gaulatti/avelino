# Native typography metrics

The owned label renderer now uses measured typography from the pinned desktop
source. It remains verification-pending for exact rasterization, system fonts,
glyph fallback and complete component acceptance. Expected source images,
reference revisions and comparison tolerances are unchanged.

The user-observable criteria are: custom-font resolution matches the source at
fractional-size boundaries; single, explicit and wrapped lines have the source's
height and first baseline; intrinsic view width rounds to the current physical
pixel grid; caller-requested sizes remain inspectable; explicit line-height
compositions retain their supplied advance; and the installed consumer preserves
these metrics through virtual X11/Wayland, both renderers and display/text scales.

[Native metric evidence](../evidence/geometry/native-typography.json) contains
2,160 direct pinned Bleecker font-expression/Text cases. The probes cover Encode
Sans and Libre Franklin, regular/medium/bold, 36 requested sizes, five text modes
and DPR 1/2. Native `Font.resolve`, CoreText metrics, measured view bounds and
first-text-baseline alignment are recorded independently. These are measured
source expressions, not new accepted component baselines. Existing native
component proposals still provide the appearance comparisons.

The source resolves custom sizes to the nearest whole point. A request of 16.5
resolves to 17. Positive requests below half a point resolve to the source's
12-point custom-font default; this discontinuity is preserved rather than
replaced by a new clamp. For nonempty text, ascent and descent round separately
in logical units: Encode Sans 14 has baseline 14 and line height 17; 21 has
baseline 22 and line height 27. DPR changes intrinsic-width rounding, not these
line metrics. Empty source Text keeps a 14-unit box and baseline 11 independently
of the declared custom font. Components can omit or explicitly size empty content
when their source composition does so.

`ButtonLabel.logicalPixelSize` retains the caller's request.
`resolvedPixelSize` reports the size used for source-family shaping and painting;
`glyphAdvance` reports the shaped advance before physical-pixel width rounding.
The renderer applies the measured rules only to the two bundled font families.
Other fonts retain their existing behavior and require separate source evidence.
Explicit `lineHeight` still sets nonempty line advance while preserving the source
baseline. Text shaping, Unicode runs and native editing stay with Qt.
The rounded line box and baseline stay in logical units through layout, avoiding
an unnecessary design-unit round trip that changed 16 into 15.999999999999998.
Both the component fixtures and independently installed consumer assert these
logical metrics exactly. Native text-field/area editing uses a separate Qt font
path and remains outside this label-metric repair.

Intrinsic width scales glyph advances and positioning separately before summing
and applying the source's physical-pixel ceil. Design-space total scaling and
compiler FMA contraction can cross an exact integer boundary and add a pixel;
regressions assert the actual source widths, including those boundaries. No
geometry or pixel tolerance is added to accommodate the difference.
Explicit tracking also includes the final glyph's spacing, as measured by the
eight existing eyebrow source cases. Their `Cards and badges` label has a
103-by-12 logical view at both DPRs, appearances and text scales. The regression
fixture exercises the public `BleeckerEyebrow` component at that boundary.

The catalog's existing reference fixtures record requested and resolved sizes,
glyph advance and scene baseline. The Qt fixture suite exercises all 2,160 source
metric cases at their matching DPR, plus button scaling, consumer overrides,
explicit line height, wrapping, empty content and input/focus regressions.
The installed consumer checks the 13-point button at text scale 1 (resolved 13,
height 16, baseline 13) and scale 1.5 (requested 19.5, resolved 20, height 25,
baseline 21), independently of the library source/build trees.

A clean extraction, verified input hashes, helper recompilation against preserved
source-verified objects and replay reproduce all 2,160 PNGs and the measurements
byte for byte. This is not a fresh full Sabella compilation. Source tooling and
Apple objects remain external at
`../avelino-reference-vault/candidates/typography-probe-20261013-39867a5/native-font-probe-replay.tar.gz`
(SHA-256 `66904facdd6e8478f347bc9b9d94ebcaeac3f0909d3e342a4a1809f6b5ba970e`).
Run its `tool/build-capture.py` and `tool/NativeCapture` into a new directory.

Reference: `Sources/Sabella/Tokens.swift` at
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`. Linux shaping uses the pinned
[Qt 6.8.3 QTextLayout implementation](https://github.com/qt/qtbase/blob/v6.8.3/src/gui/text/qtextlayout.cpp).
Screen readers, glyph assets, physical input, source-to-platform semantics and
exact images remain separate gates.

The [preserved candidate](../evidence/development/typography-repair/candidate.json) records 2,748 passing Qt checks,
34 contract checks and 40 fresh installed-package virtual-session pairs. The
component proposals are recaptured and compared at unchanged tolerances. The
[case-by-case audit](../evidence/development/typography-repair/before-after.json)
retains raw pixel improvements and regressions; no prior geometry or exact-image
pass is lost. Strict image comparisons and complete component acceptance remain
pending.

The [wrapping probe](wrapping.md) additionally measures actual Text bounds before
an external frame. Wrapped trailing spaces contribute up to the offered width;
negative glyph bearings also enlarge the source box. Qt's wrapped glyph runs omit
those spaces, while `QTextLine::naturalTextWidth()` retains their advance and ink
overhang. The renderer preserves that measured extent independently of pure glyph
advance, applies the source whitespace bound, then rounds to the physical pixel
grid. It does not add component-specific padding. The full-range pagination label
is the user-visible regression, including repeated caller resizing/updates in the
independently installed consumer.

The [alert prose matrix](alert.md) adds measured two-line wrapping boundaries
without changing font resolution or glyph advances. The [wrapping contract](wrapping.md)
records positive and negative controls and the required shared-renderer audit.

The [navigation source matrix](navigation-layout.md) adds 104 unmodified text
boundary cases at DPR 1/2. Positive final tracking is excluded when finding a
wrapped line's fit, while the resulting glyph extent remains distinct from the
proposed view width. Explicit multiline text omits positive trailing tracking
from its bounds; negative tracking retains the measured ink extent. This fixes
the page eyebrow's `FIRST\nSECOND` box and its narrow `WORKSPACE` boundary without
changing the glyph spacing. Whole-component and available-font child bounds are
checked separately from rasterization. Twenty-two source TextRenderer probes
altered pixels; their line geometry remains untrusted and these checks use the
original unmodified bounds instead. Japanese glyph fallback in `Éditions 東京`
remains unresolved and has no approved substitution or width exception.

The [data-display numeric text probes](data-metrics.md) add a clean-replayed
40-case boundary for untracked numeric strings. Native line bounds retain pair
positioning across emergency soft breaks and omit a positive final ink overhang.
The shared adapter preserves the full-string boundary adjustment for untracked
text; explicit positive/negative tracking keeps its separately measured contract.
No expected capture, font asset, tolerance or exception changes.

A separate 128-case native Medium-21 probe checks wrapped action labels and
replays after a clean build. `Create 0` at a 50-point offer measures 50 × 54 at
both DPRs. The [data-display audit](data-metrics.md) preserves twelve earlier
candidate differences caused by this correction, including four PageHeader
images whose action width now matches the existing native rectangle.
