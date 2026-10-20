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
The current Linux implementation checkpoint and its unresolved presentation,
visual and accessibility gates are documented in [file-input-linux.md](file-input-linux.md).

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
disabled. Retained type-update behavior remains unresolved; fresh-process probes
are recorded separately below. These observations do not establish a general
UTType-to-extension or MIME mapping.

The [fresh-process type supplement](../evidence/reference-investigations/file-input-types-20261017/investigation.json)
records four separately started native processes. `public.item` successfully
returns `one.txt` in a fresh process. A text/image union returns
`[one.txt, photo.png]`; a separate folder/text union returns `[folder/, one.txt]`.
The first union permits files; the second permits both files and directories.
An undeclared `org.avelino.fixture` type reaches an empty native panel type list,
while its file-choice flag remains true; clicking the controlled text file leaves
Open disabled and Cancel returns no result. This differs from the original empty
input array, which disables file choice itself.

These processes reuse the recorded source-built FileInput library object.
Their 16 filtered AX observations and three successful callbacks resolve the
fresh-process broad-type question. The earlier retained-update failure remains
preserved and unresolved; neither physical input nor an independent behavior
source replay is claimed. Run `python3 scripts/verify-file-input-types.py` to
recompute the supplemental record.

The first own-process panel helper used an unsupported `ok(nil)` action and
terminated with an AppKit exception. The corrected diagnostic canceled and
reopened all three branches, but its Return events did not complete selection.
Both attempts remain preserved. The panel's cached `directoryURL` property did
not prove the remote chooser was displaying that folder; normal CUA Go To Folder
navigation and controlled AX rows established the actual location. Filtered AX
excerpts are diagnostic records, not full accessibility acceptance. That initial
record did not capture or approve open-panel raster.

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

## Native open-panel presentation

The [panel supplement](../evidence/reference-investigations/file-input-panel-20261017/investigation.json)
adds three unmodified CUA JPEG screenshots: unselected, one selected file and two
selected files. All show the 880-by-448 native panel at bitmap scale two. Go to
Folder and the column scrollbar put controlled fixture files in view. Open
returns both selected URLs in browser order while the panel remains visible.

The native presentation includes a sidebar, back/forward and view controls,
location menu, search, selection preview, New Folder and group/sort controls.
The owned Linux implementation remains in progress; path entry and columns do
not establish complete panel equivalence.
The native OS supplies text/document previews even though the public component
itself does not read the selected files. Host sidebar names and ancestor folders
are observations of this configured host, not Linux defaults to hard-code.

The supplement retains filtered AX text, source callback trace, panel flags,
helper and binary hashes, and host versions. CUA supplies lossy JPEG bytes, so
lossless panel captures for strict comparison remain pending. It reuses the recorded source-built
library. Full context coverage, exact panel comparison, physical input/display,
readers and independent behavior-source replay remain pending. Run
`python3 scripts/verify-file-input-panel.py` to audit the supplement.

The [controls supplement](../evidence/reference-investigations/file-input-controls-20261017/investigation.json)
records actual Columns/List/Icons changes, group and Option-sort menu entries,
location menu entries, a no-match search and its scopes, and nested New Folder input.
An existing default name changes the suggestion from `untitled folder` to
`untitled folder 2`. Existing file or directory names immediately disable Create
and show `This name is already taken.` Empty input also disables Create. Return
creates the folder and navigates inside it; actual Back and Forward return to
the parent and created directory. Command+Shift+N opens the nested prompt, and
Escape closes that prompt while leaving the chooser open. None of those actions
send an owner result. This earlier supplement does not exercise positive search.
Grouping/sort behavior, menu artwork and lossless raster equivalence remain
unverified. Run
`python3 scripts/verify-file-input-controls.py` to audit these observations.

The native history-selection probe also shows that Back clears a prior single
or multiple file selection, and Forward clears a previously selected child.
Shift-clicking c after Back selects a,b,c in its controlled alphabetic fixture.
The Linux history implementation follows those observations rather than retaining
selected files across locations. Full selection/input context equivalence stays
pending.

The [views supplement](../evidence/reference-investigations/file-input-views-20261017/investigation.json)
records inline List expansion, selection across root and child rows, pruning on
collapse and view changes, Icons folder navigation through Open, and retained
view/expansion state on reopening. Four callbacks preserve their exact observed
URL order; general ordering across directories remains unresolved. List requires
a hierarchy and selection shared with the other views. Owned Linux List and Icons
have a scoped implementation; complete presentation, metadata and input parity
remain pending. The supplement's README explains a separate Return
acceptance during a menu experiment and the native panel's asynchronous AX update;
neither is treated as automatic submission by a view change. Run
`python3 scripts/verify-file-input-views.py` to audit the native observations.

The [location supplement](../evidence/reference-investigations/file-input-location-20261017/investigation.json)
records current-folder and ancestor choices, successful-folder Recent Places,
ordering and a separately started process. Choosing the current folder preserves
selection without adding a navigation step. Ancestor and recent navigation clear
file selection and enter Back/Forward history. In the three single-file cases,
Recent Places records the containing folder; browsing and cancellation do not add or reorder
those entries. Reaccepting an older folder promotes it without duplication, and
the observed order survives a fresh same-bundle process. Three successful
callbacks preserve exact controlled URLs; the fresh process finishes without an
owner result. These single-file observations leave capacity, cross-application
scope and recent updates for cross-directory or directory selections unresolved.

Go to Folder is a separate native sheet with path entry and suggestions. A
verified missing path leaves it open without a candidate; Escape preserves the
prior file selection. File-path input/dismissal experiments remain diagnostic
because the minimal helper and immediate AX observations were inconsistent.
The initial narrow-root callback redaction and snapshot-output binding limitations
are retained explicitly. Original JPEGs and filtered AX records do not establish
menu artwork, complete hierarchy, physical input, readers, timing or strict raster
acceptance. Run `python3 scripts/verify-file-input-location.py` to audit the record.

The later [recent-policy and path-input supplement](../evidence/reference-investigations/file-input-location-policy-20261017/investigation.json)
records sixteen successful callbacks across three processes. Twelve accepted
folder locations leave the latest ten Recent Places entries, newest first. A
second consumer with a different bundle identifier sees that pool before making
any selection. Cross-directory file selection and selected-directory acceptance
record the visible folder, rather than each returned URL's parent. A directory
chooser with no selected row can accept its current folder.

With normal Edit responder menus, Go to Folder selects an existing file without
calling the owner and preserves selection when the current folder is submitted.
Successful path input persists as entered across openings and these consumer
processes; cancelling invalid input keeps the previous saved input. The text-only
configuration accepts a path-selected `Blocked.png`, while ordinary pointer
selection of that same row remains disabled. This route-specific observation
does not establish the path-selection rule for other type arrays. Explicit
hidden-folder navigation succeeds; relative-input resolution and suggestion
timing remain unresolved. The source library object is reused, and the initial
missing-resource startup failure is preserved. This supplement does not establish
an independent source rebuild, native artwork, reader or physical acceptance.
Run `python3 scripts/verify-file-input-location-policy.py` to audit its bounded
observations, capture provenance and exact callback URLs.

The [Go to Folder lifecycle supplement](../evidence/reference-investigations/file-input-go-to-20261018/README.md)
measures the sheet's clear control, selected suggestions, Return/Escape, pointer
double-click and Tab completion against a controlled tree. The AX Close button
clears rather than dismisses. A suggestion can navigate independently of the raw
input retained for the next opening. Invalid input preserves the owner selection
and saved input. Child, parent-relative and prefix trials are recorded exactly;
general path normalization, ranking, history capacity and timing remain pending.
It repeats the plain-text route-specific PNG result. Failed paste, Command+A,
AX double-click and screenshot attempts remain visible with corrected trials;
their actions do not count as completed input. Audit it with
`python3 scripts/verify-file-input-go-to.py`.

The [navigation-only history supplement](../evidence/reference-investigations/file-input-go-to-history-20261018/README.md)
adds twelve successful Go to Folder navigations, three terminal processes and
76 complete capture receipts without an owner callback. Its empty field shows
five recent paths shared across two consumer identities; choosing an existing
recent target promotes it without duplication and can retain empty raw input.
Ordinary ancestor/folder-row browsing leaves that pool unchanged. Where Recent
Places does not promote the navigation-only folders. These different update
boundaries need separate persistence. Five is the observed displayed pool;
general storage capacity and suggestion ranking remain pending. The earlier
twelve-sibling capture is headed "Go to:", so it does not prove recent-history
capacity. Run `python3 scripts/verify-file-input-go-to-history.py`.

The [empty-field Close supplement](../evidence/reference-investigations/file-input-go-to-empty-close-20261018/README.md)
adds its second behavior: Close dismisses the nested sheet when the field is
empty. The nonempty-field action still clears it. The attempted relative setup
and later keyboard retry are retained as excluded diagnostics; they establish
no new resolution or input-timing rule. Audit the bounded transition with
`python3 scripts/verify-file-input-go-to-close.py`.

The [owned Linux location checkpoint](../evidence/development/file-input-location-20261017/validation.json)
adds the Where menu and shared ten-folder Recent Places store. Current-folder
choice preserves selection/history; ancestor/recent navigation clears selection
without submitting. Its Qt, independent installed-consumer, virtual-display and
AT-SPI/Orca evidence is scoped in [the Linux implementation notes](file-input-linux.md).
FileInput and strict native parity remain pending, including the separate Go to
Folder presentation and its path-selected file rules.

The [owned Linux GoTo checkpoint](../evidence/development/file-input-go-to-20261018/README.md)
now implements the separate sheet, independent recent targets/raw input and
path-selected-file route. Source60 passes eight focused Qt targets, fresh
source-free consumer checks in eight contexts and eight virtual display profiles.
The new actual AT-SPI/Orca flow, general ranking/history capacity/relative rules,
all native type/context/sizing/artwork and physical acceptance remain pending.
FileInput stays pending; no closed expectation or reference pin changes.

The [positive search observations](../evidence/reference-investigations/file-input-search-20261020/README.md)
separate filename and content matching with a single-word controlled token.
The raw query exposes a name-matching file and `pine-only.txt`, which contains
that token in its body. Choosing Name Contains through Down/Return creates the
Filename token and exposes only the name-matching file. The long query also
shows an uppercase name, a matching folder and a nested file; current-folder
mode retains that nested result. This is observed recursive inclusion, with
cross-folder exclusion and general query semantics still unverified.

These records are controlled CUA accessibility projections, not raw AX archives
or an independent native library replay. Search defaults to This Mac on this
host. Its scope radios and Where label can disagree, so the label alone does
not establish scope. Busy indicators do not establish query completion.
Clearing search restores the controlled browse folder after accessibility-tree
recovery. Open remains disabled in search and a fresh ordinary/plain-text
baseline, so the cause and search owner delivery remain unverified. The sibling
control has null queried Spotlight metadata and does not prove scope exclusion.
Run `python3 scripts/verify-file-input-search.py` to audit the retained fixture
bytes, projection and isolated Linux provider experiment. FileInput stays pending.
