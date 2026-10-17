# Retained AppTabBar badge raster correction

The original candidate remains unchanged in `../app-tabs-20261017`. This supplemental candidate fixes the two retained disabled gallery failures using the existing alpha-capable software raster renderer. All 28 states match fresh processes at DPR 1 and 2, with independent enabled-badge visibility checks. Actual XTest gallery input also passes 28/28 complete caller viewports. The 26 previously matching viewports remain byte-identical.

All 37 Qt targets pass. The final installed package runs 35 consumer modes and 143 catalog captures; all 139 legacy PNGs and complete metadata are unchanged. Full native comparison still fails: 56 exact images (all empty states), 940 matching frame sets and 1,208 matching states out of 1,208 pairs. Supplemental opaque badge masks are unchanged in 304 contexts and improve in eight; they do not replace unmasked comparison. Native disabled colors still differ.

Eight fresh virtual profiles retain 42/48 exact restore images. Six scaled Wayland software restores change the initial transparent bottom strip into opaque card pixels. This independent failure remains uncorrected. Physical displays, real hardware acceleration, native keyboard timing/accessibility, readers and independent-machine replay remain pending. No expected image, reference pin, tolerance or exception changes.

`candidate.json` binds every canonical file. `payload-map.json` reconstructs complete producer sources from immutable Git revision `c3f84a00f73a291b8f344066ee1bfd85815567f8`, prior sealed payloads and unique new content-addressed bytes. It retains all intermediate sources, failed compiler/repaint/layer attempts, raw logs, installed artifacts and images. Archives stay below 48 MiB expanded. The verifier also checks logical source paths, including content-addressed data, against the Linux-only boundary. Core dumps and build caches are excluded.

Run `python3 scripts/verify-app-tabs-raster.py` from the repository root with the visual requirements installed. See [the component contract](../../../docs/app-tabs.md#retained-badge-raster-correction).
