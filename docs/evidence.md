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
| Desktop acceptance | `docs/parity-inventory.json` | Pending; representative mirror proof precedes expansion |
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
continues. Ten contract tests check immutable extraction and comparison failures,
including RGB changes with unchanged alpha, alpha-only changes, changed expected
checksums, incompatible text/DPR scales, missing captures, and unreviewed ICC data.

The `68a5dfb` checkpoint preserves both comparison reports, x86_64 environment
metadata, and the medium primary-button candidate with checksums. It links the
full CI candidate/runtime artifacts. The medium primary case differs in 936 pixels,
with maximum channel error 211; alpha matches. No source image changed, no
exception was approved, and no component was marked complete.
