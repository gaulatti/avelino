# Owned Linux Go to Folder checkpoint

The source60 candidate replaces the inline directory field with a separate owned
Qt popup. Ctrl+Shift+G and Ctrl+L open it. Raw input, selected suggestion, recent
target history and the main chooser selection remain separate. Return or a
double-click navigates to the selected target without an owner callback; Escape
keeps the underlying selection. Close clears a nonempty input and dismisses an
empty one. The successful raw input can be empty. Where's ten accepted-folder
history remains independent of the observed five GoTo targets.

A path-selected file retains a separate selection identity while ordinary MIME
eligibility stays unchanged. The plain-text PNG route is exercised through Open,
including view transfers, Select All, invalid-target preservation and a deleted
file at acceptance. Removing the owner removes the nested window. Directory-only
consumers cannot receive a file through this route. General native type-array
conformance remains pending.

Six frozen attempts and all raw logs are retained. Source55 exposes the stale
outside-click test target and missing parent-window focus restoration. Source56
isolates the focus failure. Source57 passes the initial eight targets. Source58
adds a stronger accessible-tree assertion and proves the nested window is
unreachable. Source59 links the owned modal into its parent dialog's accessible
children and parent/focus/hit-test relationships, then passes the same assertion.
Source60 fixes a visual defect found after those checks: scrollbar thumbs
were shown even when content fit. All owned chooser scrollbars now honor their
AsNeeded policy, and the three-suggestion view is checked without a scrollbar.
The source59 UI images retain that earlier defect. Its provisional consumer and
display runs remain unchanged in task artifacts. Qt's popup input and editing machinery is retained. The parent explicitly requests
activation and restores its file-list focus after the nested window closes.

The final 567-file snapshot passes eight focused Qt targets: lifetime at DPR 1/2,
filesystem, browser, places, path proposals, and owned UI at DPR 1/2. The complete
repository Qt suite was not rerun locally. A fresh independent consumer builds
against only the installed package. Runtime receives only its ELF and the
installed prefix. Eight light/dark, text-scale 1/1.5 and DPR 1/2 contexts each
produce 30 action traces, 49 PNGs, 62 synthetic pointer events and 164 key events.

Eight separate virtual display profiles cover X11/Wayland, software/OpenGL and
standard/scaled configurations. OpenGL uses software Mesa rendering. Original
Qt popup images and external window/session captures are preserved. All 256
closed PNGs and complete closed/sizing metadata match the prior location
checkpoint exactly. The underlying strict native raster mismatches remain open.
No expected image, mask, resize, tolerance, exception or reference pin changes.

`source-specs.json` and `runtime-spec.json` describe exact bytes and modes. The
content-addressed gzip store deduplicates raw files and splits large files into
chunks expanding to at most 8 MiB. Use a new reconstruction destination:

```sh
python3 evidence/development/file-input-go-to-20261018/tools/reconstruct.py /tmp/avelino-go-to-review --source 60
```

This restores 567 core source files and 147 runtime files including the recorded
environment. Producer commands bind the repository's supporting scripts,
references, evidence, tokens and docs read-only; those support directories remain
in this repository. Apple source/tooling and sibling checkouts are not required
for the restored runtime. The recorded immutable toolchain image provides Qt
6.8.3 and Weston 13.0.4. A restored runtime replay with project/build sources
absent passes all 30 actions and reproduces its 32 closed PNGs and metadata.

Run `python3 scripts/verify-file-input-go-to-linux.py` for the recorded-output,
source/runtime chunk and raw metadata audit. The verifier does not rerun the Qt
or display commands. Their actual arguments, terminal results and outputs are
preserved here.

The new GoTo flow has not yet been exercised with AT-SPI/Orca. Earlier source54
reader evidence does not prove this flow. Full native hierarchy/reader, physical
input/display/listening, independent-machine behavior, source timing, general
suggestion ranking, history capacity, relative components, all type arrays,
sheet geometry/artwork and the complete chooser remain pending. The candidate's
name-matching/ranking rule is documented in `docs/file-input-linux.md`; it is not
accepted as AppKit's complete algorithm. Desktop coverage remains 75/80 candidates
and 0/80 accepted. TV remains a separate later phase.
