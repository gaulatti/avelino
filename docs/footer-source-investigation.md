# Footer source measurements

The pinned Sabella footer distinguishes absent content from a present zero-size
child and a present empty text line. The [source investigation](../evidence/reference-investigations/footer-slots-20261019/investigation.json)
retains 15 slot cases across light/dark appearance, text scale 1/1.5, and DPR 1/2.
The 120 bare captures and 120 transparent measurement captures have identical
PNG bytes within every pair. The 24 overlapping empty-text, text, and block
captures reproduce the existing proposed references byte for byte.

All fixtures use a 300-unit footer centered in a 400 by 180 root. Measured cases
cover absent and conditional content, zero-size and hidden children, empty and
nonempty text, multiple direct children, flattened groups, and wrapping text.
The footer contributes a one-unit separator. Each present flattened child gets
20 units above and below and is horizontally centered. Consequently, absent
content has height 1, a zero-size child has height 41, and an empty text line has
height 55. Two fixed children of heights 20/30 produce height 131. The source
font remains Libre Franklin 12 in both recorded text-scale contexts.

The helper reuses a source-verified Sabella library object built from revision
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`. Its object, helper, resources,
commands, and captured files are checksummed in the retained provenance. This
run is not another independent library rebuild or clean replay. Capture tools
and Apple sources remain outside the Linux repository.

Run `python3 scripts/verify-footer-source.py` with the dependencies in
`tools/visual-requirements.txt`. The verifier checks the file inventory, pinned
revision/archive, complete context coverage, raw measurements and fonts, decoded
PNG dimensions, pair identity, and unchanged source overlaps.

This checkpoint records source behavior. It does not establish a Linux repair,
strict pixel parity, native window/input behavior, physical display behavior,
or screen-reader acceptance. Reference pins and expected captures are unchanged;
the footer remains verification-pending in the parity inventory.

The later ButtonGroup checkpoint changes seven shared catalog/consumer helpers.
The footer verifier binds those original helpers to immutable commit
`307f9ee8d31b8e5f7a6baba0e08f1aeb7abf9a58`; the footer implementation and
fixture still match their current bytes. The new package separately replays all
120 footer captures byte for byte, recorded in the
[ButtonGroup evidence](../evidence/development/button-group-layout-20261019/footer-replay/result.json).
