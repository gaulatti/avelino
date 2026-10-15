# Isolated desktop comparisons

Status: diagnostic comparisons against **proposed** reference images. No source
baseline, expected image, visual tolerance or exception approval changes here.
Desktop and television acceptance remain independent and pending.

The [selector proposal](../evidence/reference-proposals/selectors-20261013/proposal.json)
adds 80 cases, including eight anchors. Its
[strict comparison](../evidence/development/selection-native/candidate.json)
matches all 72 selector component dimensions and all eight open-popup positions
and sizes; no image is an exact match. Native popover glass/shadow compositor
output is missing from the source view caches and remains a separate open gate.
Comparison now fails on mismatched or missing popover geometry, including when
the image pixels otherwise match. Selector diagnostics run separately on x64/ARM.

The isolated matrices cover all 34 started desktop APIs: the selector and checkbox proposals,
the original 25-API
matrix and the new [composition proposal](../evidence/reference-proposals/composition-20261012-v1/proposal.json).
The latter adds 256 cases, including an unchanged button anchor. Its
[first strict comparison](../evidence/development/composition-native-before/candidate.json)
has 184 geometry and 60 exact matches; complete component acceptance remains pending.
The [composition sizing repair](../evidence/development/composition-repair/candidate.json)
raises geometry matches to 240 of 256 while exact matches remain 60. Header,
section and feed dimensions now match every captured proposal case. The button
anchor and empty footer retain geometry differences; all remaining pixel
differences stay visible, with no tolerance or reference approval.

`AvelinoCatalog --fixture reference-case` consumes the neutral case definitions in
[the desktop proposal](../evidence/reference-proposals/desktop-20261012/fixtures.json).
It instantiates the public Avelino component for the 25 implemented desktop APIs covered by this proposal,
including every proposed card/padding, progress, avatar, status, control-size and
toggle variant. The five source monospace probes have no implemented/distributable
Linux font counterpart and are explicitly excluded, rather than replaced silently.

Each component is centered in the same fixed logical frame and palette background
as its source fixture, with the requested appearance and text scale. Centering
does not force an integer logical position. The fixture retains intrinsic sizing
unless its source definition has an explicit constraint. Card/panel/attention
content slots, header slots, button-group labels, list rows, timeline content and
the original avatar test image match their source compositions. The wrapper sets
no global font or foreground override. The inherited-toggle case deliberately
exposes Avelino's unfinished font difference.

The capture records actual component dimensions and origin, visible label fonts,
baselines and geometry, alongside window dimensions, DPR, backend, compiler and
capture method. Label records describe Qt's selected face; glyph fallback and
accessibility still need separate verification. The capture driver records exact
source input and catalog-binary hashes, the reference proposal/definition hashes,
dependencies, QML import path, per-image/metadata checksums and runtime diagnostics.
Binding loops and JavaScript runtime errors fail capture verification.

Build the pinned Linux toolchain and catalog, then capture into a new directory:

```sh
docker build -f tools/Dockerfile -t avelino-toolchain:qt6.8.3 .
docker run --rm -v "$PWD:/work" avelino-toolchain:qt6.8.3 \
  bash -c 'cmake --preset linux && cmake --build --preset linux'
docker run --rm -e QML_IMPORT_PATH=/work/build/linux/qml -v "$PWD:/work" \
  avelino-toolchain:qt6.8.3 python3 scripts/capture-proposals.py \
  --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
  --reference evidence/reference-proposals/desktop-20261012 \
  --output artifacts/isolated-desktop
```

The default matrix has 724 captures across 99 fixture definitions: both appearances
and text scales 1/1.5; DPR 1/2 for ImageRenderer reference cases, measured DPR 2 for
native-control reference cases. Repeat `--api BleeckerCard` to select API families.
The driver captures in separate offscreen processes and runtime directories. Its
four-worker default changes throughput, not the selected render dimensions.

Use `scripts/compare-captures.py` with the proposal directory, Linux capture
directory and a separate report output. Repeat `--api` to select the same families
when comparing a subset. It compares case parameters, measured component geometry,
full RGB and alpha, without resizing or ignored regions. Geometry uses only a
`1e-6` logical-unit numerical precision allowance; pixel tolerance remains zero.
A geometry difference fails even when image pixels happen to match. Reports retain
the proposal's status and cannot approve a reference baseline.

The Qt 6.8 [Loader sizing contract](https://doc.qt.io/qt-6.8/qml-qtquick-loader.html#loader-sizing-behavior)
and [window capture API](https://doc.qt.io/qt-6.8/qquickwindow.html#grabWindow)
inform the fixture wrapper and capture mechanism. This is a single-window rendering
check. Actual Wayland/X11 sessions, open overlays/separate windows, input, focus,
accessibility, installed consumption and hardware checks remain separate. Qt reduced
motion is enabled; native spinner/skeleton animation phases are not matched, so
their snapshots cannot establish deterministic animation acceptance.

The first [preserved Linux candidate](../evidence/development/isolated-desktop/candidate.json)
captures all 724 cases without runtime warnings. Its [comparison report](../evidence/development/isolated-desktop/comparison/comparison.json)
has 40 exact pixel-and-geometry matches and 684 failures. These are diagnostic
results against an unapproved proposal, not 40 accepted components. The
[API summary](../evidence/development/isolated-desktop/comparison/api-summary.json)
separates geometry, pixels and missing/invalid metadata. The raw images, label
records and full pair/overlay/difference images are checksummed and preserved.

This matrix exposes a panel sizing defect hidden by the gallery's explicit width:
an unconstrained 180-pixel content slot produces a 48-pixel-wide panel rather than
228, collapsing its title into a vertical column. The timeline's non-final connector
also fills the source's available vertical allocation; the Linux fixture initially
uses only intrinsic height. These findings remain visible in this first candidate
while their repairs are captured separately.

The panel repair derives intrinsic width directly from its content slot and visible
title, avoiding the circular relationship between the card width and its full-width
internal body. A present empty title reserves the source fixture's 14-unit line box;
omitting the title removes its line box and gap. Regression cases exercise all four
paddings with present, empty and omitted titles, slot resizing, explicit constraints,
wrapping and title removal. The timeline fixture now explicitly assigns the offered
height to a non-final connector; the final item retains its natural height. This
expresses the source's vertical allocation through Qt's own sizing API and does not
change Avelino's timeline implementation or approve its remaining visual differences.

Linux CI now captures all 724 cases on x64 and ARM. Separate proposal-diagnostic
jobs compare their images and geometry with the source proposal, preserve their
reports, and fail on raw differences. The original 112-button comparison remains a
separate gate. Neither diagnostic job can adopt or approve a reference baseline.
The composition matrix also runs independently for each architecture, producing
four proposal-diagnostic jobs across the two reference groups.

The [repaired candidate](../evidence/development/panel-sizing/candidate.json) preserves
a fresh full matrix, its comparison images, 480 passing Qt checks and sixteen
installed-package window/full-output pairs across eight virtual configurations.
All 24 panel cases now match source component dimensions. The eight non-final
timeline cases also match their offered dimensions; final-title text metrics still
differ. Overall geometry matches increase from 482 to 514 of 724 cases, while exact
pixel-and-geometry matches remain 40. Shadows, borders, typography and other
differences remain visible in the reports. No component acceptance changes.

The [checkbox proposal](../evidence/reference-proposals/checkbox-20261013/proposal.json)
and [initial candidate evidence](../evidence/development/checkbox/candidate.json) add all
three checkbox sizes, boolean/disabled states, wrapped and empty labels at both
appearances, text scales and DPRs. Its 128 checkbox cases have 88 geometry matches
and zero exact image matches; eight button anchors differ in width at that
checkpoint. Small scaled typography, medium scaled height and wrapped-line spacing
are recorded failures there, superseded by the typography results below.
The scoped verifier requires every discovered control size and both APIs; coherent
checksum updates cannot hide omission of a size or the checkbox API.
The matrices now cover all 34 started desktop APIs, without accepting any entry.

The [measured typography repair](typography.md) preserves a
[fresh full candidate](../evidence/development/typography-repair/candidate.json) for all four matrices:

| Matrix | Geometry matches | Exact image and geometry matches |
| --- | --- | --- |
| Desktop proposal | 702/724 | 40/724 |
| Composition proposal | 248/256 | 60/256 |
| Selector proposal, including anchors | 80/80 | 0/80 |
| Checkbox proposal, including anchors | 136/136 | 0/136 |

The separate original button matrix remains 0/112 exact; it has no measured source
component bounds. The four proposal matrices lose no prior geometry or exact pass.
Raw changed-pixel counts increase in 22 previously failing cases; all increases,
decreases and unchanged counts remain in the [audit](../evidence/development/typography-repair/before-after.json).
The desktop's remaining dimensions concern spinner, inherited system-font toggle
and button-group cases; the composition's eight present-empty footer cases still
differ. The eight eyebrow geometries now match after retaining final tracking.
System fonts, native editing, glyph/rasterization, compositor, physical input and
screen-reader gates stay open. No baseline or acceptance changes.

The [secure-field proposal](../evidence/reference-proposals/secure-field-20261014/proposal.json)
and [candidate](../evidence/development/secure-field/candidate.json) add 40 native
masked/revealed cases and eight button anchors. All 48 root component bounds match
and zero exact images match. Fixed source typography, native properties, reveal
state and preserved caller values are recorded independently of the raw images.
All 1,338 earlier PNGs and full metadata are byte-identical, preserving the preceding
matrix results. Coverage is now 35/80 desktop candidates with zero complete acceptance.
The native replay's one three-pixel anchor variation is retained and unaccepted;
all 40 secure-field PNGs replay byte for byte. No expected image or tolerance changes.

The [search-field proposal](../evidence/reference-proposals/search-field-20261014/proposal.json)
and [candidate](../evidence/development/search-field/candidate.json) add 108 native
search/shared-field cases plus eight anchors, with 116/116 matching root component bounds and 0/116 exact images.
The comparator also verifies the actual post-clear caller value. Source clear
states are captured defocused; runtime fixtures independently verify restored
editing focus. All 1,390 preceding PNGs and full metadata are unchanged, retaining
the previous matrix results. Started coverage is 36/80 desktop APIs, with zero
complete acceptance. Native glyphs/cache/compositor, complete editing/RTL/input
methods, physical input and screen readers remain pending.

The [collection-filter proposal](../evidence/reference-proposals/collection-filters-20261014/proposal.json)
and [Linux candidate](../evidence/development/collection-filters/candidate.json) add
128 chip cases, 44 composed collection cases and eight anchors: 180/180 matching root bounds and 0/180 exact images.
The comparator also checks actual query, selected/content state and independent
activation/removal counts. All 1,510 earlier PNGs and complete metadata remain
unchanged. Eleven native replay images vary by at most one channel level and are
retained as differences without tolerances. Started desktop coverage is 38/80,
with zero complete acceptance. Curved software clipping, source symbols,
cache/color/compositor behavior, complete editing/RTL, physical input and actual
screen readers remain pending.

The [slider v2 proposal](../evidence/reference-proposals/slider-20261014-v2/proposal.json)
and [candidate](../evidence/development/slider/candidate.json) add 84 slider cases
and eight anchors: 92/92 matching root bounds and 0/92 exact images. The matrix includes actual pointer endpoint,
disabled, drag and external caller values; the comparator checks range, step,
final value and whether the binding changed. Integral interval geometry and the
source's decimal endpoint ULP are preserved. Source/Linux intermediate write
counts remain separate diagnostics.

The initial protocol replay varied in 20 images. Its source and replay pairs remain
preserved. The local animation-disabled v2 protocol with 600 ms settlement replayed
all 93 files byte-for-byte, without changing system preferences. Six source
keyboard cases remain unverified because the helper did not obtain focus. All
1,694 earlier offscreen PNG/full metadata pairs remain unchanged. Coverage is
39/80 desktop APIs started, with none accepted. Remaining source contexts, exact
appearance, physical input/display and actual screen readers stay open.

The [Tabs/segmented proposal](../evidence/reference-proposals/tabs-20261014/proposal.json)
and [Linux candidate](../evidence/development/tabs/candidate.json) add 240 comparisons:
236/240 matching root bounds and 0/240 exact images. Final selection and activation counts match; four multiline natural
width measurements still differ by 0.5 logical pixels. Native static DPR 1/2 and
local own-window pointer DPR 2 captures remain separate. The helper replayed all
241 files exactly. The comparator checks actual caller state after activation,
reselection, disabled rejection and a later external update. Strict appearance,
source keyboard/focus, physical input/display and screen-reader gates stay open.

The [pagination/icon proposal](../evidence/reference-proposals/pagination-20261014/proposal.json)
and [candidate](../evidence/development/pagination/candidate.json) add 556 comparisons:
556/556 matching root bounds and 0/556 exact images. Actual final caller page/count, request and callback counts match.
The page remains caller-owned, including ignored requests and external updates.
Long labels retain source `en_US` integer grouping. All 557 native output files
replayed byte-for-byte. Thirty-six held-press cases check down state at capture
and one callback after release. The 48 enabled ghost-symbol measurements and
152 matching child body measurements remain diagnostic; root bounds cannot
close those gates. No glyph substitution, expected image or tolerance is approved.
