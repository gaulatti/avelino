# Surface modifier source investigation

The pinned `BleeckerSurfaceModifier` decorates caller content in this order:
card background, continuous rounded clipping, an inset border overlay, then a
light-only deep-sea shadow with opacity 0.055, radius 14 and vertical offset 5.
It adds no padding, font, foreground style, layout container or input handler.
`View.bleeckerSurface(radius:)` supplies the default radius 12.

An external client can name the public modifier type and call that extension.
Its direct radius initializer is internal. Three compiler probes against the
fresh unchanged-source module preserve the successful public type/extension
checks and the expected inaccessible-initializer error. This describes the
source API; it does not require a matching Swift constructor on Linux.

The [sealed source investigation](../evidence/reference-investigations/surface-modifier-20261016/investigation.json)
covers 52 fixtures in eight appearance/text-scale/requested-bitmap-DPR contexts,
for 416 groups. Each group retains the original public image, a separately
probed public image, a literal modifier-body witness, and the bare caller. All
416 public/probe/witness triples are byte-identical. All public and bare caller
frame sets match. The centered layouts did not request text baseline guides:
their empty baseline maps do not establish baseline behavior.

Fixtures cover omitted/default and finite custom radii, negative/zero/fractional
and oversized radii, clear/opaque/overflowing content, hidden/empty/zero/wide
callers, fixed and inherited fonts/foreground, native Button, Unicode/bidi text,
outer width offers, RTL, flat children and explicit stacks. The Surface modifier
does not read text scale; these callers retain their own font choices. Negative
radii -12 and -1 paint identically to zero in the measured clear-caller cases.

Flat caller children remain separate views. In a centered parent, the first text
and 72-by-44 rectangle overlap at their own centers, each with its own decorated
bounds. In an HStack they occupy separate positions among the parent's siblings;
their surfaces do not introduce a group-sized wrapper. An explicit HStack or
VStack is one caller with one decorated outer frame. EmptyView emits no part,
whereas a zero-size caller retains its zero frame. These observations require
per-caller decoration in a generic Linux modifier adapter.

Thirty live histories change radius, appearance and text scale and restore the
initial values. The corrected helper retains one caller instance and appearance,
with no disappearance, throughout all six steps. Public and literal-witness
history pixels match. Every final image restores its initial PNG bytes. These
are hosted state observations; the native Button was not activated in this
capture and native keyboard/input acceptance remains pending.

The initial helper switched between omitted/default and explicit-radius
ViewBuilder branches during histories. That helper choice recreated the caller;
its histories cannot establish source retention. The complete original attempt,
its exact clean replay and the diagnosis remain in `diagnostics/`. The corrected
helper holds one public-call branch throughout each history. All 1,664 closed
images remain byte-identical to the original attempt. No retained-state assertion
or expected capture was relaxed.

A source-only archive rebuilds the unchanged 89-file Sabella source tree and
reproduces all 1,845 corrected outputs byte for byte. Apple source, capture tools,
projects and source archives remain outside this Linux repository. Archive
locators and hashes are in [tooling provenance](../evidence/reference-investigations/surface-modifier-20261016/tooling-provenance.json).
Independent-machine archive availability remains pending. `NSHostingView`
bitmap captures at requested DPR one/two, with actual window backing DPR two,
do not prove physical-display or compositor equivalence.

Run `python3 scripts/verify-surface-modifier-source.py`. References CI also runs
negative contracts for missing/duplicated contexts, collapsed flat children,
changed bare geometry, caller recreation, skipped live steps, forged acceptance,
empty-baseline claims, source rebuilds, public API exposure and replay coverage.
Reference pins, approved exceptions, expected images and tolerances are unchanged.
The wiki remote remains unavailable; this contract is maintained in the repository.

## Linux surface border

The existing `BleeckerSurface` candidate renders one allocated caller surface.
Opaque content previously covered its border because the border was painted
with the background before the caller. The card fill and caller now share the
continuous clip, followed by one border overlay, matching the source's operation
order. Clear content keeps a
single border. The Data Display gallery's opaque clipped slot exercises this
presentation, and component fixtures check both themes, square/rounded corners,
opaque/clear callers, pointer/keyboard actions, local state, focus and actual Qt
accessible names at DPR one/two.

The [sealed Linux checkpoint](../evidence/development/surface-border-20261016/validation.json)
passes all 25 Qt targets, 396 Python contracts, 28 independent consumer modes,
123 catalog captures and eight executable-only virtual profiles. All 119
unrelated gallery PNGs and all 123 metadata files remain byte-identical. It also
preserves a controlled async Shape capture defect and the displayed-ready-frame
correction. Small text-pixel variations reproduced in unchanged old OpenGL
processes remain unaccepted; no image masking or tolerance change is introduced.

That paint checkpoint covers one allocated surface. The generic adapter below
is a later development checkpoint; its inventory entry remains pending and the
existing extension mapping remains verification-pending. Source investigation
does not increase the 64/80 candidate count or accept any mirror entry.

## Generic Linux adapter under verification

`BleeckerSurfaceModifier` decorates each logical caller leaf independently. Its
default radius is 12; finite custom values include zero, negative and fractional
radii. Negative radii use the existing zero-radius paint path. Nonfinite values
produce an explicit Linux diagnostic; native equivalence for those inputs is open.

```qml
BleeckerSurfaceModifier {
    radius: 12
    BleeckerText { text: "First child" }
    Rectangle { width: 72; height: 44; color: "#2c5784" }
}
```

These are two surfaces. Put the children inside an explicit `ProposalRow` or
`ProposalColumn` for a single decorated stack. `BleeckerLayout.flattenChildren`
keeps font and Loader scopes transparent to the surrounding proposal layout.
An empty modifier emits no surface; a zero-size Item remains one caller. Hidden
callers retain their extent and background.

The adapter reparents each existing caller visually into a paint/layout host
inside its original inheritance scope. It leaves QObject ownership with the
caller’s creator and keeps the same caller and decoration during radius/theme
changes. It supplies no font, foreground, padding, action or focus target.
Nested surfaces retain separate paint layers; dynamic flat scopes and Repeaters
update their emitted parts. Width proposals and implicit first baselines pass
through each part to its caller.

Component checks compare fixed-caller bounds with 248 preserved native contexts
(31 fixtures in both appearances, text scales and DPRs). Separate Linux checks
exercise flat and explicit layouts, nested decoration, dynamic removal, wrapping,
font inheritance, retained local state/focus, pointer/keyboard actions and actual
Qt accessible names. These baseline and input checks are Linux observations;
the native centered corpus does not establish first-baseline or hit-test parity.

The independent package mode `InstalledConsumer --surface-modifier` exercises
separate caller surfaces, an explicit stack, inherited font, live/restored radius
paint and retained button input. The virtual-session runner includes this mode.
Its [development evidence](../evidence/development/surface-modifier-kernel-20261016/validation.json)
preserves the frozen inputs, earlier failed assertions and actual run exits.
The complete 52-fixture capture/catalog adapter, strict native raster/shadow and
proposal/baseline comparison, source hit testing, physical displays and readers
remain open. No expected image, source pin, mapping or tolerance changes.
