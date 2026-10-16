# ActivityItem source contract

The pinned desktop `BleeckerActivityItem` has a preserved native
[source investigation](../evidence/reference-investigations/activity-item-20261016/investigation.json).
It contains 536 ActivityItem captures, eight Button anchors, eight IconBadge
anchors, 7,072 dense width queries and 13 action traces with 94 snapshots. A fresh
source-only extraction rebuilds the unchanged 89-file Sabella tree and the
capture helpers, then reproduces all 1,753 image and metadata outputs byte for
byte. The Linux candidate described below preserves these source records;
complete mirror acceptance remains pending.

`Sources/Sabella/Extended.swift:6` accepts a title, detail, timestamp, a system
image defaulting to `clock`, and caller-created actions. The source stores the
constructed actions view. It has no row action or internal model state. A
top-aligned horizontal stack uses spacing 12 between its 36-point subtle
IconBadge, text column, spacer and each action. Vertical padding is eight. The
spacer has minimum width eight. An empty actions closure introduces no item or
gap; a zero-sized action retains its item and gap. Direct multiple actions are
separate row children, while an explicitly nested stack remains one child.

The three label fonts are fixed: Encode Sans semibold 14 for the title and
Libre Franklin regular 12/10 for detail/timestamp. They ignore the outer font
and custom text-scale environment. The title inherits the foreground, including
an explicit parent red. Detail and timestamp use palette secondary text. A plain
caller action inherits the parent font and foreground; Bleecker buttons own their
font and respond to text scale. The default text column is 50 points high, with
17/15/12-point label heights and two three-point gaps. Each empty string retains a
14-point line box; three empty strings produce a 48-point column and 64-point body.
The instrumented leading guides record first baselines 14/12/10 in the normal
single-line case. These probes establish base fonts and geometry, not fallback
glyph runs or a portable system-font asset.

Offered width is not a clipping bound. At width zero, the empty-actions body is
68 points wide; one button produces 108, two flat buttons 148, and a nested pair
141. A zero-sized action produces 80. A zero-width text column still wraps to its
measured multi-line height and paints no text pixels. Dense queries cover every
integer width zero through 160 and widths 164 through 400 in steps of four, with
eight action arrangements, two requested DPRs and two text scales. All 7,072
public root frames and 8,840 public action frames equal the reconstructed
witness. In 178 queries, exclusively the nested pair at text scale 1.5, the fitted
body exceeds both its minimum and offered width. Measured flexibility ordering
explains this overflow: the enlarged nested action is offered space after the
text column. A clamp to `max(minimumWidth, offeredWidth)` would change the source.

All 552 public images equal both the separately instrumented public view and
the reconstructed witness byte for byte. Direct and grouped multiple actions,
direct and grouped empty actions, and default versus explicit clock construction
also match. All eight Button anchors preserve the previous RadioGroup anchor
bytes. Fields, empty values, multiline and long content, Unicode/bidi, narrow
widths, RTL, disabled/hidden content, inherited font/foreground, alternate symbols,
intrinsic sizing and locale contexts remain in the raw corpus.

Synthetic mouse events reach the bare public view; a separate reconstructed
window supplies target frames. Badge, label, spacer and padding clicks emit no
callback. Enabled Review/Archive releases each invoke their caller action once;
outside drags, disabled/hidden/empty actions and disable/remove/width changes
during a press cancel the release. Holding for 1.1 seconds emits nothing until
release. Updating the title during a press still permits release inside the
button. A caller counter retains local state through title/detail/timestamp/icon
updates. Removing it or replacing its action type destroys that state; restoring
it starts again at zero. These are synthetic pointer and lifecycle observations;
native keyboard, physical input and reader behavior remain unverified.

Captures use `NSHostingView.cacheDisplay` in isolated inactive, non-key/non-main
windows, with actual backing scale two. Requested display scale and explicit
bitmap DPR one/two are recorded separately; images are never resized. The source
body fits inside each canvas. Requested bitmap DPR one is not a physical DPR-one
display claim. Native SF symbol pixels remain reference evidence and are not
installed as Linux assets.

Run `python3 scripts/verify-activity-source.py` to audit the corpus, raw hashes,
coverage, triple-image identity, anchors, dense geometry, callback/lifecycle
observations and source replay. Negative contracts also run in References CI.
Swift tooling and the source-only replay archive stay outside this Linux tree.
The archive SHA-256 is
`8a76b31375f6f5b4f2df096919d3aab7c2de73d9eb80b79ae3c95ef0a79fb89d`;
the machine-local locator and source/tool hashes are in
[tooling provenance](../evidence/reference-investigations/activity-item-20261016/tooling-provenance.json)
and [replay inputs](../evidence/reference-investigations/activity-item-20261016/replay-inputs.json).
Independent-machine helper availability, exact font/symbol/frame/raster parity,
complete Linux runtime, physical display/input and reader acceptance remain
pending. Source pins, expected images, tolerances and exception
approvals are unchanged.

## Standalone text fitting diagnosis

An additional [source record](../evidence/reference-investigations/activity-text-20261016/investigation.json)
isolates the five default field/action strings in public native `Text` views.
It covers 3,374 geometry queries at half-point widths zero through 120, requested
display scales one/two and both action font scales. A separate fresh source-only
rebuild reproduces its complete JSON byte for byte. These measurements confirm
that the narrow label differences observed during Qt implementation also occur
outside ActivityItem. This corpus isolates text fitting from the row allocator.

The preserved Qt 6.8.3 diagnostic matches 3,189/3,374 proposals and disagrees on
185: 165 at DPR one and 20 at DPR two. At DPR one, 161 differ in width and eight
in height; at DPR two, 20 differ in width and four in height. Those counts overlap.
Fractional fitted widths and line breaking are distinct measured differences.
For example, native `Ready for review` at width 54 has three lines; Qt has two.
Native `Review` at width ten has six lines at display scale one and five at two.
Native `2 min ago` at width 40 has a fitted width of 28; the Qt paragraph-balancing
heuristic produces 37. The original diagnostic source, logs, raw outcomes and
shared text implementation's historical Git hash remain preserved. These are
historical candidate failures. The later implementation below passes the same
proposal histories; this does not approve an exception or change a baseline.

Run `python3 scripts/verify-activity-text-source.py` to audit this additional
record. The separate source-only archive SHA-256 is
`e6918deff925728e5e6dcedb0b6a49d46d9721852da83e3ff9c51e01ea79a782`.
Its helper/source hashes and machine-local external locator are in that record's
tooling provenance; independent-machine availability remains pending.

## Proposal and measurement-history evidence

The [layout mechanics record](../evidence/reference-investigations/activity-layout-mechanics-20261016/investigation.json)
adds transparent action-proposal probes and explicit text resize histories. All
16 bare/probed public ActivityItem image pairs match byte for byte; four bare
images also match the original public multi-action captures. At width 240, text
scale 1.5 and requested DPR one, the native row first offers Review `148/3`
points, which fits to 46 by 125. It then offers Archive 51 points, which fits to
50 by 100. Rounding the proposal before the child fits changes the result.
Fitted view frames and incoming proposals have separate rounding behavior.

Forty-eight public Text histories preserve 120 snapshots and original PNGs. A
fresh `Review` at width ten and requested DPR one is 80 points high. Growing it
from 9.5 to ten preserves its 96-point height and identical image bytes. Starting
at ten, shrinking to 9.5 and returning to ten produces heights 80, 96 and 80.
Requested DPR two has different interval boundaries. Consequently, a fresh view
does not reproduce the original dense tool's persistent increasing-width input
sequence. The original measurements remain unchanged.

The record independently reproduces all 3,374 original public Text frames and
adds 5,400 AppKit paragraph-strategy probes. AppKit `pushOut`/`standard` match
3,370 public heights and 3,360 widths in this corpus; they are diagnostic proxies
with preserved disagreements. Their font fields describe the comparison fonts,
not actual fallback glyph runs in the public Text view.

A fresh unchanged 89-file source rebuild reproduces all 156 image and metadata
outputs byte for byte. Run `python3 scripts/verify-activity-layout-source.py` to
audit the complete corpus, proposal values, resize histories, image identities,
proxy limitations and clean replay. Native helpers remain external. The
source-only archive SHA-256 is
`c50f37c948e96d6164c3bd8674c71993d91d50a9b8edd0b0627b8bc6310a0909`;
the external locator and input hashes are in that record's tooling provenance.
This evidence does not approve a Linux implementation, expected-image update,
font/symbol substitution or physical/session/reader gate.

## Linux candidate at bf30fa14

`BleeckerActivityItem` requires `title`, `detail` and `timestamp`. Its default
`actions` property accepts caller-owned items without replacing their objects or
state. `icon` accepts a component; the default is an original clock drawing whose
SF-symbol equivalence remains unapproved. `foreground` overrides the inherited
title/action foreground. The detail and timestamp retain secondary text color.
`maximumWidth` accepts a nonnegative proposal or `-1` for intrinsic sizing;
invalid negative, infinite and NaN values fail visibly.

```qml
BleeckerActivityItem {
    title: "Ready for review"
    detail: "A new edition is available"
    timestamp: "2 min ago"
    maximumWidth: 400
    BleeckerButton { text: "Review"; variant: "link"; onClicked: review() }
    BleeckerButton { text: "Archive"; variant: "link"; onClicked: archive() }
}
```

Direct actions participate as separate row children. An explicit `ProposalRow`
keeps a nested group together. Conditional loaders use
`BleeckerLayout.flattenChildren: true` and `participates: active`; this preserves
the distinction between absent content and a present zero-sized item. Hidden
items retain layout. The row never adds a callback or keyboard focus target.
Its three labels expose Qt static-text interfaces; enabled caller actions supply
their own focus and accessibility behavior.

The row passes fractional proposals unchanged and rounds the fitted frames to
the display pixel grid. It allows the source's measured minimum-width overflow.
The shared custom-font label renderer retains wrap measurements over the measured
proposal/fitted-width interval, with an earlier exact proposal taking precedence.
Text, font, tracking, line-height, alignment, elision or DPR changes invalidate
those measurements. Reentrant intrinsic-size bindings preserve the newest layout.
The shared button and breadcrumb use the same fitted-width rounding; this also
keeps standalone finite-width buttons clipped to their actual text proposal.

Component fixtures replay all 6,188 dense source queries for the seven action
arrangements using bundled fonts, all 3,374 standalone text proposals and all
48 explicit resize histories with 120 states. They retain the native input
sequence on each item. The 884 plain system-font action queries remain outside
the strict dense assertion because the Linux default-font substitution is
unapproved. All original source measurements remain preserved.

The independent consumer replays 13 native pointer and lifecycle traces with
94 snapshots. It checks actual callback counts, local state, appearance/removal,
disabled/hidden content, cancellation during reflow, hold/release, Qt Tab/Backtab
and real Qt accessibility interfaces. The catalog includes an `activity-item`
gallery and all 69 isolated native fixture groups. These synthetic and virtual
checks do not accept native keyboard behavior, physical input or screen readers.
Each producer update waits for a completed frame before subsequent synthetic
input. The preserved first display attempt passed seven configurations and
failed its first badge click on scaled Wayland/OpenGL; its fixed 10 ms producer
delay did not establish displayed geometry. Diagnostic timing changes did not
reproduce that failure. The frame-synchronized harness records its completed
producer-frame count separately from the unchanged 94 native state assertions.

The [sealed candidate](../evidence/development/activity/candidate.json) records
17 passing CTest targets across the full run and centering rerun, 217 Python
contracts, all 24 installed consumer modes, 107 catalog captures and eight
package-only virtual display configurations. Each final profile completes 38
producer updates and all 94 native state comparisons. The full 192-configuration
display script is wired into CI; that entire matrix was not run locally.

All 552 isolated captures preserve their original physical dimensions. Their
root frames match; all 536 ActivityItem initial states match, and 488 child-frame
sets match. The 48 remaining sets cover Unicode, bidi, narrow RTL and plain-font
actions. Narrow RTL has one- or two-point label/column differences that require
additional source diagnosis. The plain default/32-point native system font and
Unicode fallback are unapproved substitutions. No complete pixel comparison
passes. The inspected Unicode pair shows a missing double-struck digit in the
Linux title; clock and button glyph raster also differ.

The final validation package has no source/build trees, networking or ICU
development headers. All 112 installed files match the 552-capture package byte
for byte. The only later changes synchronize independent consumer input and
require its frame counter in the display harness. All 107 final gallery PNGs and
full metadata files remain byte-identical. Against the previous OTP checkpoint,
all 103 metadata files and 101 images match; each remaining DPR-two presentation
image differs by three pixels in its button label. Those differences are
preserved without a baseline or tolerance change.

Desktop candidate coverage is 60/80, with zero complete mirror acceptances.
All 46 television entries remain pending in their separate later phase.

## Aligned text follow-up

The [additional source investigation](../evidence/reference-investigations/activity-text-alignment-20261016/investigation.json)
isolates the narrow RTL label widths. All 3,374 prior LTR measurements and 16
original public ActivityItem images reproduce exactly. Ambient RTL changes 593
ascending text measurements, including five history-dependent heights; the older
installed Qt renderer has those 593 differences and 21 fresh-case differences.
Unmodified public Text reproduces the same width growth with physical right
alignment in an LTR environment. These measurements isolate text alignment with
the fixed bundled fonts.

The shared label now includes trailing whitespace after centering/right alignment.
All 7,000 direction/fresh measurements and 768 bare alignment cases match in the
actual ActivityItem field and Button label fixtures. A separate fresh source-only
rebuild reproduces all 1,599 new outputs. The original 614 Qt failures remain
bound to `bf30fa14`; expected images, source pins, tolerances and exception
approvals are unchanged. See [typography](typography.md) for the alignment rule and
the explicitly non-transparent custom renderer diagnostic.

The external source-only replay archive SHA-256 is
`fd17c1569ba4dce5dbf29a49bca0f4de8e887511f4dd73a37808498755ee15a4`.
Its six members contain the unchanged full source, three native helper files,
the replay script and input hashes; compiled project inputs are absent. The
external locator and toolchain are recorded in
[tooling provenance](../evidence/reference-investigations/activity-text-alignment-20261016/tooling-provenance.json).
Independent-machine helper availability remains pending.

The [bounded alignment candidate](../evidence/development/text-alignment/candidate.json)
passes all 17 CTest targets and 227 Python contracts, plus all 24 installed
consumer modes, 107 galleries and eight focused virtual profiles. The intrinsic
size regression rejects 104 cases in the earlier unbounded prototype and passes
all 768 bare cases in the final package. A later assertion strengthens the
permanent tests; both 519-result alignment profiles pass without changing the
installed library or its captured inputs.

All eight narrow RTL child-frame sets now match. The complete 552-case recapture
retains 552 matching root frames, 536 matching initial Activity states and 496
matching child-frame sets, up from 488. All 107 previous gallery PNGs and complete
metadata files remain byte-identical. Unicode/bidi and plain system-font child
frames remain different in 40 cases; complete pixel matches remain zero. Font,
symbol, raster, physical/native keyboard and reader acceptance stays pending.
