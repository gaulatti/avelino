# Empty, error and loading presentation contract

The desktop source is pinned to
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`:
`BleeckerEmptyState` and `BleeckerLoadingOverlay` in
`Sources/Sabella/Feedback.swift`, and `BleeckerErrorState` in
`Sources/Sabella/Extended.swift`. Linux candidates are now implemented; complete
mirror acceptance remains pending. The earlier source-only checkpoint did not
change implementation coverage.

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
implementation; coverage at that checkpoint was 43/80 started and zero fully accepted.

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

At the source-only checkpoint, all 431 raw outputs replay byte-for-byte after a clean extraction, verification
of the 35 build inputs and helper recompilation. All 72 contract tests passed then,
including eight new adversarial source-evidence checks. Existing reference,
proposal and inventory verification passes. This checkpoint changes source
evidence and its validation, so no new Linux runtime or visual pass is claimed.

## Native progress capture correction

Visual review found unsupported-view markers in all 64 historical LoadingOverlay
ImageRenderer images. Those immutable files remain preserved diagnostics and are
excluded from visual proposals. The [hosted investigation](../evidence/reference-investigations/loading-native-20261015/investigation.json)
records 32 actual NSHostingView captures with one visible, large, indeterminate
32×32 NSProgressIndicator in each. All 33 raw image/metadata files replay
byte-for-byte from 35 verified helper inputs. Native animation phase, active-window
context and actual native DPR 1 remain pending.

The [corrected proposal](../evidence/reference-proposals/presentation-states-20261015-v2/proposal.json)
contains 240 static empty/error/button captures and 32 hosted loading captures.
It records both capture tools and their API assignments. Its verifier rejects
ImageRenderer loading placeholders, missing native descendants, hidden progress
views and changes to the sealed source records. Component tests replace the
unsupported loading rows with the actual hosted measurements. The original
centered-text witnesses and action/pointer records remain unchanged.

## Linux adapter

`BleeckerEmptyState` requires `title` and `message`, and has nullable Component
factories `actions` and `icon`. The icon defaults to an original tray candidate;
`BleeckerErrorState` supplies the error triangle and default title. There is no
SF Symbol string resolver. A null actions factory means source EmptyView, while
a zero-size Item keeps the stack gap. The Loader keeps action identity and private
state through producer updates, and destroys that subtree when its owner or
factory is removed. `loadedActions` exposes the current factory root.

```qml
BleeckerEmptyState {
    width: 320
    title: "No editions yet"
    message: "Create an edition to get started."
    actions: Component {
        BleeckerButton {
            text: "Create edition"
            maximumWidth: parent.availableWidth
        }
    }
}
```

Qt `width` represents the caller's offered frame. The fitted pre-frame
`presentationItem` centers the actual padded stack within it. Its real Item
bounds are compared with the source's pre-frame GeometryReader, and the offered
Qt frame is recorded separately. The action factory parent exposes
`availableWidth`. For unconstrained intrinsic composition, leave a button's
`maximumWidth` at its explicit `-1` intrinsic setting. A finite proposal wraps
the default button label without changing preceding unconstrained buttons.

`BleeckerLoadingOverlay` accepts `message` (default `Loading…`) and covers its
offered Item bounds. It owns the dim layer, input blocker, card, rounded-content
host, existing large spinner and fixed-font label. It does not take focus or
declare modal accessibility semantics; those source contracts remain unverified.
Use an enclosing window/content Item for the intended overlay region. Linux
safe-area/window integration remains separate from the source's ignoresSafeArea.

Message text uses centered lines in its measured fitted width. Source line-origin
checks cover every trusted DPR 1/2 expression; the changed DPR 2.5 witness remains
untrusted. Shared text keeps its prior default left alignment. Symbols use the
measured DPR 1/2 frames with original paths; other scales, glyph shapes and exact
pixels remain unaccepted. Existing software rounded clipping limitations, generic
composition, broader scripts/RTL multiline behavior, source motion, real readers
and physical input/display remain pending.

## Candidate verification

The [Linux checkpoint](../evidence/development/presentation-states/candidate.json)
records 272/272 matching measured bounds and 0/272 exact images. Empty/error
measurements use the real fitted presentation Item before the caller frame;
loading measurements use the offered root (plus the intrinsic source case).
Actual Qt action wrapper/template bounds match the source in all 184 applicable
static cases. Source-derived pointer/lifecycle checks cover 68 source records,
with 136 Qt checks across DPR 1/2. Native source input remains DPR 2 evidence.

All 3,646 Qt checks, 77 contracts and 15 invalid-startup refusals pass. Fourteen
installed offscreen modes, a fresh 112-pair package-only virtual-session matrix
and 67 installed-catalog captures pass. Basic/Fusion/default gallery images match.
All 2,978 preceding PNG/full metadata pairs remain byte-identical. The corrected
source references and validation inputs were followed by a full new Linux run
and a new independent package matrix; the earlier run is retained locally as a
diagnostic. All 113 runtime package files also match across the reference-only
correction.

The two source tools retain their separate provenance: the original 431-file
replay includes preserved diagnostics and expression witnesses; the new hosted
loading replay contains 33 byte-identical files. No mask, resize, tolerance,
accepted exception or source pin changed. Forty-six of 80 desktop APIs have
started; none is fully accepted. Exact symbols/raster/spinner presentation,
source keyboard/focus/modal/safe-area and animation phases, broader generic
composition/scripts/RTL/fractional-scale contexts, physical sessions and actual
readers remain pending. The public wiki remains unavailable; documentation lives
in the repository. This native-only checkpoint has no backend/metrics,
configuration, authentication or TV change.
