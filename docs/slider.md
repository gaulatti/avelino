# Slider candidate

`BleeckerSlider` implements the pinned desktop source in `Extended.swift:37`.
It remains verification-pending. The observable criteria are continuous and
stepped pointer movement, drag updates, external caller updates after interaction,
range endpoints, signed/shifted ranges, disabled input, keyboard traversal,
actual Qt value/action interfaces, fixed source dimensions, dense ticks, and
independent installed consumption. Source keyboard, RTL and screen-reader equivalence,
inactive presentation, and physical display/input checks remain open.

```qml
BleeckerSlider {
    width: 320
    from: -5
    to: 5
    stepSize: 0.5
    value: model.amount
    onMoved: model.amount = value
    Accessible.name: "Amount"
}
```

`from`/`to` are the caller's finite ascending closed range; bounds must remain
valid during updates. `stepSize: 0` represents
the source's absent optional step; positive values enable stepping and tick marks.
Negative steps, reversed ranges and non-finite bounds fail at QML startup. Value
updates use a native property write to preserve the caller's QML binding.
The independent consumer verifies an external update after pointer, drag and
accessibility changes. Disabled accessibility writes are rejected while normal
external model updates still work. The root is a focus scope; `inputItem` exposes
the owned template input for platform inspection and explicit focus requests.
The caller's accessibility name is forwarded to the actual slider interface.

Source measurements show 16 logical pixels of height, a 6-pixel track and a
20-by-16 handle, unchanged at text scale 1.5. The owned palette centralizes native
track, handle, active/disabled fill and tick colors. The native tint is requested
with the source sea token, then resolved through its system presentation and cache
color conversion; the Linux native-control palette records that measured output. Circle geometry and Canvas shadows are original Linux code. Exact
rasterization, shadows, profile conversion and source system presentation remain
unaccepted. Natural unconstrained sizing and the inactive source presentation
need additional reference cases; the current implicit width of 200 is a Linux
layout value, not an accepted source intrinsic measurement.

Stepped source controls use an integral number of intervals. `0...1` with step
`0.3` offers a final selectable value of `0.8999999999999999`, with uniformly spaced
ticks. The public range remains `0...1`. A caller value of `1` is retained while
the native input displays its final stop. A single division ULP must not lose an
integral interval: `0...0.3` with step `0.1` selects `0.30000000000000004`, matching
the actual source binding. The helper advances the interval quotient by one ULP
before flooring it; tests also prove step `0.26` ends at `0.78`, rather than
rounding a partial interval up. These are numeric source behaviors, not visual
tolerances or approved exceptions.

Tick work is bounded by displayed width. Separate circles are drawn while they
remain distinct; overlapping circles are rasterized as their union by physical
column. Million-step fixtures exercise this path without creating a million UI
items or silently dropping source ticks.

The [Qt 6.8.3 value interface](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quick/accessible/qaccessiblequickitem.cpp)
reads `minimumValue`, `maximumValue`, `value` and `stepSize`. The template exposes
those range aliases and explicit increase/decrease actions; the adapter forwards
value changes through the caller boundary, including accessibility writes.
Actual interface setters/actions, disabled rejection, and subsequent external
updates are exercised. Qt keyboard movement uses its normal template mechanisms;
continuous arrows currently move by Qt's absolute 0.1 default. Source keyboard
increments are unverified and no equivalence or exception is approved. Interface
queries and synthetic actions do not establish actual screen-reader acceptance.

The source helper rendered no `NSSlider` child: SwiftUI owns the slider subtree.
It requests an active control context explicitly so tint is measured independently
of the host's activation status. The helper could not obtain an active key window,
even during separate focus probes. Six keyboard cases remain enumerated as
unverified, and failed probe output is retained. No desktop lock state is assumed
and no keyboard-navigation, accessibility or permission preferences were changed.

The first [source proposal](../evidence/reference-proposals/slider-20261014/proposal.json)
used short settlement periods. Its independent replay changed 20 of 93 files,
including substantial post-action animation differences. It remains preserved as
diagnostic evidence and is not the selected comparison input. The second protocol
uses a local SwiftUI transaction with animations disabled and a 600 ms settlement;
it does not change system accessibility preferences. Its source/object inputs,
recompilation, replay differences and selected comparisons are recorded separately.
Neither proposal updates accepted captures, reference pins or tolerances.

`AvelinoCatalog --fixture slider` shows continuous, disabled, constrained, signed,
shifted, fractional and dense controls. `InstalledConsumer --slider` exercises
real input, retained binding, accessibility updates, disabled traversal, numeric
endpoints and subsequent text editing. Source binding-write counts and Linux edit
counts are retained as diagnostics: gestures may issue different intermediate
writes. The comparator requires matching final values, bounds, step and whether
the caller binding was updated.

This native UI change has no backend, metrics or application-configuration impact.
TV remains separate and requires the previously deferred hardware target.

The selected [v2 proposal](../evidence/reference-proposals/slider-20261014-v2/proposal.json)
replayed all 93 files byte-for-byte. The [checksummed Linux candidate](../evidence/development/slider/candidate.json)
preserves 92/92 matching root bounds and 0/92 exact images; the new slider contributes 84 cases plus eight anchors.
All 2,926 Qt checks, 48 contract tests and three invalid-configuration
startup refusals pass. Nine installed offscreen modes and 72 fresh package-only
virtual-session pairs pass, including eight slider configurations. All 1,694
preceding offscreen PNGs and complete metadata remain byte-identical. Default,
Basic and Fusion gallery images match exactly. Native keyboard, inactive/natural,
ordinary-motion/RTL/touch/DPR1, exact appearance, physical input/display and real
screen-reader acceptance remain pending. No expected image, pin, tolerance or
approved exception changes.
