# Linux mirror implementation plan

## Objective and ownership

Deliver the complete desktop mirror through an independent acceptance gate, then
the television mirror through a separate gate. Bleecker defines shared language,
tokens, and platform-neutral contracts. Sabella, Orchard, and Avelino own native
integration on their platforms. Mirror acceptance compares Sabella's actual
rendered fixtures; matching Swift-specific API shapes is not required.

Desktop is pinned to `fe8a1d462fbd793d883fb92086a16aa2947e32c9`, including local
unpublished typography and attention-surface changes. TV is pinned to
`f5ac479bfceaa7eab23c1716ac47420ac53dae25`, including active-group channel tuning.
Immutable source artifacts, file hashes, dependency locks, and tooling records
must reproduce both references without altering or publishing Sabella.

## Architecture

- `Avelino`: dependency-light foundations, controls, surfaces, navigation, layouts,
  overlays, data displays, and charts. Public component names retain `Bleecker`.
- `Avelino.TV`: television presentation, focus, guide/navigation, and chrome.
- `Avelino.Playback`: Linux decoder integration and playback lifecycle; isolated
  from desktop. Linux names use `AvelinoTV`, not Apple-specific names.
- `AvelinoCatalog`: deterministic fixtures plus interactive galleries.
- Installed consumer: independent build and runtime using only installed artifacts.

Qt Quick templates supply editing, input, focus, and accessibility mechanisms.
Avelino owns backgrounds, content, indicators, focus visuals, popup delegates,
scrollbars, tooltips, menus, selection highlights, and transitions. Native themes
must not replace accepted visuals. Applications own domain data, persistence,
networking, authentication, and routing.

Use explicit properties, signals, and content slots for shared behavior. Keep
platform-specific adapters documented and tested. Do not add decoder dependencies
to desktop. Avoid GPL-only chart dependencies without a deliberate licensing
decision; the five desktop chart families need a matching controlled renderer.

## Milestones and gates

1. **Preserve references and discover scope.** Verify immutable artifacts in clean
   directories. Record Git revisions, dependencies, tooling, OS, SDK, compiler,
   fonts, symbols, public visual APIs, modifiers, styles, variants, states, slots,
   and platform adapters. Reconcile discovery automatically against inventory.
2. **Build/install foundations.** Pin Qt/toolchain, embed licensed fonts and brand
   resources, generate tokens deterministically, run the catalog, and build/run
   a separate consumer from an installed package with source/build trees absent.
3. **Prove representative mirroring.** Capture buttons (all sizes/variants/states),
   plain text fields, an open selector, cards, attention surfaces, and a shell
   using identical fixtures. Compare real SwiftUI and Linux images. Resolve asset
   and typography differences before accepting affected fixtures. Pending
   comparisons remain open while implementation proceeds in small batches across
   the remaining families; they never become accepted through coverage counts.
4. **Actions and forms.** Complete selection, editing, disabled/loading/error,
   focus, keyboard, pointer, content-slot, scaling, and accessibility cases.
5. **Surfaces, feedback, navigation, layouts.** Complete themes, dimensions,
   wrapping, compositions, focus paths, responsiveness, and motion states.
6. **Overlays, collections, charts.** Include open overlays and separate windows,
   scrolling, pagination, empty/loading/error data, axes/legends/interactions, and
   the independent consumer's internal controls.
7. **Desktop acceptance/package.** Every required case has source, implementation,
   test, capture, comparison, and runtime links. X11 and Wayland, keyboard/pointer,
   focus/accessibility, DPR/text scale, and installed consumption pass separately.
   Publish versioned CMake/QML artifacts, catalog, licenses, checksums, and docs.
8. **TV target selection and implementation.** First identify target Linux hardware,
   distribution, graphics/decoding backend, remote/input delivery, and stream
   formats. Then implement chrome/guide/playback, authoritative active-group
   ordering, pagination, wrapping, focus restoration, and channel-change notices.
   Verify HLS, raw TS, DASH, and RTMP when required by the selected target.
   Acceptance requires physical remote checks and sustained playback on that
   hardware. Synthetic input/headless playback cannot close those checks.

## Evidence and acceptance

The 76 desktop and 42 TV catalog registrations are starting inventories. Discovery
also tracks nonregistered public visual APIs and the cases within each API.
Component completion requires every required case, not a count or token match.
Only glyph-edge rasterization differences may receive narrow, measured tolerances;
incorrect assets, wrapping, baselines, spacing, geometry, or states remain failures.

Baseline updates need explicit authorization, source and image diffs, preserved old
artifacts, and reviewed metadata. Expected images are never rewritten by tests.
Proposed exceptions remain pending until the user explicitly approves that exact
difference. No exceptions are approved at initialization.

Commit and push coherent checkpoints to `main` often. Report desktop, television,
CI, packaging, accessibility, and hardware verification separately. An unfinished
gate remains visible even when implementation proceeds elsewhere.

## Current decisions

Desktop development target: Ubuntu 24.04, Qt 6.8.3, x86_64 acceptance with separate
ARM64 build/runtime evidence, actual Wayland and X11 sessions. Docker can provide
controlled offscreen and virtual-session checks; these do not claim physical
desktop or remote verification.

TV target: **TBD**, per the user. Current user work uses Apple TV and Android TV.
Those platforms inform reference behavior but do not select a Linux decoder or
remote. TV implementation and hardware acceptance remain pending target selection.
