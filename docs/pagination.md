# Icon buttons and pagination candidate

The pinned sources are `Buttons.swift:101` (`BleeckerIconButton`) and
`Navigation.swift:182` (`BleeckerPagination`). This work remains verification-pending.

Before acceptance, verify all three icon sizes and variants, enabled/disabled and
pressed presentation, pointer/keyboard activation, actual Qt accessibility names
and actions, caller-owned page updates, subsequent external updates, first/last
boundaries, single/zero/negative counts, out-of-range pages, long labels, constrained
and wide layouts, RTL, themes/text scales, independent installation and separate
X11/Wayland renderers. Exact symbol appearance, source keyboard/focus equivalence,
physical input/display and screen-reader output remain separate gates.

Icon buttons reuse the existing owned button style. Source `sm`, `md`, `lg` map
to button sizes `xs`, `sm`, `md`, with icon frames 12, 16, 20 and horizontal
padding 10, 14, 18. Their ordinary intrinsic dimensions are 32×28, 44×36, 56×40.
Source variants `default`, `subtle`, `ghost` map to `secondary`, `subtle`, `ghost`.
A Linux `icon` component slot carries caller-provided artwork; `accessibilityLabel`
names the actual template input. No unknown-symbol substitution is introduced.
Original chevron paths used by pagination remain explicitly unaccepted SF Symbol
candidates, with separate provenance and comparisons.

Pagination has caller-owned `page` and `pageCount` and emits `pageRequested(page)`.
It does not mutate the caller's state. Previous requests `max(1,page-1)` and is
disabled at `page<=1`; Next requests `min(pageCount,page+1)` and is disabled at
`page>=pageCount`. The label displays `Page N of max(1,pageCount)` with the control locale's integer
grouping (for example `Page 1,000 of 2,000` in `en_US`), without repairing
an out-of-range caller page. Zero/negative counts and pages outside the count are
preserved as source behavior. The caller decides whether to apply a request.
Qt `int` properties are a platform adapter; source Swift integers beyond the Qt
32-bit property range remain unverified.

The page label uses fixed 12-unit primary text; the source button style applies
text scaling to its symbol font while retaining the icon frame and minimum button
height. The group uses 8-unit gaps. Encode Sans 12 has a measured 15-unit line box;
a two-line narrow page label occupies 30 units inside the 36-unit group. The source's inherited primary text color is
measured independently of the Bleecker palette. Narrow/wide test frames are
external layout proposals, not page-bound defaults.

The [source proposal](../evidence/reference-proposals/pagination-20261014/proposal.json)
contains 396 icon-button cases, 152 pagination cases and eight anchors. Its 557
output files replayed byte-for-byte from a clean helper extraction/rebuild.
The [Linux candidate](../evidence/development/pagination/candidate.json) records
556/556 matching root bounds and 0/556 exact images. Final callback/page/count/request values match separately from pixels.
All 152 child body measurements also match; they are recorded independently. All 36 held-press cases preserve the pressed state at capture and
verify one activation on release afterward. Original-symbol geometry, coverage
and bounds have 48 dedicated measurements; none are approved equivalents.

All 3,056 Qt checks, 56 contracts, three invalid-startup cases, eleven
installed offscreen modes and 88 fresh package-only virtual-session pairs pass.
Eight pagination pairs cover both protocols/renderers/scales. Default/Basic/Fusion
gallery PNGs match. All 2,034 earlier PNG and complete metadata pairs are unchanged.
Coverage is 42/80 desktop APIs started, with none accepted. The full source integer
range, further source keyboard/focus, locale/text-scale/motion/touch contexts,
exact artwork/rendering, physical input/display and actual screen-reader gates
remain open. No source pin, accepted capture, tolerance or exception changed.

A separate package-only catalog probe fails to locate the installed Avelino QML
module. This remains an open catalog startup gate; the independent library
consumer passes separately. See [packaging](packaging.md).
