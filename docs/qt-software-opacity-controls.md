# Qt software opacity and Canvas2D controls

The [retained SDK controls](../evidence/development/qt-software-opacity-controls-20261019/result.json)
reproduce alpha corruption in the pinned Qt 6.8.3 software renderer without
Avelino, native fixture inputs or interposition. The probe uses an opaque window
and moves plain and clipped rectangles through five fractional positions.

X11 DPR 1 and 2 each produced thirty opaque, stable frames. Wayland DPR 1
produced thirty frames, nine with nonopaque pixels. The script stopped on that
failure; Wayland DPR 2 remains unrun. A separate Canvas2D window passed all three
frames in each attempted profile. Its nine captures follow the opacity captures
and do not cover or alter their pixels.

Run `bash tools/check-qt-software-opacity.sh <fresh-output-directory>` in the
Linux Qt 6.8.3 verification environment. This regression currently fails against
the unmodified SDK. A complete passing matrix requires 120 opacity frames and
twelve additional Canvas2D frames across X11/Wayland and DPR 1/2.

The SDK's QML JIT header contains a conditional macOS ARM fallback. Its last
literal definition is inactive on Linux ARM64. The retained C++ preprocessor
output establishes the effective Linux setting as enabled; literal text matching
does not establish the configured feature value. This distinction matters when
rebuilding Qt Quick against the SDK's private QML-engine interface.

Run `python3 scripts/verify-qt-software-opacity-controls.py` to independently
decode the original PNGs, recompute opacity, fixture colors, bounds and stable
frames, and check hashes, dimensions and effective SDK features. These controls
validate a reproducer. They do not validate a source patch, change the supported
toolchain, or accept native raster, physical input, reader behavior or a Linux API.
