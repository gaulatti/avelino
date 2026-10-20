# Derived-item teardown correction

The package replay reached MediaLibrary and aborted in InheritedControl. A
standalone disabled-parent repro and a QML removal regression reproduce the
same failure without creating FileInput or MediaLibrary. The unchanged shared
classes are bound to the recorded v13 producer and Git revision a411c51b5.

The baseline matrix has 40 processes: 16 incorrect-type assertions across five
classes and 24 successful cases. A separate fresh build from a411c51b5 plus only
the lifetime correction contains no FileInput implementation. Its matrix and
QML regression pass at DPR 1 and 2. The current test adds explicit checks for
late style notifications; that supplement passes 42 Qt checks per scale against
the same unchanged library. Both test-source versions are retained.

The independent package mounts only its installed prefix and consumer project.
All 37 original modes and 151 catalog captures complete. All 151 PNG and complete
metadata pairs are byte-identical to the previous dropdown checkpoint. No
expected images, masks, tolerances or exceptions change.

Raw logs, commands, source hashes, initial probe configuration failures and
corrected attempts are retained. Original command paths document historical
runs; they are not portable paths. Run `python3 replay.py --output
/absolute/new/directory` to rebuild the frozen corrected source and matrix from
Git history with no build cache. The toolchain image and context are pinned.
The completed portable replay and its source-file hashes are retained under
`portable-replay/`.

The separate combined FileInput run has broader regression targets. This record
does not claim its result, physical input/display, hardware acceleration, readers
or strict native mirror acceptance.
