# Platform mappings and decisions

| Concern | Avelino ownership | Acceptance status |
| --- | --- | --- |
| Shared tokens and neutral contracts | Pinned Bleecker source; controlled Linux representation | Implementation pending |
| SwiftUI visual presentation | Compare pinned rendered fixtures; implement in Qt templates | Verification pending |
| Encode Sans / Libre Franklin | Licensed static assets from exact Sabella references | Checksums/license verification required |
| System monospace | Resolve actual face per reference fixture; no Apple font redistribution | Unresolved; no substitution approved |
| SF Symbols / platform assets | Inventory literal/dynamic inputs; distributable original/equivalent assets with provenance | Unresolved; no substitution approved |
| Menus, tooltips, file/date dialogs | Avelino owns presentation, Qt supplies semantic mechanisms | Adapter fixtures and open-window comparisons pending |
| Charts | Controlled renderer for the five reference chart families | Renderer/license decision pending |
| Linux desktop sessions | Ubuntu 24.04, Wayland and X11, Qt 6.8.3 | Runtime evidence pending |
| TV hardware/decoder/remote | User target TBD; Apple TV/Android TV context does not select Linux hardware | Target selection pending |

There are **zero approved exceptions**. Record each proposed difference with a
fixture, reference image, candidate image, geometry/behavior impact, provenance,
and reason. Approval must name that difference; implementation authors cannot
self-approve. Platform API differences are documented independently of appearance
or behavior exceptions.
