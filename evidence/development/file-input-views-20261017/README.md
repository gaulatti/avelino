# Owned FileInput List and Icons development checkpoint

This Linux development record remains in progress and accepts no mirror parity.
The pinned desktop reference is unchanged. Desktop coverage remains 75/80
candidates and 0/80 accepted entries; FileInput remains pending. No baselines,
pixels, reference pins, tolerances or exceptions were changed.

The owned view menu switches between Columns, inline hierarchical List and
root-only Icons. URL identities preserve visible selection across sorting and
refresh. Collapse and view changes prune hidden children. Disclosure persists
through history and reopening; reopening clears selections/history. Selecting a
noneligible folder and pressing Open navigates without sending an owner result.
Name, Size and Kind sorting are implemented. Date Added is explicitly unavailable:
its cells show `--`, and its header is disabled. It does not use a fabricated date.

## Scoped checks

Six focused Qt targets pass for frozen source 45: item lifetime, filesystem,
browser and owned UI, including DPR-2 lifetime/UI variants. The UI regression
checks accessible menu activation and checked state, nested-menu Escape, sorting,
List/TableCell headers and level metadata, cell geometry, virtual-cell invalidation,
keyboard routes, callbacks and owner deletion. The full 47-target suite was not
rerun for this change.

The independent consumer was freshly built from source 36. Its 137 consumer
files are byte-identical to source 45, and its checksummed ELF is reused with the
final source-45 installed package. All eight source-free contexts pass, each with
20 owner/input traces, 42 PNGs, 38 pointer events and 38 key events. All 256 closed
PNGs and complete closed/sizing metadata are byte-identical to the earlier
checkpoint. This preserves the existing native mismatches: 0/256 exact pixel
pairs, 232/256 complete frame matches and 256/256 contract states.

All eight virtual X11/nested-Wayland profiles pass across software/OpenGL llvmpipe,
standard light/DPR-1 and scaled dark/text-1.5/DPR-2 settings. Hardware acceleration,
physical display/input and native raster acceptance remain pending.

Readers 9 and 10 use the source-45 installed catalog without project sources,
Orca 46.1 and Speech Dispatcher/espeak-ng with ALSA null output. Each passes 17
phases covering selection, disclosure, sort preservation, Icons pruning and
folder navigation, history, keyboard child acceptance, owner results, reopening,
errors, nested creation and cancellation. AT-SPI exposes four List columns,
TableCell/header relationships, levels, expand/collapse and selection. Orca logs
read after session exit contain file/error output and backend speaking commands;
the former missing-table-ancestor and incorrect file-disclosure speech are absent.
The final assistive multiselection calls Selection.selectChild.

Failed attempts remain visible. Sources 30/31 fail compilation, 32/33 expose empty
menu geometry, and later attempts expose missing actions/checked state, disclosure
JavaScript errors, focusability and incomplete table metadata. Source 42 fails
compilation; 43/44 pass Qt checks but reader attempts 5/6 expose missing header
relationships. Source 45 searches Repeater headers in the visual tree and tests
all four relationships. Reader attempts 7/8 fail the mixed XTest Control plus
AT-SPI Press route. That route remains unresolved; the final Selection API check
does not establish its equivalence. Earlier successful package exit codes do not
erase their retained JavaScript errors. Engine waveform/audio, physical listening,
native reader/hierarchy and timing comparison remain pending.

## Restoration

Sixteen snapshots (30 through 45), each containing 557 Linux source files, are
reconstructable from Git base `6008f0c3fd14e25194b989c0c3cd0242eeeb6624` and
checksummed changed blobs. The complete 143-file install and independent consumer
ELF are retained in gzip chunks expanding to at most 16 MiB. File modes and hashes
are checked during restoration. Mutable compiler caches and duplicate install
prefixes are excluded.

```sh
python3 evidence/development/file-input-views-20261017/tools/reconstruct.py \
  --output /tmp/avelino-views-replay --source --package
python3 scripts/verify-file-input-views-linux.py
```

The portable proof restores all 557 sources and 144 package files to a fresh
directory, then runs one context with only the installed package mounted. It
passes 20 traces and reproduces 32 unchanged closed images and full metadata.
The image's empty `/work` directory is allowed; library/consumer sources are absent.

Sidebar, location menu, search, preview, grouping and remaining sort modes are
missing. Native metadata formatting, Date Added, column resizing, artwork and
thumbnails, general cross-directory callback order, full hierarchy/input/type/
sizing/raster/timing, readers, physical hardware and independent-machine acceptance
remain open. These records support implementation work without closing those gates.
