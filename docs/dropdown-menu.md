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
matrix is recorded in the [sealed investigation](../evidence/reference-investigations/dropdown-menu-20261017/investigation.json). Desktop
candidate coverage remains 74/80, with zero accepted APIs. All native sources,
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
