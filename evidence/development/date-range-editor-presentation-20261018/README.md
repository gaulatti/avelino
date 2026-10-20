# DateRangePicker editor presentation checkpoint

This checkpoint uses pinned native font/date-style getters and unchanged original
images to improve the owned Linux editors. All 48 native before/after capture
pairs match the original source images. The 96 editor fonts explicitly request
monospaced numbers; a source-only rebuild reproduces all 97 probe outputs on the
same Mac. Apple source, platform font binaries, helper archives and executables remain
outside Avelino.

The editor requests tabular digits, reserves numeric month/day/year columns with
figure spaces, uses locale date-style number overrides (including Hebrew), and
keeps natural diagnostic labels separate from visible editable text. Full-date
and field parsing round-trip all 96 observed native dates with hidden time and
fraction retained. Japanese Gregorian blank padding is recorded from original
images; Japanese-calendar zero padding is kept distinct. Short-date getters alone
are not treated as rendered-text oracles. Fourteen observed locale/calendar
patterns and the visible override are bundled in the installed module.

The internal stepper and text alignment follow the date locale independently of
caller RTL. Synthetic Qt tests exercise both directions inside both caller layout
directions. Native-observed Hebrew and English placement and original reference
bytes remain intact. Current-label metrics replace an artificial future-year
maximum. Complete native intrinsic sizing, named-month widths, font shapes and
raster equivalence remain unresolved.

Three final Qt test runs pass. Earlier failed test evidence remains retained with
its actual exit status. A fresh independent consumer builds from the installed
prefix and runs eight package and eight gallery profiles with project sources
absent at runtime. All 384 closed model/date observations still match, as do all
17 typed history model/lifecycle, editor identity, calendar and caller-environment
observations. Complete closed geometry matches in 8; history geometry matches in
0/17. All eight virtual X11/Wayland software/OpenGL profiles and all four installed
catalog captures pass their structural/runtime checks. The four standard display
profiles each replay the complete 17-step history. Scaled profiles have no native
history in that context. No physical display, hardware acceleration, physical
input or screen-reader acceptance is inferred from these sessions.

All 401 exact whole-image comparisons execute and fail without comparison errors.
Against the previous history checkpoint, changed-pixel counts are lower in
366, higher in 18, and unchanged in 17. The default light/DPR-1 row measures
226 points against the native 222. Every regression is retained; fewer changed
pixels grants no acceptance. No mask, resize, tolerance, expected image, reference
pin or approved exception is changed.

Repeated date catalog publication previously nested fresh output inside the old
tree. The retained before/after reproduction uses actual four-capture catalog
output and proves both fresh generations replace the current tree while both
earlier generations stay byte-identical outside the temporary stage. The current
regression check also removes that stage and verifies all retained output survives.

Run scripts/verify-date-range-font-source.py,
scripts/generate-date-editor-patterns.py --check,
scripts/check-date-range-catalog-publication.py and
scripts/verify-date-range-editor-presentation.py. The final producer and fresh
consumer input hashes are bound in source-specs.json and checked against staged
Git blobs before commit. Earlier source, input, owned-editor and history capsules
remain immutable and independently verifiable. DateRangePicker remains pending;
desktop coverage remains 76/80 candidates and 0/80 accepted. The other pending
desktop entries and separate 46-entry TV phase are unchanged.
