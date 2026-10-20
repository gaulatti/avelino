# Desktop administration shell

`BleeckerAdminShell` has a Linux candidate based on the pinned desktop source at
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`. Acceptance remains pending. Existing
expected images and source pins are unchanged.

## Linux use

Supply retained `sidebar`, `header` and `content` components and a caller-owned
`navigationPresented` boolean. Handle `navigationPresentedRequested` according
to the owner's policy. A request does not assign the public boolean. The
read-only `displayedNavigation` value exposes the split view's actual state.

```qml
ApplicationWindow {
    property bool navigation: true
    header: shell.toolbarItem
    BleeckerAdminShell {
        id: shell
        anchors.fill: parent
        navigationPresented: navigation
        onNavigationPresentedRequested: value => navigation = value
        sidebar: Component { NavigationContents {} }
        header: Component { AdministrationHeader {} }
        content: Component { AdministrationContents {} }
    }
}
```

The default `sidebarWidth` is 300. `breakpoint` is retained as a source argument;
the pinned desktop branch always uses a split view. The source's explicit toolbar
action toggles the caller's value. Its separate native split-view action toggles
the displayed column. Both remain distinct when an owner ignores writeback.
The explicit action has the source shortcut, Meta+Control+S on Linux.

The split handle uses Qt's input handling with a zero-width layout extent and a
wider containment mask. Caller instances and fixed size bindings remain alive
through collapse, reopening and resizing. Native visibility requests may include
transient `true`, `false` sequences even when the final pane stays collapsed;
the candidate preserves the observed callbacks. Preferred and resolved widths
remain distinct, including the 180-point caller that initially resolves to 212.

The regular component tests and `InstalledConsumer --admin-shell` consume 80
native profiles, six owner histories containing 160 states, and 168 fresh-window
divider cases. The catalog fixture is `--fixture admin-shell`. Add
`--admin-shell-report PREFIX` to retain raw consumer body captures and results.
The fixture colours currently diagnose geometry; source colour inputs and
window compositing still require visual comparison. Native symbols, chrome,
toolbar timing, physical input and screen-reader acceptance remain pending.

The [source colour-input record](../evidence/reference-investigations/admin-shell-colour-inputs-20261020/README.md)
now resolves the original sidebar, header, content and white root colours inside
the actual SwiftUI environment. It retains exact Float32 components for both
appearances and initial visibility values. All 12 original control images remain
byte-identical, with unchanged geometry and callbacks. These source inputs differ
from pure diagnostic RGB and change with appearance. They are not yet integrated
into the Linux fixtures; the fair input bridge and raster comparison remain open.

The [initial public-candidate checkpoint](../evidence/development/admin-shell-20261020/result.json)
retains 260 passing QtTest cases in each of four contexts: offscreen at scale 1
and 2, X11 at scale 1 and Wayland at scale 2. It loads the current public QML
files with the unchanged compiled base module. It covers actual toolbar and
divider input, disabled state, retained caller controls, Tab/Space, the shortcut,
window hosting and viewport resizing. It is an interpreted-source result; at that
checkpoint, fresh compilation and execution of the new installed consumer had
not run.
Earlier attempts and their exact input snapshots remain in the capsule.

The subsequent [compiled/package checkpoint](../evidence/development/admin-shell-package-20261020/result.json)
rebuilds the library from a separate build clone and configures a fresh independent
consumer. Both scale factors pass 260 AdminShell and 40 MobileShell tests. The
first consumer compilation failed on three ambiguous Qt JSON-array comparisons;
the explicit conversion repair and successful rebuild are retained separately.

With project sources and the library build absent, four light/dark and scale 1/2
runs each pass 80 native layouts, 160 owner-history states and 168 divider cases.
The checkpoint retains all 320 raw body captures, four installed gallery captures,
all 44 installed smoke commands and the complete 167-capture catalog regression,
including refusal to start without the installed module. Qt toolbar input,
keyboard shortcut, retained caller controls and two accessibility interfaces pass.
These are package and Qt behavior results; they do not accept native pixels or
screen-reader equivalence.

The initial X11 session failed its shortcut check. That attempt and its 80 body
captures remain intact. The consumer now explicitly activates its own window and
waits for keyboard focus before Tab, Space and the shortcut. The next installed
session run passed seven complete configurations and all structural checks in
the eighth, scaled Wayland/OpenGL. Its session validator then failed because the
JSON readiness report preceded completion of the window PNG. The [failed attempt](../evidence/development/admin-shell-sessions-failure-20261020/scope.json)
retains its original command, script, logs, eight reports and all 655 produced
PNGs, including the compositor image from the incomplete final context. Seven
window captures exist; the eighth remains absent. The consumer now
saves the window first and publishes the report atomically. The failed run stays
intact.

```sh
python3 scripts/verify-admin-shell-sessions.py --failed-attempt
```

The subsequent [installed-session matrix](../evidence/development/admin-shell-sessions-20261020/README.md)
passes all eight combinations of X11/Wayland, software/OpenGL and standard/scaled
configuration. The readiness repair is rebuilt into the independent consumer;
the installed core library is unchanged. Sources and the product build are absent
from runtime. Each context matches all 80 native layouts, 160 owner-history states
and 168 divider cases. All 640 body, eight window and eight compositor PNGs remain
available as exact bytes. The canonical script is filtered only to the AdminShell
fixture; its renderer, scaling, pointer and screenshot checks remain intact.
OpenGL uses Mesa llvmpipe. These are virtual session and Qt input results; native
pixels, complete caller/toolbar equivalence, physical input, hardware acceleration
and reader acceptance remain pending.

```sh
python3 scripts/verify-admin-shell-sessions.py
```

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
