# AdminShell source investigation

`BleeckerAdminShell` still has no Linux candidate. This investigation measures
the pinned desktop source at `fe8a1d462fbd793d883fb92086a16aa2947e32c9` without
accepting a replacement presentation or changing existing expected images.

## Capture scope

The [retained evidence](../evidence/reference-investigations/admin-shell-20261020/result.json)
covers 20 caller configurations, both visibility values, light/dark source
environments, and bare/measured forms: 160 static profiles per successful run.
Six paired histories cover applying, ignoring and delaying binding writeback.
They use the native divider's programmatic position method, external visibility
updates and window resizing. They do not activate toolbar buttons or deliver
physical input.

The host uses a white caller background and hidden, non-key NSWindows. The
observed backing scale is 2; no display-scale override is applied. The recorded
environment is macOS 27.0 build 26A428 and Xcode 27.1 build 27A9275. Helpers target
macOS 26.0 and reuse the previously checksummed Sabella object, so this is not an
independent library rebuild or machine replay. All Apple tooling remains outside
Avelino.

The first helper failed compilation because a nested capture function lacked
its actor annotation. The second run retained source-root-local derived
coordinates. The third records the Cocoa host's origin and derives viewport
coordinates without moving an overflowing root to zero. Both successful runs
retain identical PNG bytes. `images.json` explicitly maps 2,912 original capture
paths to 148 exact PNG blobs; repeated bytes share storage. No image is resized,
recoloured or masked.

## Layout and binding observations

- A 360-point viewport can contain a 480-point shell at x = -60. A 24-point
  viewport can contain a 122-point shell at y = -49. Fixed content raises that
  latter minimum to 137 points. These are overflow cases, rather than a switch
  to the touch drawer.
- Empty content leaves the header/separator stack vertically centred. A
  zero-size content view retains an expanding outer frame and leaves the header
  at the top. Empty and zero-size slots remain separate inputs.
- With the tested fixed sidebar caller, requesting a 180-point column resolves
  to 212 points including caller padding. The 460-point request resolves to 460.
  An empty sidebar resolves to the host's 144-point default column in this scope;
  it is distinct from a present zero-size view.
- Breakpoints 1 and 10,000 produce the same body images as the default desktop
  case. The source desktop branch does not select the touch layout by width.
- Collapsing through the native divider can change the displayed sidebar while
  an ignoring owner retains `navigationPresented == true`. A delayed owner
  retains its previous value until writeback is applied. The Qt implementation
  must preserve the distinction between caller value and displayed state.

The raw geometry retains named, global and local coordinates. Native child
hosts report window-relative global coordinates; the recorded Cocoa frame-view
conversion maps those to the captured host viewport. This preserves negative
origins in short and narrow callers.

## Visual continuity remains unverified

Four older host controls no longer reproduce their earlier pixels. Replaying
the exact older executable without recompilation reproduces the new harness's
four controls pixel-for-pixel. The embedded ICC profile hash also differs from
the older captures. This identifies a capture-environment difference; it does
not establish that the profile alone caused every changed pixel.

Both old and new data are preserved, and the verifier records zero original
pixel identities alongside four immutable-binary replay identities. It does not
replace the older images or declare visual continuity. A matching, stable
capture context remains a gate for reproducible visual comparison of the expanded
matrix.

A subsequent [controlled-context replay](../evidence/reference-investigations/admin-shell-context-20261020/all-record-comparison.json)
sets only the owned windows' appearance to Aqua and their colour space to the
older captures' embedded ICC profile. All 32 original application/admin body and
chrome PNGs reproduce byte-for-byte. This changes the capture environment, not
the expected images or pixels after capture. It establishes a reproducible
context for those controls; it does not attribute the earlier differences to
either setting individually.

The [expanded replay](../evidence/reference-investigations/admin-shell-pinned-matrix-20261020/audit.json)
now runs all 20 caller configurations and all six paired owner histories under
that pinned context. All 480 states retain their earlier geometry, requests and
owner values. All 1,440 PNGs retain the requested embedded profile; the 480
before/after observation pairs, 80 static bare/measured pairs and six history
pairs are byte-identical. The four earlier body controls also reproduce
byte-for-byte. The corpus stores 1,440 original paths as 138 exact PNG blobs.
This closes capture-context reproducibility for this matrix. Linux visual,
toolbar, physical input and reader acceptance remain pending.

```sh
python3 scripts/verify-admin-shell-source.py
python3 scripts/verify-admin-shell-context.py
python3 scripts/verify-admin-shell-pinned-matrix.py
```

The verifier checks PNG decoding, every original-path mapping, probe identity,
binding histories, viewport-coordinate derivation, the older executable receipt,
and the staged Git bytes of every retained member. These checks add source
evidence. Toolbar activation, complete caller coverage, actual keyboard/reader
behaviour, physical display/input and Linux parity remain pending.
