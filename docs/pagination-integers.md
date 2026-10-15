# Exact pagination integers

The pinned pagination source accepts Swift `Int` values. On the selected 64-bit
source and Linux targets that means the full signed range
`-9223372036854775808...9223372036854775807`. Qt's QML `int` is narrower, and Qt
6.8.3 converts native 64-bit values to JavaScript doubles. The previous control
therefore could not preserve the source contract at large values.

The observable criteria are exact labels and page requests across the 32-bit,
JavaScript safe-integer and signed 64-bit boundaries; disabled extreme endpoints
without overflow; caller-owned updates after pointer, keyboard and accessibility
actions; negative/zero counts and out-of-range pages; locale grouping; narrow/RTL
layout; invalid-input refusal; and independent installed consumption. Complete
visual, source keyboard/focus, physical input and reader acceptance remain open.

```qml
BleeckerPagination {
    page: model.page                 // a decimal string for large values
    pageCount: "9223372036854775807"
    locale: Qt.locale("en_US")
    onPageRequested: page => model.page = page
}
```

`page` and `pageCount` accept canonical decimal strings over the complete source
range. Ordinary JavaScript numbers are accepted only when finite, integral and
within `±9007199254740991`. A C++ producer crossing the QML boundary should supply
large values as `QString::number(value)`, because QML would otherwise convert a
native integer to a double before the helper could inspect it. Strings use ASCII
digits, an optional minus for negative values, and no whitespace, leading zeros,
plus sign, decimal point or grouping. Invalid or unsafe inputs fail startup
explicitly; they are never rounded, clamped or silently converted to zero.

C++ parses and validates the inputs, computes enabled states and requests, and
formats the label with the control's actual `QLocale`. Arithmetic only executes
for enabled actions: Previous has `page>1`, so subtraction cannot underflow;
Next has `page<pageCount<=Int.max`, so addition cannot overflow. The source's
boundary behavior remains unchanged, including negative pages and counts.

This changes the QML signal signature from `pageRequested(int)` to
`pageRequested(string)`. Requests always carry canonical decimal strings,
including ordinary values such as `"5"`. QML handlers assigning to a small `int`
model continue to convert normally; full-range models must retain strings.
C++ connections to the old integer signature must use the string signature and
parse only at their own native boundary. There is one request signal, and the
caller still decides whether to apply it. The component never mutates its bound
page or count.

The new gallery is `--fixture pagination-integers`; the independent consumer uses
`--pagination-integers`. Source fixtures encode page/count as decimal strings in
their fixture definitions and record exact post-action values as strings, avoiding
JSON/JavaScript numeric precision loss. New native evidence is supplemental;
accepted references and existing expected images remain unchanged.

The [native source proposal](../evidence/reference-proposals/pagination-integers-20261014/proposal.json)
contains 176 exact-pagination cases and eight anchors. All 185 output files
replayed byte-for-byte. The [Linux evidence](../evidence/development/pagination-integers/candidate.json)
records 184/184 matching root bounds, 168/176 matching pagination bodies and 0/184 exact images. Canonical post-action page/count/request values and callback
counts match in every case. This closes the previous source integer-domain gap;
strict artwork/rasterization and the remaining physical/source-input gates stay open.

All 3,072 Qt checks, 59 contract tests, eight invalid-pagination and
three invalid-slider startup refusals pass. Twelve installed offscreen modes,
96 package-only virtual-session pairs and 59 installed-catalog captures pass.
All 2,594 preceding PNG/full metadata pairs are unchanged. Default/Basic/Fusion
gallery PNGs match. No source pin, accepted capture, tolerance or exception changed;
coverage remains 42/80 desktop APIs started, with none fully accepted.

The eight remaining body-size mismatches are all narrow cases: Linux is three
logical pixels narrower, while the 45-pixel body height matches. This remains an
open layout/typography difference and is not an accepted exception.

The subsequent [shared wrapping repair](wrapping.md) closes the eight narrow
body-width differences above using measured trailing-whitespace and ink extents.
All 176 pagination body comparisons now match. Exact appearance and the remaining
source-input/physical/reader gates stay pending; the integer/string contract is
unchanged.
