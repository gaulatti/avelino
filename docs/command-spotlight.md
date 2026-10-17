# Desktop command spotlight reference

The pinned `Overlays.swift:28` defines `BleeckerCommandSpotlight` as a search field
above caller-provided rows in a vertical scroll view. It has no filtering,
selection, command dispatch, dismissal, or global shortcut of its own. Changing
the query keeps the supplied rows present; the caller decides whether to replace
the data. A row can contain text, a button, an explicit stack or another view.
The row owns its local state and actions.

The component fixes its surface at 520 by 380 points before applying the surface
modifier. A later caller frame can be narrower or shorter without shrinking the
painted component. The search field has the literal placeholder `Search commands`
and 12-point padding on all sides. A one-point separator precedes the scroll
view. The lazy stack leads its rows, uses two-point spacing and six-point vertical
padding. Each row has 12-point horizontal padding and a 38-point minimum height;
shorter content is vertically centered. Intrinsic-width rows retain their width,
while flexible rows can fill the available width. An empty stack still has its
12 points of vertical padding.

The inherited font and foreground reach caller rows. The search field resolves
its own primary font and text scale through the existing search-field component.
At Bleecker text scale one its header is 64 points high and its scroll viewport
315 points high. At scale 1.5 these become 84 and 295. The overall surface stays
520 by 380. RTL resolves leading alignment and the search field's internal order.

The native investigation compares the unchanged public component, an outer
geometry probe, and the literal source body with internal frame probes. Its
fixtures cover intrinsic and flexible rows, tall and overflowing content, empty
and long labels, Unicode, caller frames, disabled state, inherited presentation,
RTL, light/dark appearance and requested display/bitmap scales one and two.
Native identities include strings, signed 64-bit integers, booleans and a custom
hashable record. Retained histories exercise caller-owned query policies,
local key delivery, a clear-button pointer target measured from the native PNG,
row actions, canonical identity, reorder, updates, scrolling and empty/restore.

Input branches run in separate window lifetimes. The initial simultaneous-window
pilot showed that field focus moved between the branches, making its input images
unsuitable as calibration witnesses. Its failed observations remain preserved.
The corrected pilot produces identical public, probed and literal images at all
105 history steps. The query owner can accept, observe, delay or redirect an
edit. Native editor text and the owner's query are recorded separately, including
native binding callbacks during focus and blur. These observations do not grant
physical keyboard or input-timing acceptance.

The stateful 80-row history retains its clicked row's counter through the recorded
reorder, scroll, empty and restore sequence: it remains two on restore and becomes
three after another click. The three-row history resets that counter on restore.
All three native branches agree across the eight contexts. The eight large-list
restore images therefore differ from their initial images; that is recorded
caller state, not a visual failure to hide. Linux row-lifetime behavior must be
compared with the corresponding native sequence.

A targeted three-row diagnostic uses 200-point rows. Row zero is offscreen at
removal and retains its state identity on restore; row one is visible at removal
and receives a new identity. All 24 public/probed/literal images agree in this
light, scale-one diagnostic. This supports investigating visibility at removal
as the relevant distinction; it does not establish a universal cache or eviction
policy. The complete raw diagnostic stays separate from the eight-context matrix.

All native source, build products and capture tools stay outside Avelino. The
tracked record contains original PNGs, JSON observations, hashes and a Linux
verifier. A fresh replay compiles all 89 pinned files with locked dependencies;
the source-only archive remains external. Windows are inactive and offscreen,
with actual backing scale two. Requested display scale, bitmap scale, local
window events and native subview observations are recorded separately from
physical displays, accessibility hierarchy and reader behavior.

The Linux candidate exposes `query`, `items`, `itemIdentity`, `row` and
`queryRequested`. The owner receives edit requests and decides whether to accept,
observe, delay or redirect them. The control retains the editor's local text
until the owner is synchronized or the editor loses focus. It never filters the
supplied data or installs a command action. A caller row can declare required
`rowData`, `rowIndex` and `rowActive` properties. The creation context also exposes
`rowFont` and `rowForeground` for explicit presentation inheritance.

```qml
BleeckerCommandSpotlight {
    query: page.query
    items: page.commands
    onQueryRequested: value => page.query = value
    row: Component {
        BleeckerText {
            required property var rowData
            text: rowData.title
            font: rowFont
            color: rowForeground
        }
    }
}
```

Rows use their primitive `id` by default. Custom caller records require an
`itemIdentity` function returning a supported primitive key. Canonically
equivalent strings share identity. Missing, unsupported or duplicate identifiers
and invalid row builders fail explicitly. The independent fixture preserves full
signed 64-bit identifiers as canonical wire strings; that adapter does not prove
native integer or general Hashable equivalence.

The lazy row container instantiates viewport intersections and retains created
objects across updates and reorders. Removed visible rows are destroyed; removed
offscreen rows are retained for reuse. This reproduces the recorded row-state
sequences. Broader native eviction and memory-pressure behavior remain pending.
The component reports its instantiated, active and retired counts and preserves
row context until deferred destruction, including removal from a row action.

The installed `--command-spotlight` consumer runs 32 closed fixtures and eight
24-step histories per appearance/text-scale/DPR context. `--command-spotlight-report`
requires a fresh prefix. `--command-spotlight-observe` preserves differences while
requiring structural checks to pass; the default comparison exits unsuccessfully
while strict acceptance remains open. All 1,792 public native comparisons retain
unmasked PNGs, raw frame probes, query requests, editor text, row counters and
lifecycle observations. Sizing records preserve all 3,840 public native queries;
Qt implicit measurements are recorded separately from direct-proposal equivalence.

Native callback duplicates during focus and blur remain comparison failures.
Native fonts, symbols, raster, generic identity, lazy measurement/eviction, input
timing, accessibility, physical displays and readers remain unaccepted. TV and
playback remain a separate phase.

Strict comparison has zero exact native PNG matches across 1,792 observations;
1,736 complete frame sets and 512 state records match. Callback differences
affect 1,280 records, row-count differences affect 224, and editor text and
pending-query differences each affect eight. Two long-list scroll steps differ
by two points. The original observations remain visible in the comparison.

The sealed Linux record is in
[evidence/development/command-spotlight-20261017](../evidence/development/command-spotlight-20261017/report.json).
It preserves the first failed tests, earlier focus-ring restores, original
comparison environment failures and corrected full PNG comparison. No expected
images, pins, tolerances or exceptions changed. The clear action preserves the
existing responder and then synchronizes editor text with the owner query.

The final package has 147 catalog captures; all 143 earlier PNGs and metadata
remain byte-identical. The actual XTest gallery exercise passes 23 states across
15 toolbar controls, including the final eight rows and an exact return to the
top. Both pixel ratios pass the 11 focused checks. The full Qt run passed 37 of 39
targets, with failures in a navigation timing assertion and malformed-input
fixture syntax. Corrected navigation tests pass 249 checks at each pixel ratio;
the malformed-input and catalog fixture targets also pass. These runs cover all
39 unique targets on byte-identical installed module files; the original failures
remain preserved. The existing 730 contracts and the eight additional candidate guards
are verified separately. Virtual sessions cover X11 and Wayland with software
and OpenGL rendering at standard and scaled configurations; these use software
rendering and do not establish physical display or hardware acceptance.
Of 64 retained restores, 61 agree with the native initial-pixel relationship.
Three OpenGL observations differ by 5, 11 and 54 RGB pixels, with maximum
channel differences two or three. Their original PNGs remain failed with no
tolerance; retained raster stability is a separate open gate.

Run `python3 scripts/generate-command-spotlight-witnesses.py --check` to check the
native projection and `python3 scripts/verify-command-spotlight-candidate.py` to
recompute the sealed evidence. Fresh installed captures use
`python3 scripts/capture-command-spotlight.py /path/to/InstalledConsumer /new/captures --jobs 2`;
strict comparison uses
`python3 scripts/compare-command-spotlight.py /new/captures /new/comparison`.
Diagnostic and runtime PNG archives expand relative to the evidence directory.
The source replay identifies immutable base Git objects plus exact changed
source blobs; the complete frozen input manifests and failed attempts remain
reviewable. Independent machine replay remains pending.
