# MediaLibrary teardown regression

Deleting an attached `MediaLibraryBase` can emit `windowChanged` from
`QQuickItem` teardown after the derived destructor has run. The surviving typed
connection then reaches an object whose derived state has ended. The fix
disconnects self and owned-caller observers before clearing that state.

The minimal repro creates a window, attaches the library, and deletes it. It
never creates FileInput. The unchanged source at
`a46a8dca78f6d630b7be1352757e3d0fe01c44c9` aborts with Qt's incorrect-object-type
assertion (process 133). The isolated fixed library is rebuilt from that revision
plus only the three frozen overlay files; its repro exits 0. Its focused QML
suite passes 16 checks at each of DPR 1 and 2, including attached destruction
with live tiles and removal from a tile's own action. The complete component
suite also passes at both display scales; raw Qt output is retained.

A second replay builds both baseline and fixed variants in separate fresh
source trees, using only Git history and the frozen overlay. It reproduces exit
133 versus exit 0 without FileInput in either source tree. `portable-replay/`
retains the complete commands, raw logs and source-file manifests.

`baseline/` and `fixed/` retain raw logs, commands, exit codes and source hashes.
The original baseline binary came from the FileInput development producer;
`baseline/inputs.json` binds the unchanged MediaLibrary source and that binary.
The fixed build contains no FileInput implementation. Original command paths
identify the historical runs, rather than portable replay paths.

Run `python3 replay.py --output /absolute/new/directory` from this directory to
build both variants afresh in the recorded Qt 6.8.3 toolchain. The script obtains
the baseline from local Git history and uses the frozen overlay; no sibling
checkout is used. The Docker context is explicitly `colima-avelino-verify`.

This is Linux lifetime evidence. Visual parity, physical display, reader and
other strict mirror gates remain pending; expected captures are unchanged.
