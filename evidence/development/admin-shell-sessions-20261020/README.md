# Installed AdminShell display sessions

All eight installed-package display configurations completed: X11 and nested
Wayland, software and OpenGL, standard and scaled. Each report checks 80 native
layout profiles, 160 owner-history states and 168 divider boundaries. The scaled
configuration uses DPR 2, text scale 1.5 and dark appearance; standard uses DPR 1,
text scale 1 and light appearance.

The consumer was rebuilt after the readiness repair. The independent consumer
build tree was configured in the earlier compiled/package phase; this checkpoint
reuses that tree and the unchanged installed core library. The build receipts,
source-file hashes and executed binary/library hashes are retained. Project
sources and the product build were absent from the runtime mount.

The canonical display-session script is retained at the recorded Git revision.
Only its fixture loop was filtered to AdminShell. Its protocol, renderer,
scaling, pointer parking and screenshot validation remain unchanged. All 656
original PNG paths map to exact content-addressed bytes in `images.json`: 640 body
captures, eight window captures and eight full Xvfb compositor captures.

Xvfb, nested Weston and Mesa llvmpipe are virtual/software evidence. Input is
synthetic Qt input. Qt accessibility interface checks do not establish reader
equivalence. Fixture colours diagnose geometry; native colour compositing,
symbols, toolbar timing, complete caller behavior, native raster, physical input,
hardware acceleration and screen-reader acceptance remain pending.

The earlier readiness failure remains in the sibling
`admin-shell-sessions-failure-20261020` capsule. No expected image, source pin,
tolerance, mask or exception was changed.

```sh
python3 scripts/verify-admin-shell-sessions.py
```
