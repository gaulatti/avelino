# Desktop app tab bar reference

The pinned `Mobile.swift:87` implements `BleeckerAppTabBar` as a compact row of
native plain buttons on macOS. It is separate from the segmented `BleeckerTabs`
and from `BleeckerMobileAppShell`, which uses a toolbar picker on macOS. The
[reference investigation](../evidence/reference-investigations/app-tabs-20261017/investigation.json)
is source evidence; the Linux component remains pending. Desktop candidate
coverage stays 72/80, with zero APIs fully accepted.

All 344 closed contexts and 864 retained history steps have identical public,
probed and literal-body pixels. All 344 sizing contexts agree across the three
branches. The fresh source replay reproduces all 3,627 output files byte for byte,
including 3,624 PNGs, and leaves all 89 pinned source files unchanged. All 48
retained restore steps reproduce their initial pixels. These results validate
this native record and its probes; they do not accept a Linux implementation.

Each tab has a value, label, system symbol, optional signed native integer badge,
optional accessibility label and disabled state. The value is also its identity.
The source defaults an omitted accessibility label to the visual label and
preserves an explicit empty label. It displays positive badges, caps their visual
text at `99+`, and exposes the raw integer followed by ` notifications` as its
accessibility value, including zero and negative counts. Those accessibility
strings are established by pinned source; the inactive native capture host
exposes no accessibility button children, so actual native values, selected
traits, accessibility presses and reader output remain unobserved.

The row has zero inter-button spacing, five points of top padding, a card
background and a top separator. A button has a 54-point minimum height. Its
18-point system symbol uses semibold when selected and regular otherwise. The
label uses 10-point primary text, semibold when selected and medium otherwise,
with a two-line limit, centered alignment and a minimum scale factor of 0.8.
The vertical icon-to-label gap is three points. The badge uses eight-point bold
primary text, four-point horizontal padding, a 15-point minimum width and height,
a sunset capsule and a `(10, -7)` overlay offset. Selected foreground uses sea;
other foreground uses secondary text.

Wide frames generally share their width among the buttons. A narrow proposal
can produce different button widths and overflow the caller frame: icon minima
and label fitting still participate in the native layout. The standard three-tab
fixture offered 30 points lays out a 74-point bar at requested DPR 1. Its button
widths are 26, 25 and 23. An empty bar has zero intrinsic width and a five-point
height even inside a wider caller frame. Direct sizing queries are recorded
separately from the final hosted frame; a caller's fixed height does not establish
the component's response to a height proposal. Native two-line fitting and symbol
metrics must be measured rather than replaced by an equal-width formula.

The external helper observes the unchanged public component, an outer geometry
probe, and the literal pinned body with internal frame probes. There are 43 closed
definitions across 344 contexts and 1,032 images, 15,480 direct sizing queries
across all three branches, and 48 retained histories with 864 steps and 2,592 images. It retains the
public binding in six histories: echo, observe-only, delayed and redirecting
owners, canonical Unicode strings, and signed 64-bit integers including values
outside JavaScript's safe range. Clicking a selected tab emits another request.
Disabled tabs reject pointer input. An owner may keep, delay or redirect a
requested selection; the bar does not override its owner. Later external updates
continue to reach the bar. Integer values and badges travel in the evidence as
canonical decimal strings, preserving native precision. A future QML adapter must
keep selection requests distinct from local selection writes for observe-only and
delayed owners.

The complete closed matrix also records 24 exact hidden-badge pairs, eight
`99+` cap pairs, 16 inherited font/color pairs and 172 text-scale pairs. The custom
Bleecker text-scale key does not change this public component's pixels: its fonts
use direct sizes. RTL reverses button placement and resolves the badge overlay
alignment; the literal horizontal offset remains positive ten.

The closed definitions also instantiate native `Bool` and a custom `Hashable`
record type. They cover empty data, count and width changes, caller height,
unmatched selection, selected/parent/per-tab disabled state, badges from
`Int.min` to `Int.max`, empty and long labels, invalid symbols, explicit
accessibility labels, inherited font/color and RTL. Every definition runs in
light/dark appearance, Bleecker text scales 1/1.5 and requested display/bitmap
scales 1/2. These are hosted inactive windows positioned outside the visible
display, with actual window backing scale two. Captures and synthetic local
pointer delivery do not establish physical display, focused keyboard or reader
acceptance. Geometry probes retain their last reported rectangle after removal;
`active_frames` filters those traces by the current tab data for future consumers.

All native tooling and the complete pinned source remain in checksummed external
artifacts. The tracked repository contains rendered output, JSON observations,
provenance and a Linux verifier. The source-only replay builds all 89 source files
in a fresh scratch directory, with locked dependencies and no precompiled Sabella
inputs. Independent-machine availability remains pending. Run
`python3 scripts/verify-app-tabs-source.py` to audit the sealed observations;
References CI runs the same audit. This does not execute a macOS build on Linux.

Linux implementation, label fitting, exact system symbols/fonts/raster, broader
identity and duplicate-ID behavior, keyboard/input timing, native accessibility,
physical display/input and reader checks remain separate acceptance gates.
TV rendering and playback remain a later phase requiring selected Linux hardware.
