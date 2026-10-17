# Owned FileInput navigation and New Folder checkpoint

FileInput remains pending; desktop candidate coverage stays 75/80 and accepted
desktop parity stays 0/80. This checkpoint adds owned Back/Forward location
history, nested New Folder input/creation, and modal accessibility to `164be2415`.
Pinned references, expected images, tolerances and exceptions are unchanged.

## Behavior and source observations

Source 29 is the final frozen Linux source. History preserves column locations
and navigation branches, re-enumerates directories and clears file selections
on Back/Forward. A fresh Shift range begins at the first listing row in the
observed alphabetic fixture. These behaviors follow the native history-selection
probe in `evidence/reference-investigations/file-input-controls-20261017`.
Navigating after Back replaces the forward branch. Reopening retains the last
folder and starts fresh history. Navigation marks do not become owner results.

New Folder suggests an available `untitled folder` name and disables Create for
empty, duplicate or invalid names. Explicit Create/Return creates the requested
directory atomically and navigates inside without delivering an owner result.
Escape/Cancel close only the nested prompt. A changed or vanished parent prevents
creation. Spaces and Unicode are preserved; actual filesystem name/case rules
apply. Control+Shift+N adapts the observed native Command+Shift+N shortcut.
Complete native filename, filesystem, history and input equivalence is pending.

The dialog subclass supplies modal accessibility omitted by Qt 6.8.3's Quick
item. It follows the existing scoped private-Qt accessibility pattern, asserts
that exact version and matches only its own popup item. Both dialogs expose a
name, Dialog role and modal state without redundant inner dialog roles. Native
hierarchy and reader equivalence are pending.

## Final verification

Six focused Qt targets pass: two lifetime targets, filesystem and columns, and
actual-input UI targets at DPR 1 and 2. They cover selection clearing, a fresh
Shift range, navigation marks, duplicate/invalid names, spaces/Unicode, changed
or vanished parents, actual buttons/shortcuts, nested Escape, focus restoration,
accessible Create, owner removal, and directory-filter Return. The complete
47-target Qt suite was not rerun locally for this final source.

Package v5 freshly builds an independent consumer against the source-28 installed
package without library sources or Avelino C++ headers. Its 137 consumer files
are byte-identical to final source 29. Package v6 uses the final source-29 install
and that verified consumer ELF; the binding and binary hash are explicit.
Eight source-free offscreen theme/text-scale/DPR contexts pass with 12 input/owner
traces, 21 pointer events, 32 key events and 38 PNGs each. All 256 declared closed
PNGs and complete closed/sizing metadata match the previous checkpoint exactly.
Popup fixture paths differ and are retained without normalization. The prior
native comparison still has 0/256 exact-pixel matches, 232/256 complete frames
and 256/256 matching contract states; it is not accepted raster parity.

Display v4 passes all eight X11/nested-Wayland × software/OpenGL × standard/scaled
profiles using the final package. OpenGL is llvmpipe on Linux arm64. Full-output
captures, scene captures, logs and renderer observations are retained separately.
These virtual sessions do not establish physical or independent-machine gates.

Readers v8 and v9 use the final installed catalog in X11/software/light/text-1/
DPR-1 and nested Wayland/OpenGL/dark/text-1.5/DPR-2. Both pass 12 phases: modal
input, duplicate/empty validation, nested Escape, creation, history selection
clearing/navigation marks, error recovery, cancellation and Space reopening.
Each records two assertive announcement events. Orca 46.1 logs confirm output
and backend speech requests for New Folder, the default name and both errors.
Speech Dispatcher uses espeak-ng with ALSA null output. Its level-3 dictionary
errors are not utterance proof. Engine audio, physical listening, native reader
comparison and timing acceptance remain pending.

The additional focus waits after the initial 0.35-second observation are about
0.06/0.09 seconds on X11 and 0.63/0.62 seconds on Wayland. Raw protocol logs retain
the asynchronous focus return. No production timing workaround or acceptance
tolerance is added. Qt stale-accessible/key-filter warnings remain in raw logs.

## Attempts and replay

Frozen sources 22–29 are reconstructable from base Git objects and deduplicated
Linux blobs. Source 22 records an unsupported test helper; 23 exposes shortcut/
focus problems; 24/25 verify the initial controls; 26 adds modal accessibility.
Native selection observations corrected history in 27; 28 adds directory-filter
Return coverage; reader 6 caught a missing navigation mark, fixed and regression
tested in 29. Failed/superseded package, display and reader attempts are retained.
Mutable build caches and duplicate source/install trees are excluded.

The complete installed prefix and consumer ELF are archived as checksummed gzip
chunks, each expanding to at most 16 MiB. Restoration verifies 552 Linux source
files and 143 runtime files, including file modes. The restored package runs with
neither project source mounted and repeats 12 interactions in one light/text-1/
DPR-1 context with 32 identical closed PNGs and unchanged metadata. This replay
does not claim eight independently restored runtime contexts.

```sh
python3 scripts/verify-file-input-navigation.py
python3 evidence/development/file-input-navigation-20261017/tools/reconstruct.py --output /tmp/avelino-navigation-replay --source --package
```

Use `--package` alone without Git history. Source restoration requires base Git
commit `164be2415d6e40ad4a3010e57efa8ee0e67da218`; `--snapshot file-input-qt-v22`
through `file-input-qt-v29` selects a frozen source. Image IDs and runtime commands
are recorded. Sidebar, views, location menu, search, selection preview, group/sort,
native sizing/type/input/raster/accessibility, physical and independent-machine
acceptance remain pending.
