# Native chart investigation

The five desktop chart families share the pinned `Charts.swift` implementation:
`BleeckerLineChart`, `BleeckerBarChart`, `BleeckerPieChart`,
`BleeckerScatterChart`, and `BleeckerSparkline`. The line chart's `area` option is
part of that surface. Linux implementation remains pending; the plan calls for
an owned renderer without a GPL-only chart dependency.

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
independent-machine artifact download and the complete Linux implementation and
comparison remain pending. No source pin, expected image, tolerance or exception
changes. Desktop coverage remains 66/80 candidates, with zero accepted entries.
