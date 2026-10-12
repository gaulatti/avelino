# Linux development

Qt is pinned to **6.8.3**; the version must match exactly. The checked-in Dockerfile
uses an immutable Ubuntu 24.04 base image and official Qt archives via aqt 3.3.0.
It supports separate ARM64 and x86_64 builds. ICU is included from Qt's archive,
since the prebuilt Qt binaries require its matching version.

```sh
docker build -t avelino-toolchain:qt6.8.3 -f tools/Dockerfile .
docker run --rm -v "$PWD:/work" avelino-toolchain:qt6.8.3 bash scripts/check-linux.sh
```

The check compiles the module and catalog, exercises Qt Quick pointer/keyboard
and editing tests, installs a package into a clean temporary prefix, builds and
runs a separately copied consumer, and saves light/dark PNGs with capture metadata.
The consumer verifies actions, disabled state, text selection/replacement, and
bundled font registration. It currently has no accepted overlay implementation.

These are implementation checks. The first Qt button, spinner, and text-field
presentations are **verification-pending**: the SwiftUI comparisons, shadow and
continuous-corner geometry, loading indicator, platform focus, selection treatment,
actual X11/Wayland sessions, accessibility, and scaling matrices are unfinished.
Do not interpret software-rendered PNGs as accepted mirror baselines.

The catalog is a native Qt application; this repository has no browser frontend
or application server. Application-backend Compose requirements do not apply.

Official framework references:
[Qt control customization](https://doc.qt.io/qt-6.8/qtquickcontrols-customize.html),
[QML modules](https://doc.qt.io/qt-6.8/qt-add-qml-module.html), and
[Qt Quick Test](https://doc.qt.io/qt-6.8/qtquicktest-index.html).
