# DateRangePicker fixed segment reservations

This supplement preserves the desktop reference and every earlier capture. The
public calibration copies the observed settings of the pinned source's two
NSDatePickers into isolated plain AppKit controls. All 118 endpoints across 59
configurations match intrinsic size, cell size and alignment insets exactly.
All 59 original before/after image pairs equal the earlier width/style images.

The candidate sizing recipe formats a fixed set of 16 representative dates in
the active calendar and reserves each segment's largest measured advance. These
are sizing samples, not allowed-date bounds or a claim about the widest legal
label. The separate 63-context cold probe constructs dates using input year
components from 1 through 10000; all requested dates remain exact and each
context keeps its intrinsic width. Calendar construction can normalize era
boundaries, so the Japanese year-1 case is not proof of a literal year-1 label.
Font vocabulary sampling at years 1 through 9999 is retained as a failed
explanation based on the widest possible year.

The recipe was informed by implementation diagnostics. The raw diagnostic files
are labelled separately: private subfield inspection and a forwarding diagnostic
subclass are used only on isolated calibrated cells. A separate standalone tool
traces public DateFormatter calls. No private selector or class change is applied
to the pinned source controls. Diagnostic object addresses are not a replay or
acceptance oracle. The diagnostics do not establish a documented AppKit contract.

Public validation uses Calendar, DateFormatter, NSString font measurements and
NSDatePicker properties only. It independently predicts all 472 intrinsic widths
across the 59 configurations and original/Helvetica/Times/Courier fonts. All 118
original-font raw cell widths also match exactly. Sixteen extra-font raw cell
widths differ in their last floating-point bits; all raw values and failed exact
equalities are retained. There is no epsilon or approved exception. The earlier
incorrect chrome model is preserved as prior-chrome-model.json.

NSString measurement retains Latin/neutral trailing spaces but omits trailing
spaces for an RTL paragraph. Native RTL subfields reverse literal order. The
Hebrew literal therefore reserves the bet glyph's advance without its trailing
space; the year allocation is 47.48046875 points at the original regular font.
The earlier inferred 43.900390625 year residual was incorrect. The largest
reference year sample is the label for year 3920, not the largest legal year.

All Apple source, helpers, binaries, bundles and source archives remain external.
source-only-artifact.json identifies a checksummed 102-file source-only archive,
including the unchanged 89-file pinned library. A fresh extraction and library/
helper build reproduces all 380 public calibration, validation, vocabulary and
wide-year files exactly on this Mac. The diagnostic source is included but its
address-bearing outputs are not part of that exact replay. Independent-machine,
Linux font/raster, input, physical-display and reader acceptance remain pending.

The first source-only replay retains a byte mismatch in vocabulary.json caused
by Foundation's key ordering. All parsed values and the other 379 files agree.
The forward vocabulary producer writes keys in a total order; its 14 original
images and every parsed value remain unchanged. The prior output, failed replay
and both source archive manifests remain available. The successful fresh replay
compares the corrected producer's raw bytes without normalization or tolerance.

Run python3 scripts/verify-date-range-reservation.py. This evidence grants no
component acceptance and changes no reference, mask, resize or tolerance.
