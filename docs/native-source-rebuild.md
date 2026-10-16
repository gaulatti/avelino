# Pinned desktop source rebuild

The macOS Sabella library target now builds from complete pinned source, and its
data-display capture helper reproduces every preserved output. The
[record](../evidence/reference-investigations/native-source-rebuild-20261016/investigation.json)
covers 1,048 captures and 1,330 formatter witnesses across seven process locales.
Both the initial fresh build and a second source-only archive replay match all
3,160 PNG, geometry, formatter and log files byte for byte. Existing expected
images, source pins, pixel rules and exceptions are unchanged.

The source revision is `fe8a1d462fbd793d883fb92086a16aa2947e32c9`, full Git tree
`db61113381a51fc3c7b3d12786609cd9e76627c8`. A read-only Git archive from the
existing local object supplied all 89 files; no sibling checkout or Git state
changed. Every file matches its pinned Git blob, all 53 historical scoped inputs
match their existing hashes, and both builds leave all 89 source files unchanged.
The verifier reconstructs the complete Git tree from the recorded modes and blob
IDs. This is the same source revision, with its previously omitted tests included.

The historical scoped archive remains immutable. Its standalone build fails:
SwiftPM warns that `Snapshots` is absent, then discovers the missing test target
under `Sources` and rejects mixed-language sources. The
[failed build log](../evidence/reference-investigations/native-source-rebuild-20261016/historical-scoped-build.log)
is retained. No manifest, lock, test directory or source was edited to work around
that failure. Use the complete pinned tree for fresh native builds.

Both successful builds use the unchanged package and locked KSPlayer/FFmpegKit
revisions, `--target Sabella --disable-automatic-resolution`, and deployment target
`arm64-apple-macosx26.0`, matching the earlier helper. The recorded environment is
macOS 27 build 26A428, Xcode 27 build 27A266a, Swift 6.4 and macOS SDK 27.
SwiftPM obtains the locked dependencies from its source cache; no precompiled
Sabella module, object, bundle or helper is an input. Resources are built anew.
The conditional TV implementation is not exercised by this desktop target.

The external source-only artifact contains the full Git archive, unchanged
capture helper and runner, a rebuild script, and an input-hash manifest. It has
SHA-256 `46bbcbd514fc68fec5ccc9f67618c7677d4fba53c81298b2fe3783bd74f3821b`.
Its machine-local locator and individual hashes are in
[build provenance](../evidence/reference-investigations/native-source-rebuild-20261016/build-provenance.json).
A new extraction verifies the inputs, builds into a new scratch directory, links
the helper against the new library object, then replays the full matrix. It needs
no sibling checkout or preserved compiled Sabella artifact.

Run `python3 scripts/verify-native-source-rebuild.py` to audit the tracked record.
References CI also checks the full source tree identity, dependency pins, absence
of compiled inputs and every reproduced hash against the existing source evidence.
This Linux-side audit does not execute a native build.

Independent-machine download of the full source/helper artifact remains pending;
the GitHub source API returned 404 for the pinned revision. The tracked repository
remains Linux-only. Other native helpers, native test/catalog execution, physical
sessions and all TV checks retain their separate gates. Exact Linux fonts,
symbols, locales, geometry, rasterization, animation, input and reader acceptance
are unaffected. Desktop coverage remains 56/80 started and zero fully accepted.
