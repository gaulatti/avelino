# Native AdminShell caller colour inputs

The four standard source controls retain their original pixels, geometry and
callbacks while the observation hook records the actual SwiftUI environment and
resolved sidebar/header/content/root colours. Light/dark and both initial
visibility values produce 12 byte-identical before/after/chrome controls against
the pinned matrix. Existing captures and reference pins remain unchanged.

The hook uses the public `Color.resolve(in:)` API inside the measured view. Its
[resolved components use extended linear sRGB](https://developer.apple.com/documentation/swiftui/color/resolved).
Both numeric Float32 values and their exact bit patterns are retained. These are
resolved source inputs, not colours fitted to screenshot pixels. The observed
environment has standard contrast, inactive controls and display scale 2. The
owned AppKit windows remain Aqua with the previously pinned ICC profile, while
the SwiftUI environment sets the requested light/dark scheme.

The input colours differ from the Linux fixture's pure diagnostic RGB and vary
with appearance. The projection is not yet integrated into the Linux fixtures.
A fair input bridge and exact compositor/raster comparison remain required.

The 53-file pinned library object is reused. This is a focused observation of
four existing controls, not an independent library rebuild or a new broad
matrix. The Apple helper and resource bundle remain outside the Linux repository;
command receipts and source/object hashes identify them. Physical input, readers,
independent-machine replay and mirror acceptance remain pending.

```sh
python3 scripts/verify-admin-shell-colour-inputs.py
```
