# Weston popup parent commit order

The tooltip crash in the prior checkpoint is now reproduced by a standalone
Wayland client with no Qt or Avelino. It creates a non-grabbing popup, commits
the already-mapped parent before the popup's first surface commit, then maps
the popup. Stock Weston 13.0.4 crashes on that parent commit. Its sanitizer
build reports the same null transform parent at libweston/desktop/surface.c:117
as the retained Qt tooltip failure. Both failed runs are preserved.

The checksummed local patch defers positioning a child view whose transform
parent has not yet been assigned. The child's normal first commit assigns its
parent and updates its position. The patched sanitizer build survives the same
request order and displays the complete 20 by 20 popup. The external 640 by 480
capture contains exactly 400 red popup pixels and 9600 blue parent pixels.
An earlier capture covered by startup fade remains excluded and preserved.

The repository toolchain installer applies that exact patch to the same pinned
13.0.4 archive. Every image build compiles and runs tools/weston-popup-order.c
through tools/check-weston-popup-parent.sh and checks those exact external
pixel counts. The normal release image passes too; installed logs, source,
image and result are included. The archive fetch timed out on the first image
attempt. The second supplies the saved archive through AVELINO_WESTON_ARCHIVE
and enforces the same upstream SHA-256. Neither archive nor expected appearance
is replaced. All four CJK font files and the checked Qt 6.8.3 shared libraries
are byte-identical between the base and patched images.

The 604 library/core inputs and 149 consumer inputs are unchanged from fede040.
Its compiled module and independent consumer are reused for the complete,
unchanged 304-record display gate. That process was live when this packet was
sealed; only its immutable startup inputs and driver are included here. This
checkpoint does not claim a complete display pass. The earlier 303/304 failure
remains failed. A single diagnostic replay of scaled Wayland/OpenGL FileInput
passes, but does not resolve the earlier capture failure. Its logging-only
consumer changes and results remain explicitly diagnostic.

Historical checkpoint verifiers now bind their producer Dockerfile, installer
and verifier to existing sealed copies whose SHA-256 values equal the original
bindings. Runtime driver hashes and every historical result remain unchanged;
this permits the current compositor dependency fix without rewriting captures.
The old typography/date integrity verifier passes and still reports its failed
display gate and strict date comparisons. Current Linux CI builds and exercises
the current toolchain independently.

Run python3 scripts/verify-weston-popup-checkpoint.py to audit this packet.
Desktop coverage stays 76/80 candidates, 0/80 accepted. The full runtime gate,
strict visual and native input/accessibility acceptance, remaining desktop APIs,
and the separate later TV/playback phase remain open. Pins, masks, resizing,
comparison tolerances and approved exceptions are unchanged.
