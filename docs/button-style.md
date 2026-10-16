# ButtonStyle source contract

The pinned `BleeckerButtonStyle` styles a caller-supplied native Button label.
The [source investigation](../evidence/reference-investigations/button-style-20261016/investigation.json)
records 88 fixtures across eight profiles: 704 groups whose public, geometry-probed
and independent source-expression witness images match byte for byte. A fresh
source-only extraction rebuilds all 89 unchanged Sabella source files and
reproduces all 2113 output files exactly. Separate CUA runs exercise the unprobed
public style in inactive and active/key windows. Linux implementation remains
pending; this checkpoint changes no candidate or acceptance count.

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
captures, tolerances and approved exceptions are unchanged; desktop coverage
remains 62/80 candidates, 18 pending and zero accepted, with all 46 TV entries
pending.
