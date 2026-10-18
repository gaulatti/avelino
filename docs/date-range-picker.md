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
non-finite/extreme behavior, complete native history/lifecycle replay, arbitrary
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
