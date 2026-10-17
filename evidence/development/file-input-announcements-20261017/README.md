# FileInput location-error announcements

This is a scoped correction to checkpoint `59fd2e8d2c97fe3d89a3b71aaa1760ddd6807040`.
FileInput remains pending; desktop candidate coverage stays 75/80 and strict
mirror acceptance stays open. No expected image, tolerance or exception changes.

The error label sends an assertive public Qt 6.8.3 announcement after binding
updates. The same deferred function coalesces simultaneous requests. Opening a
retained invalid folder and pressing Return on an unchanged invalid path also
request announcements. A metadata refresh stays quiet. A hidden chooser drops
queued announcements without changing keyboard focus.

## Final-source verification

`file-input-qt-v21` builds from a fresh cache in the recovered Qt 6.8.3 image.
All six focused Qt targets pass: two item-lifetime targets, the filesystem and
column targets, and the two owned-UI targets. UI tests exercise initial invalid
folders, identical-path retries, recovery, a quiet metadata refresh and closing
before a deferred announcement. The earlier complete 47-target suite belongs to
the preceding checkpoint; it was not rerun in full for this correction.

The independent installed consumer from the preceding checkpoint is reused,
with its exact binary hash and unchanged source binding. Only its installed
package and executable are mounted. All eight offscreen theme/text-scale/DPR
contexts pass against the fresh source-21 library. The 256 declared closed PNGs
are byte-identical to the preceding checkpoint; complete closed and sizing
metadata is unchanged. Popup diagnostics contain controlled temporary paths and
are not included in this closed-control comparison. No image is masked,
resized, cropped or normalized.

The source-21 installed catalog is exercised through AT-SPI and actual XTest
keys in two virtual sessions. X11/software/light/text-1/DPR-1 delivers four
assertive error events and four Orca utterances. Nested Wayland/OpenGL llvmpipe,
dark/text-1.5/DPR-2 delivers five of each, including an initially missing folder.
Both cover an identical-path retry, recovery, Escape, retained-error reopening
and final cancellation, with no extra cancellation announcement. Raw AT-SPI
events, trees, compositor screenshots, Orca and Speech Dispatcher logs remain.
The observed Weston host window is explicitly focused before Wayland keyboard
input. Orca 46.1 uses espeak-ng through ALSA's null output. There is no physical
listening, hardware acceleration, independent-machine or native reader acceptance.
These two final-source sessions do not constitute a rerun of all eight display
profiles in the preceding checkpoint.

## Provenance and retained attempts

The verification Docker profile lost its earlier images between completed runs.
`recovered-toolchain-v1` retains the new builds, Dockerfiles, inspected image
identities and exact Qt version. Ubuntu's base digest and Qt 6.8.3 remain pinned;
new image identities are kept separate from the deleted images. The final build
uses a new source/build cache. No live cache is copied or mutated.

Source 19's first successful X11 reader run and source 20's Qt/package checks
remain historical attempts. Their source overlays and full hash maps are kept;
only source 21 is bound to the final checks. The earlier draft source-20 seal is
preserved under `attempts/frozen-source20`.

Retained failed/prepared attempts include the missing-image Wayland launch
(v2, no application runtime), the package replay without an output directory
(package v2), the reader wait on Orca's buffered log (v3; the utterance appears
in the final flushed log), and an AT-SPI registration race (v5). Reader v4 was
prepared but never launched. Final reader v6/v7 wait for the showing trigger;
reader speech is checked only after normal session shutdown flushes the log.
No production workaround or changed acceptance threshold was introduced for
these harness failures.

## Audit and restore

Run `python3 scripts/verify-file-input-announcements.py` from the repository root.
The seal records 549 Linux source files against immutable Git objects from the
preceding checkpoint plus two changed-file overlays. With that Git history
available, restore a new, nonexistent output directory with:

```sh
python3 evidence/development/file-input-announcements-20261017/tools/reconstruct.py --output /tmp/avelino-announcements-source
```

`--snapshot file-input-qt-v19` or `file-input-qt-v20` restores an earlier attempt.
The source-21 `run.py` records CMake commands and the read-only repository resource
mounts needed to build; it does not stand alone without those pinned resources.
The final installed-package hashes bind both reader sessions to the package
replay. Package binaries are retained by hash in this correction; the previous
checkpoint separately retains its own reconstructable installed package.

Native raster, direct sizing, type conformance, complete chooser presentation,
native input/callback timing and physical display/input/reader gates stay open.
