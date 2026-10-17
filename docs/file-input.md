# File input source contract

`BleeckerFileInput` is pinned to `Sources/Sabella/Extended.swift:70–75` at
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`. It displays the caller title through
`BleeckerButtonStyle(.secondary)`, whose default size is medium. The default title
is `Choose file…`; an explicitly empty title remains a separate input. Its
required `allowedContentTypes` array is passed to SwiftUI's file importer, and
multiple selection is enabled. The owner receives `Result<[URL], Error>`.
The source does not read, upload, copy, rename or delete selected files.

Before Linux implementation, establish these observable criteria:

- Measure unchanged public, geometry-probed and literal-body witnesses, including
  the default/empty/literal/multiline/Unicode title, inherited styling, disabled
  state, caller bounds, native control size, layout direction, light/dark,
  text scale and display/bitmap DPR. Keep direct proposals separate from caller
  frame allocation and inherited ButtonStyle behavior.
- Observe actual panel flags and type filters for empty, specific, broad,
  overlapping, directory, mixed and custom type arrays. An OS type identifier is
  not automatically a filename extension or a MIME type; document a Linux API
  adapter and retain unresolved conformance differences.
- Record opening, successful single/multiple selection, order and URL handling,
  cancellation, repeated opening, owner updates and removal during a callback.
  Determine whether cancellation calls the owner; do not invent a cancellation
  error or an empty success result. Preserve actual error domain/code evidence.
- Probe only task-owned fixture files. Do not read file contents through the
  component or retain names from unrelated folders. Keep programmatic native
  panel/own-process events separate from physical pointer and keyboard evidence.
- Avelino owns the complete Qt trigger and chooser presentation. Use Qt semantic
  mechanisms for files, input, focus and accessibility; default platform dialog
  artwork is not an owned Linux presentation. Verify filtering, navigation,
  multi-selection, acceptance/cancellation and callback lifecycle through the
  installed independent consumer and catalog, with X11/Wayland profiles.
- Keep native fonts/raster, panel material and placement, exact type conformance,
  source input/callback timing, accessibility hierarchy, physical input/display,
  readers and independent-machine replay as distinct acceptance gates.

Desktop candidate coverage remains 75/80; FileInput is pending. The native
helpers, Apple source archives and build products remain outside Avelino.

## Native source investigation

The [sealed record](../evidence/reference-investigations/file-input-20261017/investigation.json)
contains 32 fixtures in light/dark, text scales 1/1.5 and bitmap DPR 1/2:
256 contexts and 768 closed images. The unchanged public initializer, its
geometry-probed witness and a literal body agree in every context. Body and
caller frames agree between the two measured branches. All 11,520 direct native
sizing responses agree across those branches; these proposals omit the caller's
fixed frame and remain separate from capture geometry. The offscreen native
windows are inactive with actual backing DPR 2. The deployment target is macOS
26.0; the recorded host and SDK are macOS 27.0.

The default light, scale-1 trigger measures 116 by 40; the explicit empty title
measures 36 by 40. The default title's unspecified proposal returns 116 by 40,
while a width-30 proposal returns 36 by 187. Fixed caller frames, inherited
styling and native control-size cases remain in the complete matrix.

CUA interactions through the unchanged public component selected only controlled
fixtures. Seven successful callbacks record single selection, multiple selection,
removal in the owner callback, reverse click order, a symlink, a mismatched PNG
extension and a directory. Selecting `two.txt` before Command-selecting `one.txt`
still returns `[one.txt, two.txt]` in this browser's order. The symlink returns
its target URL. The directory URL retains its trailing slash. Every observed
success callback runs while `NSOpenPanel.isVisible` is still true; removing the
control inside that callback closes the panel without a crash. Normal Cancel
leaves the result count unchanged. No owner failure domain/code was observed.

For `public.image`, clicking an extensionless file containing PNG bytes leaves
Open disabled; a controlled plain-text file named `fake.png` can be selected and
returned. `public.folder` sets directory selection on and file selection off.
The empty type list disables both file and directory selection and leaves the
tested file unselectable. A subsequent retained
instance update to `public.item` allows highlighting a file but leaves Open
disabled. This last result requires isolated fresh-process investigation before
choosing a Linux type policy. These observations do not establish a general
UTType-to-extension or MIME mapping.

The first own-process panel helper used an unsupported `ok(nil)` action and
terminated with an AppKit exception. The corrected diagnostic canceled and
reopened all three branches, but its Return events did not complete selection.
Both attempts remain preserved. The panel's cached `directoryURL` property did
not prove the remote chooser was displaying that folder; normal CUA Go To Folder
navigation and controlled AX rows established the actual location. Filtered AX
excerpts are diagnostic records, not full accessibility acceptance. No open-panel
raster was captured or approved.

Fresh source builds use the same immutable 89-file archive with no prebuilt
library inputs. Their closed/sizing outputs are compared byte-for-byte in
`source-replay.json`, including any differences. The UI diagnostic uses an earlier
source-built object from that same pin; its fresh behavior replay remains pending.
The source-only archive and native helpers stay outside Avelino, with checksums
recorded here. Independent-machine availability, Linux implementation, exact
type conformance, callback/input timing, chooser artwork, fonts/raster, physical
display/input and readers remain pending.

Run `python3 scripts/verify-file-input-source.py` and
`python3 -m unittest discover -s tests/contracts -p 'test_file_input_source.py' -v`
to verify the sealed investigation and its acceptance guards.
