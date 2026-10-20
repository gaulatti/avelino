# Visible desktop admin divider

The public candidate now paints the source divider inside the existing zero-width
split handle. The input containment mask, column geometry and caller retention
are unchanged. Native observations provide the geometry and appearance-resolved
separator colour; four generated cases exercise those observations.

Both DPR 1 and DPR 2 pass 264 component tests using the current public QML and the
previously installed compiled C++ module. The source bytes and executed payload
hashes are retained. This is interpreted-QML validation; fresh compilation and
execution of an updated installed consumer remain pending. The native divider
was observed at actual backing DPR 2. DPR 1 exercises the one-device-pixel sizing
recipe, not a new native DPR 1 raster reference.

An initial controller tuple-key error, a read-only overlay-copy refusal, and two
new test failures from an unavailable QML window scale property are preserved.
The corrected test reads the actual screen scale. All 260 pre-existing cases
passed in the failed test run as well as both final runs.

Four raw rendered controls retain the before/after divider check. At DPR 2,
physical column 599 changes while adjacent columns 598 and 600 remain identical.
The full source-colour prototypes remain under the recorded artifact roots.
The standard Qt ICC conversion is exploratory: the canonical comparison refuses
all 80 ICC-managed cases pending explicit conversion review. Four pre-divider
converted diagnostics have zero pixel differences; none is accepted. No expected
image, profile, reference pin, tolerance, mask or exception was changed.

The native sidebar glass, shadow and titlebar scroll-pocket rendering remain
unresolved, alongside complete toolbar/caller, physical input and reader gates.
