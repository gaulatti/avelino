# Implementation evidence

This is a checkpoint record, not desktop or TV acceptance.

| Gate | Evidence | Result |
| --- | --- | --- |
| Immutable source inputs | `scripts/verify-references.py`, reference CI | Both exact archives verify in clean extraction directories; source hashes and dependency locks match |
| Discovery / asset provenance | `reference/api-discovery.json`, `assets/provenance.json` | Starting registries reconciled with public modifiers/native adapters; all 18 bundled font files verify |
| Actual SwiftUI source capture | [capture run](https://github.com/gaulatti/avelino/actions/runs/38195797603), `reference/captures/desktop/buttons/` | 112 button cases captured on macOS 27.0.1 / Xcode 27 / Swift 6.4, DPR 2 |
| Font resolution | Each preserved capture's `resolvedFont` | Actual inherited label resolves EncodeSans-Md; Qt resolves Encode Sans Medium. No font substitution approved |
| Build / interaction / packaging | [Linux run](https://github.com/gaulatti/avelino/actions/runs/38198601179) | x86_64 and ARM64 build, pointer/keyboard/editing tests, and independent consumer pass; second consumer has no product source/build trees |
| Initial visual comparison | [comparison CI](https://github.com/gaulatti/avelino/actions/runs/38199378037), `evidence/checkpoints/68a5dfb/` | 0/112 source cases pass on each architecture. Raw candidate pixels match across architectures; button edges and glyphs still differ from Sabella. Cases remain verification-pending |
| Wayland / X11 / accessibility / scaling matrix | [display-session CI](https://github.com/gaulatti/avelino/actions/runs/38199094278), `scripts/check-display-sessions.sh`, package-only consumer | Eight virtual-session configurations pass on x86_64 and ARM64 using software and OpenGL/llvmpipe; full parity, accessibility, input delivery and overlay gates remain pending |
| Desktop acceptance | `docs/parity-inventory.json` | Pending; required visual, behavior, and runtime cases remain open per component |
| Television / hardware | User target TBD | Pending; no physical remote or sustained playback verification |

Font-probe instrumentation changed zero rendered pixels across all 112 source
cases compared with the earlier capture tool. Reference PNGs and hashes are now
preserved in Git. Capture jobs write candidates into `artifacts/`; they never
replace these files. Future source/capture baseline changes require explicit
reviewed updates. There are zero approved visual exceptions.

The first measured Linux button used an unnecessary integer width ceiling and
center snapping. Removing those preserves fractional font/layout measurements;
the resulting captures still need to pass geometry and glyph comparisons. This
change does not create a tolerance or accept the remaining differences.

The 14 px medium label's native font metrics have a 17.5 px line height. Keeping
that fractional height and disabling center snapping avoids an extra half-pixel
baseline shift at DPR 2. Font family, face, size, and weight remain the reference
values. Raw glyph and rounded-edge differences remain open after this correction.

The source-comparison job now reports raw button differences separately from the
build/runtime/package jobs. Its strict failure remains visible while mirroring
continues. Nineteen contract tests check immutable extraction, Linux-only source
storage, ignore rules, forced additions, archive contents, and comparison failures,
including RGB changes with unchanged alpha, alpha-only changes, changed expected
checksums, incompatible text/DPR scales, missing captures, and unreviewed ICC data.

The `68a5dfb` checkpoint preserves both comparison reports, x86_64 environment
metadata, and the medium primary-button candidate with checksums. It links the
full CI candidate/runtime artifacts. The medium primary case differs in 936 pixels,
with maximum channel error 211; alpha matches. No source image changed, no
exception was approved, and no component was marked complete.

The continuous-corner implementation adds supplemental native contour measurements
in `evidence/geometry/native-rounded-rectangle.json`. The probe runs outside the
Linux repository and records its checksum, OS, SDK, and compiler. Its macOS 27.0
diagnostic does not replace the macOS 27.0.1 source images. Sixteen geometry cases
compare all fill and inset-border control points, with at most one Float32 rounding
unit of difference; the screenshot comparator still allows zero changed pixels.
Qt Quick tests now report 26 passing cases including this contour coverage.

The first local software-rendered contour candidates still fail all 112 image
comparisons. Relative to the previous preserved candidates, total absolute RGB
error fell from 17,682,799 to 16,488,999, while changed-pixel counts improved in
17 cases, stayed equal in 36, and increased in 59. The light medium primary case
changed from 936 to 1,001 differing pixels. This mixed result is diagnostic evidence,
not visual acceptance. A native text-rendering/no-hinting probe changed zero pixels
in eight light/dark primary cases, so those experimental settings were removed.

The clean `75cb37a` CI checkpoint reproduces these metrics on x86_64 and ARM64.
`evidence/checkpoints/75cb37a/` preserves both strict reports, the medium primary
candidate and metadata, source/compiler environment, and per-case change metrics
with checksums. It also retains all eight x86_64 session metadata records and two
representative whole-output/window capture pairs; the linked runtime artifact
contains the remaining captures. All 112 candidate images match across architectures. Both
build/runtime/package jobs pass; both visual comparison jobs fail. The package
regeneration check seeds obsolete consumer/install files and proves their removal.
The eight installed-session configurations confirm software Shape rendering and
RHI curve rendering at the expected logical radius; full desktop, accessibility,
overlay, and television acceptance remain pending.
[Checkpoint CI](https://github.com/gaulatti/avelino/actions/runs/38263908908)

The next local button candidate aligns painted background origins and label
baselines to physical pixels, rounds label line boxes at the effective DPR, and
positions default content explicitly. This fixes a positioner/anchor interaction
that displaced short link labels. Thirty-seven Qt checks pass at each of DPR 1
and 2, including movement, transformed ancestors, displayed-window reparenting,
all four link sizes, and pointer activation. The fresh installed package also
passes its eight virtual X11/Wayland software/OpenGL configurations, including
painted-coordinate checks after loading changes the composition.

Against the preserved `75cb37a` candidates, this local 112-case matrix lowers
absolute RGB error from 16,488,999 to 12,672,387. Changed-pixel counts improve in
105 cases, stay equal in two, and increase in five. Color error improves in 108
cases and increases in four: small link buttons in both themes, enabled and disabled.
The light medium primary case falls from 1,001 to 863 changed pixels, with maximum
channel error 168. These are dirty-tree development measurements, awaiting clean
CI reproduction and a checksummed checkpoint. All 112 strict comparisons still
fail. Expected captures, fonts, and zero-pixel tolerance remain unchanged; no
visual, accessibility, overlay, desktop, or TV acceptance is implied.

The clean `efb2a90` CI run reproduces the local metrics on x86_64 and ARM64.
Both build/runtime/package jobs pass, and both strict image comparisons fail.
All 112 candidate PNGs match across architectures. The checksummed
`evidence/checkpoints/efb2a90/` preserves the complete candidate matrix and metadata,
both comparison reports, the compiler/dependency/source environment, per-case
changes from `75cb37a`, and all eight x86_64 whole-output/window capture pairs
with their capture-tool and compositor records. These files remain available
independently of CI artifact retention. The reference verifier checks complete
candidate coverage and painted coordinates as well as hashes. Replay the strict
comparison against this candidate directory with an output under `artifacts/`;
exit status 1 is the preserved failed result.
[Clean CI](https://github.com/gaulatti/avelino/actions/runs/38273039988)

The fractional-typography candidate preserves a 19.5 px requested button font
instead of rounding it to 20 px. Fifty-seven Qt checks pass at each of DPR 1 and
2. The default 14 px label's advance becomes 46.487 logical pixels. Its first
dirty-tree comparison has mixed results: total absolute RGB error increases
from 12,672,387 to 12,731,331; 42 cases improve, four stay equal, and 66 worsen.
The light medium primary case decreases from 863 to 859 changed pixels. All
112 strict comparisons still fail. The new painted text path also exposes
opacity-composition differences in disabled text. Clean CI reproduction and
preserved candidate evidence are still required. Source images and tolerance
remain unchanged, and no component or exception is accepted.

Desktop implementation now proceeds in small component-family batches alongside
these pending comparisons. Shared typography and asset issues remain attached
to every affected fixture; broader implementation does not close their gates.

The next batch adds separator, skeleton, Bauhaus background, determinate progress,
button group, header, and panel-layout candidates. The new contracts exposed and
corrected invalid CSS alpha-color strings at the Qt token boundary. This preserves
the pinned neutral token values while making border/input colors usable by Qt.
The component suite passes 97 checks at each of DPR 1 and 2. A fresh package-only
container passes independent consumption and all eight virtual X11/Wayland
configurations, including grouped keyboard activation/tab order and return to
editing. Four light/dark, DPR 1/2 gallery captures were inspected. Native image
comparisons for the seven new components remain missing. The inventory
continues to report zero accepted components and zero approved exceptions.

The clean typography checkpoint also passes both architecture build/runtime/package
jobs and reference CI; all 112 visual comparisons fail on each architecture. Its
painted text path produces different raw pixels between x86_64 and ARM64, so the
earlier checkpoints' cross-architecture identity does not carry forward. No
architecture difference is accepted or hidden by a tolerance.
[Typography CI](https://github.com/gaulatti/avelino/actions/runs/38280257407)
