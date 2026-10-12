# Supplemental desktop reference proposal

Status: **proposed; no baseline or exception approval**. The existing 112 expected
button images, pinned source archives and comparison tolerance are unchanged.

The proposal preserves [764 captures](../evidence/reference-proposals/desktop-20261012/captures.json)
from [104 fixture definitions](../evidence/reference-proposals/desktop-20261012/fixtures.json).
It covers all 25 started desktop APIs and five additional monospace-expression
probes. The [API index](../evidence/reference-proposals/desktop-20261012/api-index.json)
links every capture; the [proposal manifest](../evidence/reference-proposals/desktop-20261012/proposal.json)
checksums every file. None is an accepted expected image.

Pure SwiftUI fixtures use ImageRenderer at DPR 1 and 2, both appearances and text
scales 1 and 1.5. Sixty-eight native-control captures use a separate offscreen
NSWindow and NSHostingView cacheDisplay, including actual AppKit text-field and
text-view descendants. Their measured backing DPR is 2. The environment display
scale matches each exported image's DPR, and component dimensions are recorded
separately from the fixed outer frame. Native cached bitmaps originate in the
host's Color LCD profile and are converted to sRGB; each capture records the
original profile checksum and conversion. All 764 images have verified dimensions
and nonempty content. These paths do not establish compositor, overlay, focus,
accessibility or physical-session acceptance. Animated phases remain diagnostic.

| API family | Example source candidate |
| --- | --- |
| Text field / actual AppKit font | [Default field](../evidence/reference-proposals/desktop-20261012/textfield-md-light-text1.0-hosting-dpr2.0.png) |
| Multiline editing | [Scaled dark text area](../evidence/reference-proposals/desktop-20261012/textarea-filled-dark-text1.5-hosting-dpr2.0.png) |
| Card variants | [Outlined card](../evidence/reference-proposals/desktop-20261012/card-outlined-md-light-text1.0-offscreen-dpr2.0.png) |
| Native loading presentation | [Spinner](../evidence/reference-proposals/desktop-20261012/spinner-md-light-text1.0-hosting-dpr2.0.png) |
| Inherited toggle label | [System font](../evidence/reference-proposals/desktop-20261012/toggle-inherited-false-light-text1.0-offscreen-dpr2.0.png), [explicit Encode Sans](../evidence/reference-proposals/desktop-20261012/toggle-default-false-light-text1.0-offscreen-dpr2.0.png) |
| Monospace expression | [15 pt regular](../evidence/reference-proposals/desktop-20261012/mono-15-regular-light-text1.0-offscreen-dpr2.0.png) |

The source is the exact desktop artifact at `fe8a1d462fbd793d883fb92086a16aa2947e32c9`.
All 53 extracted source/resource files still match their preserved checksums after
building. The capture package's dependency revisions match the original source
lock. The host uses macOS 27.0, Xcode 27.0 and Swift 6.4, while the existing button
baseline records macOS 27.0.1. A DPR 2 anchor comparison changes seven light-theme
pixels by at most one channel unit; the dark anchor is identical. These are
[recorded differences](../evidence/reference-proposals/desktop-20261012/anchor-comparison.json),
not tolerance or baseline approval.

The [tooling record](../evidence/reference-proposals/desktop-20261012/tooling-provenance.json)
identifies a checksummed source bundle stored outside Avelino at
`../avelino-reference-vault/candidates/desktop-20261012-332aae8/native-capture-source.tar.gz`.
Its SHA-256 is `352984d39eb2010b5e33065af939581c6e3873f6d4f94a5824ba8becfd43f2db`.
It includes the source artifact, capture tool and lock files; clean extraction was
verified separately. Copy this artifact outside Avelino on another Mac to replay
the recorded commands. The external artifact has no public download endpoint.
Swift/Apple capture code and source archives are absent from Avelino's current tree.

After replaying the native capture command from the external tooling record, use
the public Linux-compatible postprocessor to prepare the review metadata:

```sh
python3 -m venv .cache/proposal-tools
.cache/proposal-tools/bin/pip install -r tools/visual-requirements.txt
.cache/proposal-tools/bin/python scripts/prepare-proposal.py \
  --captures ../avelino-reference-vault/candidates/desktop-20261012-332aae8/review-candidates \
  --tooling ../avelino-reference-vault/candidates/desktop-20261012-332aae8/tooling-provenance.json \
  --output artifacts/native-proposal-replay
```

The output must be a new directory. The postprocessor copies only named PNGs,
validates their dimensions and nonempty content, and checksums its own source in
the proposal manifest. A replay of the preserved inputs reproduced all 764 PNGs
and all proposal metadata byte for byte. It refuses accepted-reference locations;
preparing a proposal grants no baseline or exception approval.

The monospace [resolution record](../evidence/reference-proposals/desktop-20261012/monospace-resolution.json)
reports `.AppleSystemUIFontMonospaced-Regular/Medium/Semibold/Bold` as returned by
Core Text in the fixture environment. The catalog text says “IBM Plex Mono,” but
its implementation requests a system monospaced font. These are source-expression
probes; actual affected-component/glyph-fallback verification is still required.
No Apple font is bundled. The unconfigured toggle probe resolves `.SFNS-Regular`
at 13 pt; its explicitly configured counterpart resolves Encode Sans Regular at
14 pt. Current Avelino's default toggle uses the latter and remains pending.

`python3 scripts/verify-proposals.py` checks image hashes, logical/pixel dimensions,
environment DPR, case matrices, source/dependency provenance links and required
enum combinations discovered in the pinned source. A valid-looking matrix that
omits the outlined card variant fails. The verifier rejects self-approved proposals
and never copies files into `reference/captures/`.

Matching isolated Linux fixtures and their comparisons, complete behavior cases,
native DPR 1 captures, overlays, animation timing, fonts/emoji decisions and actual
display-session acceptance remain open. A future baseline update must explicitly
select reviewed cases and preserve the current source imagery.
