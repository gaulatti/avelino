# Native date editor font and format investigation

Read-only public NSFont, NSDatePicker and DateFormatter getters extend the pinned
reference investigation. All 48 before/after captures are identical to each other
and the earlier public source PNGs. No reference image/pin or source is changed.
The 96 observed editor fonts explicitly carry number spacing type 6, selector 0,
which the installed SDK names monospaced numbers. Figure-space and Latin digit
advances agree. Family/shape/raster equivalence on Linux remains unaccepted.

The plain string and attributed-string getters describe the complete date in the
host time zone, rather than the visible date-only fields. The separately measured
locale short-date patterns explain some formatting, including Japanese-calendar
zero-padded month/day fields and Hebrew numerals. The original Japanese Gregorian
image instead shows blank-padded month/day fields, unlike its short-date getter;
visible-pattern-observations.json records that distinction and its image hashes. Native date fields show the full year even when the
locale short-date pattern abbreviates it. These getters and original visible
captures must be considered together; a string getter is not a rendering oracle.

Failed actor-isolation compilation and successful attempts are retained. Raw
pointer-bearing feature descriptions from attempt2 remain there; attempt3/4 encode
public feature identifiers structurally. All Apple tooling, source, resource
bundles and executable products remain outside this Linux repository. Their
checksums and locators are recorded; no font binary or Apple implementation is
included. No additional OS input, reader, physical-display or Linux acceptance is
claimed. The original source-only artifact and native reference pins remain fixed.

A fresh source-only archive replay extracted 93 members (89 pinned source files
and four helper/input/runner files), built without precompiled products, and
reproduced all 97 output files exactly on this same Mac. The immutable external
archive locator, checksum, build receipt and output hashes are retained under
source-only-replay/. This is not independent-machine or Linux acceptance.
