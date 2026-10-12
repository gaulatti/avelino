# Reproducible reference sources

`reference/source-manifest.json` records checksummed, immutable source archives
for the exact desktop and television revisions. The archive scope is `Sources`,
`Package.swift`, and `Package.resolved`: all library, catalog, shell-example, native
workaround, resource, and dependency inputs needed to build/render the reference.
It deliberately excludes repository management metadata and unrelated test fixtures.
It is a source artifact, not a replacement Git repository or a new Sabella release.

The preservation script reads Git objects without creating refs, checking out,
merging, resetting, committing, or pushing in Sabella. It uses a deterministic
Git archive compressed with a zero gzip timestamp. Individual file hashes, Git
blob IDs, commit/tree metadata, and archive SHA-256 are recorded. Run verification
in a clean temporary directory; every file, dependency lock, and artifact checksum
must match. An unexpected or missing member fails verification.

```sh
python3 scripts/verify-references.py
```

Another machine needs only this repository to extract identical reference inputs.
Apple SDKs are still necessary for SwiftUI rendering. Tooling provenance and
per-capture metadata distinguish the original preservation environment from the
environment used for each later capture. A dependency revision is not proof of
an installed SDK or a verified device render.

The source archives are immutable. A reference update requires an explicit
baseline-update change with reviewed source and visual differences. Keep the old
artifact and captures; change fixtures and expectations only with a recorded
reason and approval. CI can compare baselines but cannot update them.

## Initial rendered candidates

`scripts/capture-reference.sh` builds a thin capture executable against the
verified desktop source artifact in an isolated directory. The GitHub `xcode-27`
runner supplies macOS 27 and Xcode 27; the actual versions are saved per run rather
than assumed to equal the preservation host. This produces 112 offscreen button
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
