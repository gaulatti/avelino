# Source text wrapping

The observable criteria are that offered widths preserve source text width,
line count/height and first baseline, including partially fitting trailing
whitespace, explicit lines, ordinary words and long numeric labels. Pagination's
narrow full-range label must occupy the measured source body width and height,
with subsequent caller updates and installed-package behavior preserved.

The pinned source text/font expressions are measured separately from component
appearance. No accepted capture, source revision, tolerance or exception changes.
The shared label implementation, all existing isolated comparisons, catalog
fixtures and independent installed consumer must be checked together. Exact
rasterization, physical displays/input and screen readers remain separate gates.

The source matrix uses primary regular 12-unit text, five strings (full-range and
ordinary pagination, normal words, an explicit trailing space and explicit line
breaks), twelve offered widths and DPR 1/2. It records actual inner Text bounds,
not the external frame. All 121 output files replay byte-for-byte from clean
extraction and helper recompilation against preserved pinned source objects.
The [measured data](../evidence/geometry/native-wrapping.json) records provenance,
input hashes, every image hash and the external replay artifact. This is not a
fresh full source compilation. Other font/script/layout contexts retain their
separate acceptance obligations.

At 156 offered pixels the full-range label is 156 pixels wide at DPR 1 and 155.5
at DPR 2, with a 45-pixel height. Its HStack body is 260 or 259.5 pixels wide.
At an offered width of 32, comma ink overhang expands the longest line from its
30-unit rounded advance to a 31-unit box. Both defects are handled in shared text
metrics while pure `glyphAdvance` remains separately inspectable.

The [candidate evidence](../evidence/development/text-wrapping/candidate.json)
verifies 3,198 Qt checks, 59 contracts, eight pagination and three slider invalid-startup cases, twelve installed offscreen modes, 96 package-only virtual-session pairs and 59 installed-catalog captures. All eight full-integer narrow source body comparisons now
match: 176/176 pagination bodies, compared with 168/176 before this repair.
The 120 direct source Text cases pass at their matching DPRs.

Every one of the 2,782 prior PNG/full metadata pairs was recaptured and audited:
2,770 pairs remain byte-identical. The
[case-by-case audit](../evidence/development/text-wrapping/before-after.json)
records 0 gained root-bound matches, zero lost root/exact matches or measured pagination-body matches, 8 cases with fewer changed pixels
and 0 with more. Changed pairs retain fresh strict raw
diagnostics; byte-identical pairs retain checksummed canonical files and earlier
pixel statistics, linked to current capture/environment records. Sixteen historical report gaps were also checked with fresh strict diagnostics.
The catalog's Basic/Fusion/default gallery images match. Source artwork/rasterization, broader
font/script/layout contexts, physical input/display and actual readers remain open.
No source pin, accepted image, tolerance or exception changed. Coverage stays
42/80 desktop APIs started, with none accepted.

The installed resize check now awaits the exact expected row width/height rather
than assuming that 20 ms elapsed means layout finished. Qt 6.8.3
[positioners synchronize layout with painting](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quick/items/qquickpositioners.cpp#L123).
A one-second failure bound retains exact numeric comparisons and reports actual
dimensions on failure. An isolated Wayland/OpenGL profile passed after an earlier
full-matrix failure, consistent with frame scheduling; the complete installed
matrix is required again after this harness change. No control geometry or
comparison tolerance is changed.

The [alert investigation](alert.md) adds 96 secondary-font prose cases: regular
and semibold, 13/18 units, two strings, six widths and DPR 1/2. Both the measured
Text bounds and line probes match untouched source PNGs exactly in every case;
the clean replay is part of its 722-file source witness. A final token of up to ten measured ASCII characters in the two-line examples
stays with the preceding word when both fit. Explicit 10/11-character controls
include narrow repeated letters and short numeric tokens. Longer tokens,
three-line paragraphs and full-range numeric labels are negative controls. The label renderer performs a shaping-preserving preliminary layout,
then shortens only the affected penultimate line through Qt's public line API.
Existing explicit paragraph boundaries, elision and pure glyph advance are
preserved. This is measured Latin behavior, with broader scripts/contexts still
unaccepted. All preceding component images and geometry must be audited after
this shared change; a passing new helper case is insufficient.

The [supplemental boundaries](../evidence/geometry/native-prose-boundaries.json)
provide 84 further trusted cases from a 179-file clean replay. One native-hosted
primary18 TextRenderer image changes under instrumentation and is excluded;
its raw diagnostic is retained. The initial broader rule worsened four actual
loading-overlay images. The corrected full run must independently rerun the
entire old-image and package/session matrix before a checkpoint. Physical/native
keyboard and broader Unicode grapheme handling remain separate gates.
