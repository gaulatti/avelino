# Desktop app tab bar reference

The pinned `Mobile.swift:87` implements `BleeckerAppTabBar` as a compact row of
native plain buttons on macOS. It is separate from the segmented `BleeckerTabs`
and from `BleeckerMobileAppShell`, which uses a toolbar picker on macOS. The
[reference investigation](../evidence/reference-investigations/app-tabs-20261017/investigation.json)
is source evidence for the Linux candidate now under verification. Desktop
candidate coverage is 73/80, with zero APIs fully accepted.

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
alignment. Its logical horizontal offset of ten paints to the left in RTL. The
badge frame probe reports the layout box before the `(10, -7)` paint transform,
so that frame and the capsule's painted bounds must remain separate.

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

Label fitting, exact system symbols/fonts/raster, broader
identity and duplicate-ID behavior, keyboard/input timing, native accessibility,
physical display/input and reader checks remain separate acceptance gates.
TV rendering and playback remain a later phase requiring selected Linux hardware.


# Linux candidate API

`BleeckerAppTabBar` takes `selection`, a `tabs` array and a required caller-owned
`icon: Component`. Each tab retains the source fields `value`, `label`,
`systemImage`, optional `badge`, optional `accessibilityLabel` and `disabled`.
The bar emits `selectionRequested(value)` for every enabled activation, including
reselection; the caller owns the resulting selection. This preserves observe-only,
delayed and redirecting bindings without a local selection write.

```qml
BleeckerAppTabBar {
    width: 300
    selection: model.currentTab
    tabs: [{value: "home", label: "Home", systemImage: "house", badge: "7"}]
    icon: Component {
        MyApplicationIcon {
            symbol: parent.systemImage
            color: parent.foregroundColor
            font: parent.font
        }
    }
    onSelectionRequested: value => model.currentTab = value
}
```

The icon creation context provides `systemImage`, `tabValue`, `selected`,
`pixelSize` (18), `font` and `foregroundColor`. It must create an Item with finite,
nonnegative implicit dimensions. An empty Item can represent an explicitly empty
symbol. Icon presentation belongs to the Linux caller; the catalog's original
fixture artwork and 22 measured native view boxes are unaccepted SF-symbol
candidates. An unknown fixture combination fails explicitly.

Primitive identities keep their types and canonical Unicode equality. A
`valueIdentity: value => value.id` callback supplies stable primitive identity for
custom values. Assign a new array to update the data. Reorder and edits retain
button objects by identity; removing a tab removes its button. Duplicate keys,
invalid callbacks and malformed data fail explicitly. Broader native identity and
duplicate-ID behavior remain an acceptance gate.

Badges accept safe JavaScript integers or canonical decimal strings. Native
producers should also use decimal strings beyond JavaScript's safe integer range. Their accessibility value retains the raw integer, including zero and
negative counts, while visual text is hidden or capped according to the source.
The owned Qt button adapter exposes the explicit title and notification value
through actual Qt accessibility interfaces and retains Qt pointer, keyboard and
press-action behavior. Native accessibility and reader equivalence remain pending.

The row shares offered space while preserving each icon's minimum width and may
overflow a narrow caller. Without an explicit width proposal, cells retain natural
widths. The empty bar has intrinsic size zero by five. Natural labels use the
existing measured text renderer; the two-line fitting path remains under strict
native comparison. The badge layout box and its paint transform are recorded
separately, including the mirrored horizontal offset in RTL.

Use `AvelinoCatalog --fixture app-tabs` for owner modes, pending acknowledgement,
external selection, reorder, empty/reset, width, badges, disabled state, RTL,
theme and text scale. The installed consumer exposes `--app-tabs` for strict
comparison and `--app-tabs-observe` to record differences while retaining
structural failures. The replay adapter keeps all 344 closed contexts and 864
retained steps; direct Linux sizing remains unobserved. Package, session,
physical input and reader checks remain separate from candidate registration.

The [sealed Linux candidate](../evidence/development/app-tabs-20261017/candidate.json)
retains all 1,208 image/frame/state comparisons. All binding and selected-state
observations agree, 940 frame sets agree, and 56 images match exactly, all empty
states. All 48 retained restores reproduce their initial candidate pixels. The
5,160 public native sizing responses remain preserved, with Linux direct sizing
unobserved. These results keep visual parity failed.

The candidate passes 17 focused checks at DPR 1 and 2, 34 full Qt targets and an
additional isolated-catalog target. It rejects 18 malformed configurations and
26 malformed catalog definitions; all 43 valid catalog definitions load. The
installed package runs 35 consumer modes and 143 catalog captures, leaving all
139 earlier PNGs and complete metadata unchanged. Eight virtual X11/Wayland
profiles pass structural checks with fresh environment records and the exact
installed artifact hashes. Their OpenGL paths use software rendering.
Seven profiles reproduce all six initial history images after restore. All six
restores differ in the scaled Wayland software profile, on the same bottom
physical pixel row with bounds `(340, 459, 940, 460)` in its 1280 by 800 images.
Those strict failures remain preserved separately from the passing state checks.

Real XTest input through the original installed gallery exercises 14 controls, 27 clicks
and 28 states. Twenty-six viewport images equal their separately mounted
candidates. Two retained disabled states differ by 109 pixels, with maximum
per-channel difference one. Fresh offscreen and X11 instances agree, while
resizing and remapping the retained window leave the difference present. Its
failed observations remain unchanged. The subsequent correction is described below.
This gate is separate from the larger native symbol, narrow-label and raster
differences. Physical displays/input, reader behavior and independent-machine
replay remain pending.

Run `python3 scripts/verify-app-tabs-candidate.py` to recompute sealed strict
comparisons, artifact bindings, legacy regression results, operator observations,
archive contents and complete frozen input reconstruction. References CI runs
the same verifier. `scripts/verify-app-tab-offset.py` independently measures the
native badge paint bounds; its full opaque masks remain unequal after translation.

## Retained badge raster correction

The original candidate above remains immutable. A subsequent fix isolates each
software-rendered badge through the existing alpha-capable `SoftwareContentMask`
renderer. Its rectangular outline covers the complete capsule and raster gutter;
the badge's public layout box, RTL offset and text placement stay unchanged.
Other Qt renderer paths keep the original child presentation. Icon, label,
capsule and badge text each retain their own disabled opacity. Applying opacity
after composing the complete badge changes the native disabled glyph colors.

Qt 6.8.3's ordinary item layer is unsuitable here: the diagnostic builds lose
the badge at DPR 2. Fractional layer extents also change capsule pixels at DPR 1.
Those discarded attempts remain diagnostic evidence. The alpha-capable renderer
uses a bounded transparent gutter and redraws its complete small image, avoiding
the retained window's partial repaint clip without introducing another renderer.

The `app-tabs-retained-raster` and `app-tabs-retained-raster-dpr2` CTest targets
click through all 28 gallery states and compare each complete caller viewport
with a newly started process. They also require visible enabled badge pixels;
equality between two missing badges is a failure. The original candidate fails
both targets at `disabled` and `disabled-home`. Native mirror comparison remains
separate from this local fresh-versus-retained regression.

All 26 previously matching operator viewports remain byte-identical. Across the
312 positive native badge contexts, 304 opaque sunset masks are unchanged and
eight improve, with no mask regressions. These are supplemental diagnostics,
not a replacement for full unmasked comparison. Native disabled colors and the
larger font, symbol, fitting and raster differences remain unaccepted.

The final supplemental module passes all 37 Qt targets, all 35 installed consumer
modes and 143 catalog captures. All 139 legacy PNGs and complete metadata are
unchanged. Eight fresh virtual profiles retain 42/48 exact restores; the six
scaled Wayland software failures remain separate. Run
`python3 scripts/verify-app-tabs-raster.py` to audit the complete supplemental
[record](../evidence/development/app-tabs-raster-20261017/candidate.json), frozen
inputs, discarded attempts, pixel pairs and installed artifact bindings.
