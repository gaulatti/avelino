# Native date field width investigation

The unchanged pinned Sabella component is driven through public caller date
bindings. Fourteen regular locale/calendar contexts cover three calendar years;
nine additional small/mini/large contexts cover the current year. All 1,848
updates retain constant intrinsic widths within each of the 23 contexts. Both
pickers report the requested date in all 3,696 observations, with no binding
requests. The minimum/maximum formatter-text cases are repeated with cold
controls: all 46 retained/cold image pairs match exactly, as do all 23 initial
and restored image pairs. All 48 baseline before/after pairs also match the
original source captures. No reference, pin, image mask or tolerance changes.

For regular controls, examples include en_US Gregorian 95, ar_EG Gregorian and
fa_IR Persian 91.5, he_IL Hebrew 139.5, ja_JP Japanese 104.5, ar_SA Umm al-Qura 162,
and en_US ISO 99.5 points. These are complete intrinsic control widths, not text
advances or pixel-snapped alignment frames. Large controls retain the regular
13-point font but add three intrinsic width points. Font, chrome and calendar
field reservation must therefore be kept distinct.

The raw key initialEditors in output/widths.json is assigned after restoration
in the helper. It is a restored-editor observation and is never used as a
pre-update intrinsic observation. Baseline rows and the cold extrema are separate
observations. The image restore check compares actual initial/restored PNGs.

Direct per-picker public accessibility/frame getters extend the measurement.
All 23 before/after pairs are unchanged and match the corresponding width-probe
initial images. The exposed hierarchy has an AXDateTimeArea and an AXIncrementor
with buttons. It does not expose month/day/year child rectangles in this context.
Accessibility rectangles are recorded separately from alignment/intrinsic sizes;
these getters establish no pointer hit-test or reader acceptance. Cold small
Hebrew intrinsic/alignment height is 18; this does not replace the separately
retained control-size-change history or its geometry observations.

A source-only archive containing 89 unchanged pinned files and six helper/input/
runner files is freshly extracted and built without precompiled products. It
reproduces all 282 width/bounds output files exactly on the same Mac. The same
freshly source-built helper also reproduces 73 additional style-matrix files
from the separately provided deterministic JSON fixture input. The total is 355
exact output files; the archive remains immutable at 95 source members. The earlier
235-file width-only replay is retained. Archive locators, checksums, member hashes
and command receipts are recorded; all Apple source, tooling and products remain
outside Avelino. A failed CGFloat/Double helper run is preserved. The investigation
adds no native input, physical display, hardware acceleration, independent-machine,
font/raster or Linux acceptance. DateRangePicker remains pending.

The supplemental 36-context field/stepperField/compact matrix covers Gregorian,
Hebrew and Umm al-Qura calendars at all four control sizes. Stepper-style minus
field-style intrinsic widths are 17 regular, 15 small, 11 mini and 20 large.
Field-style heights are 21 regular, 19 small, 16 mini and 21 large, while stepper
heights are 20, 18, 16 and 24. Regular and large field-style images are byte-exact
in all three calendars. The earlier width helper failed after capturing its
style baseline because it requires its original baseline IDs; that attempt is
preserved, and the arbitrary-fixture getter helper supplies the completed matrix.
