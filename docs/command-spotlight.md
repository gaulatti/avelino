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

Linux implementation and comparison remain pending. Desktop candidate coverage
stays 73/80 with zero fully accepted APIs. TV and playback remain a separate phase.
