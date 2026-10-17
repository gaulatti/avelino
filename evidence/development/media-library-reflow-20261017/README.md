# MediaLibrary reflow correction

All 1608 native observations remain strict: 1008 complete matches, 1168 pixel matches, 1288 frame matches and all 1608 lifecycle matches. No previously passing pixel, frame, lifecycle, state or retained-raster observation regressed. All 139 earlier catalog images and metadata remain byte-identical.

Auto-height reflow publishes content height before viewport activity changes. The generic caller fill snaps its two scene edges independently, preserving subpixel-width fills and removing the virtual Wayland restore gap. The grid adds no tile styling. All eight virtual profiles and 48 restore observations pass, 15 focused checks pass at each DPR and all 33 Qt targets pass. These virtual checks do not establish physical display/input, hardware acceleration or reader acceptance.

The gallery exercises 14 controls and 23 XTest clicks through 24 states; 20 match exactly. Four RTL button-text states remain failed. Direct sizing, fractional/text geometry, lazy estimates, fonts/raster, native input timing, physical displays, readers and independent-machine replay remain pending. Earlier unsuccessful attempts and their frozen inputs remain preserved. Pins, expected images, tolerance and exceptions are unchanged. See [the grid contract](../../../docs/media-library.md).
