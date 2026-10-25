# Linux desktop SDK preview

This preview contains the Avelino QML/CMake SDK, desktop catalog and independent
smoke-test executable. It is for **Ubuntu 24.04 arm64** and requires an existing
**Qt 6.8.3 SDK**. Qt is not bundled. It is not a macOS application or an x86 build.

Download `avelino-0.1.0-preview.1-linux-arm64.tar.gz` and `SHA256SUMS` from the
[preview release](https://github.com/gaulatti/avelino/releases/tag/v0.1.0-preview.1).

```sh
sha256sum -c SHA256SUMS
tar -xzf avelino-0.1.0-preview.1-linux-arm64.tar.gz
cd avelino-0.1.0-preview.1-linux-arm64
export AVELINO_QT_PREFIX=/path/to/qt-6.8.3
QT_QUICK_BACKEND=software ./catalog --fixture foundations
```

Other catalog views include `controls`, `file-input`, `date-range`, `admin-shell`
and `charts`; select one with `--fixture`. Use `--dark` for the dark appearance.
On a machine without a display, capture a view with:

```sh
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software \
  ./catalog --fixture file-input --capture "$PWD/file-input.png"
```

The validated Qt runtime includes this repository's Qt 6.8.3 software-rendering
patches. See [the toolchain recipe](https://github.com/gaulatti/avelino/blob/e1fb61cd38b436b5c4e01446a67d9cbbb333e404/tools/Dockerfile)
and [build instructions](https://github.com/gaulatti/avelino/blob/e1fb61cd38b436b5c4e01446a67d9cbbb333e404/docs/development.md)
for that configuration. Other Qt builds and physical GPU drivers are not verified
by this preview. Ubuntu runtime dependencies include ICU 74, Tracker SPARQL 3,
Fontconfig, the XCB/Wayland client libraries and OpenGL/EGL. The existing toolchain
recipe lists their exact Ubuntu packages. Indexed search also needs a supported
running Tracker indexer; it reports unavailable service rather than changing
your index settings.

For a CMake consumer, add both `install/` from this archive and your Qt SDK to
`CMAKE_PREFIX_PATH`, then use `find_package(Avelino 0.1 REQUIRED)` and link
`Avelino::Avelino`. `Avelino_QML_IMPORT_PATH` identifies the installed QML module.
The included `smoke` launcher can exercise the installed controls:

```sh
xvfb-run -a env QT_QPA_PLATFORM=xcb QT_QUICK_BACKEND=software ./smoke --date-range --date-range-observe
xvfb-run -a env QT_QPA_PLATFORM=xcb QT_QUICK_BACKEND=software ./smoke --file-input --file-input-observe
```

Observation mode keeps functional failures fatal and reports native parity
differences separately. It does not accept those differences.
The headless smoke commands require Ubuntu's `xvfb` and `xauth` packages.

No system-wide installation is required. Extract a newer preview into a separate
directory to upgrade; remove the extracted directory to uninstall. Your application
can instead use the `install/` directory as its CMake/QML prefix. `BUILD-INFO.json`
records the release and source commit; `FILES-SHA256.json` records payload hashes.

Known gaps are tracked in [DateRangePicker](https://github.com/gaulatti/avelino/issues/3),
[FileInput Unicode/RTL](https://github.com/gaulatti/avelino/issues/4),
[desktop search](https://github.com/gaulatti/avelino/issues/5),
[button compositing](https://github.com/gaulatti/avelino/issues/6),
[fonts/symbols/visual parity](https://github.com/gaulatti/avelino/issues/7) and
[physical desktop/reader acceptance](https://github.com/gaulatti/avelino/issues/8).
[TV/playback](https://github.com/gaulatti/avelino/issues/9) is a separate pending
phase. This is a usable development preview, not a claim of complete native parity.
