# ButtonStyle source contract

The pinned `BleeckerButtonStyle` styles a caller-supplied native Button label.
The [source investigation](../evidence/reference-investigations/button-style-20261016/investigation.json)
records 88 fixtures across eight profiles: 704 groups whose public, geometry-probed
and independent source-expression witness images match byte for byte. A fresh
source-only extraction rebuilds all 89 unchanged Sabella source files and
reproduces all 2113 output files exactly. Separate CUA runs exercise the unprobed
public style in inactive and active/key windows. The Linux adapter adds catalog,
independent package and eight virtual profiles, with unresolved native pixel and
font/frame differences. Complete acceptance remains pending.

`Sources/Sabella/Buttons.swift:3` exposes primary, secondary, outline, subtle,
ghost, link and destructive variants. It reads color scheme, enabled state and
Bleecker text scale. Its four sizes have these defaults:

| Size | Primary medium font | Horizontal padding per side | Minimum height |
| --- | ---: | ---: | ---: |
| xs | 12 | 10 | 28 |
| sm | 13 | 14 | 36 |
| md | 14 | 18 | 40 |
| lg | 15 | 24 | 48 |

The font scales with Bleecker text scale; padding and minimum height stay fixed.
Link omits the minimum height. The style sets default foreground and font, paints
the variant/pressed background, clips with continuous rounded corners, then adds
a separate circular rounded-rectangle stroke border of width one. A press offsets
the painted result down one point and scales it to 0.99 with the source's
0.19-second ease-out control animation. Disabled opacity is 0.45. These source
parameters do not establish exact raster or animation timing acceptance.

SwiftUI's [ButtonStyle contract](https://developer.apple.com/documentation/swiftui/buttonstyle)
supplies platform interaction while the style supplies appearance. Its
[configuration](https://developer.apple.com/documentation/swiftui/buttonstyleconfiguration)
contains the label and pressed state. [Font values](https://developer.apple.com/documentation/swiftui/view/font%28_%3A%29)
flow through the environment until a nearer view overrides them. The library's
existing `BleeckerButton` additionally puts its label in an HStack and supplies
loading behavior; its captures cannot stand in for this generic style.

## Labels and layout

The style decorates each emitted flat label part separately. A two-part flat
label produces two styled bodies, two root geometry instances and one caller
counter mount. The bodies overlap in a ZStack. In a surrounding HStack or VStack
they occupy separate cells or rows, including the parent's spacing between them.
An explicit caller stack remains one styled participant. A Linux adapter must
preserve this layout participation instead of placing every label in one shared
padded rectangle.

At light appearance, text scale 1.5 and requested DPR two, the flat label's first
part measures 92.5 by 27 and its second part 72 by 44 points. Their styled bodies
measure 128.5 by 40 and 108 by 44. With 11-point parent spacing, a leading 40-by-12
rectangle and trailing 30-by-20 rectangle, the HStack measures 339.5 by 44. The
VStack measures 128.5 by 149. Sorted arrays retain each live geometry writer;
private identities do not enter the serialized data.

At light appearance, text scale one and requested DPR one, the default body is 83 by 40, containing
a 47-by-17 label. Link's body is 83 by 17. EmptyView emits no control and no caller
mount. A zero-size view emits a 36-by-40 body and mounts its caller; a hidden
200-by-80 view retains a visible 236-by-80 style body. These cases are distinct.

An outer width offer does not force the decorated body to that width. At offer
zero the root is zero wide, but the body remains 36 by 102 and the zero-width
label retains six lines. At offer 40 the body is 40 by 102; at offer 80 the root
is 80 wide and the body 71 by 40. Oversized labels, fixed rectangles, explicit
stacks, Unicode/bidi, RTL, semantic role and inherited context are also captured.
Parent font 32, parent red and destructive Button role leave the default image
unchanged in every measured profile. Explicit inner font and foreground remain
caller inputs; fixed inner fonts do not grow with Bleecker text scale.

## Input observations

The public row exposes two accessibility buttons in a container, named
`First child` and an empty name. Each receives a separate hit target and invokes
the same caller action. Holding either target changes both styled bodies; the
two steady held images are byte-identical. The action count changes on release.
Dragging from the first target and releasing over the second cancels activation.

A held click at canvas point (201.5, 180.5) activates the first target even though
its baseline pixel is white in the rounded transparent corner. The painted clip
and pressed scale therefore do not narrow that measured rectangular input area.
Points just outside the body, including the parent gap and above the first body,
do not activate it. A Linux implementation needs separate paint and input bounds.

The first CUA run retains 49 captures and 22 delivered events. Its two held samples
are inactive/non-key; Tab activates the application late in the run. A fresh
source-only app rebuild supplies a second run with 47 captures and 20 events.
Both held samples and all row captures in this second run are active/key, and the
same shared-press, cross-target cancellation and transparent-corner behavior is
observed. Global `mouseButtons` stays zero under the CUA window route; the app's
own delivered down/up intervals establish when the samples occurred. No global
physical input claim follows from those flags.

The caller counter survives variant and disabled-state updates. Disabled input
does not invoke it. Theme updates retain the row action count. The app harness
relocates its hosting view during setup, causing three appearances and two
disappear observations; these are not accepted source lifecycle equivalents.
Tab leaves accessibility focus on the window. Focused keyboard behavior,
physical displays/input and screen-reader output remain pending. Both helpers
were closed through CUA and their process termination was verified.

## Reproduction and limits

The first direct `makeBody` probe matches only 134 of 672 public images because it
bypasses installed style environments. Its independent witness matches all 672.
The second installed-style probe matches all pixels and replays all 2017 files,
but a scalar last-writer geometry map omits repeated parts. Both complete datasets
remain in PNG/JSON-only diagnostic archives. The final live-part collector keeps
all 672 prior public images unchanged, adds four parent-layout fixtures and
matches all 704 probe/witness state maps. A standalone diagnostic that omitted
the required resource bundle, its corrected prebuilt-object diagnostic, and a
superseded input-helper draft remain explicitly excluded.

The [tooling provenance](../evidence/reference-investigations/button-style-20261016/tooling-provenance.json)
records external source-only archives, input hashes and toolchain versions. The
closed replay archive SHA-256 is
`d387be708c883bdac274563f7670757cbe1229b716962cc435a7ec7fc4ab6416`;
the active-helper source archive is
`89749cfd13730f7d88f19cd96249d7f040b812b87e315c184ec69c4a963d4c0c`.
The active archive rebuilds the app; it does not automatically replay live input
or promise identical timed samples. Swift source, native executables, bundles
and source archives remain outside the Linux repository. Independent-machine
archive availability remains pending.

Closed captures use light/dark, text scale one/1.5 and requested bitmap DPR
one/two on a host with actual backing DPR two. They disable animation only for
closed poses. The live helper preserves source animation defaults. Neither
requested DPR one nor timer samples prove physical display or timing equivalence.

Run `python3 scripts/verify-button-style-source.py` to audit complete contexts,
sealed bytes, probe transparency, per-view allocation, parent layout, source-only
replay and bounded input claims. The [checkpoint validation](../evidence/development/button-style-source-20261016/result.json)
records all 310 host and 310 Linux contracts passing, including 19 new negative
and corpus checks. References CI runs the verifier and contracts. Native
system fonts, symbols, raster, full framework contexts, focused keyboard, caller
lifecycle, physical input and readers remain open. Reference pins, expected
captures, tolerances and approved exceptions are unchanged. That source-only
checkpoint retained 62/80 candidates, 18 pending and zero accepted; the candidate
below advances coverage without accepting any component.

## Linux adapter

The `BleeckerButtonStyle` adapter accepts live caller items through
its default `labels` property. Each item gets an independently sized Qt template
button. All parts invoke the style's `clicked` signal and share pressed visuals.
An explicit caller stack remains one label; direct sibling labels remain separate
parts. `ProposalRow` and `ProposalColumn` preserve their separate participation.
An empty label list creates no input; a zero-size item retains padding and the
minimum height.

```qml
import QtQuick
import QtQuick.Templates as T
import Avelino

ProposalRow {
    maximumWidth: 320
    BleeckerButtonStyle {
        variant: "outline"
        onClicked: edition.publish()
        T.Label { text: "Publish"; color: palette.windowText }
    }
}
```

`maximumWidth` supplies a containing layout's available width. `widthOffer`
models a fixed outer allocation and can be zero while the decorated body and
its rectangular input remain wider. Both default to minus one for an absent
proposal. Labels retain their objects through variant, size, theme and enabled
updates. Qt font/palette inheritance supplies defaults, and explicit inner
typography and foreground take precedence. Rounded clipping affects paint;
the native input rectangle remains separate from the pressed transform.

The focused core runs match 680 native frame contexts across requested DPR one
and two, with ten additional behavior/layout checks per DPR. The system-font,
Unicode and bidi fixtures remain outside those frame assertions. The checks also
cover Qt Space activation, actual accessibility names, caller identity, disabled
input, cross-part cancellation, corner clicks and synchronous nested-column
measurement. These focused runs use the software renderer. Complete suites, catalog,
independent package and virtual profiles are recorded below. Exact native
pixels, focused keyboard/timing, physical input and readers remain pending.

The caller fixture's green/orange decorations use explicit platform sRGB values.
Its [color record](../evidence/development/button-style/platform-colors/result.json)
matches 64 original PNG samples and a fresh source-only color-helper replay.
That helper resolves platform colors without instantiating Sabella or performing
UI input. The helper and source archive stay external. No reference image,
reference pin, tolerance, exception or acceptance count changes.

## Candidate evidence

The [sealed candidate](../evidence/development/button-style/candidate.json)
preserves 704 original-size installed-catalog captures and actual label objects,
per-part rectangles and caller state. Strict comparison matches
680 frame contexts, 704 initial states and
16 complete pixel/frame cases. The remaining
688 pixel differences stay visible in the
comparison report. System-font, Unicode and bidi frames remain unresolved in
24 contexts. No resizing, ignored regions, tolerance
changes or approved exceptions are used.

Both full component suites and all 23 CTest targets pass. All 328 host and 328
Linux contracts pass, including ten adapter checks and a complete pixel/frame
comparison invocation. The fresh independent package passes 27 modes and 119
gallery captures. All 115 previous gallery PNGs and their full metadata remain
byte-identical. The 121 installed files and five Qt private-integration files
match across package and runtime boundaries.

In each of eight virtual X11/Wayland, software/OpenGL, standard/scaled profiles,
the compiled consumer checks 88 original states, 85 exact frame sets, caller
identity, actual Qt keyboard/accessibility and all 13 native pointer phases.
Holding either target produces identical shared pressed pixels; cross-target
release cancels, and the rounded transparent corner remains clickable. Native
hold durations are replay targets, not accepted timing. The native input profile
and current Qt display profile are recorded separately. Runtime containers have
neither consumer sources nor the producer build.

The new pixel check covers the primary preview's right padding and the gap
outside it during text-scale growth and shrink. The same compiled consumer
rejects the original library and passes with the rebuilt package. Both the
continuous background and clipping shapes use asynchronous curve processing.
In the pinned [Qt 6.8.3 curve renderer](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quickshapes/qquickshapecurverenderer.cpp),
queued path edits restart through the asynchronous runner. Paired captures
reproduce the earlier painted width and verify the corrected result; the
offscreen metadata/input checks alone had missed it.

All pre-fix evidence remains in the checksummed diagnostic archive, including
the four-profile capture-acknowledgment deadline failure, incompatible mount
cache, comparison adapter failure and six original Qt attempts. Later shared-VM
frame/configuration timeouts and the first isolated CTest mount failure are
preserved too. The final pipeline uses an isolated six-GiB VM and the same pinned
images. Source/build inputs are read-only during CTest, with separate writable
trace and Testing directories. The original VM and active Docker context remain
intact. The capture observer acknowledges completion explicitly; the runner owns
cancellation and deadlines.

Per-body paint aligns to the DPR grid while logical outer/label frames retain
fractional positions. Nested columns refresh before row measurement and after
allocation. Logical label bounds remain separate from glyph ink, including
zero-width overflow. Explicit fractional `font.pointSize` properties preserve
sizes that Qt 6.8.3 rounds down when supplied through a `Qt.font()` map.

Press motion uses a 190 ms OutCubic approximation. Exact native ease-out timing,
focused keyboard, complete caller lifecycle, system fonts/raster, physical input
and readers remain pending. Virtual software/OpenGL does not establish hardware
acceleration or physical acceptance. Coverage is 63/80 desktop candidates,
17 pending and zero accepted; all 46 TV entries remain pending.

Run `python3 scripts/verify-button-style-candidate.py` to audit sealed captures,
measured frame/state outcomes, the eight virtual profiles, package identity,
pre-fix archive and negative/positive paint regression. CI captures all 704 cases
on x64 and ARM64 and publishes strict diagnostics separately from build/runtime
success.
