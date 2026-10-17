# Charts

The five desktop chart families share the pinned `Charts.swift` implementation:
`BleeckerLineChart`, `BleeckerBarChart`, `BleeckerPieChart`,
`BleeckerScatterChart`, and `BleeckerSparkline`. The line chart's `area` option is
part of that surface. The Linux candidate uses an owned Qt Quick painted renderer
without a chart-library dependency. Strict mirror acceptance remains pending.

The [source record](../evidence/reference-investigations/charts-20261017/investigation.json)
contains 120 closed fixtures in eight light/dark, custom-text-scale and bitmap-DPR
contexts. Each has the unmodified public chart, a transparent plot-proxy probe,
the literal pinned chart body, and a separate style-color lookup diagnostic.
The public/probed/literal PNGs are byte-identical. Plot frames, continuous and
categorical domains, point positions, category ranges and series ordering remain
in the observations, including fractional layout sizes and rounded plot frames.

Cases include empty, singular, zero, signed, fractional and large data; multiple
series; repeated and unsorted coordinates; stacked bars; long and Unicode
categories; pie radii; RTL, caller font/color, disabled state and constrained
frames. Six retained fixtures have eight data/size/theme/scale/direction/disabled/
restore steps in all eight contexts. Every public/probed/literal branch restores
its initial pixels and measurements with one retained wrapper. This observes the
wrapper, not native mark identity or animation timing.

Separate layout queries exercise 13 unspecified, zero, finite, mixed and infinite
proposals for all 120 fixtures and eight contexts. The direct public chart has a
100-by-100 ideal size and a 1-by-1 response to a zero proposal. These queries omit
the caller's fixed frame and disabled modifier; those modifiers are covered by
the closed captures. A fixed zero caller frame and a zero layout proposal are
different operations.

Fifty additional cases include 45 non-finite inputs and five finite controls.
They pass actual NaN and positive/negative infinity values into chart coordinates,
sparkline values or pie radii. Every process
completes, and its pixels remain separate from the empty-data cases. Finite
controls match their corresponding closed fixtures exactly. A Linux adapter must
preserve the observed outcome before deciding how to handle invalid numbers.

Source details that affect the implementation include the sparkline's retained
`Value` legend, signed pie values, clamped tested inner-radius endpoints, cyclic
series palettes and the independent contribution of axes and legends to layout.
The custom Bleecker text-scale environment does not change these captured public
chart pixels. Parent font overrides do not replace the native chart's axis font.

The 5,238 ordinary chart outputs reproduce exactly in a second unchanged-source
build and a fresh extraction of the source-only archive. The 450 edge-case outputs
remain in strict comparison. Six NaN-bar PNGs differ in the second build; those
variants and the archive variants remain preserved as failures. Eight fresh
initializations produce three images, each stable through subsequent 0.2-second
and 1.0-second waits. Native non-finite-input determinism remains unresolved.
No case is removed and no expected image is changed. All builds use the complete
89-file pinned tree and locked dependencies. Original pilot and failed helper
inputs are preserved; the failed helper used the wrong AppKit accessibility
protocol name. Apple source/tooling and the source-only artifacts stay outside
the Linux tree, with checksummed locators in the provenance.

The hidden native window exposes only a minimal accessibility group. This does
not establish chart data exploration or actual reader behavior. No pointer input
was delivered. Native input/timing, physical display/input, reader acceptance,
independent-machine artifact download remain pending. No source pin, expected
image, tolerance or exception changes.

## Linux candidate

All five public QML types share `ChartBase` and `ChartRenderer`. The four full
charts accept `points`, an array of objects with numeric `x` and `y`. Optional
string fields `id`, `series` and `label` default to the row index, `Value` and
an empty string. A bar chart groups by `label` and stacks signed values by series.
`BleeckerLineChart.area` enables signed stacked areas behind the line strokes.
`BleeckerPieChart.innerRadius` is a ratio, default zero; the observed endpoint
clamping and NaN/infinity cases are retained as separate diagnostics.
`BleeckerSparkline.values` accepts a numeric array and uses its index as x.

```qml
BleeckerLineChart {
    width: 460
    height: 260
    points: [
        { id: "a", x: 0, y: 10, series: "Readers" },
        { id: "b", x: 1, y: 18, series: "Readers" },
        { id: "c", x: 2, y: 14, series: "Readers" }
    ]
    area: true
}
```

The public roots have a 100-by-100 ideal size. A zero caller frame centers the
one-by-one chart inside that frame. Roots retain their renderer under data, size,
theme, custom text scale, RTL and disabled updates. Rendering expands to actual
paint bounds, so endpoint symbols, curve controls, labels and stroke edges are
not clipped to the plot. No expected image is used to render the charts.

The renderer owns continuous domains, categorical order, series palettes, caption
layout, dashed vertical and solid horizontal grids, centripetal Catmull-Rom curves,
area gradients, signed bar stacks, scatter circles and rounded inset sectors.
Both continuous domains include zero. Sparkline hides its axes and keeps the
source's `Value` legend. Font and palette inheritance follow the measured source;
custom Bleecker text scale does not scale chart captions. The current system-font
candidate differs from the native font and affects both plot width and raster.

Malformed arrays, objects, coordinate types and string fields fail explicitly.
Numeric NaN and infinities remain numeric inputs; valid independent channels and
legend entries survive. This does not claim native equivalence for non-finite
data: the source's NaN-bar initialization is nondeterministic and the candidate's
deterministic finite-stack behavior remains an unresolved difference. Extreme
finite and subnormal inputs also have separate robustness checks.

Charts are read-only graphics and stay outside keyboard tab focus. Actual Qt
interfaces expose the chart's name/point count and one static data row per input,
including non-finite values. `accessibleName` and `locale` can be supplied by the
Linux caller. Querying these interfaces does not establish source reader behavior.

Open `AvelinoCatalog --fixture charts` for the five chart choices, area/donut,
data, empty state, size, direction, theme, text scale and disabled controls.
Isolated chart definitions use the same `ChartsCase`; the catalog validates the
complete schema and rejects malformed input before loading QML. The installed
consumer uses `--charts`. Its default mode fails when source frames or measured
metrics differ; `--charts-observe` records those differences while keeping every
runtime, lifecycle, data-change, restore, input and Qt accessibility failure fatal.

Run `python3 scripts/generate-chart-witnesses.py --check` to verify the packaged
projection. `scripts/capture-charts.py CONSUMER OUTPUT` captures all 1,744 images:
960 closed contexts, 400 edge contexts and all 384 steps of 48 retained histories.
`scripts/compare-chart-captures.py CAPTURES OUTPUT` compares every RGB and alpha
pixel, all observed source frames/metrics and caller state. Edge captures have
no native plot-proxy metrics; their reports say `unobserved`. The canonical
NaN-bar captures stay in comparison, with their known source variation disclosed.
No images are removed, resized, masked, recalibrated or accepted through these
diagnostics. Native geometry, fonts/raster, non-finite behavior, input/timing,
physical displays/input and reader acceptance remain open.

Current Linux evidence passes all 31 Qt targets, including 5,341 component checks
at DPR one and 5,569 at DPR two. The installed package passes 33 modes and 135
catalog captures; all 131 earlier PNGs and their complete metadata are unchanged.
Forty virtual profiles cover base, font, surface, pill and chart fixtures across
X11/Wayland, software/OpenGL and two display/text scales. This includes eight
complete chart profiles. Actual XTest input reaches all 14 gallery controls over
24 clicks and 25 states, with each entire caller viewport equal to a separate
installed isolated Qt fixture. These are virtual implementation checks.

The strict 1,744-case comparison has 32 complete matches, all empty line/bar/
scatter/sparkline charts. All 40 empty-chart pixels match, including pie, but
pie metrics still differ. All 1,744 layout/state observations and all 1,344 native
outer-frame sets match; 120 complete native metric sets match. Zero nonempty or
retained-history cases pass the complete strict comparison. No acceptance follows
from these counts.

The [sealed candidate](../evidence/development/charts-20261017/candidate.json)
preserves every warning-producing earlier attempt, frozen source inputs,
installed executables, runtime captures, arithmetic diagnostics and raw pixel
differences. A read-only arithmetic experiment reproduces 2,696 continuous x/y
positions exactly using a precomputed reciprocal. A separate native measurement
finds a 0.5-point DPR-two plot-height change in 110 nonempty/nonzero cases. Both
remain named geometry corrections after this captured implementation; the
candidate and its expectations are preserved. Run
`python3 scripts/verify-chart-candidate.py` to recompute the published evidence.
Desktop coverage is 71/80 candidates and zero accepted entries.
