# Qt 6.8.3 software layer alpha probe

This isolated public-Qt-only program reproduces black holes around an opaque
island rendered through ShaderEffectSource. It imports no Avelino code and uses
no Qt private API. Expected background is #123456; the software layer paints the
empty interior black. Source remains red, then updates to blue.

Build with the pinned toolchain and run from this directory:

```
cmake -S . -B build -G Ninja
cmake --build build
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software build/probe "$PWD/main.qml" "$PWD/dpr1"
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software QT_SCALE_FACTOR=2 build/probe "$PWD/main.qml" "$PWD/dpr2"
```

The exit status is zero only when the pinned defect is reproduced. The JSON and
before/after images record measured colors, Qt, platform and DPR. The production
adapter's sparse-content tests independently verify preservation of background
and unchanged islands on both software and RHI paths.
