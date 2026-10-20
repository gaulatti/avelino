# Native typography metrics

The [font raster investigation](font-raster-investigation.md) independently checks
physical font tables, glyph sequences, hinting and fractional placement. It rules
out the tested global snapping model and preserves the current renderer; exact
raster and complete mirror acceptance remain pending.

The owned label renderer now uses measured typography from the pinned desktop
source. It remains verification-pending for exact rasterization, system fonts,
glyph fallback and complete component acceptance. Expected source images,
reference revisions and comparison tolerances are unchanged.

The [font-modifier investigation](font-modifier.md) separately measures the
public modifier's default-font precedence, all nine weights, three families,
flat caller layout and retained property updates. Its centered layouts supply
no first-baseline measurements; the narrower baseline probes below retain their
original scope.
The separate first-baseline parent supplement measures 720 modifier contexts
with transparent public probes. All frame/baseline witness sets match, while
three expression-witness raster differences remain preserved and unresolved.

The [ActivityItem investigation](activity-item.md#proposal-and-measurement-history-evidence)
also establishes that source Text fitting depends on its resize history. The
custom-font renderer preserves measured wraps between an earlier proposal and
its pixel-rounded fitted width, checking exact previous proposals first. It
invalidates those measurements when shaping inputs or DPR change. ActivityItem
and button fixtures replay all 3,374 original standalone proposals and 48 explicit
histories; fresh instances are not substituted for persistent native sequences.
Fractional row proposals remain raw until each child returns its fitted frame.

Centered and right-aligned wrapped text also measures the whitespace retained
after alignment. The [alignment source record](../evidence/reference-investigations/activity-text-alignment-20261016/investigation.json)
contains 7,000 direction/history measurements and 768 unmodified public Text
samples. For Libre Franklin 12, `Ready for review` at proposal 40 and DPR one
fits to widths 38, 39 and 40 with left, center and right alignment. Encode Sans
semibold 14 `Edition updated` at proposal 60 fits to 55, 55 and 58.
RTL maps logical leading/trailing alignment to physical right/left; 384 matching
physical-alignment image pairs remain byte-identical across ambient directions.

The label aligns trimmed line advances against the largest trimmed advance,
retains each full line extent including trailing whitespace, then rounds the
result to the physical pixel grid. Incoming proposals stay fractional. The finite
fitted bounds constrain paint alignment, keeping ending glyphs inside the view's
clip, and feed the existing measurement-history intervals. The older
`bf30fa14` installed renderer's 614 RTL geometry failures remain preserved in
the source record; the corrected calculation matches all 7,000 measurements and
all 768 bare alignment samples without changing expected data or tolerances.

The custom `TextRenderer` probe is a diagnostic proxy: all 768 image pairs
differ from unmodified Text, and 142 fitted frames differ. Its line/run records
are not transparent observations of bare Text. Tests use the separately captured
bare frames. A fresh unchanged full-source rebuild reproduces all 1,599 outputs
byte for byte. Native helpers and the source-only replay archive remain external;
independent-machine helper availability and exact raster/physical/reader acceptance
remain pending.

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


The [font-scope candidate](font-modifier.md#linux-candidate) carries these measured
custom-font sizes and baseline guides into inherited caller content, including
flat siblings and nested scopes. Its kernel passes 487 checks per DPR. Tiny
noncustom requests now use a one-pixel raw-font lookup solely for metadata;
requested/shaping/paint sizes remain unchanged. This prevents the preserved
Qt 6.8.3 tiny raw-font family lookup crash. Monospaced/system font mapping,
noncustom line-box metrics, attributed runs, Unicode/bidi and exact rasterization
remain unaccepted in the complete 1,656-case comparison.


The [pill candidate](pill-modifier.md#linux-candidate) extends `BleeckerText` with
explicit plain/styled/rich/Markdown formats, finite line limits on Qt's supported
paths, tracking, kerning, baseline shift and accessible text. Plain callers keep
the original renderer. Formatted callers allocate separate unwrapped measurement
and displayed text only when requested, so proposal changes do not re-enter the
natural-width getter or resolve unused tiny fonts. Inline resources load on the
GUI thread before scene-graph rendering. Empty plain text keeps the observed
14-unit line box and baseline 11 across the twenty measured font/parent cases.
Native font/system-symbol/raster and full format-combination acceptance remain
pending; the capsule does not apply the custom text-scale environment.
