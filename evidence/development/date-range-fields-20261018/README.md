# Independent date-field presentation checkpoint

One Qt 6.8.3 template field retains the logical UTF-16 text, focus, selection,
and input-method composition. Calendar fields and literals use independent
fixed reservations, shaping and clipping. Sizing and drawing share the same ICU
sample reservations. Longer leap labels keep their prefix without moving the day;
locale field direction remains independent of caller direction. Hit testing,
cursor/anchor queries and assistive character geometry use the same layouts.
Pointer calendar selection follows the template mouse path. Assistive edits use
Qt commits and the existing owner request path. Source/reference pins are intact.

Producer29 reproduces the original prefix at x=-13 instead of left padding3.
Producer30 preserves a compile failure. Producer31 corrects the prefix coordinates
and retains a failing pointer-boundary regression. Producer32 passes the first full checks. Producer33 is explicitly invalidated:
preserved file timestamps skipped new input compilation. Producer34 activates
all changed inputs with container timestamps. Producer35 adds the reviewable
leap-month gallery fixture and fresh consumer; it passes all three test groups at both DPRs,
including independent day position, month/day boundary selection, composition and
assistive editing, and field clicks for all 17 captured locale/calendar patterns
with both caller directions. Existing owner/lifetime/input, chrome, stable widths,
Chinese formatting/parsing and glyph checks are retained. API review records four
installed headers matching the inspected official Qt 6.8.3 sources byte for byte;
the inclusive text-node selection end is version guarded.

Consumer11 is freshly configured and compiled from all 149 source
inputs against producer35's installed prefix. The updated gallery exposes a
Leap month control and validates its displayed dates, strings, editable roles
and hidden calendar parts against the captured source case. Runtime mounts
contain neither project source tree. Eight package and eight gallery profiles
(with21 operators each), eight virtual X11/Wayland software/OpenGL profiles and
four installed catalog captures pass. These remain separate from physical
display, acceleration, native OS-input and screen-reader acceptance.

All 384 legacy model observations and 17 history model, editor identity, calendar
and environment observations remain exact. All 288 Chinese package and 288 display
semantic observations match. All 401 legacy whole-image comparisons execute and
fail: 100 changed-pixel counts lower, 212 higher,
89 unchanged against the Chinese checkpoint. The separate36
Chinese comparisons also retain all raw differences. Models, geometry, logical
strings and pixels remain separate observations; no mask, resize, tolerance,
reference/pin update or approved exception is introduced.

Field font/bezel drawing, complete geometry/raster and native input histories,
physical displays and readers, the remaining desktop controls and separate TV
phase remain pending. Coverage stays 76/80 desktop candidates and 0/80 accepted.
Run scripts/verify-date-range-fields-checkpoint.py. Source specs bind exact
compiled core inputs, the freshly compiled consumer, native evidence and integration
changes. Prior sealed evidence is unchanged.
