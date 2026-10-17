# Complete closed surface candidate

This is verification-pending evidence, with no accepted mirror entry. All 52
closed native fixtures are captured in eight contexts (416 cases). Strict native
comparison has 36 exact pixel/frame matches, 376 exact frame sets and 416 matching
caller states. The five remaining frame cases are system font, native button,
Unicode, bidi and inherited system font. No native baseline guides were requested.

Run `python3 scripts/verify-surface-modifier-candidate.py` with the repository's
visual requirements installed. It rechecks preserved image bytes, raw pixel
errors, complete emitted rectangles/states, all display profiles and actual XTest
viewports. All 427 host contracts pass; nine negative contracts protect the integrity boundary. Source pins,
expected images, font/symbol mappings, masks and tolerances are unchanged.

- `captures/`: every final PNG, full metadata, command/exit receipt and log.
- `comparison/`: every strict result, raw difference, overlay and source/candidate
  pair. The comparison remains failed; counts are not acceptance.
- `runtime/`: sixteen final executable-only profile records. Eight surface
  profiles each measure 52 contexts, 47 exact frame sets and five retained six-step
  histories. Another eight base profiles cover the shared capture helper.
- `operator-ui/`: actual XTest delivery to all ten toolbar controls, with eleven
  complete 640-by-400 Qt viewports matching independently captured Qt fixtures.
  Only the operator executable's diagnostic metadata adds toolbar hit centers;
  the public QML and installed module are unchanged. Producer/consumer sources
  and producer builds are absent from the operator runtime mount.
- `implementation-inputs/`: the exact reviewed code and pipeline snapshots.

The full 27-target Qt suite passed on v2 (5,319/5,547 component checks at DPR
one/two). The final RTL/readback changes pass both affected surface targets on
v4. All library and other component inputs are identical; all 96 published module
files remain byte-identical. Final package checks run 29 modes and 127 galleries,
retaining all 123 older PNGs and metadata; all 125 installed files match across
final producer, independent package and executable-only runtime copies.

Six archives retain complete earlier attempts and manifests. `builds` includes
the first missing-manifest failure and both complete suite attempts.
`earlier-captures` retains both the palette-loop and pre-RTL-fix captures plus raw
comparisons. `packages-and-host` records original/corrected consumers and host
checks. `display-runtimes` keeps the original GL failure and all final profiles.
`readiness-diagnostics` preserves original/restored images, twenty later frames,
the mount trace and corrected replay. All actual exits remain recorded.

The palette-loop correction changes none of its 416 PNG or metadata bytes. The
RTL semantic-anchor correction changes only eight candidate images. The GL
failure was a premature initial readback: both Shapes were Ready with their final
paths/colors, yet the first image lacked its border. The next readback contained
it. Capture readiness now requires identical window readbacks plus ready geometry;
the original exact restoration assertion remains unchanged and passes all five
histories with the same installed library.

Native raster/shadow, system fonts/native button, first-baseline/hit testing,
physical displays/input and readers remain open. Desktop is 65/80 candidates with
15 pending and zero accepted. All 46 TV entries remain a separate pending phase.
