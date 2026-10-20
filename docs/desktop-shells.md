# Desktop shell contracts and verification status

`BleeckerMobileAppShell` has a Linux candidate; `BleeckerAdminShell` remains
pending without a Linux implementation. Neither API is accepted. Their reference is pinned to Sabella
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

Selection remains caller-owned. The [application-shell candidate](mobile-shell.md)
records native slot geometry, hidden-window toolbar attachment, and apply,
ignore and delayed owner histories. An activation request does not prove that
the external selection changed. Broader value/identity policies, native keyboard
timing, physical input and screen-reader acceptance remain pending.

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

The [retained host investigation](../evidence/reference-investigations/desktop-shell-host-20261019/provenance.json)
compiled and ran external macOS helpers against the checksummed Sabella object
from the earlier date investigation. It is not an independent library rebuild.
The completed initial host run retains 16 records: eight for the application
shell and eight for the admin shell, covering widths 360/840, both visibility
states and bare/measured forms. Its hidden NSWindows were neither visible nor
key; AppKit cached their own views without capturing the user's screen.

The initial admin records include raw content/chrome images, toolbar items and
the native split-view hierarchy. The later [AdminShell investigation](admin-shell.md)
adds paired caller layouts, native divider calls, visibility writeback and
resizing in hidden windows. Its immutable-host replay also exposes a capture
environment difference from the older pixels; visual continuity remains open.
The picker owner histories above cover the application shell separately. Other value types,
duplicate identities, animation, physical input and reader acceptance remain
separate work. All Apple tooling and binaries remain external to this tree.
