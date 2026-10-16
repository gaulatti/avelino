# Native number locale profile

The formatter now uses measured source locale symbols and compact patterns with
the existing private ICU 74.2 engine. The native data and numeric witnesses are
[preserved here](../evidence/reference-investigations/number-locales-20261016/investigation.json).
This changes strings produced by metrics and stat-card deltas. It does not accept
font rendering, images or complete locale parity outside the measured matrix.

The pinned source's Foundation runtime reports ICU 78.1 and CLDR 48. The Linux
engine has ICU 74.2 and CLDR 44.1. Direct resource reads identify these differences:

| Locale | Native data used by the adapter |
| --- | --- |
| `ja_JP`, JPY currency | U+00A5 `¥`, rather than U+FFE5 `￥` |
| `ar_EG`, NaN | `ليس رقمًا`, including U+00A0 and the final diacritic |
| `es_CL`, short compact | `0k M`, `00k M`, `000k M` for powers 10^9, 10^10, 10^11 |

ICU's `DecimalFormatSymbols` supplies the first two adjustments before formatting.
Currency precision, grouping, signs, digit conversion and rounding remain ICU
operations. The invalid-currency path still returns the source's raw Double
description, including nonfinite values and negative zero.

The stable formatter API has no custom compact-pattern input. The Chilean adapter
therefore uses the measured shared divisor and affix with ICU's normal compact
precision, `Precision::integer().withMinDigits(2)`. It preserves the original
Double until ICU performs scaling and half-even rounding. At the lower boundary,
the original formatter's rounded coefficient determines whether millions advance
to the billion pattern. At the upper boundary, a coefficient rounded to 1000
advances to the inherited trillion pattern. No formatted string is searched or
replaced, and there is no table of complete outputs.

For example, `999499999` remains `999 M`, `999500000` becomes `1k M`,
`999499000000` becomes `999k M`, and `999500000000` becomes `1 B`. Negative values
use the same magnitude rules while ICU retains their signs.

The source-free consumer's strict diagnostic contains 49,448 witnesses:

| Group | Scope | Witnesses |
| --- | --- | ---: |
| Original | Preserved component formatter probes in seven locales | 1,330 |
| Wide Double | 278 exact bit patterns, seven locales, ten format/currency combinations | 19,460 |
| Compact boundaries | 4,094 exact bit patterns in seven locales | 28,658 |

The wider set includes adjacent representable values, signed zero, subnormal and
largest finite values, infinities, NaNs, ties and deterministic random bit
patterns. The compact set adds decimal rounding boundaries and 500 deterministic
random samples around the affected magnitude range, each with both signs and
adjacent representable values. The consumer reconstructs bit-pattern inputs
without a decimal-text round trip and exercises the installed QML singleton.
Signed percentages use the actual signed-percent API argument.

The ARM64 source-free package run matches all 49,448 strings exactly. All eight
CTest targets pass (7,042 Qt checks), and all 119 contract tests pass on macOS
and Linux. Twenty installed consumer modes, 91 installed catalog captures and
eight focused X11/nested-Wayland/software/Mesa/scaled configurations pass. The
package container has neither Avelino library sources/build trees nor ICU
development headers; it uses the installed ICU 74 runtime.

All 1,048 preceding isolated data-display PNGs and full metadata records are
byte-identical, as are all 91 installed catalog pairs. Their earlier strict
native pixel failures remain failures. The scaled Weston virtual keyboard still
extends beyond its captured output; this OS presentation remains unaccepted.
The [candidate record](../evidence/development/number-locales/candidate.json)
keeps this verification separate from native visual and physical acceptance.

`scripts/generate-number-format-witnesses.py --check` verifies the embedded
projection against the sealed native sources. References CI also runs
`scripts/verify-number-locales-source.py`; Linux CI requires all 49,448 strings to
match and verifies each group's coverage. Any difference remains a strict failure.
Existing metrics react to producer and process-locale updates without replacing
their label objects.

The native oracle archive contains only helper source, original input manifests
and a replay script. A fresh extraction compiles both Foundation probes and reads
native locale resources again; all three raw outputs are byte-identical. Its
checksum and machine-local locator are in
[provenance](../evidence/reference-investigations/number-locales-20261016/tooling-provenance.json).
Independent-machine helper download remains pending. The archive and Swift source
stay outside the Linux repository.

Other locales, native resource versions, broader numeric inputs, glyphs, numeric
transitions, physical sessions and actual readers retain their separate gates.
The source pins, expected images, pixel tolerance and exception list are unchanged.
