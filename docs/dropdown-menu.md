# Dropdown menu source contract

The desktop reference is `BleeckerDropdownMenu` in
`Sources/Sabella/Overlays.swift:22`, pinned to
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`.
It passes caller-provided `BleeckerMenuItem` values into a SwiftUI `Menu` with
borderless-button style. Each item supplies a title, an optional system image,
a destructive flag and an owner action. The source substitutes `circle` when
an item's system image is absent. Each item gets a UUID when constructed.
There is no selection binding, filtering, command dispatch service or global
shortcut in this component.

Before implementation, establish these observable criteria:

- Measure the closed trigger's native label conversion, dimensions and fitting.
  The generic caller label is not evidence that the platform renders arbitrary
  caller content inside the trigger. Preserve text, image, empty, explicit stack,
  flat and unsupported visual-label observations separately.
- Preserve item order and distinct actions for repeated titles. Opening or
  canceling a menu must not invoke an owner action. Record destructive roles and
  missing-image source expressions separately from the platform's actual paint.
  Keep the complete item array, including long and overflowing menus.
- Establish producer updates, disabled behavior, opening, cancellation, pointer
  release and keyboard behavior through measured source traces. Direct menu
  dispatch is a callback diagnostic; it does not establish normal pointer input.
- Measure the inherited font, foreground, control size, text scale, layout
  direction, caller frame and light/dark appearance. Keep direct native sizing
  proposals separate from a later fixed caller frame.
- Own the complete Qt trigger, popup and item presentation. Keep original Linux
  symbol and system-font candidates distinct from native appearance acceptance.
  Do not redistribute native font or symbol assets.
- Verify installed packaging, catalog controls, an independent consumer,
  offscreen captures and separate X11/Wayland input and rendering profiles.
  Physical displays, keyboard timing, accessibility hierarchy, readers and
  native window shadow/backdrop behavior need their own evidence.

The diagnostic closed pilot has fourteen fixtures in light and dark appearance.
All 28 unchanged public captures match both the separately probed public view
and the literal source witness. They run at requested DPR one in inactive,
non-key windows whose actual backing scale is two. Their label geometry probes
report zero-sized metadata labels; the native popup button supplies the painted
trigger. A rectangle label leaves only the indicator, while a text/image stack
contributes both native text and image metadata. In these fixtures, changing the
inherited font or foreground produces byte-identical closed PNGs.

The opening diagnostic observes a three-row native popup menu. Direct
`NSMenu.performActionForItem` dispatch invokes the three corresponding owner
actions once each. A separate own-process queued-pointer attempt invokes
`Duplicate` but also reaches its timed cancellation. That mixed trace does not
establish normal pointer activation. Menu content-view captures exclude the
outer window shadow. The host remains offscreen; AppKit constrains the popup
window to the screen. None of these observations establishes physical display
or input acceptance.

The first behavior helper failed Swift's isolation check while capturing an
`NSMenu` in a timer. Its compiler output is preserved outside the repository;
the corrected helper owns that menu through a main-actor record. The source-only
matrix is recorded in the [sealed investigation](../evidence/reference-investigations/dropdown-menu-20261017/investigation.json). At that source-record checkpoint, desktop
candidate coverage was 74/80, with zero accepted APIs. All native sources,
source archives, helpers and build products remain outside Avelino.


The full matrix covers 32 definitions across light/dark appearance, text scales
one/1.5 and requested bitmap/display DPR one/two: 256 public contexts and 768
original PNGs. Every public image, probed image and literal witness agrees; all
256 native view hierarchies and probed/literal frame sets also agree. All 3,840
direct sizing queries per branch agree, totaling 11,520 native responses. The
fixture set includes empty, single, repeated-title, destructive and 40-item data;
text, image, unsupported, flat, stack and button labels; local and inherited
styling; caller constraints, disabled state, RTL and native control sizes.

The default Actions trigger measures 65 by 16 at requested DPR one. An explicit
28-point bold Text label measures 120 by 33; an inherited parent font leaves the
default dimensions and pixels unchanged. Explicit label color also changes the
pixels, while inherited foreground does not. A wide caller frame leaves the
trigger at its natural size; a narrow caller constrains its width. A zero-height
caller preserves the trigger height. Mini and small native control sizes are
recorded separately.

A fresh extraction rebuilds all 89 unchanged pinned source files and three
helpers, then repeats the capture, sizing and direct-dispatch runs. The replay
reproduces all 773 output files byte for byte. The external source-only
archive SHA-256 is `be8c686d2747851fdf84d5c35faefea3f626806d17d5bf080c006ebed9c908df`.
Its locator, input hashes, toolchain, original build logs and fresh replay logs
remain in the sealed record. The archive and every Swift source/build product
stay outside Avelino. Independent-machine replay remains pending.

Run `python3 scripts/verify-dropdown-menu-source.py` to recompute the native
witnesses, sizing, dispatch diagnostics and retained replay hashes. The source
integrity guards reject Linux acceptance, omitted contexts, altered references,
new tolerances, prebuilt source inputs and overstated pointer or window evidence.

The [native supplement](../evidence/reference-investigations/dropdown-menu-supplement-20261017/README.md)
adds nine label variants and intrinsic image/button measurements. All 59
label/image outputs reproduce exactly from a fresh source build. Three
own-process queued-pointer traces still select Duplicate without the timed
fallback cancellation, but their raw JSON retains a 15-pixel vertical popup
placement difference. Opening uses the native button's programmatic click;
physical input, placement and reader acceptance remain pending. Run
`python3 scripts/verify-dropdown-menu-supplement.py` to verify these observations.

## Linux candidate

The Qt adapter supplies `BleeckerMenuItem` objects and a
`BleeckerDropdownMenu` with caller-owned `items` and a `label` Component.
Each item receives a UUID when created. `title`, optional `systemImage` and
`destructive` remain separate from its `triggered` owner callback. Repeated
titles retain distinct item identities and callbacks; the menu has no selection
binding or application command dispatcher.

```qml
BleeckerMenuItem {
    id: openItem
    title: "Open"
    systemImage: "folder"
    onTriggered: documentController.openDocument()
}
BleeckerMenuItem {
    id: removeItem
    title: "Remove"
    systemImage: "trash"
    destructive: true
    onTriggered: documentController.removeDocument()
}
BleeckerDropdownMenu {
    items: [openItem, removeItem]
    label: Component { BleeckerText { text: "Actions" } }
}
```

The label is evaluated in a local font/color context. Its first visible text
and image contribute trigger metadata. Wrapper geometry and decorative
rectangles do not become trigger content; opacity-zero text still contributes
metadata. Local text styling remains available. Images retain the caller's Qt
URL and intrinsic image dimensions. The native diagnostic also ignores an
image's outer frame, including a resizable image with a 200-by-80 frame.
Native reference PNGs and system symbol assets
are not installed as Linux artwork. `BleeckerText` provides the library's
inherited presentation behavior; a plain Qt Text retains its own resolved color.

The trigger keeps its natural height within an outer caller frame. A wide frame
centers its natural width; a narrow frame constrains it. `controlSize` accepts
`mini`, `small`, `regular` and `large`. The custom Bleecker text-scale environment
does not enlarge the native-style trigger.

The popup uses an owned Qt template Menu in a separate window. Its item
delegates are created on first opening and retained after closing. The complete
item list remains available for scrolling. Producer replacements and reorders
use item identity; callbacks can update the owner, including removing the menu's
items. Qt item fields can participate in bindings, while the Swift source uses
immutable item values. Native identity/update timing, label builders, system
fonts and symbols, popup material/shadow/placement, input, accessibility and
reader equivalence remain pending. Desktop candidate coverage is now 75/80; zero APIs have native parity acceptance.

The window input adapter corrects the pinned Qt 6.8.3 menu release path, which
passes viewport coordinates to a content-coordinate row lookup. It hit-tests
the actual row through its global transform, then preserves template activation
and normal event delivery. The filter is attached only to this menu's popup
window. The retained 40-row regression presses command 39 after scrolling and
requires its own callback. See the upstream
[menu release implementation](https://raw.githubusercontent.com/qt/qtdeclarative/v6.8.3/src/quicktemplates/qquickmenu.cpp)
and [popup-window event routing](https://raw.githubusercontent.com/qt/qtdeclarative/v6.8.3/src/quicktemplates/qquickpopupwindow.cpp).

The retained Wayland investigation exposed a callback-lifecycle issue: removing
all rows from inside the owner callback could leave an empty modal popup open.
The candidate now closes the popup before invoking the owner action. Its focused
component and independent consumer checks require the popup to be closed after
removal. The original reports and compositor trace remain failed evidence; an
extra wait did not fix that lifecycle defect.


The [sealed Linux record](../evidence/development/dropdown-menu-20261017/report.json)
retains all 256 complete native comparisons. Every closed state matches; exact
pixels and complete frame sets remain zero. Forty-eight body/caller-only frame
sets match, and all native metadata-label frames remain in the strict comparison.
No expected images, pins, tolerances or approved exceptions changed.

All 41 Qt targets pass before the single callback-lifecycle correction. The
corrected build passes the 16 focused checks at both pixel ratios and both
dropdown helper targets: nine malformed inputs, 32 isolated definitions and 19
malformed catalog definitions. All 37 independent consumer modes and 151
installed catalog captures pass on the corrected package. All 147 prior PNGs
and metadata remain byte-identical. Eight virtual X11/Wayland profiles cover
software/OpenGL rendering and standard/scaled configurations. These are virtual
software-rendered sessions; physical display and hardware acceleration are not
accepted. The actual XTest gallery exercise matches all 24 isolated caller states
across 15 controls; the three owner-result screenshots were visually inspected.
The earlier callback-removal failures and unsuccessful wait diagnostic remain
preserved alongside the corrected results.

The full 762-contract run and six additional candidate guards are recorded
separately. Frozen source replay binds 12 snapshots to immutable base Git objects
and exact changed Linux blobs. The installed package and independent consumer
have their own hashes; build caches are excluded. Independent-machine replay,
source sizing, native label and item-update timing, native popup material,
shadow/placement, fonts/symbols/raster, input timing, accessibility, physical
input/display and readers remain open gates.

Run `python3 scripts/generate-dropdown-menu-witnesses.py --check` and
`python3 scripts/verify-dropdown-menu-candidate.py` to check the projection and
sealed evidence. Fresh installed capture uses
`python3 scripts/capture-dropdown-menu.py /path/to/InstalledConsumer /new/captures --jobs 2`;
strict comparison uses
`python3 scripts/compare-dropdown-menu.py /new/captures /new/comparison`.
