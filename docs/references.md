# Reproducible reference sources

`reference/source-manifest.json` records checksummed, immutable source archives
for the exact desktop and television revisions. Their bytes are preserved in
Avelino historical commit `0a075b23a6e8911a6e664191849901effc495180`, with an
explicit Git object path for each archive. They are absent from the current tracked
tree, which is Linux-only. Verification recovers them into the ignored
`.cache/reference-sources/` directory and checks the archive hash before use.
The archive scope is `Sources`,
`Package.swift`, and `Package.resolved`: library, catalog, shell-example, native
workaround, resources, and dependency locks. It excludes repository management
metadata and test fixtures. A fresh SwiftPM build of this scoped archive fails
because the unchanged manifest also declares a test target. The
[complete pinned source rebuild](native-source-rebuild.md) records the required
full-tree supplement and its current availability limits.
It is a source artifact, not a replacement Git repository or a new Sabella release.

The original preservation script read Git objects without creating refs, checking out,
merging, resetting, committing, or pushing in Sabella. It uses a deterministic
Git archive compressed with a zero gzip timestamp. Individual file hashes, Git
blob IDs, commit/tree metadata, and archive SHA-256 are recorded. Run verification
in a clean temporary directory; every file, dependency lock, and artifact checksum
must match. An unexpected or missing member fails verification.

```sh
python3 scripts/verify-references.py
```

Another machine needs a full clone of this repository to extract identical inputs.
For a shallow checkout, fetch the recorded historical object explicitly:

```sh
git fetch origin 0a075b23a6e8911a6e664191849901effc495180
python3 scripts/verify-references.py
```

CI fetches the full history for reference verification. The resolver never fetches
or mutates a sibling repository. A corrupt cached archive fails verification and
is never silently replaced. The original source revisions, file hashes, dependency
locks, and archive hashes are unchanged by the storage cleanup. The local migration
also preserved exact copies and tooling checksums in the separate
`../avelino-reference-vault/` directory; reproduction does not depend on that
machine-local directory for recovery of those scoped archives. Full native source
build and helper availability are documented separately. Existing Git history
has not been rewritten.

Apple SDKs are still necessary for SwiftUI rendering. Tooling provenance and
per-capture metadata distinguish the original preservation environment from the
environment used for each later capture. A dependency revision is not proof of
an installed SDK or a verified device render.

The source archives are immutable. A reference update requires an explicit
baseline-update change with reviewed source and visual differences. Keep the old
artifact and captures; change fixtures and expectations only with a recorded
reason and approval. CI can compare baselines but cannot update them.

## Initial rendered candidates

The original external capture pipeline built a thin executable against the
verified desktop source artifact in an isolated directory. Its source and shell
tooling remain recoverable from the same historical Avelino commit; use a separate
directory outside the Linux repository for any future Apple reference work.
There is no Apple build or capture workflow on the current branch.
The recorded GitHub `xcode-27` run used macOS 27 and Xcode 27; actual versions were
saved per run rather than assumed to equal the preservation host. It produced 112 offscreen button
cases: two appearances, seven variants, four sizes, and enabled/disabled states,
each at 240×96 logical pixels and DPR 2. No Apple system fonts or symbol assets
are copied; these initial fixtures use the bundled Encode Sans medium face only.

Outputs are **candidates**, not accepted expectations. The ImageRenderer path
does not establish pressed/focus/loading, menus, overlays, separate native windows,
or actual display-session behavior. Linux generates the corresponding case matrix.
Review comparisons and metadata before establishing immutable expected captures.

Discovery includes nested public native view adapters and `sabellaTVPanel`, in
addition to the registered components. These record Sabella's platform integration
for comparison; they do not mandate UIKit-shaped APIs in Avelino. Asset verification
also checks every bundled font and brand file against the preserved source bytes.

Button capture instrumentation resolves the font inherited by the actual label
using SwiftUI's public `Font.resolve(in:)` and its real environment context. This
records the Core Text face, size, and weight trait rather than assuming the face
from a token name. Linux records its rendered label font and layout metrics too.
Capture-tool changes produce new candidates; previous images remain available for
source and visual review and are never overwritten as accepted expectations.

The initial 112 source images are now preserved with hashes in
`reference/captures/desktop/buttons/`. Verification detects missing, extra, or
changed PNGs. This establishes reproducible source imagery, not Linux acceptance.
The original capture dependency lock is retained byte-for-byte as
`capture-dependencies.json`, with its original path, historical revision, and
checksum in the source manifest. This is provenance rather than a Swift package.

[Supplemental desktop candidates](reference-proposal-20261012.md) now cover all
started APIs, with native AppKit controls captured separately from ImageRenderer.
They live under `evidence/reference-proposals/`, retain proposed status, and have
their own integrity/matrix verifier. Their Apple tooling remains in an immutable
external source bundle. The current expected-image baseline is unchanged.

The [native spinner investigation](spinner.md) preserves 186 hosted context
images and 144 controlled public animation-model frames. Its external source
bundle and 35 input hashes are identified in
[`tooling-provenance.json`](../evidence/reference-investigations/spinner-20261015/tooling-provenance.json).
A clean extraction, input-hash check, helper recompilation and replay reproduced
all 335 raw image/metadata files byte-for-byte. Phase-zero snapshots match the
uninstrumented native image in each size/appearance case. The helper links
preserved pinned-source objects; fresh full Sabella compilation and a public
helper download remain pending. `scripts/verify-spinner-source.py` checks the
tracked geometry, complete model-frame matrix, source identity witnesses and
product opacity measurements. These witnesses are separate from physical native
animation timing and from Linux image acceptance. No native bitmap or vector is
installed as a product asset.

## Linux-only repository boundary

Ignore rules cover Swift files, Apple projects and resources, and local reference
source directories. They do not remove already tracked files or prevent forced
adds. `scripts/check-linux-boundary.py` therefore inspects the Git index and
recognized tar, zip, gzip, bzip2, and xz contents, including nested archives and
archives with disguised filenames. Unsupported archives and inspection limits
fail the check. CI runs this check before recovering external references.

The [alert investigation](alert.md) preserves 256 actual component renders,
96 native lifecycle records and 96 isolated text-layout cases. All 352 image
instrumentation witnesses are byte-identical to uninstrumented rendering. Its
37-input external source bundle replays 722 raw files exactly; the linked
`investigation.json` and provenance retain the full-source/public-download limits.
The 256-image proposal stays review-only, with expected images and pins unchanged.

The supplemental [prose boundaries](../evidence/reference-investigations/prose-boundaries-20261015/investigation.json)
preserve explicit short/long token and renderer-context counterexamples. A
separate 37-input clean extraction replays all 179 files exactly. The 84 trusted
Qt cases retain their source paths; a native-hosted primary18 renderer witness
that changes under instrumentation is excluded and preserved as a diagnostic.
Neither replay approves a new expected image or a visual tolerance.

The [desktop source rebuild](native-source-rebuild.md) compiles the complete
pinned Sabella library target twice without preserved modules or objects. Both
runs reproduce the 1,048-case data-display evidence and seven locale checks:
3,160 files are byte-identical per run. This closes the cached-object limitation
for that helper on the recorded host. Other helpers and independent-machine
input download remain pending; no expected image or Linux acceptance changes.

The [RadioGroup investigation](radio-group.md) preserves 440 hosted public/witness
captures, controlled binding and pointer traces, native String identity and a fresh
source-only replay of 1,358 output files. The tracked Qt normalization diagnostic
retains 17 disagreements. Its source images and Unicode facts do not establish
Linux implementation, visual or reader acceptance. Native tooling remains external.

The [Modal investigation](modal.md) preserves 288 public/probed/witness capture
triples, three sheet triples and 14 behavior traces. A fresh unchanged-source
rebuild reproduces all 977 raw capture/behavior outputs. It separates embedded
dismissal of the hosting window from the caller's sheet context and preserves
inactive accessibility and post-dismissal input diagnostics. Linux implementation
and acceptance remain pending.
