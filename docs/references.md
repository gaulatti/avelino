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
