# DateRangePicker reference contract

The owned Linux component is under implementation; its inventory entry remains
pending until the complete candidate verification is recorded. The pinned desktop source is
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`,
`Sources/Sabella/Extended.swift:63–68`. Its two independent date bindings are
presented by date-only native pickers, with an arrow between them. A supplied
closed range applies to both fields. The source imposes no ordering between the
bindings: crossed start/end values remain crossed. From/To labels are hidden
visually; visible inactive native accessibility getters still expose those labels.

The [native investigation](../evidence/reference-investigations/date-range-20261018/README.md)
retains 48 fixtures across light/dark, text scale 1/1.5 and logical DPR 1/2:
384 contexts and 1,152 unmodified images. Public, outer-probed and literal source
branches agree in pixels, model values and observed outer geometry. The direct
sizing matrix retains the actual outer probe and includes 17,280 proposal
results. These observations use macOS 27.0 build 26A428, SDK 27.0 and Swift 6.4;
the compiler's macOS 26 deployment floor is not the observed operating system.
Actual window backing DPR is 2 even when the logical fixture DPR is 1.

In the default en_US/UTC/Gregorian, regular, light, text-scale-1, DPR-1 context,
the picker measures 222 by 20: two 95-by-20 fields, a 16-by-12 arrow and two
8-point gaps. Its native date-picker view is 98 by 24, with alignment insets
top 4/right 3. Caller width 100 does not shrink the component; it overflows its
centered caller frame. Preserve fractional measurements at other DPRs instead
of treating the default dimensions as universal constants.

Date fields use the observed system date-field font, not the parent's EncodeSans
or supplied 28-point bold font. Parent font changes still affect the arrow and
overall geometry. Control size, locale, calendar, time zone, inherited styles,
disabled state and RTL belong to the contract. Field style measures 188 by 21
and graphical style 309 by 148 in the default DPR-1 context. Automatic, compact
and stepperField match the default stepper presentation on this host; an iOS
compact popover is not established by those macOS observations. Hebrew, Persian,
Japanese, Islamic and ISO calendars produce distinct field widths and values.

Raw model dates and sub-day time values survive closed-state rendering. An
out-of-bounds native field displays a clamped date while the binding model stays
unchanged and emits no request. This is presentation clamping, not permission to
rewrite caller values. The crossed, equal, single-instant-range, endpoint,
fractional, pre-epoch and zero fixtures preserve their raw observations.

Seventeen typed history steps agree across all three reference branches in
images, model values, native picker properties and weak native instance IDs.
Nil-to-supplied-range and supplied-to-nil changes recreate native picker objects;
changes between supplied bounds retain them. The caller wrapper survives both.
The helper switches its outer ViewBuilder branch for explicit styles, so the
observed wrapper remount there is specific to that helper structure. History
changes are typed model/configuration updates and do not prove keyboard editing
or binding-owner response to native input.

A fresh unmodified 89-file source build succeeds. Extracting and rebuilding a
source-only archive reproduces all 1,206 cold, sizing and history files exactly
on this machine. Source and Apple tooling stay outside this Linux repository;
their checksums, locators and command receipts are retained. Independent-machine
availability remains pending. Resource-bundle, actor-isolation and interactive
helper failures remain documented alongside the successful attempts.

The first two visible helpers could not be acquired through CUA:
`cgWindowNotFound`. A third uses matching app/executable names, explicit desktop
space presentation and the current activation API; CUA can acquire it. These
changes were made together, so the recovery is not attributed to one cause.

The [native input supplement](../evidence/reference-investigations/date-range-input-20261018/README.md)
retains 116 state observations, 82 OS events and 168 root/popup images. Twenty-one
milestones cover default keyboard/numeric/stepper/calendar input, independent
endpoint edits, owner echo/ignore/delay, bounds, disabled input, graphical preview
and field style. Ignore and delay each produce identical source images and binding
values across the public, probed and literal variants. These observations use
light appearance, text scale 1, logical DPR 1, actual DPR 2, en_US/Gregorian/UTC;
they do not establish other contexts or reader/physical acceptance.

The native display can advance while an ignoring/delayed owner retains its old
model. A caller configuration update restores the ignored value; applying a
delayed value commits it. Default keyboard, stepper, pointer-calendar and field
edits preserve the observed hidden time/fraction. An out-of-range year edit clamps
to the exact bound, replacing hidden time. Graphical Right-arrow navigation
previews the next day with hour/minute/second retained and the fractional second
discarded, without a binding request; Space commits that whole-second value.
Graphical pointer selection preserves hidden time. An end-date edit can cross
start without reordering. Disabled pointer/Up input emits no additional request.

CUA's compact AX date string can differ from the UTC visual day at midnight;
retain and compare raw NSDate values and source images. The interactive helper
also has a source-only extraction and fresh library/app build, without prebuilt
inputs; that rebuild does not replay OS input. Complete traversal, parsing and
cancellation, additional locale/calendar/time-zone/owner/style histories,
non-finite/extreme inputs, the owned Linux presentation, catalog, installed
consumer, strict comparisons, display sessions, input, scaling, readers and
physical acceptance remain required. No mask, tolerance, reference-pin change or
approved exception is introduced.

The [interpretation correction](../evidence/reference-investigations/date-range-interpretation-20261018/README.md)
preserves the earlier incorrect midnight description and the Linux regression
that exposed it. Timestamp 1710345600 means March 13 at 16:00 UTC. All native
observations, PNGs and reference pins remain unchanged.

Recompute the retained source observations with:

```sh
python3 scripts/verify-date-range-source.py
python3 scripts/verify-date-range-input.py
```

## Current Linux implementation

`BleeckerDateRangePicker` exposes independent `start` and `end` Unix-second values,
optional `range: {lower, upper}`, and `startRequested`/`endRequested` signals. The
owner decides whether to echo, ignore or delay requests. It also exposes `locale`,
`calendar`, `timeZone`, `pickerStyle` and `controlSize`. Presentation clamping does
not rewrite caller values, and crossed endpoints remain independent.

The ICU-backed calendar layer preserves Foundation Date double construction,
hidden time, locale/calendar segments and range endpoints. The owned Qt template
editors include field, stepper/overlay and graphical presentations. Optional range
presence chooses distinct editor components, while supplied-bound changes retain
the editor. The caller wrapper is retained. Graphical keyboard preview retains
whole-second time and drops the fraction; pointer selection retains it.

The catalog route is `--fixture date-range`. Its gallery changes bounds, crossed
values, owner policy, style, locale, calendar, time zone, size, RTL, caller width,
disabled state and theme. The independent installed consumer route is
`--date-range`; `--date-range-report PREFIX` writes observations and unchanged
captures, and `--date-range-gallery` exercises the gallery's actual operators.
`--date-range-observe` retains exact native model/geometry differences while
structural and input failures remain fatal. It grants no acceptance.

`python3 scripts/generate-date-range-witnesses.py --check` verifies that the
consumer's 384 native observations are the deterministic projection of the sealed
source capture journal. Local Qt tests cover exact native timestamp/calendrical
observations and synthetic owned-editor input; these are separate from native
CUA input. Current builds, test results, package execution, strict capture
comparisons and display-session evidence must each be reported separately.

Parsing/cancellation and traversal beyond the retained native histories,
non-finite/extreme behavior, complete native history geometry/raster acceptance, arbitrary
caller fonts, strict raster/geometry equality, reader and physical acceptance
remain pending. The original four pending desktop inventory entries and all 46 TV
entries remain pending; registration does not change candidate coverage.

The consumer resolves its installed QML import directory relative to its executable,
using the relationship established by CMake. Moving that executable and installed
prefix together therefore preserves imports without a build-time absolute path.
The first virtual-session attempt retained a missing-module failure after changing
the runtime mount path; the repeated source-absent package/session checks pass after this repair.

## Recorded implementation checkpoint

The [owned-editor evidence](../evidence/development/date-range-owned-editors-20261018/README.md)
records three passing Qt test runs, eight source-absent package/gallery profiles,
four installed catalog captures and eight virtual display profiles. All 384 native
model/displayed-date observations match; complete geometry matches in 8. All 384
strict raster comparisons execute and fail. The default Linux row measures 232
points against the reference's 222. These failures remain open with no baseline,
mask, resize, tolerance or exception change. DateRangePicker stays pending and
candidate coverage remains 76/80; no desktop entry is accepted.

The relocated consumer repeats all 560 package output files exactly after the
import-path repair. The earlier missing-module display run is preserved. Xvfb,
Weston and software-rendered OpenGL sessions are virtual runtime evidence;
physical display/input, hardware acceleration and reader acceptance remain pending.

## Retained history replay

The installed consumer projects the 17 typed native caller updates into explicit
initial, external-date, configuration, appearance and restore actions. The helper
checksum is retained with those actions; Apple source stays outside this repo.
The fixture replaces complete configurations when the source removes optional
bounds, and patch-style gallery updates still merge caller values.

The replay assigns editor IDs from actual weak Qt object pointers. It records
model/lifecycle, displayed dates, calendar parts, locale/calendar/time zone,
control size, enabled/RTL/appearance, and complete geometry separately. The native
source's final restore has current 95-by-20 editors but retains a 148-point outer
probe height from the preceding graphical step. Both native observations remain
unchanged. Raw outer frames do not establish current outer layout; raster and
complete geometry acceptance remain separate and pending.

The owned-input test also removes the caller while Up, Left or Tab commits a
partially typed field, requiring one request, actual destruction and no QML
warnings. This is synthetic Qt input and does not establish additional native OS
input or physical/reader acceptance.

The [history checkpoint](../evidence/development/date-range-history-20261018/README.md)
records exact model/lifecycle, editor identity, calendar and environment matches
at all 17 steps. Complete geometry matches at none of those steps. All 401 strict
closed/history image comparisons execute and fail; all 544 earlier package images
are unchanged. The native pins, reference PNGs, masks and tolerances are unchanged.

## Editor font, fields and locale direction

The [native font investigation](../evidence/reference-investigations/date-range-font-20261018/README.md)
records explicit monospaced-number font features for all 96 editors. Its 48 pairs
of before/after images match the original native captures exactly. A fresh build
from the external source-only archive reproduces all 97 output files on the same
Mac; this does not establish independent-machine or Linux font acceptance.

The owned editor now requests tabular digits and reserves two numeric month/day
columns and four year columns with figure spaces. Its editable segments and
selection offsets use that visible representation. Natural date labels remain
separate. Parsing removes the padding and retains hidden hours, minutes, seconds
and fractions. Named and algorithmic calendar fields retain their locale number
format; the tests round-trip all 96 observed native editor dates and fields.

The editor-presentation checkpoint's pattern resource was generated from 14
observed locale/calendar date-style patterns and original visible images. The
current resource also includes the three Chinese-calendar presentations below. Foundation
short-date patterns alone do not describe NSDatePicker rendering: Japanese
Gregorian visibly uses blank-padded month/day fields, whereas the Japanese
calendar uses leading zeroes. The recorded override is bound to both original
images. Unmeasured contexts use ICU's short-date algorithm and remain unaccepted.
Run `python3 scripts/generate-date-editor-patterns.py --check` to verify the
resource. The resource is part of the installed module, including source-absent
consumer execution.

Stepper placement and text alignment follow the date locale's direction while
the caller's layout direction still governs the enclosing row. Native English
editors keep their right-side steppers inside an RTL caller; Hebrew editors put
their steppers on the left inside an LTR caller. Qt tests exercise both locale
directions inside both caller directions. The editor-presentation checkpoint
replaced the earlier artificial future-year/month maximum with current-label
measurements. The fixed reservation recipe below now replaces those measurements;
complete segment positions and font/raster equivalence remain open.

Repeated Linux-check publication now moves each earlier date catalog tree to a
unique sibling directory before copying the fresh tree. The archive stays outside
the temporary build stage. The retained reproduction demonstrates the previous
nested-copy failure and two fresh publications with both earlier generations
preserved byte for byte.

Run `python3 scripts/check-date-range-catalog-publication.py` to exercise the actual
publication block twice against retained installed-catalog output, including
cleanup of its temporary stage.

The [editor presentation checkpoint](../evidence/development/date-range-editor-presentation-20261018/README.md)
retains all 401 exact closed/history comparisons, including every failure. Against
the history checkpoint, 366 changed-pixel counts are lower, 18 are higher and 17
are identical. The Japanese Gregorian correction removes four earlier increases.
The remaining increases cover Islamic-calendar captures, dark ISO-calendar
captures, light large-control captures and two history steps; they grant no
exceptions. The new default row is 226 points against native 222. All 384 closed
model/date observations and all 17 history model, identity, calendar and caller
environment observations still match. Complete geometry matches in 8 closed
contexts and no history steps. Native pixels, font shapes, intrinsic widths,
physical displays/input and readers remain pending.

## Reserved widths across caller dates

The [width investigation](../evidence/reference-investigations/date-range-width-20261018/README.md)
retains 1,848 public caller date updates across 23 locale/calendar/control-size
contexts. Intrinsic control widths stay constant within every context; all 3,696
picker dates match the caller. All 46 retained/cold image pairs and all 23
initial/restored pairs match exactly. The 48 baseline getter pairs also match
the original source images. Cold controls therefore provide a separate check
against an explanation based only on retained value or width caches.

Representative regular intrinsic widths are:

| Locale and calendar | Complete intrinsic width |
| --- | ---: |
| en_US Gregorian | 95 |
| ar_EG Gregorian | 91.5 |
| fa_IR Persian | 91.5 |
| he_IL Hebrew | 139.5 |
| ja_JP Japanese | 104.5 |
| ar_SA Islamic | 162 |
| en_US ISO | 99.5 |

These dimensions differ from text advances and snapped alignment frames. Large
controls keep the regular 13-point font but add three intrinsic width points.
Cold small Hebrew controls have 18-point intrinsic/alignment height; the earlier
retained control-size-change history and its geometry remain separate evidence.
The raw `initialEditors` key in the width helper is recorded after restoration;
it is interpreted as a restored observation, with the initial PNG and baseline
getters kept separately.

Direct per-picker accessibility getters expose the date area and stepper hierarchy,
including their rectangles, with all 23 before/after pairs unchanged. They expose
no month/day/year child rectangles in this context. These getter rectangles
establish no pointer hit-test, physical-input or screen-reader acceptance.

The [Linux measurement analysis](../evidence/development/date-range-width-analysis-20261018/README.md)
measures the unchanged installed module at the same 1,848 dates and repeats its
output bytes exactly. Current editor text advances vary in ten contexts while
native intrinsic widths stay fixed. Single-string figure spaces do not establish
numeric column geometry across scripts; named and algorithmic fields also need
reserved widths. The analysis keeps Qt text advances separate from complete
native dimensions and treats the Foundation short-date string as metrology text,
rather than a visible-editor oracle. Font, field reservation, chrome and snapped
frames remain distinct implementation work.

A fresh source-only build reproduces 282 width/bounds output files and, using the
separately provided style-matrix JSON, 73 more files on the same Mac (355 total). All Apple helpers, source archives and products remain external; their
checksums and immutable archive locators are recorded. Run
`python3 scripts/verify-date-range-width-investigation.py` to check the sealed
evidence. This investigation changes no product code, reference, tolerance,
approved exception or acceptance status.

The supplemental 36-context matrix compares field, stepperField and compact styles
in Gregorian, Hebrew and Umm al-Qura calendars at all four sizes. Complete
intrinsic width differences and heights are:

| Control size | Stepper minus field width | Field height | Stepper height |
| --- | ---: | ---: | ---: |
| Regular | 17 | 21 | 20 |
| Small | 15 | 19 | 18 |
| Mini | 11 | 16 | 16 |
| Large | 20 | 21 | 24 |

These differences agree across all three calendars; compact matches stepperField intrinsic dimensions.
Regular and large field-style captures are byte-identical in all three calendars.
The owned presentation now uses these size-specific stepper widths and field
heights. Backend tests derive each width delta from the native field/stepper pair;
owned-editor tests verify both endpoint heights, input width allocation and
stepper visibility across all 36 profiles at DPR 1 and 2. Reserved-column, font,
complete geometry, raster and reader work remains pending.

The [chrome correction checkpoint](../evidence/development/date-range-chrome-correction-20261018/README.md)
retains the old-code regression failure (17 against native small width delta 15)
and three passing corrected Qt test runs. All 384 closed model/date observations
and 17 history model, identity, calendar and environment observations remain
exact. All 401 strict raster comparisons still fail: 23 changed-pixel counts are
lower, six are higher and 372 are unchanged from the editor-presentation
checkpoint. The six increases are large-control captures; complete Qt fields
remain 100 points against native 98 despite the corrected stepper allocation.
Font, text reservation and bezel presentation remain open.

The package/session checks reuse the prior consumer ELF with byte-identical
148-file source inputs and unchanged CMake/QML public package contracts. The
updated installed module is from producer20; this is a compatibility replay,
not a new consumer compilation. Both project source trees are absent at runtime.

## Fixed field-width reservations

The [reservation supplement](../evidence/reference-investigations/date-range-reservation-20261018/README.md)
calibrates 118 isolated AppKit endpoints against 59 pinned-source configurations.
All intrinsic sizes, cell sizes and alignment insets agree; every before/after
image agrees with the earlier width/style capture. Separately labelled
implementation diagnostics identify a fixed set of sizing samples. Public
Calendar, DateFormatter, font-measurement and NSDatePicker checks predict all 472
intrinsic widths across four font profiles. Original-font raw cell widths match
all 118 endpoints. Sixteen extra-font raw cell last-bit differences are retained;
they are not accepted through an epsilon or exception.

The owned field reserves the largest advance of each segment across those sizing
samples, independently of the edited date. This uses the active ICU calendar,
locale and number-format overrides; the samples impose no allowed-date limit and
do not assume a largest legal year. Native RTL literal measurement is applied
before half-point rounding and the size-specific stepper allocation. Visible
single-string editing and padding remain, so stable overall width does not prove
correct segment positions, selection geometry or font/raster equivalence.

The [implementation checkpoint](../evidence/development/date-range-reservation-20261018/README.md)
retains the old-code width-jitter failure and three passing final Qt runs. Exact
checks cover 1,848 native caller date updates, 3,696 retained endpoint widths and
92 fresh endpoint widths at each DPR, plus 118 independently captured native
font-sample sets through the Linux measurement path. Editor identities, displayed
dates, zero requests and QML warnings remain checked alongside existing input,
owner, teardown, calendar and chrome tests.

Eight source-absent package/gallery profiles, eight virtual-display profiles and
four installed catalog captures pass. The prior independently compiled consumer
ELF is reused with all 148 source hashes and public package contracts unchanged;
this does not claim fresh consumer compilation. All 384 closed model/date values
and 17 history model, identity, calendar and environment observations still match.
All 401 exact image comparisons fail: 16 changed-pixel counts are lower, 46 are
higher and 339 are unchanged from the chrome checkpoint. Every failure remains.

A fresh 102-file source-only extraction/build reproduces all 380 public probe
files exactly. The earlier replay's vocabulary JSON key-order mismatch and the
forward deterministic writer are both retained; every value and original image
is unchanged. Private diagnostic addresses are excluded from the replay oracle,
not normalized into a passing comparison. All Apple code and products stay
outside this repository.

The broader Chinese/Dangi helper run starts and completes, but Chinese related-
year presentation and sizing require pinned-source captures before that calendar
can be accepted. Complete segment layout, native font/bezel rendering, parsing
histories, geometry/raster, physical display/input and reader gates remain open.
Desktop coverage remains 76/80 candidates and 0/80 accepted; TV remains a separate
pending phase. Run `python3 scripts/verify-date-range-reservation.py` and
`python3 scripts/verify-date-range-reservation-checkpoint.py`.

## Chinese-calendar presentation

The [Chinese source supplement](../evidence/reference-investigations/date-range-chinese-20261018/README.md)
retains 36 pinned-source configurations: English, Chinese and Korean locales,
ordinary/leap-month/new-year dates, and four control sizes. All 72 source endpoints
agree with isolated AppKit controls in intrinsic/cell sizes and insets; every
before/after source image is unchanged. Public font/sizing validation matches all
864 observations exactly. A fresh 99-file source-only extraction/build reproduces
all 153 public files exactly, with the 89-file library unchanged. Diagnostic
addresses remain outside the replay oracle.

English Chinese-calendar fields show a literal `r` after month/day; Chinese and
Korean omit the year. The recorded editor patterns are `M/d/'r'`, `MMMddd` and
`M. d.`. Chinese day fields use CLDR's `hanidays` numbering through ICU's per-field
number-format API. The resource's second schema version records both patterns
and numbering overrides. Other fields retain their date-style number formats,
including Hebrew year/day rules. Cyclic-calendar sizing samples use the current
era instead of ICU's astronomical maximum era, independently of the edited date.

Backend and owned-editor tests check all 72 source dates and strings, both
editable month/day roles, leap-month/year/time/fraction preservation, full-date
and field parsing, and native font-sample width reservations. Synthetic Qt input-
method commits cover three Chinese date roles at both DPRs; they do not establish
native OS-input or reader acceptance. Full logical leap labels can exceed a
native reserved slot, so string agreement does not establish clipping or
selection geometry.

The shared catalog/consumer gallery adds Chinese-calendar controls for the three
locales. A fresh independent consumer embeds the generated observations and
checks all 36 cases in each package/display profile. It records models, padded
logical field strings, editable roles, calendar parts and intrinsic sizes
separately. The original 48-case/17-history comparisons remain separate from the
36 new light/text1/DPR1 whole-image comparisons. No reference, mask, resize,
tolerance or approved exception is changed. Complete geometry/raster, field
positions, font/bezel drawing, native input, physical displays and reader gates
remain pending; the full desktop and later TV objective remains active.

Image review exposed missing CJK fonts in the earlier verification toolchain.
That run retains its missing-glyph captures. The toolchain now installs
`fonts-noto-cjk` and `fontconfig`, and glyph-run checks cover all 72 source strings.
Glyph coverage, native font metrics and exact raster acceptance remain separate.
The joined text field can scroll a longer leap-month label and hide its prefix;
native per-field clipping and selection must replace that whole-string behavior.

Run `python3 scripts/generate-date-chinese-witnesses.py --check`,
`python3 scripts/verify-date-chinese-source.py` and
`python3 scripts/verify-date-chinese-checkpoint.py`.
