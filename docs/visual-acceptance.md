# Strict mirror acceptance

For each fixture, match content, logical dimensions, DPR, appearance, text scale,
state, animation time, clock, random seed, and fixed media frame. Record source
revision, OS/build, SDK, compiler, Qt version, graphics backend, font resolution,
and capture method. Do not compare two images at incompatible logical sizes.

Use side-by-side images, overlays, and per-component differences. Tolerances may
address measured glyph-edge antialiasing only. Do not broaden tolerances or mask
regions to conceal fonts, symbols, wrapping, baselines, geometry, spacing, missing
states, shadows, clipped surfaces, or transitions. A whole-screen similarity score
alone is insufficient.

Capture open selectors, menus, tooltips, dialogs, scrollbars, selection highlights,
and separate popup windows when applicable. A component-tree capture that omits
an overlay cannot accept it. Session screenshots must include the actual displayed
window/overlay path; record whether capture used a compositor, X11 root, native
window, or item renderer.

Maintain independent evidence for deterministic offscreen rendering, actual
Wayland, actual X11, keyboard/pointer behavior, focus restoration/accessibility,
display/text scaling, and installed-package consumption. Test host styles that
would expose accidental theme inheritance. Package-consumer tests must exercise
open overlays and internal controls, not only instantiate top-level types.

Fonts and assets are prerequisites for affected fixtures. Encode Sans and Libre
Franklin must resolve to the bundled licensed faces. Record the actual Apple
monospace face per fixture without redistributing it. Inventory literal and
dynamic SF Symbol inputs; compare distributable equivalents for geometry, weight,
alignment, and size. An unavoidable substitution needs an exact proposed exception
and explicit approval. Keep the fixture pending while unaffected work continues.

Each parity entry records reference source, implementation, required cases, tests,
captures, comparison result, session evidence, and exceptions. `complete` requires
all required cases and applicable gates. `implemented` and `verification-pending`
remain unfinished. Proposed exceptions are separate from approved exceptions;
platform adaptation cannot be used to relabel an unfinished mirror.

Desktop has its own gate. TV additionally needs selected hardware/backend/input
and real physical-remote and sustained-playback evidence. Headless playback,
screenshots, and synthetic key events do not close TV hardware acceptance.

## Candidate comparison tool

Install `tools/visual-requirements.txt`, then run:

```sh
python3 scripts/compare-captures.py --reference reference/captures/desktop/buttons \
  --candidate artifacts/linux --output artifacts/comparison
```

The tool verifies each reference image's preserved checksum and emits per-case
side-by-side images, overlays, raw pixel differences, and
a JSON/HTML report. It fails on missing cases, incompatible logical dimensions,
DPR, text scale, fixture identity, themes or states, physical image sizes, alpha differences, and any RGB pixel
difference. ICC-managed captures require an explicit reviewed conversion; the
tool refuses to strip profiles or quietly reinterpret them. Initial tolerance is
zero. A later calibrated glyph-edge rule must preserve layout and asset failures;
it cannot be inferred from a favorable whole-screen percentage.

The Linux workflow runs `button-mirror-comparison` independently for x86_64 and
ARM64 candidates after the build/runtime/package checks. It uses preserved Git
references and publishes the JSON report, image pairs, overlays, and raw diffs.
The visual job fails until those 112 source cases match; it is not marked optional
or converted into a successful build result. This initial button matrix still
does not close pressed, focus, loading, composition, motion, or the remaining
desktop cases. A failing comparison never updates the reference images.
