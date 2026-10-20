# Ordinary AdminShell fixture source-colour integration

The consumer and catalog now use the recorded native root, sidebar, header and
content inputs for light/dark appearances. The generated JavaScript preserves
their original linear-sRGB Float32 values and bit patterns, alongside the standard
sRGB-encoded values passed to Qt.rgba. Values come from the immutable native input
record, without fitting screenshot colours. The new resource is registered in
both consumer and catalog QML modules. Capture ICC conversion is unchanged.

Both scales pass 265 source-interpreted component cases. The native profiles
check colour delivery to fixed, flexible, empty and zero-sized callers. An
additional case changes appearance while retaining the caller objects and their
geometry. Each scale also captures all 80 native layouts, with 82 capture tests.
All 160 raw PNGs are retained; 158 visible caller pixels per scale exactly match
the encoded Qt input bytes. These are input/render checks, not native equivalence.

The first render inspection failed because its filename shadowed Python's
standard inspect module. Its source, failure and untrusted output remain recorded.
The renamed controller subsequently passes; only that second result is used.
Earlier receipts remain bound to their original producers for the evolved files.

The compiled base module is reused. A fresh consumer/catalog build, complete
display matrix, native glass and other materials, reviewed capture-profile
conversion, screen readers and physical acceptance remain pending. Expected
images, reference pins, comparator bytes and visual policy are unchanged.

The input transfer follows the [standard sRGB conversion](https://www.w3.org/TR/css-color-4/#color-conversion-code)
and the fixture uses [Qt 6.8 Qt.rgba](https://doc.qt.io/qt-6.8/qml-qtqml-qt.html#rgba-method).

```sh
python3 scripts/generate-admin-shell-colours.py --check
python3 scripts/verify-admin-source-colour-fixture.py
```
