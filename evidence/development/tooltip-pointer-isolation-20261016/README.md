# Synthetic pointer isolation

The installed Tooltip consumer could fail its unchanged retained-pixel assertion
when a real Wayland pointer event interrupted its independent QTest pointer.
This is a display-harness correction, with native parity still unaccepted.

The actual ARM64 installation from failed CI run
[38961229340](https://github.com/gaulatti/avelino/actions/runs/38961229340)
was replayed with the original pre-font consumer sources. The source checker
SHA-256 is `29d5f6123b9029a3294b8a388848e32b24c8e5c0f328a0e8a7141214a49af02c`,
also the unchanged delivered checker. Diagnostic variants add logging and image
capture; they retain the original waits, input and exact equality assertions.

The v6 stress replay failed on process 14: the popup hid during its first frame
wait, while its text stayed unchanged. The v7 hover trace again failed on process
14, this time during the hint update, with a native Wayland Leave immediately
before the caller's HoverHandler changed from true to false.

The v8 Wayland protocol trace identifies the recipient. The parent is
`wl_surface@18`; its native pointer enters at `(846,881)`. The first tested
tooltip is `wl_surface@34`, configured at `(691,866)` with size `314x42` in
protocol surface coordinates. The pointer leaves the parent and enters that
tooltip at `(155,15)`. Meanwhile QTest's last Qt scene position is `(344,400)`
over the caller. These independent positions made popup mapping inject a genuine
hover departure into the synthetic test. The popup then closes and the native
pointer returns to the parent. No text mutation caused this closure.

The v9 attempted cursor park did not persist: Xvfb reset when its last client
disconnected, and the captured position returned to `(1280,960)`. Its process 14
failure is retained. In v10, `-noreset` retains the parked `(2559,1919)` position
outside all clients and the nested compositor. All 30 fresh processes pass,
including exact before/after tooltip pixels, caller state/input, focus, and Qt
accessible interfaces. Runtime-only containers mount neither producer nor
consumer source. This is virtual-session evidence with synthetic input.

`prior-replays.json` records all ten original attempt exits, completed session
counts, installation hashes and archive checksums. Each archive has a complete
member hash/size manifest; extraction was checked against the original bytes.
Consumer/build binaries and installed libraries are identified by hash rather
than embedded in these diagnostic archives. The original CI installation is
identified by artifact ID and complete file hashes in v3's archived inputs.

| Archive | Attempts | Purpose |
| --- | --- | --- |
| `initial-replays.tar.gz` | v1-v3 | Isolated current package, full fixture order, actual CI installation |
| `old-consumer-replays.tar.gz` | v4-v5 | Original consumer resources and frame lifecycle tracing |
| `pointer-diagnosis.tar.gz` | v6-v10 | Repeated failure, hover/protocol cause, ineffective park, persistent park |

Inside `pointer-diagnosis.tar.gz`, inspect
`tooltip-wayland-protocol-v8/display-evidence/tooltip-wayland-software-scaled-attempt14.log`
at lines 420-523 for the mapping, native Leave/Enter, closure and failed frame.
The v7 attempt 14 also preserves both differing PNGs and `-hint-failure.json`.
Direct copies of those original pixels are [before](failure-before.png) and
[after](failure-after.png): the latter is fully transparent RGBA at the same
314x42 size. The corrected process 14's [before](passing-before.png) and
[after](passing-after.png) PNG files are byte-identical. Their original paths
and hashes are in `visible-pixel-witnesses.json`.
All failed observations remain present. The earlier v4 OpenGL frame failure
remains unresolved by that isolated replay alone; the complete final display
matrix is recorded separately.

The delivered harness adds `-noreset`, parks and checks the native cursor, saves
`native-pointer.txt`, and identifies that control in every session record. It
does not change Tooltip implementation, waits, expected images, source pins,
font mappings or tolerances. Native popup timing/dismissal, physical input,
physical displays and reader acceptance remain pending.

The `startup-guard/` probe executes the exact delivered startup prefix twice in
fresh containers. The persistent server exits zero with `(2559,1919)` recorded;
removing only `-noreset` exits one at the new position assertion, recording
`(1280,960)`. This checks the failure at the harness boundary before consumers
start. Both scripts, logs, actual exits and raw pointer records are retained,
with hashes in `startup-guard-files.json`.

`runtime-only/` preserves a fresh eight-profile Tooltip replay with the current
canonical consumer executable and installed package only. Its compiled-consumer
directory contains just `InstalledConsumer`; no generated build files or source
checkouts are mounted. All X11/Wayland, software/OpenGL and standard/scaled
profiles pass the original exact retained-pixel, caller/input, focus and Qt
accessibility assertions. Its actual outer exit is zero, with complete session
and separate-window captures. `runtime-only-files.json` seals every retained
output. The unchanged consumer's 82 canonical source files were independently
compared with the package build's source inputs and are all byte-identical.
`runtime-installation-audit.json` verifies the same consumer executable and all
123 installed files as the full display replay.

The complete final display replay passes all 224 sessions: 28 fixtures in each
of the eight X11/Wayland, software/OpenGL and standard/scaled profiles. Its actual
outer exit is zero after 991.672 seconds. `full-matrix.json` records every session,
and `full-matrix.tar.gz` retains the original captures, logs, scripts, frozen
inputs, installation hashes and result. `full-matrix-files.json` seals all archive
members, verified against the originals after extraction.

That full replay mounts the generated consumer build directory, with the
producer checkout/build and canonical consumer checkout absent. Its original
input description incorrectly implied that no consumer source was present;
`boundary-audit.json` preserves the correction and all generated build-file
hashes. The frozen original receipt was not rewritten. The separate
`runtime-only/` replay above establishes the executable-only boundary.
