# Owned Go to Folder path editing

This is a Linux development checkpoint, not accepted Sabella parity. The desktop
reference remains `fe8a1d462fbd793d883fb92086a16aa2947e32c9`; no expected capture,
mask, tolerance, exception or reference pin is changed. Desktop candidate coverage
remains 75/80, with no accepted desktop entry. TV remains a separate later phase.

`FileChooserPathInput` adds the editable-text interface absent from Qt Quick
6.8.3's accessibility implementation. It sends replacement, insertion and deletion
through a Qt input-method commit. The GoTo model follows text changes. Native Qt
validation, length limits and undo machinery remain responsible for editing;
read-only and disabled fields reject changes. This does not change the owner
result boundary: choosing a proposal navigates or selects; the main Open action
submits the file.

Final source61 has 569 frozen core files. Its eight focused Qt targets include the
new editable-text regression at DPR 1 and 2, with the complete Qt output retained.
The fresh installed consumer runs without library or consumer sources in eight
contexts and eight virtual display profiles. All 256 previous closed PNGs and
complete raw closed/sizing metadata are byte-identical. The restored runtime is
also exercised separately, with only its runtime directory mounted.

The final X11/software and scaled dark Wayland/OpenGL probes each perform twenty
phases through actual AT-SPI and native XTest input. They cover assistive text
replacement, insertion, deletion, Unicode, a single replacement's native
undo/redo, a nonzero mixed edit's undo/redo roundtrip, navigation, missing input,
owner delivery through Open, cancellation and focus restoration. Raw Orca output,
Orca speech-dispatcher commands, server logs and process termination receipts are
retained. Null audio output is not physical listening or engine-audio acceptance.

Earlier attempts remain intact. Probe1 counted the same accessible dialog twice
because Qt exposes it through the owner and popup frame; its identity diagnostic
shows one object. Probe2 found the original missing EditableText interface.
Probes3/4 completed native keyboard flows while recording that limitation.
Probes5/6 assumed fine-grained undo units; the screenshot after Undo shows an empty
field. Probes7/8 then checked a net-zero insert/delete sequence as though undo had
to change its text. Corrected probes9/10 preserve Qt's undo grouping and test a
nonzero change. No library edit was made to accommodate those probe assumptions.
The separate Qt regression and final single-replacement probe verify a defined
replacement boundary as well.

Complete native hierarchy, suggestion-selection events and announcements, reader
comparison, native raster/artwork/sizing/timing, complete chooser behavior,
physical display/input/listening and an independent machine remain pending.

`source-specs.json`, `runtime-spec.json` and `records-spec.json` identify exact
bytes, modes and bounded gzip chunks. `files.json` seals every member. Raw receipt
files can be restored with `--records`; scripts ending in `-record.py` retain the
original host commands and paths. They are provenance records. The reconstruction
tool itself has no sibling or build-tree dependency:

```sh
python3 evidence/development/file-input-go-to-editing-20261018/tools/reconstruct.py /tmp/avelino-go-to-editing --records
```

The recorded portable run mounts only the reconstructed `runtime` directory into
the checksum-identified Qt 6.8.3 toolchain image. Its exact command and terminal
result are in `portable/result.json`; captures are preserved beside that receipt.
