# Native dropdown supplement

This record adds first-visible-text and image-metadata probes to the pinned
DropdownMenu investigation. It contains both original and fresh source-build
outputs. It is source evidence; Linux and physical input acceptance remain open.

All 59 label/image files reproduce byte for byte: 27 images plus metadata for
nine label definitions, and 30 images plus metadata for image/button measurements.
The first visible text and first image supply metadata. Hidden text is omitted;
opacity-zero text remains. Wrapper decoration and 200-by-80 image frames do not
replace the intrinsic metadata. A folder contributes 18 by 14 points, and an
ellipsis 14 by 5. A text/image stack adds a 3.5-point gap in this context.

All three behavior branches select Duplicate through their own application event
queue, without reaching the timed fallback cancellation. Trigger opening still
uses NSPopUpButton.performClick. Their fresh JSON outputs differ: AppKit places
the popup and corresponding global pointer target 15 pixels higher. Both raw
versions remain here. This is not an exact placement replay or physical input
acceptance, and the earlier mixed cancellation diagnostic remains unchanged.

The fresh source build preserves all 89 pinned source files. The external source
archive contains the reference source archive, helper sources, fixtures and input
manifest; it has no prebuilt library. Apple source/tooling archives stay outside
Avelino. The archive locator and checksum are in investigation.json. Independent
machine replay, native popup placement, physical pointer/keyboard and reader
acceptance remain pending.

Run `python3 scripts/verify-dropdown-menu-supplement.py` from the repository root
to verify every retained byte and the explicit three replay differences.
