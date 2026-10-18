# Native DateRangePicker input supplement

This extends the closed/sizing/history source checkpoint without changing its
bytes or granting Linux acceptance. Desktop candidates remain 76/80; none is
accepted. All source and Apple tooling/products remain outside the Linux repo.

Interactive helper v3 uses matching app/executable names, canJoinAllSpaces and
fullScreenAuxiliary window behavior, and the current activation API. CUA can now
acquire its window. Those changes were made together; no single-cause recovery
claim is made. The first two window failures remain in the earlier checkpoint.

The completed session retains 116 state observations, 82 OS input events
(15 mouse-down/up pairs and 26 key-down/up pairs), 116 root images and 52 owned
calendar-window images. CUA supplies native pointer/keyboard input and the exposed
stepper Increment action. Harness buttons change typed fixtures, modes or owner
policy and are labeled separately. The local event monitor only reads events in
this app. It synthesizes none. CUA closes the window; the launcher exits zero and
the process is confirmed absent. A post-close CUA read reports procNotFound.

Twenty-one milestones bind their complete raw observations and images. The
public, probed and literal ignoring-owner states have identical root images and
binding values; the three delayed-owner states do too. Raw wrapper lifecycle is
retained, but helper root/mode remount histories are not equated. These are source
comparisons at light appearance, text scale 1, logical DPR 1, actual backing DPR
2, en_US, Gregorian and UTC. They do not establish other contexts or Linux parity.

Default year/day keyboard edits, numeric year entry, the native stepper action,
calendar pointer selection and field-style month editing retain the observed
16:00:00.625 hidden time. A native end-date edit can cross start without reordering
and retains 16:00:00.125. Opening the default calendar produces a same-value
binding request in the observed activation history; this is not a universal
per-click request guarantee. Tab events are retained; complete traversal is not
accepted from these observations.

Ignoring and delayed owners leave the bound model unchanged while the native
display advances. A caller configuration update restores an ignored model value.
Applying the pending delayed value commits it. A year increment/decrement outside
the supplied March range clamps to the exact upper/lower UTC instant and replaces
the hidden time with that bound's time. The UI shows March 31 at the upper bound,
while CUA's compact AX date string says March 30; preserve the raw NSDate values
instead of using that compact string as the UTC rendering oracle.

Graphical pointer selection retains hidden time, but Right-arrow navigation
previews the next day at UTC midnight without requesting a binding change. Space
then commits that midnight value. Field-only focus/Up increments its selected
month and opens no calendar overlay. Disabled pointer and Up events produce no
additional request and leave both dates unchanged. These style differences must
remain explicit in the Linux implementation.

The exact interactive helper and pinned 89-file source are packaged outside this
repository as a deterministic source-only archive. Extraction and a fresh library
and app build pass with no prebuilt/sibling inputs; source files remain unchanged.
This compile replay does not replay the recorded OS input. Native input replay,
additional locale/calendar/time-zone/owner/style histories, parsing/cancellation,
non-finite/extreme inputs, readers, physical displays/input, independent-machine
availability and all Linux implementation/runtime/parity gates remain pending.

Recompute the retained checks with python3 scripts/verify-date-range-input.py.
No expected capture, reference pin, mask, tolerance or exception changes here.
