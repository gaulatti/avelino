# Formatted text reflow correction

All 24 actual XTest gallery states now match fresh callers. The old module reproduces two pixel failures in the separated-capture regression; the correction passes all 14 text/alignment rows at DPR 1 and 2. Qt 6.8.3 retains a fractional line layout on width growth, so the formatted wrapper now calls the public forceLayout method at the current width. Failed helper and capture attempts remain preserved.

All 1608 native media comparisons remain strict: 1008 complete matches, 1168 pixel matches, 1288 frame matches and all 1608 lifecycle matches. No earlier passing observation regressed. All 139 earlier catalog images and metadata remain identical. Full Qt, installed package and virtual media/font/pill profiles are recorded separately from physical display, hardware acceleration, input and reader acceptance.

The complete 1656 font and 2112 pill corpora are captured and compared with unchanged native sources. Every mismatch remains visible. Pins, expected images, tolerances and exceptions are unchanged; direct sizing and complete mirror acceptance remain pending. See [the grid contract](../../../docs/media-library.md).
