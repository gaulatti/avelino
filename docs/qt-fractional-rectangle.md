# Fractional rectangle experiment

The isolated Qt 6.8.3 software-renderer candidate improves the shell's native
body comparison from 76 to 80 exact images out of 144. Eight captures have fewer
mismatched pixels, none have more, and 136 remain byte-identical. All 144 body
layouts and eight virtual display contexts pass. This checkpoint does not update
the canonical toolchain: `tools/Dockerfile` still installs the earlier opacity
patch. No mirror API is accepted.

## Cause and candidate

Qt's software rectangle node converts its local `QRectF` to an aligned integer
rectangle before painting. A fractional size can therefore gain a painted row or
column before device scaling. A size change within the same aligned rectangle
also leaves that node's material unmarked.

The [candidate patch](../tools/qt-software-rectangle.patch) retains exact bounds
for plain rectangles and marks changes to those exact bounds. It keeps the
existing paths for borders, rounded corners and gradients. The existing opacity
patch remains applied. This is a Qt source change; the application supplies no
fixture-specific paint offsets or colour substitutions.

The published patch uses zero-context unified format and applies with GNU
`patch --fuzz=0 -p1` to the verified source files. The verifier applies both this
form and the retained build patch and requires identical resulting C++ bytes.

The experiment uses the pinned Qt source archive with SHA-256
`1f03a2b8f5588b4face7da87926e9b2c1372b3a32157c52df07a75067a9db1af`.
The source snapshots retain Qt's copyright and licensing; LGPL 3 and GPL 3 licence
texts accompany them in the evidence capsule.

## Measured runtime

The [retained evidence](../evidence/development/qt-fractional-rectangle-20261019/result.json)
binds the source patch, compilation, SDK audit, package identity, raw native body
comparisons and virtual sessions. The actual immutable runtime image is
`sha256:478a1669218e3d2a3dc302a4929a8ebd7fe2d21b21b140eba5d15bd3a24296e3`.
Its Qt Quick library and matching private rectangle header are the only two
changed entries among 9,236 SDK entries. The other 9,234 entries, including the
original QML and GUI libraries, are unchanged. All 49 effective feature settings
match; QML JIT remains enabled. This local image is an experimental artifact, not
an independently published or accepted toolchain.

The installed application package and consumer ELF have the same bytes as the
prior shell runtime. Both library and consumer project sources are absent during
execution. Eight offscreen contexts retain 144 body images, their raw parent
captures and all source layout witnesses. Eight X11/Wayland contexts cover
software/OpenGL and standard/scaled sessions, using synthetic Qt input. These
checks establish neither a physical display nor hardware acceleration or reader
acceptance.

The fractional light body now matches at DPR 1 and 2. The dark body loses its
extra edge differences, but its separator still differs by one blue-channel
level. There are 64 remaining failed body-image comparisons. The full window
chrome, symbols, physical input, general caller composition and accessibility
acceptance remain separate from these body fixtures.

The unchanged opacity regression passes 120 opaque, stable frames and 12 Canvas
frames across X11/Wayland and DPR 1/2. The first SDK-staging attempt failed before
replacement because its standalone preprocessor command omitted `qglobal.h`;
that attempt is preserved alongside the corrected attempt.

## Verification and next gates

```sh
python3 scripts/verify-qt-software-rectangle-candidate.py
```

The verifier applies the patch to the original rectangle files, audits the actual
image's recorded SDK inventory, decodes every native before/after image and raw
parent capture, checks the virtual-session reports, and independently decodes the
opacity/Canvas controls. Comparison tolerance remains zero. Existing native
images, pins, masks and exceptions are unchanged.

At this checkpoint, the fresh full component suite was still running and direct
rectangle controls were prepared separately; this capsule claims neither result.
Canonical installer and
Docker wiring, a complete driver run with accurate chained SDK provenance,
independent-machine replay, physical-device checks and reader acceptance remain
pending. Desktop candidate coverage stays 77/80, with zero accepted entries.
