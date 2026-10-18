# DateRangePicker fixed field-width checkpoint

The owned field now reserves each formatted segment from the native sizing
samples, independently of its current date. It uses the active ICU calendar,
locale, number-format overrides, time zone and system date-field font. The samples
are not input bounds or an arbitrary assumed maximum year. Half-point rounding
and the previously verified control-size chrome are applied after measurement.
Visible single-string editing/padding remains; this fixes the overall reserved
width without claiming complete segment positions or font/raster equivalence.

The native supplement records 118 exact calibrated endpoints, 472 exact public
intrinsic-width predictions and a fresh source-only replay of 380 public files.
Original-font raw cell predictions match all 118 endpoints. Sixteen extra-font
raw cell last-bit differences remain recorded with no epsilon or exception.
Private implementation hints and the public sizing validation are labelled
separately; the source controls and pinned reference captures stay unchanged.

Producer21 first reproduces width jitter in the previous implementation (88 to
90 points in the owned editor). Producer22 passes the first correction. Producer23
passes all three final Qt test runs, with exact-equality checks at all 1,848
native caller updates, 3,696 endpoint widths and 92 fresh endpoint widths per
owned-editor DPR. It also checks 118 independently captured native font-sample
sets through the Linux ICU/font measurement path. Retained editor pointers,
exact displayed dates, zero requests and no QML warnings are checked. Existing
input, owner, teardown, calendar and 72 chrome-profile checks still pass.

The installed module runs eight package and eight gallery profiles with both
project source trees absent. The unchanged consumer5 ELF is reused after checking
all 148 source hashes, public CMake/QML package contracts and its binary hash.
This is a compatibility replay, not new consumer compilation. Eight virtual
X11/Wayland software/OpenGL profiles and four installed catalog captures pass.
Physical display/input, acceleration and screen-reader acceptance remain pending.

All 384 closed model/date observations and all 17 history model/lifecycle, editor
identity, calendar and environment observations still match. Complete closed
geometry matches in 8; complete history geometry
matches in 0/17. All 401 whole-image comparisons
execute and fail without comparison errors. Against the preceding chrome
checkpoint, changed-pixel counts are lower in 16, higher in
46 and unchanged in 339. Every failure remains.
No reference update, mask, resize, tolerance or approved exception is introduced.

DateRangePicker remains pending. Candidate desktop coverage stays 76/80, strict
accepted coverage 0/80, and the separate 46-entry TV phase remains pending.
Source specs bind producer23, the reused consumer, native validation bytes and
all integration edits. Run scripts/verify-date-range-reservation-checkpoint.py.
