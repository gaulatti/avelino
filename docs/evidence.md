# Implementation evidence

This is a checkpoint record, not desktop or TV acceptance.

| Gate | Evidence | Result |
| --- | --- | --- |
| Immutable source inputs | `scripts/verify-references.py`, reference CI | Both exact archives verify in clean extraction directories; source hashes and dependency locks match |
| Discovery / asset provenance | `reference/api-discovery.json`, `assets/provenance.json` | Starting registries reconciled with public modifiers/native adapters; all 18 bundled font files verify |
| Actual SwiftUI source capture | [capture run](https://github.com/gaulatti/avelino/actions/runs/38195797603), `reference/captures/desktop/buttons/` | 112 button cases captured on macOS 27.0.1 / Xcode 27 / Swift 6.4, DPR 2 |
| Font resolution | Each preserved capture's `resolvedFont` | Actual inherited label resolves EncodeSans-Md; Qt resolves Encode Sans Medium. No font substitution approved |
| Build / interaction / packaging | [Linux run](https://github.com/gaulatti/avelino/actions/runs/38198601179) | x86_64 and ARM64 build, pointer/keyboard/editing tests, and independent consumer pass; second consumer has no product source/build trees |
| Initial visual comparison | [comparison CI](https://github.com/gaulatti/avelino/actions/runs/38199378037), `evidence/checkpoints/68a5dfb/` | 0/112 source cases pass on each architecture. Raw candidate pixels match across architectures; button edges and glyphs still differ from Sabella. Cases remain verification-pending |
| Wayland / X11 / accessibility / scaling matrix | [display-session CI](https://github.com/gaulatti/avelino/actions/runs/38199094278), `scripts/check-display-sessions.sh`, package-only consumer | Eight virtual-session configurations pass on x86_64 and ARM64 using software and OpenGL/llvmpipe; full parity, accessibility, input delivery and overlay gates remain pending |
| Desktop acceptance | `docs/parity-inventory.json` | Pending; required visual, behavior, and runtime cases remain open per component |
| Television / hardware | User target TBD | Pending; no physical remote or sustained playback verification |

Font-probe instrumentation changed zero rendered pixels across all 112 source
cases compared with the earlier capture tool. Reference PNGs and hashes are now
preserved in Git. Capture jobs write candidates into `artifacts/`; they never
replace these files. Future source/capture baseline changes require explicit
reviewed updates. There are zero approved visual exceptions.

The first measured Linux button used an unnecessary integer width ceiling and
center snapping. Removing those preserves fractional font/layout measurements;
the resulting captures still need to pass geometry and glyph comparisons. This
change does not create a tolerance or accept the remaining differences.

The 14 px medium label's native font metrics have a 17.5 px line height. Keeping
that fractional height and disabling center snapping avoids an extra half-pixel
baseline shift at DPR 2. Font family, face, size, and weight remain the reference
values. Raw glyph and rounded-edge differences remain open after this correction.

The source-comparison job now reports raw button differences separately from the
build/runtime/package jobs. Its strict failure remains visible while mirroring
continues. Nineteen contract tests check immutable extraction, Linux-only source
storage, ignore rules, forced additions, archive contents, and comparison failures,
including RGB changes with unchanged alpha, alpha-only changes, changed expected
checksums, incompatible text/DPR scales, missing captures, and unreviewed ICC data.

The `68a5dfb` checkpoint preserves both comparison reports, x86_64 environment
metadata, and the medium primary-button candidate with checksums. It links the
full CI candidate/runtime artifacts. The medium primary case differs in 936 pixels,
with maximum channel error 211; alpha matches. No source image changed, no
exception was approved, and no component was marked complete.

The continuous-corner implementation adds supplemental native contour measurements
in `evidence/geometry/native-rounded-rectangle.json`. The probe runs outside the
Linux repository and records its checksum, OS, SDK, and compiler. Its macOS 27.0
diagnostic does not replace the macOS 27.0.1 source images. Sixteen geometry cases
compare all fill and inset-border control points, with at most one Float32 rounding
unit of difference; the screenshot comparator still allows zero changed pixels.
Qt Quick tests now report 26 passing cases including this contour coverage.

The first local software-rendered contour candidates still fail all 112 image
comparisons. Relative to the previous preserved candidates, total absolute RGB
error fell from 17,682,799 to 16,488,999, while changed-pixel counts improved in
17 cases, stayed equal in 36, and increased in 59. The light medium primary case
changed from 936 to 1,001 differing pixels. This mixed result is diagnostic evidence,
not visual acceptance. A native text-rendering/no-hinting probe changed zero pixels
in eight light/dark primary cases, so those experimental settings were removed.

The clean `75cb37a` CI checkpoint reproduces these metrics on x86_64 and ARM64.
`evidence/checkpoints/75cb37a/` preserves both strict reports, the medium primary
candidate and metadata, source/compiler environment, and per-case change metrics
with checksums. It also retains all eight x86_64 session metadata records and two
representative whole-output/window capture pairs; the linked runtime artifact
contains the remaining captures. All 112 candidate images match across architectures. Both
build/runtime/package jobs pass; both visual comparison jobs fail. The package
regeneration check seeds obsolete consumer/install files and proves their removal.
The eight installed-session configurations confirm software Shape rendering and
RHI curve rendering at the expected logical radius; full desktop, accessibility,
overlay, and television acceptance remain pending.
[Checkpoint CI](https://github.com/gaulatti/avelino/actions/runs/38263908908)

The next local button candidate aligns painted background origins and label
baselines to physical pixels, rounds label line boxes at the effective DPR, and
positions default content explicitly. This fixes a positioner/anchor interaction
that displaced short link labels. Thirty-seven Qt checks pass at each of DPR 1
and 2, including movement, transformed ancestors, displayed-window reparenting,
all four link sizes, and pointer activation. The fresh installed package also
passes its eight virtual X11/Wayland software/OpenGL configurations, including
painted-coordinate checks after loading changes the composition.

Against the preserved `75cb37a` candidates, this local 112-case matrix lowers
absolute RGB error from 16,488,999 to 12,672,387. Changed-pixel counts improve in
105 cases, stay equal in two, and increase in five. Color error improves in 108
cases and increases in four: small link buttons in both themes, enabled and disabled.
The light medium primary case falls from 1,001 to 863 changed pixels, with maximum
channel error 168. These are dirty-tree development measurements, awaiting clean
CI reproduction and a checksummed checkpoint. All 112 strict comparisons still
fail. Expected captures, fonts, and zero-pixel tolerance remain unchanged; no
visual, accessibility, overlay, desktop, or TV acceptance is implied.

The clean `efb2a90` CI run reproduces the local metrics on x86_64 and ARM64.
Both build/runtime/package jobs pass, and both strict image comparisons fail.
All 112 candidate PNGs match across architectures. The checksummed
`evidence/checkpoints/efb2a90/` preserves the complete candidate matrix and metadata,
both comparison reports, the compiler/dependency/source environment, per-case
changes from `75cb37a`, and all eight x86_64 whole-output/window capture pairs
with their capture-tool and compositor records. These files remain available
independently of CI artifact retention. The reference verifier checks complete
candidate coverage and painted coordinates as well as hashes. Replay the strict
comparison against this candidate directory with an output under `artifacts/`;
exit status 1 is the preserved failed result.
[Clean CI](https://github.com/gaulatti/avelino/actions/runs/38273039988)

The fractional-typography candidate preserves a 19.5 px requested button font
instead of rounding it to 20 px. Fifty-seven Qt checks pass at each of DPR 1 and
2. The default 14 px label's advance becomes 46.487 logical pixels. Its first
dirty-tree comparison has mixed results: total absolute RGB error increases
from 12,672,387 to 12,731,331; 42 cases improve, four stay equal, and 66 worsen.
The light medium primary case decreases from 863 to 859 changed pixels. All
112 strict comparisons still fail. The new painted text path also exposes
opacity-composition differences in disabled text. Clean CI reproduction and
preserved candidate evidence are still required. Source images and tolerance
remain unchanged, and no component or exception is accepted.

Desktop implementation now proceeds in small component-family batches alongside
these pending comparisons. Shared typography and asset issues remain attached
to every affected fixture; broader implementation does not close their gates.

The next batch adds separator, skeleton, Bauhaus background, determinate progress,
button group, header, and panel-layout candidates. The new contracts exposed and
corrected invalid CSS alpha-color strings at the Qt token boundary. This preserves
the pinned neutral token values while making border/input colors usable by Qt.
The component suite passes 97 checks at each of DPR 1 and 2. A fresh package-only
container passes independent consumption and all eight virtual X11/Wayland
configurations, including grouped keyboard activation/tab order and return to
editing. Four light/dark, DPR 1/2 gallery captures were inspected. Native image
comparisons for the seven new components remain missing. The inventory
continues to report zero accepted components and zero approved exceptions.

The clean typography checkpoint also passes both architecture build/runtime/package
jobs and reference CI; all 112 visual comparisons fail on each architecture. Its
painted text path produces different raw pixels between x86_64 and ARM64, so the
earlier checkpoints' cross-architecture identity does not carry forward. No
architecture difference is accepted or hidden by a tolerance.
[Typography CI](https://github.com/gaulatti/avelino/actions/runs/38280257407)

The foundations checkpoint passes both architecture build/runtime/package jobs
and reference CI. Both strict visual jobs fail. These outcomes are independent;
the green runtime jobs do not imply desktop acceptance.
[Foundations CI](https://github.com/gaulatti/avelino/actions/runs/38282966451)

The cards-and-badges batch adds six more desktop candidates, bringing started
entries to 16 of the 80 discovered APIs (20% coverage, zero accepted entries).
The local suite passes 157 checks at each of DPR 1 and 2. A fresh package-only
container passes all eight virtual X11/nested-Wayland software/OpenGL configurations,
including pointer/keyboard actions and editing inside a card. Four light/dark
DPR 1/2 gallery captures and the installed OpenGL window were inspected. This
is local development evidence; clean CI is separate. Native images for these
six entries remain missing. Software rounded content clipping is unfinished;
GPU clipping, shadow calibration, typography, wrapping, accessibility and complete
scaling/session acceptance remain pending. No baseline, tolerance or approved
exception changed. See [the candidate contract](cards-and-badges.md).

The clean cards-and-badges checkpoint passes both architecture build/runtime/package
jobs and reference CI. Both strict visual jobs still fail. Its downloadable artifacts
are also recovered locally under `artifacts/ci-333ddcd/`; preserving that evidence
independently of artifact retention remains outstanding.
[Cards and badges CI](https://github.com/gaulatti/avelino/actions/runs/38287570519)

The data-display batch adds avatar, ordered lazy data list, timeline item and the
surface modifier candidates: 20 of 80 discovered desktop entries are started
(25% coverage), with zero accepted. It adds grapheme-aware initials, centered image
cover cropping, inherited timeline typography, explicit constrained title wrapping,
and corrects extra DPR scaling in Canvas images and shared shadows. The local suite
passes 186 checks at each of DPR 1 and 2. A fresh package-only container passes all
eight virtual X11/nested-Wayland configurations, including pointer and keyboard
list actions, tab order and return to field editing. The light DPR 1 and dark DPR 2
galleries and installed Wayland/OpenGL DPR 2 window were inspected.

These checks are candidate behavior evidence. Native images for the four new entries,
font fallback/emoji assets, complete wrapping/bidi, model adapters, scrolling,
accessibility, shadow calibration and rounded clipping acceptance remain pending.
The software rounded-content gap is still visible in its fixture. No expected image,
visual tolerance, reference source or approved exception changed.
See [the data-display contract](data-display.md).

The clean data-display checkpoint passes both architecture build/runtime/package
jobs and reference CI. Both strict button comparisons fail.
[Data-display CI](https://github.com/gaulatti/avelino/actions/runs/38290063185)

The form-control batch adds field composition, multiline editing, switch style,
toggle style and segmented selection candidates. Twenty-five of 80 desktop APIs
have started (31.25% coverage); zero have passed the full mirror gate. The local
suite passes 220 checks at each of DPR 1 and 2, retaining the earlier action tests
alongside the new form-control tests. Fresh installed consumption passes both
fixtures and all sixteen window/full-output pairs across eight virtual X11 and
nested-Wayland software/OpenGL/scaling configurations. Input remains synthetic.

Rendered inspection exposed the existing text field's missing software background
and placeholder, and a switch label wrapping at its exact intrinsic width. These
are corrected and covered by rendered composition, pointer-focus, intrinsic-width
and narrower-width tests. The new multiline fixture exercises its owned scrollbar.
The local source-input hashes, toolchain record, checksummed gallery and complete
session captures are preserved in [the development candidate](../evidence/development/form-controls/candidate.json).
Its environment explicitly records an uncommitted tree based on `ec309ff`; clean
CI verification is separate. New native comparisons, context menus, accessibility,
complete component cases and physical/hardware verification remain pending.
No reference image, comparison tolerance or approved exception changed.
See [the form-control contract](form-controls.md).

The clean form-controls checkpoint passes both architecture build/runtime/package
jobs and reference CI; both strict button comparisons fail.
[Form-controls CI](https://github.com/gaulatti/avelino/actions/runs/38295058885)

The next checkpoint preserves a [supplemental native reference proposal](reference-proposal-20261012.md):
764 candidate images from 104 isolated fixture definitions, covering all 25 started
desktop APIs plus monospace probes. Sixty-eight captures include actual AppKit
descendants through an isolated hosting-window cache; the rest use ImageRenderer.
Both methods remain separate from compositor, overlay and physical-session gates.
The proposal records matched display/raster DPR, actual native editor fonts,
source system-font resolution, component dimensions and color-profile conversion.
Its capture tool/source bundle is checksummed and verified outside Avelino.
The original source artifacts and 112 expected images are unchanged.

Native fixture preparation found the missing `outlined` card variant. The Linux
candidate now supplies the source's card fill and border with no shadow. Forty
card theme/padding/variant contracts pass; the total Qt suite passes 228 checks at
each DPR (456 total). Fresh installed consumption and the sixteen virtual-session
window/full-output pairs pass locally. The outlined gallery is visible within its
expanded logical height. These checks do not close native comparison or full
variant/runtime acceptance. Two font differences have specific proposed exceptions;
none is approved. Twenty-three contract tests include proposal integrity,
self-approval rejection, false DPR rejection and discovered variant reconciliation.

The reference-proposal checkpoint passes both architecture build/runtime/package
jobs and reference CI. Both strict button comparisons still fail.
[Reference proposal CI](https://github.com/gaulatti/avelino/actions/runs/38301755792)

The next [isolated-fixture candidate](isolated-desktop-comparisons.md) preserves
724 Linux captures across all 25 started APIs and their proposed native counterparts.
Forty cases match pixels and component geometry exactly; 684 fail. None closes
component acceptance or approves the proposed baseline. All captures finish without
binding loops or JavaScript runtime errors. The first matrix reveals the panel's
intrinsic-width collapse and the timeline fixture's missing vertical allocation.
The capture inputs, raw images/label metadata and complete comparison reports are
checksummed in [the candidate manifest](../evidence/development/isolated-desktop/candidate.json).
Twenty-seven contract tests cover geometry rejection, case parameters and proposal
status alongside the existing reference and repository boundary tests.

The [panel sizing repair](../evidence/development/panel-sizing/candidate.json)
preserves a second full 724-case matrix and fresh installed-session evidence.
All 24 panel geometries now match the source, including the distinct 14-unit
present-empty title. The non-final timeline fixture now fills the same offered
height. Total geometry matches rise from 482 to 514; exact image/geometry matches
remain 40. These results close neither baseline approval nor component acceptance.
The expanded Qt suite passes 240 checks at each DPR (480 total), and sixteen
installed-consumer window/full-output pairs pass across eight virtual configurations.
Input remains synthetic and accessibility/overlays/physical hardware remain pending.
Both architecture CI jobs will now produce isolated API captures, with independent
strict proposal-diagnostic jobs retaining raw differences and unapproved status.

The [desktop composition candidate](../evidence/development/composition/candidate.json)
adds seven APIs, raising started coverage to 32 of 80 (40%); none are accepted.
It preserves four catalog captures, 498 passing Qt checks and twenty-four
installed-package window/full-output pairs. Adaptive tiles retain fractional
logical widths and their focused delegate across column changes. The virtual
outputs are enlarged so the complete DPR 2 composition client fits. Exact runtime
harness source and its hash are separate from the retained pre-enlargement build
provenance. Native composition fixtures, full comparisons, large-grid virtualization,
physical input/display and screen-reader acceptance remain pending. The existing
25-API matrix still has 514 geometry matches and 40 exact matches of 724 cases.
Fresh raw diagnostics are local; prior full comparison evidence remains committed.
No reference, tolerance or approved exception changed. See [the contract](composition.md).

The [composition sizing repair](../evidence/development/composition-repair/candidate.json)
preserves 256 fresh isolated captures and their strict comparison: 240 geometry
matches and 60 exact image-and-geometry matches, compared with 184 and 60 before
the repair. Section headers, dashboard sections and feeds now match all proposed
dimensions; progress capsules follow their segment extent and clear when empty.
The button anchor, empty footer and remaining pixel differences stay open.
The fresh original 724-case PNG matrix matches the prior panel-sizing evidence
byte for byte. Linux build, 498 Qt checks and all 24 package-only virtual-session
window/full-output checks pass. Input remains synthetic; source approval, complete
cases, physical display/input, accessibility and TV hardware acceptance remain
pending. Both reference groups now have separate x64 and ARM CI comparisons.

The [selector candidate](../evidence/development/selection/candidate.json) adds
`BleeckerSelect`, raising started desktop coverage to 33 of 80; none are accepted.
Its source-inspired button/popover has caller-owned values, disabled options,
ordered keyboard movement, explicit dismissal/focus behavior and a bounded
scrolling viewport. The preserved evidence includes 512 passing Qt checks,
four gallery images and 32 package-only window/full-output pairs, eight with the
selected row, disabled row and scrollbar visible in the open selector.
Basic/Fusion/default-style images are identical. All 724 original desktop and
256 composition PNGs and comparison metadata remain unchanged. Native selector
captures, OS popover presentation, original-symbol equivalence, complete cases,
RTL, edge placement, physical input and screen-reader acceptance remain pending.

The [native-derived selector repair](../evidence/development/selection-native/candidate.json)
corrects popup direction/centering, its independent width and viewport/chrome
allocation, initial list position, disabled-row opacity and single-line newline
truncation. All 72 selector geometries and eight popup positions/sizes match the
80-case proposed source matrix; exact comparisons remain zero and anchor widths
still differ. The source replay reproduces its PNG parts and metadata after clean
extraction and helper recompilation against preserved reference objects. Source
glass/shadow compositor output is missing, so no OS presentation is accepted.
The repair passes 516 Qt checks, 32 contract checks and 32 package-only virtual
session checks; all 980 prior regression PNGs and component dimensions remain
unchanged. No expected source baseline, tolerance or exception has changed.

## Checkbox candidate

The [checkbox checkpoint](../evidence/development/checkbox/candidate.json) adds
`BleeckerCheckbox`, raising started desktop coverage to 34 of 80; none are accepted.
Its 128 checkbox source cases plus eight button anchors replay byte for byte from
clean external extraction and helper recompilation against preserved source objects.
The native tools/source remain outside the tracked Linux tree.

All 574 Qt checks, 34 contract checks and 40 installed-package virtual-session
checks pass. Eight of those session pairs exercise caller state, pointer/keyboard
activation, disabled input, focus traversal, wrapping and a real Qt accessibility
role/name/checked-state query. Default, Basic and Fusion galleries are byte-identical.
All 1,060 earlier regression PNGs and their component dimensions remain unchanged.

Strict checkbox comparisons match 88/128 geometries and 0/128 exact images.
Scaled font sizing/height, wrapped-line spacing, symbol equivalence, complete
focus/hover/RTL behavior and physical/screen-reader acceptance remain pending.
The explicit Qt accessibility role and source regular font weight correct template
and host-inheritance omissions; they do not close platform acceptance.

For the preceding selector repair `67e9262`, the
[References workflow](https://github.com/gaulatti/avelino/actions/runs/38492804316)
passed. The [Linux workflow](https://github.com/gaulatti/avelino/actions/runs/38492804344)
passed build/runtime/package jobs on both architectures; strict visual comparison
jobs failed. This is separate from the checkbox's local evidence and future CI.

## Measured typography candidate

The [typography repair](../evidence/development/typography-repair/candidate.json) follows 2,160 pinned native font/Text probes and
eight existing eyebrow cases. Source font resolution, independently rounded line
metrics, physical-pixel intrinsic widths and final tracking are carried through
the shared renderer, public components, catalog metadata and installed package.
Exact logical metrics avoid the design-unit round trip that produced
15.999999999999998 for a 16-unit line.

| Matrix | Geometry matches | Exact image and geometry matches |
| --- | --- | --- |
| Desktop proposal | 702/724 | 40/724 |
| Composition proposal | 248/256 | 60/256 |
| Selector proposal, including anchors | 80/80 | 0/80 |
| Checkbox proposal, including anchors | 136/136 | 0/136 |

All 2,748 Qt checks, 34 contract checks, five offscreen installed modes and
40 fresh package-only virtual-session pairs pass. Source/build trees are absent
from the package-only container; it is read-only apart from temporary build and
evidence mounts. Sessions distinguish X11/nested Wayland, software/Mesa OpenGL,
standard/scaled text and display, synthetic input/focus and real Qt interface
queries. They do not establish physical or screen-reader acceptance.

No geometry or exact-image pass is lost in the four proposal matrices. The
[audit](../evidence/development/typography-repair/before-after.json) preserves all
raw pixel regressions (22 cases have higher changed-pixel counts). Original
buttons remain 0/112 exact. Started coverage stays 34/80 desktop entries with zero
complete acceptance; television remains separate and pending. Expected images,
reference pins, tolerances and approved exceptions are unchanged. Relevant
in-repository docs and the parity inventory are updated; the public wiki remote
is unavailable. This native library change has no application-backend or metrics
endpoint impact.

For the preceding checkbox checkpoint `39867a5`, the
[References workflow](https://github.com/gaulatti/avelino/actions/runs/38496406343)
passed. Its [Linux workflow](https://github.com/gaulatti/avelino/actions/runs/38496406419)
passed both architecture build/runtime/package jobs and failed the strict visual
jobs. Those results are separate from this candidate's local checks and its CI.

## Secure-field candidate

The [secure-field checkpoint](../evidence/development/secure-field/candidate.json)
adds masked editing and the visibility action through a Qt TextField template,
owned eye/slash candidates and the shared surface. Started desktop coverage is
35/80; none are accepted. The 40 secure-field native cases plus eight button anchors
have 48 matching root component bounds and zero exact images. Native editor state,
font and caller-value preservation are recorded; declared colors and cached ink
still differ. Source images remain proposed, with native DPR 1/compositor and
complete behavior/focus/glyph/input-method/RTL/physical/screen-reader gates pending.

All 2,784 Qt checks, 37 contract checks, six installed offscreen modes and 48 fresh
package-only virtual-session pairs pass. Eight pairs cover secure editing,
reveal/hide, disabled input, clipboard, traversal and actual Qt password/value/action
interfaces. The reveal action uses an explicit Button role. Its candidate glyph
provenance is installed with the library and verified against the source record.
Default, Basic and Fusion secure-field gallery PNGs are byte-identical.

All 1,338 prior PNGs and full metadata are unchanged; the current capture drivers,
source inputs and per-file hashes are retained with links to preceding raw evidence.
Clean native helper replay reproduces all 40 secure-field PNGs and the manifest;
one scaled DPR 1 button anchor varies by three pixels at channel level one. Its
raw alternate and differences remain preserved without a new tolerance or reference
adoption. Documentation and inventory are updated in-repository because the public
wiki remote is unavailable. No application backend, metrics endpoint, configuration
or TV behavior changes.

For typography `b31551b`, [References CI](https://github.com/gaulatti/avelino/actions/runs/38638734160)
passed and [Linux CI](https://github.com/gaulatti/avelino/actions/runs/38638734175)
passed both x64/ARM64 build/runtime/package jobs. Its ten strict visual jobs failed.
Those results are separate from this candidate's local checks and future CI.

## Search-field candidate

The [search-field checkpoint](../evidence/development/search-field/candidate.json)
adds the magnifier and conditional clear action through shared text-field slots.
Pointer/keyboard clear updates the caller once and restores focus. Empty slots
restore padding and height; default regular typography overrides a bold ancestor
while explicit caller fonts remain available. Coverage is 36/80 desktop candidates;
none are accepted.

The 116-case native matrix covers search plus shared-field sizes/error states,
with 116/116 matching root component bounds and 0/116 exact images. Post-action values are compared independently of
pixels. All 108 field PNGs and data replay byte-identically; one scaled DPR 1 anchor
varies by three pixels at channel level one, retained without a tolerance or baseline
update. All 1,390 earlier PNGs and complete metadata remain unchanged.

All 2,846 Qt checks, 41 contract tests, seven installed offscreen modes and 56 fresh
package-only session pairs pass. Eight search pairs exercise model editing, clear,
Return, disabled traversal, fixed slots and actual Qt editor/action interfaces.
Default/Basic/Fusion DPR 2 gallery PNGs are identical. Installed symbol provenance
is checked against the source. Native glyph/cache/compositor, custom-font and
complete editing/RTL/input-method, physical input/display and actual screen-reader
gates remain pending. Documentation and inventory are updated in-repository;
the public wiki remote is unavailable. This native UI change has no backend,
metrics endpoint, configuration or TV behavior impact.

For secure field `02ac648`, [References CI](https://github.com/gaulatti/avelino/actions/runs/38643225493)
passed and [Linux CI](https://github.com/gaulatti/avelino/actions/runs/38643225490)
passed both architecture build/runtime/package jobs while all twelve strict visual
jobs failed. Those results remain separate from this checkpoint's local checks and CI.

## Collection filters and chip candidates

The [collection-filter checkpoint](../evidence/development/collection-filters/candidate.json)
adds bound search with caller content and chips with independent label/removal
actions. The caller owns query, selection and removal. Replacing tall content with
a chip exposed a Loader geometry loop; positioning now belongs to a separate
parent, and the regression fails on binding warnings and checks resulting sizes.
Coverage is 38/80 desktop candidates, with none accepted.

The 180-case native matrix has 180/180 matching root bounds and 0/180 exact images. Query, content, selected state and
callback counts are checked independently of pixels. A clean helper replay
reproduced 170/181 files byte-for-byte; eleven images varied by at most one channel
level. Replay pairs and differences are preserved without baseline or tolerance
changes. All 1,510 earlier PNGs and full metadata remain unchanged.

All 2,888 Qt checks, 45 contract tests, eight installed offscreen modes
and 64 fresh package-only session pairs pass. Eight pairs cover the new workflow
in Xvfb/nested Weston, software/Mesa OpenGL, light/DPR 1 and dark/DPR 2/text 1.5.
Those are synthetic-input/interface checks; physical displays/input, real desktop
compositors, source glyphs and actual readers remain pending. Software curved
content clipping is explicitly unsupported and unaccepted. Default/Basic/Fusion
DPR 2 gallery PNGs match exactly. Source/package symbol provenance is verified.

Documentation and inventory use in-repository files because the public wiki
remote remains unavailable. No backend, metrics, configuration or TV changes are
included. For preceding search-field commit `b8cb7db`,
[References CI](https://github.com/gaulatti/avelino/actions/runs/38646185312) passed;
[Linux CI](https://github.com/gaulatti/avelino/actions/runs/38646185524) passed both
architecture build/runtime/package jobs while all fourteen strict visual jobs
failed. These results are separate from this checkpoint's local evidence and CI.

## Slider candidate

The [slider checkpoint](../evidence/development/slider/candidate.json) adds the
horizontal range control using an owned Qt template. A native property adapter
preserves caller bindings through pointer/drag, Qt keyboard and actual accessibility
value/action updates. Disabled interface writes are rejected. The exposed caller
range/value is retained while the input offers the source's integral stepped
intervals, including `0...1`/step `0.3` ending at `0.8999999999999999` and the
`0...0.3`/step `0.1` endpoint `0.30000000000000004`. Dense tick rendering is bounded
by display width; a million-step case is exercised.

The 92-case native matrix has 92/92 matching root bounds and 0/92 exact images. Final values, bounds, step and binding
update occurrence are verified independently of pixels. The initial protocol
varied in 20 replay images; it remains preserved with all changed replay pairs.
The animation-disabled 600 ms v2 protocol reproduced all 93 files byte-for-byte.
Source helpers use preserved verified objects, not a new full source build, and
request an active control context explicitly. They did not obtain an active key
window; six source keyboard cases and the failed probe remain explicit.

All 2,926 Qt checks, 48 contract tests, three invalid-startup cases,
nine installed offscreen modes and 72 fresh package-only virtual-session pairs
pass. Eight slider pairs cover both protocols/renderers/display-text scales.
Default/Basic/Fusion gallery images are identical. All 1,694 earlier offscreen
PNGs and complete metadata remain unchanged. Started coverage is 39/80 desktop
APIs, with none accepted. Native keyboard/other missing source contexts, exact
appearance, physical input/display and actual screen-reader gates stay open.

The public wiki remains unavailable; documentation and inventory are updated in
this repository. This native library work has no backend, metrics, configuration
or TV behavior changes. For preceding `aed193d`,
[References CI](https://github.com/gaulatti/avelino/actions/runs/38649754611) passed;
[Linux CI](https://github.com/gaulatti/avelino/actions/runs/38649754666) passed both
architecture build/runtime/package jobs while all sixteen strict visual jobs
failed. Those results remain separate from this checkpoint's local checks and CI.

## Tabs and retained selection bindings

The [Tabs checkpoint](../evidence/development/tabs/candidate.json) adds the source's
segmented-control wrapper and repairs the existing control's detached caller
binding. A native QVariant property update preserves the binding; the activation
signal updates the caller model and a sibling control. Pointer, keyboard and real
Qt accessibility press actions are followed by another external update in the
installed consumer. Disabled input, typed IDs, reorder/empty options, RTL and
constrained labels are covered. Explicit Qt button interfaces now expose labels
and selected descriptions. Exact screen-reader behavior remains pending.

The native matrix has 236/240 matching root bounds and 0/240 exact images; all final selections and callback counts match.
All 241 helper output files replayed byte-for-byte. Four multiline width
measurements differ by 0.5 units. Layout allocation and presentation retain exact
natural gaps and fractional widths; disabled labels dim without fading selected
backgrounds. Accepted references and tolerances remain unchanged.

All 2,954 Qt checks, 52 contracts, three invalid-startup cases, ten
installed offscreen modes and 80 package-only virtual-session pairs pass.
1,770 earlier PNG/full metadata pairs
are unchanged; 20 intentional segmented/gallery
changes retain before/after evidence. All host-style gallery PNGs match. Coverage
is 40/80 desktop APIs started, zero accepted; TV's 46 entries remain pending.

The public wiki is unavailable, so this checkpoint updates in-repository docs.
No backend, metrics, configuration or TV behavior changes. Previous `a090ab2`
[Linux CI](https://github.com/gaulatti/avelino/actions/runs/38655571611) passed both
architecture build/runtime/package jobs while all strict visual jobs failed;
[References CI](https://github.com/gaulatti/avelino/actions/runs/38655571956) passed.
Those remote results are separate from this checkpoint's local evidence.

## Icon buttons and caller-owned pagination

The [pagination checkpoint](../evidence/development/pagination/candidate.json)
adds the source's three icon sizes/variants and previous/next page controls.
Icon frames map to the existing owned button style; accessibility names reach
the actual Qt template inputs. Pagination emits requests and leaves page state
to the caller. Source boundary formulas, zero/negative counts, out-of-range pages,
external updates, localized integer grouping, constrained/wide and RTL layouts
are exercised. The inherited primary color is measured separately from the
Bleecker palette. The page label exposes a real Qt static-text interface.

The native matrix has 556/556 matching root bounds, all 152 matching child body measurements, and 0/556 exact images.
All final page/count/request/callback states match. The source helper replayed
557 files exactly. Held pointer events retain down state through all 36 snapshots
and produce one callback after release; source keyboard/focus remains pending.
Original chevrons have independent bounds/coverage diagnostics, with no approved
substitution. Qt int's narrower range remains an explicit incomplete source gate.

All 3,056 Qt checks, 56 contracts, three invalid-startup cases, eleven
installed offscreen modes and 88 package-only virtual-session pairs pass. All
2,034 earlier PNG/full metadata pairs and host-style gallery PNGs are unchanged.
Coverage is 42/80 desktop APIs started, none accepted; all 46 TV entries stay
pending. No backend, metrics, configuration or TV behavior changes.

The public wiki is unavailable; this checkpoint updates in-repository docs.
Previous `c50af93` [Linux CI](https://github.com/gaulatti/avelino/actions/runs/38659598871)
passed x64/ARM build/runtime/package jobs and failed all twenty strict visual
jobs; [References CI](https://github.com/gaulatti/avelino/actions/runs/38659598840)
passed. Those results remain separate from this checkpoint's local evidence.

## Installed catalog relocation

The [catalog runtime checkpoint](../evidence/development/catalog-runtime/candidate.json)
closes the installed QML import failure recorded at `eed9aac`. CMake supplies the
relative executable-to-QML directory from its install layout; the catalog adds
that module path before loading a fixture. No new environment variable or source
path is required.

A fresh read-only container mounts only the package, copies it to a different
prefix and unsets both QML import overrides. All 55 catalog captures pass, with
PNG and complete metadata byte-identical to the preceding renders. The import
trace loads the relocated `Avelino/qmldir`. An executable copied without its
module refuses startup with the expected missing-module error. The normal
source-build catalog also remains byte-identical. All 3,056 Qt checks, 56
contracts and eleven installed library-consumer modes pass. The library binary
is unchanged. CI now retains both staged and package-only catalog captures.

This verifies offscreen startup and relocation. It does not turn the preceding
88 library virtual sessions into catalog sessions or close physical, compositor,
screen-reader, exact visual or remaining desktop/TV gates. Reference pins,
expected captures, tolerances and exceptions are unchanged.

## Full pagination integer domain

The [exact pagination checkpoint](../evidence/development/pagination-integers/candidate.json)
removes the Qt 32-bit domain restriction. Qt 6.8.3 converts native 64-bit values to
JavaScript doubles; the native helper therefore validates safe numeric inputs or
canonical decimal strings and performs all arithmetic/formatting in C++. The
request signal now carries strings, including ordinary values such as `"5"`.
This is an explicit breaking signature change, documented in the migration.

The native source executes the same Int64 cases and records exact strings:
184/184 matching root bounds, 168/176 matching pagination bodies and 0/184 exact images. All final page/count/request and callback values match. Disabled
extremes cannot overflow. Actual Qt pointer, keyboard and accessibility paths
are followed by external caller updates. Invalid or unsafe input fails startup.
All 185 helper output files replayed byte-for-byte.

All 3,072 Qt checks, 59 contracts, eight pagination and three slider
invalid-startup cases, twelve installed offscreen modes, 96 package-only virtual
session pairs and 59 installed-catalog captures pass. The previous 2,594 PNG and
complete metadata pairs are unchanged; host-style gallery PNGs match. The integer
behavior gap is closed, while exact appearance, source keyboard/focus, physical
input/display and screen readers remain pending. No backend, metrics,
configuration, TV, source-pin, expected-image or tolerance changes. Public wiki
access remains unavailable; the in-repository contract/inventory is updated.

## Wrapped text bounds

The [shared wrapping checkpoint](../evidence/development/text-wrapping/candidate.json)
uses 120 direct pinned source Text/font-expression cases and a byte-identical
121-file clean native replay. Source-proposed whitespace and ink overhang are
preserved independently of glyph advance and final tracking. The original
narrow full-range pagination body's three-pixel gap is closed: all 176 body
measurements match, including DPR 1/2 and source pointer cases. The installed
consumer checks narrow-body dimensions through 257/260/264 width changes and
continues its pointer, keyboard, accessibility and external caller-update path.

All 3,198 Qt checks, 59 contracts, eight pagination and three slider invalid-startup cases, twelve installed offscreen modes, 96 package-only virtual-session pairs and 59 installed-catalog captures pass. The 2,782 preceding PNG/full metadata pairs were checked;
2,770 pairs are unchanged. Fresh strict raw
comparisons cover every changed pair. Existing strict statistics are reused only
after both current files and the original source image are byte-identical to
preserved evidence. The [audit](../evidence/development/text-wrapping/before-after.json)
records every gain/loss and raw pixel-count change; no root/exact or measured pagination-body pass is lost. Exact visual acceptance remains open. No backend/metrics, configuration,
TV, source-pin, expected-image or tolerance changes. The public wiki is still
unavailable; in-repository typography, development and inventory documentation
are updated.
