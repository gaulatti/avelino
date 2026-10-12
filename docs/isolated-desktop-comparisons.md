# Isolated desktop comparisons

Status: diagnostic comparisons against **proposed** reference images. No source
baseline, expected image, visual tolerance or exception approval changes here.
Desktop and television acceptance remain independent and pending.

`AvelinoCatalog --fixture reference-case` consumes the neutral case definitions in
[the desktop proposal](../evidence/reference-proposals/desktop-20261012/fixtures.json).
It instantiates the public Avelino component for all 25 started desktop APIs,
including every proposed card/padding, progress, avatar, status, control-size and
toggle variant. The five source monospace probes have no implemented/distributable
Linux font counterpart and are explicitly excluded, rather than replaced silently.

Each component is centered in the same fixed logical frame and palette background
as its source fixture, with the requested appearance and text scale. Centering
does not force an integer logical position. The fixture retains intrinsic sizing
unless its source definition has an explicit constraint. Card/panel/attention
content slots, header slots, button-group labels, list rows, timeline content and
the original avatar test image match their source compositions. The wrapper sets
no global font or foreground override. The inherited-toggle case deliberately
exposes Avelino's unfinished font difference.

The capture records actual component dimensions and origin, visible label fonts,
baselines and geometry, alongside window dimensions, DPR, backend, compiler and
capture method. Label records describe Qt's selected face; glyph fallback and
accessibility still need separate verification. The capture driver records exact
source input and catalog-binary hashes, the reference proposal/definition hashes,
dependencies, QML import path, per-image/metadata checksums and runtime diagnostics.
Binding loops and JavaScript runtime errors fail capture verification.

Build the pinned Linux toolchain and catalog, then capture into a new directory:

```sh
docker build -f tools/Dockerfile -t avelino-toolchain:qt6.8.3 .
docker run --rm -v "$PWD:/work" avelino-toolchain:qt6.8.3 \
  bash -c 'cmake --preset linux && cmake --build --preset linux'
docker run --rm -e QML_IMPORT_PATH=/work/build/linux/qml -v "$PWD:/work" \
  avelino-toolchain:qt6.8.3 python3 scripts/capture-proposals.py \
  --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
  --reference evidence/reference-proposals/desktop-20261012 \
  --output artifacts/isolated-desktop
```

The default matrix has 724 captures across 99 fixture definitions: both appearances
and text scales 1/1.5; DPR 1/2 for ImageRenderer reference cases, measured DPR 2 for
native-control reference cases. Repeat `--api BleeckerCard` to select API families.
The driver captures in separate offscreen processes and runtime directories. Its
four-worker default changes throughput, not the selected render dimensions.

Use `scripts/compare-captures.py` with the proposal directory, Linux capture
directory and a separate report output. Repeat `--api` to select the same families
when comparing a subset. It compares case parameters, measured component geometry,
full RGB and alpha, without resizing or ignored regions. Geometry uses only a
`1e-6` logical-unit numerical precision allowance; pixel tolerance remains zero.
A geometry difference fails even when image pixels happen to match. Reports retain
the proposal's status and cannot approve a reference baseline.

The Qt 6.8 [Loader sizing contract](https://doc.qt.io/qt-6.8/qml-qtquick-loader.html#loader-sizing-behavior)
and [window capture API](https://doc.qt.io/qt-6.8/qquickwindow.html#grabWindow)
inform the fixture wrapper and capture mechanism. This is a single-window rendering
check. Actual Wayland/X11 sessions, open overlays/separate windows, input, focus,
accessibility, installed consumption and hardware checks remain separate. Qt reduced
motion is enabled; native spinner/skeleton animation phases are not matched, so
their snapshots cannot establish deterministic animation acceptance.

The first [preserved Linux candidate](../evidence/development/isolated-desktop/candidate.json)
captures all 724 cases without runtime warnings. Its [comparison report](../evidence/development/isolated-desktop/comparison/comparison.json)
has 40 exact pixel-and-geometry matches and 684 failures. These are diagnostic
results against an unapproved proposal, not 40 accepted components. The
[API summary](../evidence/development/isolated-desktop/comparison/api-summary.json)
separates geometry, pixels and missing/invalid metadata. The raw images, label
records and full pair/overlay/difference images are checksummed and preserved.

This matrix exposes a panel sizing defect hidden by the gallery's explicit width:
an unconstrained 180-pixel content slot produces a 48-pixel-wide panel rather than
228, collapsing its title into a vertical column. The timeline's non-final connector
also fills the source's available vertical allocation; the Linux fixture initially
uses only intrinsic height. These findings remain visible in this first candidate
while their repairs are captured separately.
