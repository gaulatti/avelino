# Linux typography and tooltip windows

The source-backed font shaper now requests typographic line metrics for the two
bundled font families and their fallback runs. The shared `Éditions 東京` header
keeps its native 32-point title line and 68-point body with Noto CJK installed.
The caller font and pixel size are unchanged. CJK glyph coverage is retained.

The retained A/B uses the same binary, module and 602 source inputs with and
without the CJK font layer. The new regression fails four rows against the old
module. Before applying the policy, a diagnostic matrix verifies all 192 native
navigation geometries per DPR and 144 bundled-family/weight/size measurements
per DPR with no metric changes. The Qt 6.8.3 header used by the build matches the
reviewed release header; `matrix/api/sources.json` records exact hashes and URLs.
The retained parent CI run 39167761744 fails only the Unicode page-header height
assertions on x86_64 and arm64: each architecture passes 53 of 55 CTests. The raw
log and its failure summary bind the same 72-versus-68 regression to `e330fe3`.

The first complete display attempt stops after 253 records at a Wayland/OpenGL
tooltip remount with a null EGL surface and no displayed frame. A focused A/B
uses the same consumer ELF and immutable CJK image: the previous library fails
5/10 runs and the font-only fix fails 1/10. Every failure has the same surface
and frame error. The failed run and A/B remain failures, not passing coverage.

A diagnostic releases hidden tooltip graphics and scene graph resources through
public Qt APIs and passes 20 fresh-compositor runs with the original assertions.
The library applies that policy when the owned popup content enters a separate
Qt::ToolTip window. It leaves caller windows alone and retains Popup.Window.
The final consumer adds twenty visible-owner remounts with displayed frames,
fresh caller state and retained editor focus. That consumer reproduces the
failure against the prior module. Its identical ELF passes 19 of 20 runs and
380 remount frames with the new library. Attempt 18 crashes Weston 13.0.4; its
shell and client logs remain in the packet. The reviewed Qt 6.8.3 QuickWindow header
matches the installed header exactly; `tooltips/api/sources.json` records it.

The final 604-input build passes all 55 CTests, including the Unicode regression at
both DPRs. A freshly compiled 149-input independent consumer passes eight
navigation profiles and all 41 smoke invocations from the unchanged Linux
driver, with project source/build trees absent at runtime. Title updates retain
the caller action, private state and editing focus. The unchanged catalog check
passes 159 captures. All 792 Python contract tests pass in one run. The unchanged
display check produces 303 of 304 required records, then fails a FileInput capture
under scaled Wayland/OpenGL. Seven virtual session profiles contain all 38
fixtures; the eighth contains 37. The complete display gate is FAILED, not a
passing matrix. Window and full-session captures are retained with SHA-256
bindings. All eight tooltip profiles complete twenty remounts, for 160 frames.

The compositor failure remains unresolved. Forty ordinary runs using the same
client and compositor binaries pass 800 remount frames with bounded core capture
and the server cwd set to the diagnostic output directory. Two sets of forty
GDB runs also pass (one disables ASLR; one preserves it). None proves the prior
crash resolved. A separate ASan/UBSan build of unmodified Weston 13.0.4, bound
to the exact upstream archive hash, catches a null parent view at
`libweston/desktop/surface.c:117` in `weston_desktop_surface_update_view_position`
on attempt 32. The client ELF is unchanged. This diagnostic instruments only
the compositor and provides no acceptance or full-runtime pass. No compositor
patch or toolchain upgrade is included in this checkpoint.

The same fresh consumer replays eight date and eight date-gallery profiles.
All 437 raw date candidates used by the parent checkpoint's strict comparisons
are byte-identical. The parent comparisons remain 0/437 strict pixel matches;
this typography checkpoint does not improve or accept those comparisons.

The retained failures include the Unicode metrics, parent CI, partial display
runs, focused A/B, red remount regression and compositor diagnostics. The packet binds 604 final core
inputs, 149 fresh consumer inputs, integration copies and unchanged runtime
drivers. `files.json` seals every packet member except itself. Run
`python3 scripts/verify-navigation-cjk-metrics.py` with the visual requirements
installed to verify checkpoint integrity and recompute the parent date
comparisons. A passing checkpoint verifier does not override the failed runtime
gate. Repeat the complete unchanged display gate after resolving the failures.

Desktop coverage remains 76/80 candidates and 0/80 accepted. Native font/glyph
and raster equivalence, OS input histories, physical sessions, actual reader
output and the later TV phase remain pending. No reference pins, masks,
resizing, comparison tolerances or approved exceptions change here.
