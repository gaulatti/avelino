# OTP input source contract

The pinned desktop `BleeckerOTPInput` now has a
[sealed native investigation](../evidence/reference-investigations/otp-20261016/investigation.json).
It preserves 328 public OTP images, 16 anchors, eight editor traces, nine state
binding traces, two input edge traces and native Unicode measurements. All 344
public images are byte-identical to a reconstruction of the source body. The
eight button anchors also match the existing RadioGroup anchors exactly. A fresh
source-only build of all 89 unchanged pinned files reproduces all 897 images and
metadata files byte for byte. The Linux component remains unimplemented; desktop
coverage remains 58/80 started and zero fully accepted.

`Sources/Sabella/Extended.swift:56` accepts a caller-owned string binding and a
length defaulting to six. It passes a repeated bullet placeholder, an explicit
system monospaced semibold font at size 20, centered alignment and the accessibility
label `Verification code` to `BleeckerTextField`. Its inner binding filters edited
characters with `Character.isNumber`, then takes a character prefix of the chosen
length. It does not validate or truncate the getter. Initial values can therefore
contain letters or exceed the requested length, including a nonempty value with
length zero. Changing the length does not truncate that getter.

With a 240-point offer the source body is 240 by 40. At custom text scale 1.5,
its minimum height becomes 60 while the explicit font remains 20. A parent font
at size 32 does not replace it. Offers below 28 points overflow to a 28-point
body, corresponding to the two 14-point horizontal pads. Without the explicit
width wrapper it fills the available 600-point canvas. The native text field
reports centered alignment, a scrolling single-line cell and clipping. Its base
font does not establish the actual fallback glyph runs or portable font assets.

The source windows are inactive, non-key borderless windows with actual backing
scale two. Requested environment/display scales one/two and explicit bitmap
sizes retain their original physical pixels. These are hosted source references;
they do not prove physical DPR-one behavior, normal application sessions, native
keyboard/IME operation or reader equivalence.

## Unicode transformation

A native scan covers all 1,112,064 valid Unicode scalars. Its 2,023 numeric values
exactly match [Unicode 17 Numeric_Type](https://www.unicode.org/Public/17.0.0/ucd/extracted/DerivedNumericType.txt).
This includes Han numerals, Roman numerals, fractions, superscripts and multiple
digit scripts. Attached combining marks, variation selectors, keycaps and joiners
can remain in the retained numeric character. Prefix length counts characters,
not UTF-16 units. No conversion to ASCII or normalization of scalar spelling is
performed by the measured transformation.

The native profile matches 758 of the 766 official Unicode 17 grapheme vectors.
Its eight differences concern Myanmar, Balinese and Khmer conjuncts; their
filtered results are empty. Those measured differences remain in the data.
Numeric classification and general character segmentation must not be treated as
one interchangeable version label.

Original Qt 6.8.3 diagnostics remain separate. `QChar::isNumber` misses 112 native
number scalars. `QTextBoundaryFinder` matches only 636 of the 766 native boundary
vectors and 13,780 of 17,801 numeric/mark boundaries. Supplying the native numeric
table alone still matches only 13,782 of those mark-filter results. The selected
204 ordinary examples all pass that variant, illustrating why those examples
alone are insufficient.

A specialized numeric transformation can use the pinned numeric, joining and
prepend properties directly. All 2,023 numeric scalars have grapheme class
`Other`; neither they nor the joining scalars overlap extended pictographs or
Indic consonants. Retained numeric characters therefore consist of their numeric
start and attached Extend/SpacingMark/ZWJ scalars. A preceding Prepend scalar
prevents that numeric start from being the first scalar of its character.
The source first-scalar numeric rule is also visible in the
[Swift standard-library implementation](https://github.com/swiftlang/swift/blob/main/stdlib/public/core/CharacterProperties.swift);
the measured runtime is authoritative for this investigation.

Native checks cover every numeric start against every joining scalar, every
numeric start against every Prepend scalar, and seven numeric starts against
every valid following scalar: 13,137,306 cases with zero differences, including
exact scalar spelling and the first-character prefix. The independent C++
projection also matches all 204 examples, 17,801 mark contexts and 766 filtered
vector outcomes. These are transformation/prototype checks; no QML component,
public Linux editing behavior or complete parity gate is accepted by them.

## Editing and caller state

Rendered snapshots distinguish the editor from the caller's model. Inserting
`a1b٢Ⅳ1́2` leaves that raw text visible while the model contains `1٢Ⅳ1́2`.
The recorded Return/blur paths replace the display with the getter's value.
The isolated single-field Return command leaves an editor active with selected
getter text; it does not establish traversal in a complete application.

This split occurs with the catalog's projected `@State` binding and with custom
functional bindings. The latter retain repeated setter calls around focus,
editing, Return and blur. Focusing an unfiltered `A12` value can itself request
and display `12`. After rejected or unchanged filtered writes, an external model
update can remain unreflected in the editor until another configuration update.
The zero-length projected-state trace exhibits that behavior too. The complete
sequences and snapshots remain preserved; a simple text-to-model binding does
not prove their equivalence.

The real native editor accepts a 40,001-character insertion ending in `1` and
produces model code `1`; its raw text stays visible until commit. Applying Qt's
default text limit, an editor length equal to the code length, or a validator
that refuses nonnumeric editing text would change these observed results.
Marked text retains the old model until it is unmarked, then commits the numeric
Han characters. These operations use the actual AppKit field editor rather than
physical keyboard or input-method services.

The pinned source declares `Verification code` as its SwiftUI accessibility
label. Direct underlying AppKit field-label queries return nil in these hosts;
they do not establish the SwiftUI proxy tree or actual reader output. Native
keyboard/IME, reader, complete session, font and Linux visual gates remain open.

Run `python3 scripts/verify-otp-source.py` to audit coverage, immutable bytes,
source-only replay, primitive results, observed editor/model separation and the
original Qt failures. Negative contracts prevent replacing those diagnostics or
claiming Linux parity. The checksummed native source/helpers remain in the
external reference vault; independent-machine availability remains pending.
