# Empty, error and loading presentation contract

The desktop source is pinned to
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`:
`BleeckerEmptyState` and `BleeckerLoadingOverlay` in
`Sources/Sabella/Feedback.swift`, and `BleeckerErrorState` in
`Sources/Sabella/Extended.swift`. These APIs are still implementation-pending.
Source investigation and proposed captures do not change acceptance or coverage.

Before implementation, establish these observable criteria:

- Empty/error states retain the title, message, icon and always-present action
  subtree across producer updates. EmptyView and a zero-size action view must
  preserve their distinct stack spacing. Action activation, disabled rejection,
  private state and subtree removal must pass through normal input paths.
- Measure intrinsic, ordinary, narrow, long, empty, explicit multiline and RTL
  layouts. Preserve the source's 32-unit padding, 12-unit stack spacing,
  primary 17 semibold title and secondary 13 message. Message lines are centered;
  title lines retain the source's default alignment. The custom text-scale
  environment must not change these fixed-font expressions.
- ErrorState reuses EmptyState with the source's error symbol and default title
  `Something went wrong`. Caller-provided titles and action content remain live.
- LoadingOverlay covers its offered region with background opacity 0.72 and
  centers the source large spinner and primary 14 medium message in a card with
  24-unit padding, 12-unit spacing and dialog radius. Measure actual source input
  behavior before deciding whether this visual overlay blocks underlying input.
- Source symbol geometry, original Linux icon candidates, spinner presentation,
  clipping, line alignment and motion require separate evidence. No Apple symbol
  artwork or system font is redistributed, and no equivalence is implied by an
  original candidate.
- The installed Linux catalog and an independent package consumer must exercise
  all three APIs, producer updates, actions, keyboard/focus/accessibility and
  overlay insertion/removal in separate offscreen, X11 and Wayland sessions,
  with software/Mesa rendering and standard/scaled environments.

Existing captures and metadata must remain unchanged when shared text rendering
is extended. Source keyboard/focus, animation phases, safe-area integration,
arbitrary clipping, physical display/input and actual screen-reader acceptance
remain open until supported by their own evidence. TV needs its separately
selected target before implementation. This native-only work has no backend,
metrics, application configuration or authentication surface.

## Source investigation checkpoint

The [investigation](../evidence/reference-investigations/presentation-states-20261014/investigation.json)
contains 304 static source captures: 120 EmptyState, 112 ErrorState, 64
LoadingOverlay and eight preserved-button anchors. The matrix separates light/dark,
text scales 1/1.5 and DPR 1/2. These are source measurements before Linux
implementation; coverage remains 43/80 started and zero fully accepted.

Sixty-eight source pointer/lifecycle cases run in isolated helper-owned windows
at DPR 2. Empty/error actions activate normally, reject disabled/canceled clicks,
retain private counter state across title/message updates, unmount on removal
and reset on recreation. EmptyView omits the action spacing; an explicit zero-size
action view retains twelve units. LoadingOverlay blocks the center and edge
controls within its offered rectangle, allows a control outside that rectangle,
and restores underlying input after removal. Each loading test first activates
the same measured underlying control with the overlay absent. These observations
establish the tested pointer boundary; source keyboard trapping and modal
accessibility semantics have not been established.

Independent source symbol expressions resolve tray to 39×28 at DPR 1 and
39.5×28.5 at DPR 2; the error triangle measures 35×30 and 35×31 respectively.
The nominal system-symbol font size of 28 is not a square image-frame mandate.
The future Linux symbol adapter must preserve measured layout while exact glyph
and raster acceptance remain pending.

Sixty-three centered secondary-text expressions record line origins, bounds,
trailing spaces and fitted view sizes at DPR 1 through 3. The public TextRenderer
instrumentation redraws the actual source layout. Sixty-two probe PNGs are
byte-identical to their uninstrumented witnesses, including all DPR 1/2 cases.
The long message at offered width 180 and DPR 2.5 changes raster output under
instrumentation. Its line data is untrusted and cannot establish parity.
These expressions are separate from the unchanged public EmptyState body.

Run `python3 scripts/verify-presentation-state-source.py` to check the recorded
matrix, source fixed-font resolution, state transitions, positive controls,
image hashes and instrumentation claims. The integrity tests deliberately falsify
acceptance, coverage, overlay input, action lifetime and text-witness claims.
References CI runs this verifier. Source evidence is kept separate from the
implemented-API proposal matrix, so it cannot inflate Linux coverage.

The capture helper and Apple build inputs stay in a checksummed external archive.
They link preserved source-verified Sabella objects; a fresh complete source
build and public helper distribution remain pending. Static spinner frames do
not establish native animation phases. No source pin, expected capture,
tolerance, approved exception, Linux renderer or TV implementation changes.

All 431 raw outputs replay byte-for-byte after a clean extraction, verification
of the 35 build inputs and helper recompilation. All 72 contract tests pass,
including eight new adversarial source-evidence checks. Existing reference,
proposal and inventory verification passes. This checkpoint changes source
evidence and its validation, so no new Linux runtime or visual pass is claimed.
