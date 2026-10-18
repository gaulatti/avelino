# DateRangePicker reference contract

The Linux component remains unimplemented. The pinned desktop source is
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

The visible interactive helper could not be acquired through CUA:
`cgWindowNotFound`. It remained inactive/non-key, and no native keyboard, stepper,
calendar, owner echo/ignore/delay or reader acceptance is claimed. Native editing
and time preservation after edits, non-finite/extreme inputs, further calendar
and style combinations, the owned Linux presentation, catalog, installed consumer,
strict comparisons, display sessions, input, scaling, readers and physical
acceptance remain required. No mask, tolerance, reference-pin change or approved
exception is introduced.

Recompute the retained source observations with:

```sh
python3 scripts/verify-date-range-source.py
```
