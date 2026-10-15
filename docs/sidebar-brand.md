# Sidebar and branding candidates

`BleeckerSidebarItem`, `BleeckerBrandMark` and `BleeckerBrandLockup` have Qt
candidates. Complete native visual, keyboard/focus, physical and screen-reader
acceptance remains pending. Desktop and TV evidence stay separate.

The source authority is desktop revision
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`,
`Sources/Sabella/Navigation.swift:3–119`. The
[native investigation](../evidence/reference-investigations/sidebar-brand-20261015/investigation.json)
preserves 416 public-component captures: 208 sidebar, 120 mark, 80 lockup and
eight button anchors. Each fixture uses light/dark appearance, text scale 1/1.5
and ImageRenderer DPR 1/2. All 416 root-geometry and 416 reconstructed-layout
witness images match the independently unmodified public component bytes.
A clean external helper extraction verified 35 inputs, recompiled the helper
and reproduced all 1,249 output files byte for byte. Swift source and native
build inputs remain outside the tracked Linux tree.

## Sidebar items

```qml
BleeckerSidebarItem {
    title: "Editions"
    selected: controller.page === "editions"
    maximumWidth: 320
    icon: Component { MyEditionIcon { color: parent.foregroundColor } }
    onClicked: controller.requestPage("editions")
}
```

The caller owns selection. Every enabled activation emits `clicked()`, including
repeated clicks on an already selected item. The control does not select itself
or change a route. `maximumWidth` is a finite layout proposal; `-1` requests
intrinsic sizing. The actual fitted button is available as `presentationItem`
and `inputItem`, independently of an explicitly sized outer frame.

The owned row has 12-point horizontal padding, two 12-point gaps, a 20-point icon
slot and an eight-point minimum Spacer. Its title uses fixed Encode Sans Medium
at 14 points. The source minimum height is 40; wrapped titles can increase it.
At DPR 2, an intrinsic `Editions` item measures 127.5 × 40. A 120-point proposal
wraps the title into two lines while retaining height 40. A 40-point proposal
produces a 76 × 136 fitted button; fixed slots can exceed the caller's proposal.

Selection uses palette `sea`, a `muted` background at opacity 0.8, and a two-point
leading bar of height 24. Unselected content uses `textSecondary`. Rounded
background/content clipping uses the source's circular seven-point corners.
The button's hit region remains the whole rectangle: transparent corners and
blank Spacer clicks activate it. The native pointer witnesses verify those
regions, repeated activation, disabled/canceled presses and caller title/selection
updates. RTL reverses the content and moves the leading bar to the physical right.

Qt Templates supply input/focus/accessibility mechanisms; Avelino owns the
presentation. Disabled items retain the measured dimmed presentation and emit no
action. `icon` is a required caller Component, replacing the source SF Symbol name
lookup. Its parent exposes `foregroundColor`, a 15-point medium system-font
context and `pixelSize: 15`. A supplied icon keeps its intrinsic height in the
fixed-width slot. The source house/wide-arrow/minus frames are recorded separately
at each DPR. [`SidebarGlyph.qml`](../tests/consumer/SidebarGlyph.qml) contains
original fixture paths; their native artwork/raster equivalence is unaccepted.

## Brand mark and lockup

```qml
BleeckerBrandMark { size: 64 }
BleeckerBrandLockup { name: "Editorial workspace"; maximumWidth: 240 }
```

The mark uses the exact existing Gaulatti-owned PNG from the pinned source:
[`BleeckerLogo.png`](../assets/brand/BleeckerLogo.png), SHA-256
`3eadafd84a1f3b37261bad85b8a8e5512ed7aa9b3baae38aa8321cc3a6cbb9c2`.
The source asset catalog marks it as a template. Avelino embeds its unchanged
bytes in the QML module and also installs the PNG plus
[`brand-presentation.json`](../assets/brand-presentation.json) as provenance.
No logo redrawing, Apple font or Apple symbol artwork is distributed.

`size` defaults to 64. The mark keeps its requested square extent, aspect ratio,
and `textPrimary` tint at opacity 0.9, centered within an optional caller frame.
Sizes must be finite and nonnegative. Zero has zero layout bounds. The recorded
one-point source mark has 1 × 1 bounds but no visible coverage at either DPR:
both the source and the mask's sample positions are retained in evidence.
The Qt image adapter uses bilinear samples of the original alpha mask; it has no
size-specific visibility rule. Exact tint/interpolation/raster remains a separate
comparison gate. Fractional dimensions, theme changes and real software/RHI output
are tested independently from native pixel equivalence.

The lockup owns a 25 × 32 mark slot, a 16-point gap and Encode Sans Bold at
20 points with tracking −0.4. It wraps the caller's name and fits its returned
width to the source layout proposal. Its fixed styles ignore the recorded text
scale and parent-font changes. Empty names preserve a 14-point text line box and
the gap, producing a 41 × 32 lockup. At a 40-point proposal the source overflows
to width 41 and grows to height 200 for `Bleecker`. Brand marks are decorative in
the Qt accessibility tree; the lockup's name is static accessible text. Native
accessibility correspondence and actual reader output remain pending.

## Verification and remaining gates

Run `AvelinoCatalog --fixture sidebar-brand` for the shared gallery and
`InstalledConsumer --sidebar-brand` for the independent package workflow.
The installed mode exercises full rectangular hit regions, normal Qt pointer,
keyboard and actual accessibility actions, caller selection/title updates,
preserved editing/focus, disabled/canceled input, RTL/narrow layout, the embedded
PNG checksum, one-point coverage and fractional logo sizing.

The native integrity check is `python3 scripts/verify-sidebar-brand-source.py`.
Source/proposal integrity tests reject altered identity claims, reclassified
one-point output and callbacks that select themselves or lose corner activation.
The full Linux check captures all 416 isolated cases and CI runs their strict
comparison. Offscreen, independently installed X11/nested-Wayland, software/Mesa,
scaling, focus/accessibility and packaging evidence remain separate.

The preserved Linux run passes 5,596 Qt checks, 97 contract tests, 30 invalid
startup refusals, 19 installed offscreen workflows, 87 relocated catalog
captures and 152 independent virtual window/output pairs. All 3,918 prior
image/full-metadata pairs are byte-identical to checkpoint `cff856e0`. The build
and captures share one frozen 272-input snapshot. These are candidate checks;
none closes a complete native mirror gate.
The 416 component bounds and all 288 title bounds match their sealed native
witnesses. Twenty images match exactly; the remaining 396 fail strict pixels,
so the batch remains unaccepted. See the [comparison report](../evidence/development/sidebar-brand/comparison/index.html)
and [candidate record](../evidence/development/sidebar-brand/candidate.json).

Native SF artwork, exact fonts/tint/interpolation/raster, pressed/focus behavior,
broader scripts/compositions, physical display/GPU/input, actual readers and TV
acceptance remain pending. The helper links preserved source-verified reference
objects; fresh complete Sabella compilation and public helper distribution remain
pending. No reference pin, accepted image, tolerance or approved exception changes.
