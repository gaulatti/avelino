# HeroCarousel Linux candidate

This is a development checkpoint: 76/80 desktop candidates and 0/80 accepted.
Desktop reference `fe8a1d462fbd793d883fb92086a16aa2947e32c9`, expected images,
tolerances and exceptions remain unchanged. TV remains a separate later phase.

The public `BleeckerHeroCarousel` owns a horizontal Qt `ListView` and retained
caller slides. Each allocation has viewport width and a 16-point gap. Fixed
callers remain centered. Typed primitive identities and pinned Unicode equality
preserve caller objects across edits, reordering, scrolling, removal and empty
restoration. The measured first-slide height drives fitted height. Offscreen
callers and removed identifiers remain retained; memory-pressure behavior and
native lazy timing remain open. The component adds no navigation or autoplay UI.

The allocations align their scene origin to device pixels before centering the
caller. Source5 exposed a teardown crash after an activity callback detached its
owner and a later allocation queried a null window. Source6 captures the layout
pixel ratio before callbacks; source7 adds gallery and keyboard evidence. All
seven source attempts, including source5's failed Qt logs/stack, are preserved.
Final source7 contains 584 exact core files. Five focused Qt targets pass: retained
slides and owner teardown at DPR 1/2, the isolated catalog matrix, and existing
item lifetime regressions at DPR 1/2. The complete Qt suite was not rerun locally.

The installed package is copied into a new consumer project and compiled without
the library source or producer build. Runtime mounts contain only the installed
prefix and independently built executable. Eight offscreen contexts cover light
and dark, text scales 1/1.5 and DPR 1/2. Eight virtual display profiles exercise
X11 and nested Weston Wayland with software and OpenGL at standard and scaled
settings. OpenGL uses software rendering; physical displays and input are unproven.
Full session screenshots, renderer metadata and actual window screenshots remain
unedited. Accessible caller button queries and synthetic Qt pointer delivery pass.

Eight gallery contexts each exercise 17 actual operator clicks through 21 recorded
states: four caller slots, edits, reorder, empty/restore, width, RTL, theme, text
scale and disabled state. Tab reaches the actual caller button; Space activates
it; Right leaves the view and focus unchanged; disabled callers reject clicks
and are excluded from Tab traversal. These are Qt input checks, not native OS
input or reader acceptance. The installed catalog's initial gallery is byte-equal
to the consumer's initial gallery. Adding the gallery harness preserves all 192
previous native-context PNGs and eight complete JSON reports byte-for-byte.

All 192 native observations stay in strict full-image/frame/lifecycle comparison.
Source6's allocation correction improves active-frame matches from 100 to 184.
There are 108 matching images, 184 matching active-frame sets and 168 matching
lifecycle records; 84 match all three together. All 32 history images and active
frames match, but only eight history lifecycle records match. SwiftUI transiently
realizes another slide during width expansion. No invented appearance events
hide the difference. Eight inherited system-font frame sets still differ.
The default consumer and strict comparator both exit 1 rather than accepting parity.

History frames are explicitly an active projection of cached native preferences;
raw stale frames remain preserved, and caller wrapper geometry was unobserved by
the native history helper. Direct native sizing is not fully replayed on Linux.
Full geometry, fonts/raster, generic native ID contexts, lazy/gesture timing,
retained gallery raster comparison against fresh callers, readers, physical
display/input and independent-machine acceptance remain pending.

`source-specs.json`, `runtime-spec.json` and `records-spec.json` preserve exact
bytes and modes through checksum-addressed gzip chunks, each at most 8 MiB
expanded. This also preserves the 88 MB debug library without weakening the
Linux archive boundary. `files.json` seals every member except itself. Raw host
command paths are provenance; the reconstruction tool has no sibling dependency:

```sh
python3 evidence/development/hero-carousel-20261018/tools/reconstruct.py /tmp/avelino-hero --runtime-only
```

Omit `--runtime-only` to restore source7; select `--source 1` through `--source 7`
for an earlier producer and add `--records` for the raw build/runtime records.
The recorded portable replay mounts only reconstructed `runtime`, asserts that
project sources and consumer CMake state are absent, and runs all eight native
contexts plus eight galleries. All 376 PNG and JSON outputs reproduce exactly.
This is a same-machine replay, not an independent-machine result.

The CI registration supplement preserves the added package commands, catalog
matrix entry, dedicated display driver and workflow artifact paths. A source-free
run of the added installed-consumer commands reproduces the recorded gallery;
four installed catalog contexts match their corresponding consumer galleries.
Shell syntax passes. This is focused local evidence, not a full CI result.
The helper's earlier substring-count preflight failure is retained separately;
it started no runtime command and was corrected before the successful run.

Run `python3 scripts/verify-hero-carousel-candidate.py` with the repository's
visual Python requirements to recompute the checksums and strict diagnostics.
