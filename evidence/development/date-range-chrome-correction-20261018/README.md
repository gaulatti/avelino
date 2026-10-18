# DateRangePicker size-specific chrome correction

The owned presentation uses the native field/stepper differences for regular,
small, mini and large controls: 17, 15, 11 and 20 points. Field-style heights are
21, 19, 16 and 21; stepper-style heights remain 20, 18, 16 and 24. This fixes the
uniform 17-point stepper and the universal extra field-height point. The values
come from the unchanged 36-context Gregorian/Hebrew/Umm al-Qura source matrix.
The recorded reference captures, source pins and earlier evidence stay unchanged.

A source-driven regression test first fails on the old small width allocation,
reporting 17 against native 15. The failed producer19 run is retained. Producer20
passes all three Qt test runs. Backend checks derive 72 endpoint height/width
observations from actual native field/stepper pairs. Live owned-editor tests
check all 72 endpoint observations at each of DPR 1 and DPR 2, including input
width allocation, stepper visibility, zero requests and no QML warnings. Complete
ctest output is retained alongside the compiled input hashes.

The installed module runs all eight package and eight gallery profiles with both
project source trees absent at runtime. The consumer ELF is reused from the
previous fresh consumer5 build: all 148 source hashes, CMake exports, QML type
metadata and qmldir files are unchanged, and its binary checksum is identical.
The updated installed library and catalog are from producer20. This checkpoint
does not claim a new consumer compilation. Eight virtual X11/Wayland software/
OpenGL profiles and four installed catalog captures pass their runtime checks.
These are separate from physical display/input, acceleration and reader gates.

All 384 closed model/date observations still match. All 17 typed history steps
match model/lifecycle, editor identity, calendar and caller environment. Complete
closed geometry matches in 8; complete history geometry matches in 0/17.
All 401 exact whole-image comparisons execute and fail without comparison errors.
Against the previous editor-presentation checkpoint, changed-pixel counts are
lower in 23, higher in 6, and unchanged in 372. Every result is retained.
No mask, resize, reference/pin change, tolerance or approved exception is added. All six
increases occur in large-control captures. Their 20-point stepper allocation now
matches the native profile; each complete Qt field remains 100 points against
native 98. Font, reserved-text and bezel presentation still differ and remain
unaccepted.

This fixes chrome profiles, while current-label widths, script-dependent figure
spaces, named/algorithmic reserved fields, font shapes, native input and history
geometry still need work. The cold intrinsic measurements do not replace the
retained native control-size-change history. DateRangePicker remains pending;
desktop coverage is 76/80 candidates, 0/80 accepted. The other pending desktop
entries and separate 46-entry TV phase are unchanged.

Run scripts/verify-date-range-chrome-correction.py. source-specs.json binds the
compiled producer20, unchanged consumer sources and exact native matrix. Staged
Git blobs are checked against these bytes before the Linux boundary and commit.
