# Page header and breadcrumb

`BleeckerPageHeader` and `BleeckerBreadcrumb` now have Linux candidates based on
the preserved source investigation. Both remain verification-pending. Source
images, input/runtime evidence and complete mirror acceptance are separate.

The authority is the preserved desktop revision
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`,
`Sources/Sabella/Navigation.swift:122–173`. The
[investigation](../evidence/reference-investigations/navigation-layout-20261015/investigation.json)
preserves 392 public source captures: 232 page headers, 152 breadcrumbs and eight
button anchors. Each fixture covers both appearances, text scales 1/1.5 and
ImageRenderer DPRs 1/2. These are source rendering contexts; the separate 32
pointer/lifecycle records use isolated inactive native windows at backing DPR 2.

The proposal's shared wrapper description describes the default context. Explicit
`parent-font20` cases apply the recorded 20-point parent override. Per-case
`value`, `intrinsic`, `rtl`, geometry and source metadata establish those contexts.

## Page header

The initializer requires eyebrow, title, description and caller actions. The
source uppercases the eyebrow and always creates all three text views. It uses
Encode Sans Bold at 10 points with 1.2 tracking, Encode Sans semibold at 25 points
with −0.5 tracking, and Libre Franklin Regular at 13 points. Their colors are
`desert`, `textPrimary` and `textSecondary`. The recorded font resolution confirms
these fixed styles across the captured text scales and parent-font context.

The label column has four points between views and leading alignment. Its outer
row vertically centers the label column, a Spacer, and the action row, with 24
points between those three children. The action row owns 12-point spacing.
Empty actions still leave an empty action row participating in the outer layout.
In an intrinsic capture the Spacer measures eight points, so the natural width
includes 56 points beyond the labels and actions. In a fitted capture the Spacer
takes the remaining width. Labels and actions can both compress; retaining the
actions' natural width is incorrect.

At light appearance, text scale 1 and DPR 2, the ordinary 560-point header is
68 points tall. The same strings with a Create button at width 240 produce an
84-point header; at width 120 the header is 312 points tall and the action is
36 × 119. Two buttons at width 240 give a 119-point action row beside an 84-point
label column. These measurements describe actual source layout, including its
zero-width action label. They are not recommended application widths.

Empty text is not an absent view. In the recorded default inherited font context,
each empty label has zero width and a 14-point line box, irrespective of its
nonempty font size. Three empty strings produce a 50-point column. Tall and
overflowing caller views remain distinct from layout size. RTL reverses the
outer visual order and preserves leading label alignment.

The source pointer witnesses cover activation, disabled and canceled presses,
producer title changes, explicit replacement, removal/reinsertion and RTL.
Changing the header title preserves the action's private counter and mounted
identity; replacement or removal/reinsertion resets it. The helper's PageHeader
case named `nil-handler` supplies empty actions. PageHeader has no optional
selection callback.

The shared navigation fixture starts with `Éditions 東京`. Its Unicode title uses
the captured 32-point line box and 68-point header height with CJK fonts installed.
The owned text shaper requests typographic metrics for bundled-font text and its
fallback runs. The installed consumer changes the title to Latin and back while
checking the height, action state and editing focus. The existing source geometry
assertions remain intact; glyph/raster and reader acceptance are still pending.

## Breadcrumb

The source accepts an item array and optional `(Int) -> Void` callback. Item titles
and optional symbols are caller data. Rendering uses the logical array index;
the generated item UUID is not the `ForEach` identity. Every item is a plain
button, including the final item. Earlier items use `sea`; the final logical item
uses `textPrimary`. The row applies Encode Sans Regular at 12 points, overriding
the captured 20-point parent font and remaining fixed across text scale 1/1.5.

Each optional icon precedes its title with five points between them. The outer
row inserts a `chevron.right` with the source caption2 font before every item
after the first, and uses eight points on each side of the separator. Empty
titles retain their text view and relevant spacing. The empty array measures
0 × 0; a single empty title without an icon measures 0 × 14. A three-item array
with empty titles and no icons still measures 47 × 14 at DPR 2 because the two
separators and their gaps remain.

At DPR 2 the normal row measures 203.5 × 15. Offering width 140 produces a
138.5 × 60 row; offering 60 produces a 69 × 135 row that exceeds its proposal.
Source fitting must therefore be distinguished from a caller's outer frame.
The actual symbol expression witnesses measure 7.5 × 11 for the caption2
separator at DPR 2 and 8 × 11 at DPR 1. They document source geometry and do not
authorize redistributing native symbol artwork.

Own-window pointer scans record actual callback hit positions for every logical
item. Repeated final-item clicks produce `[2, 2]`; replacing the array with one
item produces `[0, 0]`. Producer label updates preserve index callbacks. RTL
reverses the visual order while callbacks retain logical indices. Disabled,
canceled and absent-handler cases produce no callback. These observations do
not establish native keyboard or accessibility correspondence.

## Trust and replay

Each of the 392 captures has an independently rendered unmodified public
component, a root-geometry witness and a reconstructed layout witness. The two
witness images must match the unmodified component byte for byte before their
internal geometry or font records are used. All 784 comparisons pass after the
helper explicitly warms every public API at both DPRs. Earlier cold-cache
attempts remain in the external candidate directory; they are not substituted
for the final source captures.

The separate text investigation retains 104 original/rendered pairs and records
unmodified view bounds, actual resolved fonts, and line-layout diagnostics.
Only 82 pairs preserve both PNG bytes and bounds. The other 22 very narrow
TextRenderer contexts alter pixels, and the width-zero probe also changes the
view's width. Their line geometry is explicitly untrusted. Their original
unmodified images and diagnostic files remain available; source component
geometry comes from the independently verified whole-component witnesses.

[Tool provenance](../evidence/reference-investigations/navigation-layout-20261015/tooling-provenance.json)
records the exact OS, SDK, compiler, pinned archive and preserved module/object
hashes. Swift source and native build inputs remain in an immutable external
helper archive. A clean extraction verified all 37 inputs, recompiled both
helpers and reproduced all 1,416 output files byte for byte, including complete
geometry, behavior and text metadata. The helpers link the previously
source-verified reference object; fresh compilation of all Sabella sources and
a public helper download remain pending.

Run the integrity checks with:

```sh
python3 scripts/verify-navigation-layout-source.py
python3 -m unittest discover -s tests/contracts -v
```

The earlier source-only checkpoint passed the native integrity check, 91 contract tests,
immutable-reference and existing-proposal verification, API/inventory
reconciliation and the staged Linux-only boundary check. These checks validate
source evidence and its trust boundaries; they do not exercise new Linux controls.

## Qt API and layout adapter

```qml
BleeckerPageHeader {
    width: 560
    eyebrow: "Workspace"
    title: "Editions"
    description: "Prepare the next edition."
    BleeckerButton { text: "Create"; onClicked: controller.createEdition() }
    BleeckerButton { text: "Import"; variant: "secondary" }
}

BleeckerBreadcrumb {
    maximumWidth: 140
    items: [{ title: "Home" }, { title: "Workspace" }, { title: "Editions" }]
    onSelected: index => controller.navigateTo(index)
}
```

PageHeader's default `actions` property retains caller items in its owned
12-point action row. `width` supplies the header's layout proposal; its natural
implicit width includes the label column, Spacer and both 24-point gaps.
Breadcrumb uses `maximumWidth` (`-1` means intrinsic) and exposes its fitted row
through `presentationItem`. An explicitly sized outer Item remains distinct
from that fitted presentation.

Breadcrumb accepts ordered JavaScript arrays or C++ `QVariantList` sequences.
Each item requires a string `title` and may provide an `icon` Component. The
loaded icon can read its parent slot's `foregroundColor` and `font`. The caller
owns navigation; the control emits `selected(index)` and changes no route or
item model itself. All items, including the final one, use native Qt Template
buttons. An absent signal handler is valid. Empty arrays and empty strings
retain the measured source distinctions. Invalid models, nonstring titles,
non-Component icons and invalid width proposals fail startup explicitly.

`BleeckerLayout` is the Qt content-layout adapter. Fixed children can use their
implicit size. Flexible children publish `minimumWidth` and `idealWidth`, consume
the readonly `proposedWidth`, and report their fitted implicit size. The row owns
child width, height and position. BleeckerButton supplies these metrics directly;
its caller's `maximumWidth` remains an additional constraint. Factory Loaders
forward the child's metrics and the proposal explicitly, as shown in
[`NavigationCase.qml`](../tests/consumer/NavigationCase.qml). The row allocates
less-flexible content first, rounds offers to physical pixels and retains
zero-size children and their gaps. Removal/replacement uses normal Qt object
lifecycle. Invisible children keep layout space; use a conditional Loader to
remove their content.

The separator uses Avelino's original chevron candidate in the measured source
frame. Optional icons use caller Components; there is no SF Symbol lookup.
[`BreadcrumbHouse.qml`](../tests/consumer/BreadcrumbHouse.qml) is original,
fixture-only artwork. Neither symbol artwork nor OS default action-text fonts
have approved native equivalence.

The `Éditions 東京` fixture exposes unresolved Japanese glyph fallback: the
Linux characters currently render missing-glyph boxes, and the title's width
differs from the source. Its immutable image comparison and
actual metadata remain in the diagnostics. Component-bound checks still run;
the title's glyph-dependent child geometry is explicitly outside the available
font assertions. No font substitution or visual exception is approved.

Run the gallery with `AvelinoCatalog --fixture navigation` and the independently
installed consumer with `InstalledConsumer --navigation`. Source-derived tests
also run the isolated fixtures, model/index updates, canceled/disabled presses,
fixed header fonts and caller state preservation. Package and display-session
checks exercise pointer/keyboard input, actual Qt accessibility roles/actions,
focused text editing, producer changes, factory replacement and remounting.

Additional inherited empty-text contexts, broader scripts and caller
compositions, exact font/symbol pixels, native keyboard/focus, physical sessions,
actual readers and all TV gates remain pending. No source pin, expected capture,
tolerance or exception changed.

## Candidate verification

The [sealed candidate](../evidence/development/navigation-layout/candidate.json)
records 5,106 Qt checks, 93 contract tests, 25 invalid-startup refusals, 18 installed
modes, 83 relocated catalog captures and 144 independent virtual window/output
pairs. All 3,522 preceding image/full-metadata pairs are byte-identical. The
new 392-case comparison matches whole-component bounds in every case, with 24
exact empty presentations. It remains failed overall. The separate child-bound
audit records eight unresolved Japanese title widths among 1,320 checks; its
source/candidate images retain the missing-glyph failure.
