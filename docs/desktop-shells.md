# Desktop shell contracts awaiting native window verification

`BleeckerMobileAppShell` and `BleeckerAdminShell` remain pending in the desktop
inventory. Their reference is pinned to Sabella
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`, `Sources/Sabella/Mobile.swift`.
The existing `BleeckerAppShell`, `BleeckerTabs` and `BleeckerAppTabBar` are separate
APIs and do not supply these window-level behaviors.

## MobileAppShell on desktop

The macOS branch at lines 240–260 stacks the caller's header, a separator,
filling content and footer with zero vertical spacing. The initializer with an
omitted footer supplies an empty view.

Nonempty tab data attaches a principal toolbar picker. Its title is `Section`,
its accessibility label is `Application section`, and its style is segmented.
Each item uses the tab's label, system image and value tag. This branch does not
forward the tab's badge, disabled state or custom accessibility label. Empty tab
data omits the principal picker. It does not add the touch/TV bottom tab bar.

Selection remains caller-owned. Echoing, ignored, delayed and redirected setters
need separate observations; an activation request does not prove that the
external selection changed. Native toolbar attachment, segment layout, empty and
unmatched selection, keyboard behavior and actual accessibility remain unmeasured.

## AdminShell on desktop

The macOS branch at lines 414–451 uses a native split view. The visibility
binding maps caller `true` to all columns and `false` to detail only; a native
visibility write maps to `true` unless it is detail only. The source's desktop
branch does not use the touch breakpoint/drawer presentation.

The sidebar receives component padding, fills height with top alignment, and has
the card background. Its column-width declaration uses minimum
`min(220, sidebarWidth)`, ideal `sidebarWidth`, and maximum
`max(sidebarWidth, 420)`. The public default sidebar width is 300. These declared
constraints do not establish the actual width resolved by the native split view.

The detail stacks the caller's header, separator and filling content. The
toolbar button toggles the caller's visibility binding, uses `sidebar.left`,
and changes between `Hide navigation` and `Show navigation`. Its shortcut is
Command+Control+S. Resizing, native collapse, splitter input, owner policies,
focus and retained caller state require actual window observations.

## Reference preparation

An external macOS helper now hosts the unchanged public components in a real
SwiftUI window scene. It compiled successfully. Its 17
prepared String-valued fixtures cover the initial toolbar and split-view
questions, including optional caller-slot probes. It reuses the checksummed
Sabella object from the earlier date investigation, so it is not an independent
library rebuild.

The helper has not been launched or observed. The desktop was locked during
preparation. Raw window/view, toolbar, split-view, accessibility and OS-input
records are still required, as is a public-versus-probed comparison. Other value
types, duplicate identities, direct sizing, animation, physical input and reader
acceptance remain separate work. No Linux candidate or accepted API is added by
this preparation. All Apple tooling and binaries remain external to this tree.
