# Compiled divider and independent package consumer

The updated module builds from a separate APFS clone at source `166ac74cc`.
Both DPRs pass 264 compiled AdminShell and 40 MobileShell cases. Installation and
a fresh independent consumer configure/build succeed. This is an incremental
module rebuild with a fresh consumer tree. The previous build and package remain
unchanged; clone and preservation audits identify the checked bytes.

Four source-absent offscreen runs cover light/dark and DPR 1/2. Each matches all
80 native layouts, 160 owner-history states and 168 divider boundary cases and
passes Qt toolbar, keyboard, shortcut, retention and two accessibility interfaces.
All 320 raw body captures and reports are retained. These use diagnostic caller
colours and do not establish native pixel equivalence.

The updated X11/Wayland software/OpenGL session matrix was running when this
checkpoint closed and is excluded. The earlier complete matrix uses its earlier
recorded source. Physical input/display, hardware acceleration, reader acceptance,
native materials and reviewed ICC comparison remain pending. No source pin,
expected image, comparison policy, tolerance, mask or exception was changed.

```sh
python3 scripts/verify-admin-divider-package.py
```
