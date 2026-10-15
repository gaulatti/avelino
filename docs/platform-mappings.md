# Platform mappings and decisions

| Concern | Avelino ownership | Acceptance status |
| --- | --- | --- |
| Shared tokens and neutral contracts | Pinned Bleecker source; controlled Linux representation | Implementation pending |
| SwiftUI visual presentation | Compare pinned rendered fixtures; implement in Qt templates | Verification pending |
| Encode Sans / Libre Franklin | Licensed static assets from exact Sabella references | Files and licenses verified; component typography acceptance pending |
| Japanese glyph fallback in page headers | The supplied title reaches Qt unchanged; current Linux fallback does not match the source glyph widths | `Éditions 東京` title width remains verification-pending; no replacement font, tolerance or exception approved |
| System monospace | Source-expression probes resolve `.AppleSystemUIFontMonospaced` faces; no Apple font redistribution | Actual affected components, Linux candidate assets and comparisons pending; no substitution approved |
| SF Symbols / platform assets | Inventory literal/dynamic inputs; distributable original/equivalent assets with provenance | Unresolved; no substitution approved |
| Menus, tooltips, file/date dialogs | Avelino owns presentation, Qt supplies semantic mechanisms | Adapter fixtures and open-window comparisons pending |
| Charts | Controlled renderer for the five reference chart families | Renderer/license decision pending |
| Linux desktop sessions | Ubuntu 24.04, Wayland and X11, Qt 6.8.3 | Virtual software/OpenGL sessions pass on both architectures; complete visual, input and accessibility acceptance pending |
| TV hardware/decoder/remote | User target TBD; Apple TV/Android TV context does not select Linux hardware | Target selection pending |

There are **zero approved exceptions**. Record each proposed difference with a
fixture, reference image, candidate image, geometry/behavior impact, provenance,
and reason. Approval must name that difference; implementation authors cannot
self-approve. Platform API differences are documented independently of appearance
or behavior exceptions.

Two specific font exceptions are proposed in the inventory, with approval and
implementation/comparison work still pending:

- `FONT-MONO-001`: use licensed IBM Plex Mono for source system-monospace usages,
  retaining each requested logical size and weight. This includes the desktop
  `bleeckerFont` modifier when its requested family is `mono`; television faces
  are outside the scope of these probes. The native face resolution is
  recorded in [the supplemental proposal](reference-proposal-20261012.md); Linux
  assets, licensing/provenance and geometry/weight/alignment comparisons must be
  prepared before an approval request. No broader raster tolerance is proposed.
- `FONT-TOGGLE-001`: use bundled Encode Sans Regular at 13 logical pixels for the
  toggle's unconfigured inherited-label case, where the native probe resolves
  `.SFNS-Regular` at 13 pt. Preserve padding 12 and minimum height 34. Current
  Avelino's 14 px default is unfinished work, not an accepted adaptation. The
  configured 14 pt Encode Sans case is separate and needs no system-font exception.
  Linux captures and exact geometry/weight/alignment differences remain to be
  prepared before review.

Neither proposal is approved or applied to an accepted fixture. Affected entries
remain pending while work continues on components using distributable source assets.

[Icon buttons and pagination](pagination.md) use a required caller Component icon slot in place of SF Symbol lookup. Pagination owns original left/right chevron candidates. This is a documented API adapter, with no approved symbol exception; dynamic SF Symbol coverage, exact artwork, source keyboard/focus remain pending. The [exact pagination integer update](pagination-integers.md) verifies the complete signed 64-bit domain using a decimal-string QML boundary.

[Accordion](accordion.md) maps the source initializer to `initiallyExpanded` and
represents conditional generic content by a Component factory. Only the title and
chevron rectangles participate in pointer activation; the blank spacer does not.
The plain header uses a native Qt template and original rotated chevron candidate.
Source state/lifecycle and physical/reader/motion/asset acceptance remain separate.
