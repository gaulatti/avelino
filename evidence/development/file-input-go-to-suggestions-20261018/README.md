# Owned Go to Folder suggestion accessibility

This is a Linux development checkpoint. Strict Sabella parity remains pending:
75/80 desktop candidates, 0/80 accepted, with TV in the separate later phase.
Desktop reference `fe8a1d462fbd793d883fb92086a16aa2947e32c9`, expected captures,
tolerances, masks and exceptions remain unchanged.

The owned suggestion list exposes the existing model's single selected proposal
through Qt's accessible selection interface. Assistive selection and native
arrows use that same model, leaving raw input and keyboard focus in the editor.
Headings cannot be selected; unsupported multi-selection and deselection do not
invent new chooser policy. Explicit selection notifications cross Qt 6.8.3's
AT-SPI adaptor, whose generic state-change path ignores the selected bit. Clearing
the list reports its empty selection followed by the actual focused editor.

Final source64 preserves 571 exact core files. Eight focused Qt targets pass,
including DPR 1 and 2 regressions for selection queries/events, closed updates,
clearing focus and closing/deleting the owner during selection notification.
Source62's failed teardown is retained: a base list destructor emitted a callback
after the derived class had gone. Source63 disconnects it before base destruction;
source64 also reports editor focus after an empty list. Both passing source
attempts and the source63 provisional package are recorded separately.

Final reader13/14 are actual X11/software and dark scaled Wayland/OpenGL probes.
Both pass 21 phases. Measured arrow windows contain selected-state changes and
parent selection events. Exact log byte windows contain actual Orca destination
output and speech-dispatcher commands before Return for native arrows and AT-SPI
Selection.selectChild. Query results match the selected proposal while the editor
keeps keyboard focus and unchanged raw input. Direct text replacement/insertion/
deletion, native undo/redo, Unicode, navigation, cancellation and owner delivery
through the main Open button also pass.

Reader11/12 failures remain unchanged. Both timed out waiting for destination
speech; Wayland's complete log contains the speech after the failure snapshot's
last byte. Final probes flush Orca's original debug file after actual speech and
backend diagnostic messages. This changes log visibility, not speech generation
or reader policy. The ten-second observation limit is unchanged; final probes ran
sequentially without task compiler load. The raw logs retain accessibility
warnings, object-identity errors and timing information. Native hierarchy and
reader comparison remain open. Speech-dispatcher uses null audio output; command
receipts do not establish speech-engine audio or physical listening acceptance.

The fresh source64 installed consumer passes eight offscreen contexts and eight
virtual display profiles with project sources absent at runtime. All 256 prior
closed PNGs and complete raw closed/sizing metadata remain byte-identical. A
separate replay uses only the reconstructed runtime, without library or consumer
project sources, and reproduces the 32 closed PNGs and raw metadata exactly.

Native hierarchy, object identity, sizing/raster/artwork, timing and reader
comparison, complete chooser behavior, physical display/input/listening and
independent-machine acceptance remain pending. This capsule does not close any
parity inventory status or approve an exception.

`source-specs.json`, `runtime-spec.json` and `records-spec.json` preserve exact
bytes/modes using bounded checksum-addressed gzip chunks. `files.json` seals all
members. Source62/63 can be selected explicitly; default source is 64. Raw command
scripts with original host paths are provenance records, not portable entrypoints.
The reconstruction tool needs no sibling or build tree:

```sh
python3 evidence/development/file-input-go-to-suggestions-20261018/tools/reconstruct.py /tmp/avelino-go-to-suggestions --records
```

The portable run mounts only reconstructed `runtime` into the checksum-identified
Qt 6.8.3 toolchain image. Its exact command, terminal receipt and unedited output
are retained in `portable/`. This is a same-machine replay, not an independent
machine result.
