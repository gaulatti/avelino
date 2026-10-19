# Desktop application shell

`BleeckerMobileAppShell` implements the pinned desktop branch of the source API.
Its name does not select a touch presentation. The desktop body is header,
one-unit separator, expanding content wrapper and optional footer. Sections live
in a separate principal toolbar picker. No bottom tab bar is added.

The [slot source investigation](../evidence/reference-investigations/mobile-shell-slots-20261019/provenance.json)
retains 18 caller cases across light/dark and DPR 1/2: 72 profiles, each with a
byte-identical uninstrumented/measurement pair. Empty, zero, hidden, fixed,
fractional, narrow, short and large-footer cases remain distinct. Empty content
does not expand; a zero-size view still has an expanding frame wrapper. Fixed
minimum sizes overflow constrained callers, centered in the offered rectangle.

`header` and `content` are required Component slots; explicitly supply `null`
for source EmptyView. `footer` defaults to `null`. Fixed root width/height
bindings are retained. Adaptive width uses the existing `BleeckerLayout` proposal
contract. A flexible caller may declare `BleeckerLayout.fillsHeight`; the owned
slot keeps that allocation separate from a fixed child's rectangle. For an
unframed flexible color, use minimum width zero and implicit ideal size 10.

## Host the toolbar

Use a Qt template ApplicationWindow and assign `header: shell.toolbarItem`.
The retained toolbar item is outside the body, like the source toolbar modifier.
Its absence from an unhosted body capture does not prove the toolbar works.
The shared catalog and installed consumer use this actual window integration.
The source's OS titlebar and the Linux window manager's decorations remain
separate from the client-area slot capture.

Set `tabs`, caller-owned `selection`, and an explicit `sectionIcon` Component for
nonempty tabs. The icon Loader supplies `systemImage`, `tabValue`, `selected`,
`pixelSize` and `foregroundColor`. No native-symbol lookup or fallback is added.
The fixture supplies original caller artwork; it is not an accepted SF-symbol
substitution. Native toolbar appearance, symbols, overflow and broader sizing
remain verification-pending.

The hosted source probe observes a 78 by 36 point control for its two section
icons, in a 52-point toolbar/titlebar region. These measurements are scoped to
that host and source environment, not a complete native-toolbar specification.

## Caller and displayed selection

The [hosted source investigation](../evidence/reference-investigations/desktop-shell-host-20261019/provenance.json)
uses hidden NSWindows and the pinned library object. It renders its own views
with AppKit caching; it does not capture the user's screen or claim physical
input. Three owner histories exercise apply, ignore and delayed writeback.

The desktop Picker does not consume a tab's badge, disabled flag or alternate
accessibility label. Its label comes from the tab label. A parent-disabled shell
disables the picker. Clicking the already selected section still requests its
value. Unknown caller selections clear the native selected segment.

`selectionRequested(value)` requests a writeback without changing the caller's
`selection`. The picker updates its displayed segment even if the caller ignores
or delays the request. A caller update or parent-enabled change synchronizes that
display again. `synchronizeSelection()` explicitly reasserts an unchanged caller
value: Qt properties do not emit a change when assigned the same value, while the
source's observed publisher can invalidate its view on that assignment. The
operator fixture uses this adapter for explicit external updates.

Source histories use programmatic native control actions. The recorded direct
right-arrow probe did not change selection even though the hidden window accepted
the first responder. It does not establish physical keyboard equivalence. Qt
pointer/Space delivery and Qt accessibility interfaces are checked separately
from native keyboard timing and actual screen-reader acceptance.

The picker uses one [Qt focus scope](https://doc.qt.io/qt-6.8/qtquick-input-focus.html#acquiring-focus-and-focus-scopes)
for tab entry, with its selected segment as the focus child. An earlier probe
changed a focused button's tab policy during caller updates and produced Qt
warnings. The scope keeps the tab policy fixed while moving focus inside the
picker; the consumer verifies the selected child receives scope focus and Space.

## Verification and remaining gates

```sh
python3 scripts/verify-mobile-shell-source.py
python3 scripts/generate-mobile-shell-witnesses.py --check
python3 scripts/verify-mobile-shell-candidate.py
InstalledConsumer --mobile-shell --mobile-shell-report /fresh/output/prefix
AvelinoCatalog --fixture mobile-shell
```

The slot and input witnesses are embedded in the independent consumer. Source
images remain unchanged in the investigation capsule; pixel comparison is
separate from runtime geometry and binding checks. The owned slot uses the pinned
Qt 6.8.3 width/height validity information to preserve explicit caller dimensions.

The [Qt 6.8.3 snapshot implementation](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quick/items/qquickitemgrabresult.cpp)
converts an item's default extent to an integer before applying DPR. Fractional
caller captures therefore use the integer client parent, retain its raw image,
and copy the complete native viewport rectangle without scaling. Both images and
the exact viewport are recorded; comparison does not discard any source pixel.

The first compiled probe exposed retained height bindings being overwritten by
allocation; that attempt is retained. Later probes caught intrinsic control hints
overriding explicit caller widths and the control's default property placing the
toolbar inside the body. Explicit dimensions now survive allocation, and a
nonvisual owner retains the separately hosted toolbar. Both DPR preflights check
that an unhosted toolbar has no visual parent. Final build, package, pixel, display and
regression results belong to the development checkpoint. Native toolbar/raster,
general slot composition, full keyboard/lifecycle, physical display/input,
independent-machine and reader gates remain pending. No mirror API is accepted
by adding this candidate.

The installed consumer checks 18 native layouts and 25 settled caller/display
states in each of eight appearance/text-scale/DPR contexts, using 12 Qt pointer
actions and two Qt accessibility interfaces per context. Eight virtual display
contexts separately cover X11/Wayland, software/OpenGL and standard/scaled output.
The state-report accessor uses the existing fixtures' untyped JavaScript return
convention; an earlier typed return converted its nested request array to null.
That failed run is retained.

All 144 body layouts match the native witnesses; 76 of 144 body images match at
zero pixel tolerance. The dark separator differs by one blue-channel level
(native 32/42/51, candidate 32/42/50), and fractional cases retain additional
edge differences. All 144 body PNGs are byte-identical before and after the focus
repair. Raw integer-parent captures and their complete native viewport copies
remain separate, so the comparison can be recomputed without masks or scaling.

The full 55-group Linux suite passed before the fixture-return and private picker
focus repairs. The final build records those exact source differences and repeats
the 40 focused checks at each DPR plus the fresh independent-consumer build.
Core inheritance is scoped to unchanged existing controls and component tests;
it does not claim the full suite was repeated after those repairs.

The [compiled checkpoint](../evidence/development/mobile-shell-20261019/result.json)
retains failed attempts, source snapshots, fresh consumer builds, raw captures,
pixel diagnostics and display reports. All 43 installed-consumer smoke commands
pass. Cold replays preserve 437 date, 120 footer and 184 button-group PNGs byte
for byte. Four light/dark and DPR 1/2 catalog captures were inspected for layout
and legibility; they establish startup and capture, with gallery-operator input
acceptance still pending. No source pin, expected image, mask or tolerance changes.
