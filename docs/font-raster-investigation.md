# Font raster investigation

This checkpoint diagnoses button-label raster differences without changing the
renderer, fonts, expected images, tolerances, exceptions or API acceptance. Its
implementation snapshot is `86334226962e67d2a102b6bed720fe723a7eaae3`.
The [raw capsule](../evidence/development/font-raster-investigation-20261019/result.json)
retains 26,496 PNGs in four ZIP archives: 5,760 SwiftUI source/witness images and
20,736 direct CoreText experiments. Archive members preserve original PNG bytes.
Apple helpers stay external; their hashes, commands and raw logs are retained,
including the first failed helper compilation.

## Font and hinting controls

The Linux Qt 6.8.3 probe reproduces the label's design-unit shaping and physical
paint-face selection for Encode Sans and Libre Franklin, regular/medium/bold,
sizes 12/15/18/23, and `Short`, `Tall`, and `Keep edition`: 72 profiles. Eleven
font tables agree with the bundled files and native faces in every profile.
All glyph sequences match; the largest observed position delta is approximately
`1.42e-14` logical units. Native font/glyph traces agree across appearance and DPR.
This narrows the tested boundary without proving other strings, fallback fonts,
wrapping, attributed text or rasterization. It does not support changing weights
or the established metric rules.

The installed package renders eight canonical button-group contexts with each
of four Qt hinting preferences. Default controls reproduce all eight compiled
catalog PNGs byte for byte. All 32 geometry checks pass; no image is pixel-exact
against the preserved source. Total changed pixels are 7,584 for default/vertical
hinting, 7,551 for no hinting and 7,339 for full hinting. Aggregate improvement
does not establish source behavior; no hinting policy changes. The first probe
omitted the opaque capture background and failed its compiled control; its
output and failure remain separate from the repaired probe.

## Draw and placement controls

Public source typography/palette primitives produce 288 contexts. Each bare Text
image equals its geometry/baseline witness byte for byte. Versions 2, 3 and 4
preserve all 288 source controls and previously generated direct-draw PNG bytes.
The source library object is reused after validating 53 scoped pinned source
files; this is not an independent rebuild or replay.

CoreText variants cover opaque draws, smoothing/subpixel options, vector outlines,
transparent glyph layers and flattened layers. None reproduces every source
pixel. Mode 17 draws a transparent glyph layer with all three font options
enabled, then composites it over the background. It has 113,871 changed pixels;
140/288 profiles have maximum channel error one.

Mode 19 additionally rounds the horizontal draw origin upward to a physical
pixel; mode 20 rounds it downward. Upward rounding leaves maximum channel error
two in all 288 original profiles, still with zero exact images. That observation
does not establish a general placement rule.

Version 5 adds an offset wrapper and seven horizontal offsets from -0.75 to
0.75 points: 2,016 source/witness pairs and 6,048 direct-draw comparisons. Only
286/288 zero-offset source controls retain their bytes. The two changed controls
differ by ten and five pixels, each by one channel level. The wrapper and expanded
capture order cannot be treated as transparent instrumentation of the earlier
fixture. The initial audit requiring all controls to match fails and is retained.

Mode 19 has channel error up to 212 in this expanded matrix; only 1,728/2,016
profiles stay within two levels. Quarter-point offsets expose the failures.
No direct-draw profile is exact. The global upward-rounding model is not promoted
into the renderer. Further work must preserve the actual component composition
and distinguish layout origins, glyph placement and subsequent transforms.

## Recheck and scope

```sh
python3 -m pip install -r tools/visual-requirements.txt
python3 scripts/verify-font-raster-investigation.py
```

The verifier checks inventories/hashes, decodes the archived pixels, checks all
2,880 measurement pairs and prior controls, recomputes comparisons, parses bundled
TrueType tables, compares font/glyph traces and checks hinting controls. It does
not rebuild the package or rerun native helpers. It records observed failures
with zero tolerance and grants no exception.

The existing button-group checkpoint retains 128/184 exact images. These isolated
diagnostics do not replace component source controls or increase that count.
Physical input/display, readers, independent-machine and complete mirror gates
remain pending. Desktop acceptance remains 0/80.
