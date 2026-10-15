# Tabs and segmented selection candidate

The pinned `Navigation.swift:176` implementation of `BleeckerTabs` delegates to
`BleeckerSegmentedControl` in `Buttons.swift:146`. Avelino follows that contract:
Tabs chooses a value; the caller owns any corresponding page content. Both
controls remain verification-pending.

```qml
BleeckerTabs {
    selection: model.currentView
    options: [
        { value: "morning", label: "Morning" },
        { value: "evening", label: "Evening", disabled: true }
    ]
    onActivated: value => model.currentView = value
}
```

The acceptance criteria cover pointer selection, reselection, disabled options
and groups, an unmatched caller value, empty/reordered options, typed values,
external updates following interaction, keyboard traversal, actual Qt button
interfaces, constrained text wrapping, RTL, theme/scaling, and independent
installed consumption. Every candidate check is separate from strict image and
physical input/screen-reader acceptance.

A native property write preserves the caller's QML `selection` binding. The
`activated(value)` signal lets the caller update its model once per activation,
including reselection. Earlier segmented controls assigned `selection` inside a
QML handler, detaching that binding. The regression test clicks a segment and
then changes the caller's value; the control must reflect the new value. String,
number, boolean and empty-string identifiers retain their types. The Qt adapter
uses strict equality; tested identifiers are strings, numbers, booleans and empty
strings. Object-value identity and additional source value types remain unverified.

Each option uses the owned Qt button template. Disabled options and groups reject
input. Their labels dim while selected background surfaces retain their source
color. Accessibility exposes the label, button role and selected description;
actual screen-reader output remains pending. The independent consumer exercises
Qt pointer, keyboard and accessibility press actions before changing the external
model again. Source keyboard equivalence remains pending.

The source group has 4-unit padding, 2-unit gaps, 12-unit horizontal label padding,
a 32-unit minimum segment height and 13-unit medium primary text. Unconstrained
labels keep their natural line count; constrained layouts wrap. Wide caller
frames center the natural group, and narrow fixtures retain the source width
proposal. A `RowLayout` allocates constrained widths; a visible `Row` retains fractional
intrinsic widths, exact natural gaps and RTL positioning. Allocation cells have
no input or accessibility surface. Fractional allocation,
multiline intrinsic sizing and exact rendering remain diagnostic comparison work;
no tolerance or approved exception is introduced.

The native helper uses the pinned preserved source objects and owns its isolated
windows. Static DPR 1/2 cases use ImageRenderer; action cases use native DPR 2
window caching with local events. The helper and its build inputs remain in a
checksummed external archive. The repository contains only proposed rendered
captures and provenance. These are supplemental review evidence and do not
replace accepted references.

Use `AvelinoCatalog --fixture tabs` for the visual fixture and
`InstalledConsumer --tabs` for the independent interaction fixture. The Linux
pipeline captures both controls under the same native matrix. Its action fixtures
invoke the Qt template click method and record actual model state; the installed
consumer verifies pointer dispatch separately. The package-only
harness separately covers X11 and nested Wayland, software and Mesa OpenGL,
DPR 1/light/text scale 1 and DPR 2/dark/text scale 1.5. Virtual sessions and
synthetic events do not establish physical display/input or reader acceptance.

The [proposed source matrix](../evidence/reference-proposals/tabs-20261014/proposal.json)
contains 116 cases per control plus eight anchors. Its 241 files replayed
byte-for-byte. The [Linux candidate](../evidence/development/tabs/candidate.json)
records 236/240 matching root bounds and 0/240 exact images. The four multiline width differences and all nonmatching pixels
remain visible in the report. Final selection and activation counts match across
the matrix. No expected capture, pin, tolerance or exception changed.

All 2,954 Qt checks, 52 contract tests, three invalid-startup cases,
ten installed offscreen modes and 80 fresh package-only virtual-session pairs
pass, including eight Tabs configurations. Default/Basic/Fusion gallery images
are identical. Of 1,790 preceding PNG/full metadata pairs,
1,770 are unchanged;
20 segmented/gallery pairs record the
intentional disabled-label opacity repair, with previous and current evidence
retained. Candidate coverage is 40/80 desktop APIs started, with none accepted.
