# Data-display candidates and native evidence

The remaining `BleeckerIconBadge`, `BleeckerMetric`, `BleeckerStatCard` and
`BleeckerKbd` desktop APIs have Qt candidates backed by sealed native source evidence.
Complete mirror acceptance remains pending. No font, symbol, pixel tolerance or
exception is approved.

The authority is desktop revision
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`,
`Sources/Sabella/DataDisplay.swift:16–66`, with its pinned `Contracts.swift`,
`Surfaces.swift` and `Tokens.swift` dependencies. The
[investigation record](../evidence/reference-investigations/data-metrics-20261015/investigation.json)
seals the source PNGs, geometry, resolved fonts, formatter strings and replay.
The [verifier](../scripts/verify-data-metrics-source.py) checks their integrity.

| Public API | Source images | Measured coverage |
| --- | ---: | --- |
| `BleeckerIconBadge` | 184 | md/lg × primary/subtle/outlined × house/wide-arrow/minus; intrinsic, narrow, RTL, disabled and parent font |
| `BleeckerMetric` | 416 | Four formats; normal/intrinsic/narrow/very narrow, empty/long/multiline label, RTL, disabled, parent font and German environment locale; extra negative/small/currency/compact values |
| `BleeckerStatCard` | 344 | Absent/zero/positive/negative delta, intrinsic/narrow/very narrow, empty/long label, RTL, disabled, parent font and German environment locale; currency/percent/compact values |
| `BleeckerKbd` | 96 | Normal/empty/space/long/multiline/Unicode keys, intrinsic/narrow/very narrow, RTL, disabled and parent font |
| Button anchor | 8 | Existing public button, recorded independently with the same environment axes |

Each fixture crosses light/dark, text scale 1/1.5 and DPR 1/2. All 1,048 public
component images match their root-instrumented image bytes. All 1,048 separately
reconstructed layout witnesses also match the unmodified public image bytes.
Recorded child rectangles and resolved fonts therefore have an independent image
identity check; source reconstruction is not an accepted replacement baseline.

## Icon badges and key labels

The badge retains a fixed square of 36 or 48 points even when its outer width
proposal is 12. Its symbol uses a medium system font at edge × 0.4. Primary uses
`primaryForeground` over `primary`; subtle/outlined use `sea` over `muted`.
The circular seven-point outline clips content. Outlined adds a sea border at
opacity 0.4. Native correspondence for caller-supplied Linux icon artwork remains unaccepted;
no SF artwork or native font is redistributed.

The key label uses the native `.AppleSystemUIFontMonospaced-Medium` face at
10 points, six points of horizontal padding and a minimum height of 22. Its
background is `muted`, its border is `border`, and its circular radius is four.
The source does not set its foreground color. At DPR 2, `⌘K` is 24.5 × 22 and an
empty key is 12 × 22. A 30-point outer proposal for `Control` yields 24.5 × 52;
a 12-point proposal yields 12 × 91 with a zero-width text rectangle. The source
monospaced face remains unresolved for Linux; these bounds do not establish an
accepted replacement face or justify forcing its width.

## Metrics, stat cards and layout

The metric uppercases its label, uses Encode Sans Bold 10 with tracking 1 and
`textSecondary`, then a four-point gap and Encode Sans Semibold 24 with
`textPrimary`. Its fixed font styles ignore the recorded text-scale and
parent-font changes. The numeric text declares a numeric content transition;
transition frames have not been measured.

With the recorded US process locale, `Readers` and number `12345.6789` produce
`READERS` / `12,345.6789`. At DPR 2 the fitted metric is 130.5 × 46; an 80-point
outer proposal yields 75 × 76. A 12-point proposal yields 12 × 418. An empty label
retains a 14-point line box, making the ordinary metric height 48. Narrow layout
can report zero-width text with nonzero wrapped height; do not replace the
measured source behavior with a generic text truncation rule.

The stat card uses the original default card with 24-point padding. Its top-aligned
row holds the metric, a Spacer and a trailing column. The measured Spacer minimum
is eight; there are no additional gaps around that Spacer. The trailing column
holds a subtle md icon badge and, when delta is present, an eight-point gap and
Encode Sans Semibold 11 signed percentage. Zero is present and displays a plus
sign. Positive and zero use the source **light** palette `live`; negative uses its
`destructive`, including in dark appearance.

At DPR 2, a 320-point stat card with a positive delta is 320 × 105. Its row is
272 × 57. With no delta and intrinsic sizing it is 222.5 × 94. A 60-point outer
proposal overflows to width 92 and reaches height 466. The badge retains its fixed
extent while the metric can return width zero. RTL geometry is captured separately.

## Formatting and locale ownership

The native metric's private implementation calls `Double.formatted` and hands a
finished string to `Text`. That string follows the **process locale**. Giving the
SwiftUI hierarchy a German environment locale leaves the US metric string and
bounds unchanged. The stat-card delta uses `Text(value, format:)`, so its formatted
percentage follows the **environment locale**. For delta `0.123456789`, the recorded
US environment renders `+12.345679%`; German renders `+12,345679 %` with U+00A0.
These two producer paths must remain distinct in the Linux implementation.

Seven isolated process runs use `en_US`, `de_DE`, `es_CL`, `fr_FR`, `ja_JP`, `ar_EG`
and `hi_IN`. Per-process argument overrides change no system preferences. Each
records 190 formatter witnesses: 19 values across number, currency, percent and
compact, including seven currency-code inputs. The 1,330 locale witnesses cover
negative zero, rounding boundaries, tiny/large values, infinity and NaN. Currency
precision is source-driven: US dollars use two digits, JPY/CLP zero, KWD three.
Nonbreaking spaces, narrow nonbreaking spaces, directional marks, native digits
and localized compact forms are preserved as exact strings.

The native framework's invalid seven-letter currency input returns a raw Double
description in this matrix, including `-0.0`, `inf` and `nan`. This is an observed
source behavior, not a new Linux error policy. No implementation choice is made
by this investigation.

A standalone, non-product Linux prototype uses Ubuntu 24.04 ARM64's ICU 74.2 C API
and skeletons `.######`, `percent scale/100 .######`, `compact-short` and
`currency/CODE`. It matches 1,169 of the 1,330 strings exactly. Of the 161 failures,
133 concern the invalid currency input, 19 concern Japanese JPY symbol width and
nine concern Arabic locale strings. The [full result](../evidence/development/data-metrics-source/icu-comparison.json)
retains every failure. The existing Qt package bundles ICU 73.2; the prototype
uses the separate system ICU 74 library. That initial probe changed no product dependency or formatter. The Qt candidate
described below now uses system ICU74.2; complete parity remains unaccepted.

The inspected mechanisms are the pinned major/minor
[Qt 6.8 locale API](https://doc.qt.io/qt-6.8/qlocale.html),
[ICU number skeletons](https://unicode-org.github.io/icu/userguide/format_parse/numbers/skeletons.html)
and the [ICU 74.2 C API declarations](https://github.com/unicode-org/icu/blob/release-74-2/icu4c/source/i18n/unicode/unumberformatter.h).
The first ctypes probe used the wrong open-function signature and crashed; its
corrected standalone rerun and core cleanup record are preserved. No application
process, installed library or reference capture was changed by the probe.

## Reproduction and remaining gates

The archived helper remains outside the Linux tree. A clean extraction verifies
36 build inputs, recompiles the helper and reproduces all 3,160 output files byte
for byte, including the seven locale runs. The helper links the preserved
source-verified Sabella module/object. A later
[complete pinned source build and source-only archive replay](native-source-rebuild.md)
each reproduce all 3,160 files without preserved compiled Sabella inputs.
Public helper/full-source distribution remains pending. The original [provenance](../evidence/reference-investigations/data-metrics-20261015/tooling-provenance.json)
records the archive checksum, source revision, compiler, SDK, OS and dependencies.

Run `python3 scripts/verify-data-metrics-source.py` and the contract suite. Tests
reject false witness identity, shrunken fixed badges, changed currency precision,
merged locale ownership and substitution of the observed native mono face.

Full native font/symbol/locale/raster, numeric animation, broader composition,
physical sessions/input and actual readers remain pending. Qt candidate runtime
and package evidence are separate from these complete mirror gates.
Desktop source evidence does not close any TV target or playback gate.


## Qt interfaces and verification

```qml
BleeckerMetric { label: "Readers"; value: 12345.6789; format: "compact" }
BleeckerStatCard {
    label: "Readers"
    value: 12345.6789
    delta: 0.12
    maximumWidth: 320
    locale: Qt.locale("de_DE")
    icon: Component { MyChartIcon { color: parent.foregroundColor } }
}
BleeckerIconBadge { variant: "outlined"; size: "lg"; icon: myIcon }
BleeckerKbd { key: "Ctrl + K"; maximumWidth: 120 }
```

Metric `label`/`value`, stat-card `label`/`value`/`icon`, badge `icon` and key-label
`key` are required. Metric format defaults to `number`, currency to `USD`; badge
size defaults to `md` and variant to `primary`. Stat-card delta defaults to null;
zero remains present. Both metric/card and key-label `maximumWidth` use `-1` for
intrinsic layout. Their fitted presentation is exposed as `presentationItem`,
centered independently of an explicitly sized outer frame. Stat card retains
its fixed badge even when the row must overflow a narrow width proposal.

The icon slot's parent supplies `foregroundColor`, `pixelSize` and a medium font
context. Linux callers own the Component; the source's default SF chart lookup
has no implicit replacement. The gallery paths are original fixture artwork with
unaccepted native correspondence. The key label uses the platform's
`QFontDatabase::FixedFont` candidate. Its native mono geometry/glyphs remain
unaccepted; no Apple font is redistributed. Callers can set its normal Qt font
and palette. The owned default foreground uses the measured native-primary token.

`BleeckerNumberTools` uses the Qt process-default locale for metric formatting.
A Qt application locale-change event refreshes existing metric strings. Stat-card
deltas use the inherited Qt Control `locale`. The consumer proves that changing
only the delta locale leaves the metric's US currency string intact. The
invalid-currency path preserves the recorded raw Double description. Unknown
format strings and ICU construction/format errors fail visibly; there is no
alternate formatting engine or silent locale repair.

System ICU 74.2 is an explicit private dependency for number, currency, percent
and localized compact notation. The build selects its versioned libraries and
links a versioned-namespace probe before configuring successfully. Qt's bundled
ICU73 stays separate. The source-free consumer checks runtime availability
without ICU development headers. Static source captures disable animation;
numeric-transition frame equivalence remains unimplemented and unaccepted.

The separate [width-input dump](../evidence/reference-investigations/data-metrics-inputs-20261015/provenance.json)
executes the original archived fixture construction and records all 131 width
proposals. A clean helper rebuild verifies 35 inputs and reproduces that output.
It adds no rendering branch and changes none of the original 1,048 source PNGs.

[Forty additional numeric-text probes](../evidence/geometry/native-numeric-text.json)
compare plain/numeric-transition static Text bounds with CoreText line advances
at two DPRs and widths. Their independent clean replay verifies 35 inputs.
Untracked emergency breaks retain pair positioning from the full string;
ordinary final ink overhang does not enlarge the source view. Shared text sizing
now handles that boundary. Existing explicit tracking contracts remain distinct
and retain their prior source tests.

The full prior-candidate audit found twelve related corrections, retained in
[the source action record](../evidence/development/data-metrics/source-action-corrections.json).
Eight empty/error captures change label metadata; four PageHeader captures also
change pixels. Their wrapped `Create 0` label now measures 50 × 54 at both DPRs,
matching a separate 128-case native Text probe and its clean build/replay. The
PageHeader action now matches the sealed native 86 × 54 rectangle; the earlier
Linux candidate was 86.5 or 87 points wide. All twelve current action rectangles
match their existing source records. The audit retains 4,326 unchanged image and
complete-metadata pairs, all twelve differences, and the old/new captures.
Strict equality against those earlier candidates still fails for these cases;
this is source geometry evidence, with no baseline or pixel-tolerance approval.

Run `AvelinoCatalog --fixture data-metrics` and
`InstalledConsumer --data-metrics`. The gallery and installed consumer share the
same QML fixture. Normal Qt actions update caller-owned labels, values, formats,
delta presence and key text. Tests cover preserved objects/focused editing,
actual static-text interfaces, fixed badge dimensions, narrow and RTL layout,
source numeric geometry and all 190 US formatter witnesses. The separate strict
`--format-diagnostics PATH` comparison covers all seven process locales and
keeps remaining source string differences visible.

Installed delta-removal checks wait for the exact hidden-label and fitted-height
state, with a two-second bound. A traced Wayland/Mesa run showed the label hidden
at 20 ms while the card still had its old height; the expected height appeared
by 520 ms. The check retains the source height assertion and does not add
an application animation or delay.
