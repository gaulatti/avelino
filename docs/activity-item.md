# ActivityItem source contract

The pinned desktop `BleeckerActivityItem` has a preserved native
[source investigation](../evidence/reference-investigations/activity-item-20261016/investigation.json).
It contains 536 ActivityItem captures, eight Button anchors, eight IconBadge
anchors, 7,072 dense width queries and 13 action traces with 94 snapshots. A fresh
source-only extraction rebuilds the unchanged 89-file Sabella tree and the
capture helpers, then reproduces all 1,753 image and metadata outputs byte for
byte. This checkpoint adds source evidence. The Linux implementation remains
pending; desktop candidate coverage stays 59/80, with zero complete acceptances.

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
Linux runtime sessions, installed consumer, physical displays/input and reader
acceptance remain pending. Source pins, expected images, tolerances and exception
approvals are unchanged.
