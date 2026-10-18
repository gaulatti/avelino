# File input Linux implementation in progress

FileInput remains pending in the parity inventory. The filesystem model, owned
column chooser, trigger, catalog and independent consumer form an implementation
checkpoint. Candidate coverage stays at 75/80 because the complete native chooser
presentation is still missing. The pinned
native observations are documented in
[file-input.md](file-input.md).

`BleeckerFileInput` has a default `title` of `Choose file…`, a required typed
`allowedContentTypes` list, and an `onResult` signal carrying `{ kind: "success",
urls: [...] }`. Cancel does not emit that signal. `initialFolder` is the Linux
presentation adapter; by default it uses Qt's Documents location. `widthOffer`
adapts a fixed caller width and `maximumWidth` propagates a containing layout's
available width. The reference fixture supplies the same 600-point parent width
as the native capture helper. It retains explicit empty titles separately from
the default-title property initializer.

The Linux type adapter uses MIME types and explicit custom descriptors. It does
not reinterpret an arbitrary Apple type identifier as a filename suffix.

| Input | Meaning in the Linux adapter |
| --- | --- |
| `"text/plain"`, `"image/png"`, `"application/pdf"` | Registered MIME type and its MIME descendants |
| `"image/*"` | Registered MIME image family |
| `"*/*"` | All existing file items; directory selection requires a separate directory type |
| `"inode/directory"` | Directory selection |
| `[]` | No eligible file or directory selection |
| `{ identifier: "org.example.article", filenameExtensions: ["article"] }` | Explicit caller-declared filename association |
| `{ identifier: "org.example.article", mimeTypes: ["text/plain"] }` | Explicit caller descriptor using registered MIME associations |
| `{ identifier: "org.example.undeclared", filenameExtensions: [] }` | File type with no declared eligible associations; distinct from an empty type array |

Descriptors may combine MIME associations and literal extensions. Unknown MIME
strings, malformed descriptors and unknown descriptor fields are errors. There
is no implicit all-files filter. The candidate adapter will project each native
fixture explicitly and retain the original source type list in comparison
metadata. MIME inheritance, extension ambiguity, declared/imported custom types,
packages and retained native type-update behavior still require parity evidence.

The model uses [Qt 6.8 filename-only MIME matching](https://doc.qt.io/qt-6.8/qmimedatabase.html#MatchMode-enum).
It never reads document contents to determine their type. Qt's MIME database is
platform data, so its conformance graph must not be reported as Apple's UTType
graph. The repository still pins the build to Qt 6.8.3 exactly.

Directory enumeration and metadata access are read-only. Hidden entries are
excluded by default, while directories remain available for navigation regardless
of file eligibility. Selection stores entry identity and returns resolved local
URLs in browser order, retaining URL encoding and directory trailing slashes.
It does not deduplicate distinct selected aliases that resolve to the same URL.
Open validates the selected items again, and a missing or changed item leaves an
explicit chooser error without sending an empty success or cancellation failure.

Cancel sends no result. A successful result is delivered while the model is
active, matching the observed native callback-before-dismissal order. A guarded
callback permits the owner to delete the model synchronously. The chooser's
presentation coordinator must preserve that order across all columns and close
every owned surface when its owner disappears.

No native owner failure result has been observed. Failure-result equivalence
remains unverified; cancellation and chooser validation errors must not be
reclassified as an invented native failure.

The UI must preserve the source action path: the secondary medium trigger opens
the complete chooser; directory navigation, multiple selection and type filtering
reach an owner result through actual Qt input. The observed native column browser
needs a corresponding owned presentation and column-selection coordination.
Default Qt/native file-dialog artwork is not a substitute. Closed trigger
proposals, complete open presentation, input timing, accessibility and physical
reader/display acceptance remain separate gates.

Column coordination must keep selection separate from navigation. A folder row
can expose its children while its parent-column selection remains the result
target. Selecting a child file replaces that result target; Command/Control
selection of a folder alongside a sibling file keeps both parent-column URLs.
Ineligible file clicks leave an existing valid selection intact. Row URLs must
be copied before resetting a directory model, including navigation initiated
directly from an entry. Current-folder errors must not redirect navigation to
the process working directory.

The first focused C++ suite covers filename-only filters, ordering, ranges and
toggles, empty/custom filters, navigation, mixed directory/file choice, Unicode
and spaces, symlinks, disappearing files, visible location errors, cancellation,
reopening, filter updates and synchronous owner deletion. These are filesystem
semantics checks; they do not establish the requested complete FileInput feature.

The Qt input suite also exercises real trigger, row, Open and Cancel controls;
Control-click selection; Escape and reopen; child-column navigation; location
typing, invalid-location recovery and Return acceptance; typed empty/custom/mixed
filters; and removal during the result callback. It captures raw diagnostic
screenshots at DPR 1 and 2. Accessible Open-button semantics are checked separately
from native hierarchy and reader acceptance.

Chooser columns and navigable rows explicitly expose accessible focus. Eligible
rows expose selectable/selected states, and the assistive Press action follows
the same browser-selection path as a pointer click. Ineligible documents retain
their visible name and unavailable description. The Qt regression invokes row
and Open actions through QAccessible and checks the resulting owner URL; AT-SPI
and Orca observations remain separate runtime evidence.

Dismissal restores keyboard focus to the enabled, visible trigger and requests
activation of its owner window. Open, Cancel and Escape exercise that return;
Space then reopens the chooser without another pointer click. A removed owner
has no surviving trigger or chooser to receive focus.

The installed consumer uses no Avelino C++ headers or library source checkout.
`--file-input` keeps native frame failures fatal. `--file-input-observe` retains
those failures for investigation while contract-state and runtime failures remain
fatal. Every context retains 32 native closed frames and all 480 direct native
sizing proposals, alongside actual Qt implicit sizes. Full direct proposal
equivalence remains pending. The first clean installed-consumer context reports
29/32 complete frame matches, 32/32 contract states and six actual owner/input
traces; this is a scoped development result, with no raster, native type,
physical-input or reader acceptance.

Generate and check the complete 256-context projection with
`python3 scripts/generate-file-input-witnesses.py --check`. The catalog accepts
`--fixture file-input`, optional `--file-input-folder`, and the 32 isolated
`file-input-*` definitions in `tests/consumer/native-file-input-witnesses.json`.
The [sealed development checkpoint](../evidence/development/file-input-20261017/validation.json)
retains all 256 closed contexts: 0 exact pixel pairs, 232 complete frame matches
and 256 contract states. All 151 earlier catalog PNG/full-metadata pairs are
byte-identical. The full installed regression runs 38 modes and 155 catalogs;
the final focused consumer rebuild reruns FileInput after its capture-helper
changes, with identical installed library bytes.

All eight virtual X11/nested-Wayland software/OpenGL profiles pass on Linux
arm64, including dark/text-1.5/DPR-2 profiles. External compositor captures retain
three actual catalog chooser/result cycles in both standard and scaled Wayland
OpenGL sessions. This is llvmpipe rendering, with physical display and hardware
acceptance pending. The complete 47-target Qt regression and final focused Qt
reruns have an explicit source binding. A new build from frozen Linux source
also passes all four focused filesystem/column/UI targets.

Earlier native-window GL popup readbacks fail on Wayland and remain preserved.
Waiting for native exposure did not resolve those readbacks. Popup diagnostics
now capture the entire scene asynchronously at native DPR, checking dimensions
and two identical readbacks. Closed strict captures keep the original method.
Cross-run popup images also contain different controlled temporary folder names,
so their raw comparison does not establish capture-method pixel equivalence.
No pixels are masked or normalized. See the checkpoint README for restoration
and `python3 scripts/verify-file-input-linux.py` for its audit.

The Linux AT-SPI operator exercise covers all eight gallery type modes, actual
multiple selection and owner URLs, Cancel/Escape, keyboard reopen, title,
disabled state, RTL, theme, text scale, callback removal and remount. A second
exercise types an invalid location, recovers, selects a child through the column
keyboard route and reopens the retained folder. It inspects showing surfaces;
Qt can retain a hidden popup window after dismissal.

Orca 46.1 and Speech Dispatcher's espeak-ng engine produce utterances for the
folder list, file names, document descriptions and location field. These are
software observations through the installed catalog with ALSA's null output.
The first reader attempts stalled after the container's absent PulseAudio server
prevented audio initialization; their logs and reader stacks remain preserved.
No physical listening acceptance is claimed. In that checkpoint the visible
invalid-location error was not announced in the observed reader log. Qt's location field exposes editable
state but not an AT-SPI EditableText interface in this environment; actual keyboard
editing works. Native hierarchy, native error-announcement and reader equivalence
remain open requirements.

The [announcement correction](../evidence/development/file-input-announcements-20261017/validation.json)
uses Qt 6.8.3's public `Accessible.announce` API with assertive priority. A visible
error is announced after the text binding updates, when reopening a retained
invalid folder, and when Return explicitly retries the same invalid path.
Deferred calls coalesce, metadata refresh stays quiet, and closing the chooser
suppresses queued announcements without moving focus. The focused Qt regression
covers initial errors, identical-path retries, recovery and cancellation.
See its evidence README and `python3 scripts/verify-file-input-announcements.py`
for the final-source build, installed-package and actual reader checks. This
correction does not close native reader or complete-chooser acceptance.

The [navigation checkpoint](../evidence/development/file-input-navigation-20261017/validation.json)
adds Back/Forward location history and a
nested New Folder prompt. History retains column locations and navigation
branches, re-enumerating directories when restoring a location. Back and Forward
clear file selection, matching the native observations. A fresh Shift range
starts at the listing's beginning in the measured alphabetic fixture. A new
navigation after Back replaces the forward branch.
History is local to the open chooser; reopening retains its last folder and
starts a fresh history. The existing typed-location error adapter remains in
place; its complete native Go to Folder presentation and invalid-path/history
equivalence are still pending.

New Folder suggests the first available `untitled folder` name, disables Create
for empty or existing names, and creates a directory only after explicit Create
or Return. It then navigates into the directory without sending an owner result.
Escape or Cancel in the nested prompt leaves the chooser open. The Linux input
adapter preserves the entered name, including spaces and Unicode, and rejects
path separators, NUL, `.` and `..` as folder names. It uses the actual filesystem's
name/case rules and an atomic `mkdir`; failures stay visible without replacing
an existing entry. A changed or vanished parent prevents creation. Directory
enumeration and type matching stay read-only; this separate explicit user action
is the filesystem mutation. Control+Shift+N is the Linux shortcut adapter for the
observed native Command+Shift+N action. Exact names, filesystem behavior,
history/input timing and native prompt artwork still require parity acceptance.

The owned dialog subclass supplies the modal state omitted by Qt 6.8.3's Quick
accessibility item. Its adapter is pinned to that exact Qt version and applies
only to the subclass's popup item. Both dialogs expose their name, Dialog role
and modal state without redundant inner dialog roles. Final Qt tests and live
AT-SPI inspection verify those states; native hierarchy equivalence stays open.
Navigable folder rows expose their current navigation selection separately from
the URLs eligible for the owner's result.

The final frozen source 29 passes six focused Qt targets, eight independent installed
contexts and eight virtual X11/Wayland renderer profiles, with 12 owner/input
traces per context. All 256 closed PNGs and complete closed/sizing metadata remain
unchanged. The consumer was freshly built against source 28; its sources are
byte-identical to source 29, and its verified binary is exercised with the final
source-29 install. The complete installed package and consumer can be restored from
bounded, checksummed chunks and run without their project sources. X11 and
scaled Wayland/OpenGL Orca exercises verify modal input, errors, creation,
history, cancellation and Space reopening. Wayland focus returns asynchronously,
about a second after cancellation in this environment; its measured delay is
retained and timing equivalence is pending. Orca output/backend commands are
logged through ALSA null output; engine audio and physical listening remain
unverified. Speech Dispatcher's level-3 dictionary errors are not evidence of
utterance contents. Run `python3 scripts/verify-file-input-navigation.py` to audit
this scoped checkpoint.

The [owned List/Icons checkpoint](../evidence/development/file-input-views-20261017/validation.json)
adds a shared model for inline List hierarchy and root-only Icons. Selection is
identified by URL across sorting and refresh; changing views prunes hidden child
selection and retains visible root selections. List disclosure survives view
changes, history and reopening, while reopening clears selection/history. Open
on a noneligible selected folder navigates without sending an owner result.

Frozen source 45 passes six focused Qt targets, including accessible menu
activation, four-column Table/TableCell and header relationships, metadata hit
testing, hierarchy levels, selection and virtual-cell cleanup during owner
removal. The consumer was freshly built against source 36; its sources remain
byte-identical to source 45, and the verified binary runs with the final install.
Eight source-free package contexts and eight virtual display profiles each
exercise 20 owner/input traces and retain 42 PNGs. All 256 closed PNGs and their
complete closed/sizing metadata remain byte-identical to the earlier checkpoint.
A restored package independently repeats one source-free context and its 32
unchanged closed images. The full 47-target suite was not rerun for this change.

X11 and scaled Wayland/OpenGL Orca runs each pass 17 phases, including disclosure,
cross-level selection through AT-SPI Selection, sorting, view changes, keyboard
acceptance, reopening, errors, history and folder creation. Four metadata cells
belong to each List row; names expose hierarchy levels and folders expose Toggle.
Visual disclosure controls are excluded from the accessible row's children.
Earlier failures, including missing header relationships and the mixed XTest
Control-plus-AT-SPI-Press selection route, remain preserved. The latter route is
unresolved; the final assistive multiselection uses Selection.selectChild.
Orca output and backend commands are observed after session exit with ALSA null
output. Native reader hierarchy, timing and engine/physical audio remain pending.

Date Added metadata is unavailable; its column shows `--` and disables sorting
without substituting creation or modification time. Name/Size/Kind sorting,
metadata formatting, exact glyphs/thumbnails, column resizing, complete native
hierarchy and broader view/input equivalence still require parity acceptance.
Run `python3 scripts/verify-file-input-views-linux.py` to audit this checkpoint.

The [native location observations](../evidence/reference-investigations/file-input-location-20261017/investigation.json)
also distinguish three states the Linux location controls must preserve: current
folder choice is a selection-preserving no-op; ancestor/recent navigation enters
open-panel history and clears file selection; persistent Recent Places changes
only after successful selection and promotes an existing folder without duplication.
The observed order survives a fresh same-bundle process. The later
[native policy supplement](../evidence/reference-investigations/file-input-location-policy-20261017/investigation.json)
records a ten-folder pool shared by two distinct consumer bundle identifiers.
Cross-directory file acceptance and selected-directory acceptance record the
visible folder. A directory chooser can also accept that folder without a selected
row. Linux locations have the scoped implementation described below.
The native Go to Folder sheet has its own path field and suggestions. Its missing-
path Escape preserves the underlying selected file. The current always-visible
Linux path field does not establish equivalence to that nested presentation, and
the earlier file-path input/dismissal experiments remain diagnostic. The later
helper with normal Edit menus confirms existing-file selection without owner
submission, selection retention for same-folder submission, explicit hidden-folder
navigation and successful raw path-input retention. Cancelled invalid input does
not replace that retained input. A path-selected PNG is accepted under the
text-only configuration while ordinary selection of the same row is disabled;
other type arrays, relative-input resolution and suggestion timing remain pending.
The inline directory field does not implement those native path-selection rules.

The [later Go to Folder lifecycle trials](../evidence/reference-investigations/file-input-go-to-20261018/README.md)
also require separate state for the raw field, selected proposal and underlying
chooser selection. The native AX Close button clears the field, Escape cancels
the nested sheet, and Return or a completed pointer double-click navigates to
the selected proposal. Down changes that proposal without rewriting raw input;
Tab can extend a shared prefix. Invalid input/cancellation must not mutate the
owner selection or remembered successful input. The observed `..`, `../` and
`../A.txt` outcomes do not justify applying an assumed POSIX normalization rule
or claiming complete relative-path equivalence. Suggestion ranking/history,
native timing and atomic paste remain unproven. The separate Linux sheet,
suggestion model and path-selected file route are still missing.

The [navigation-only history trials](../evidence/reference-investigations/file-input-go-to-history-20261018/README.md)
distinguish two more persistence boundaries. Go to Folder shows five observed
recent targets shared across consumer identities, promotes a chosen target on
successful navigation before any owner acceptance, and separately retains the
literal successful field, including empty input. Ordinary ancestor/row browsing
does not change that observed pool. Where Recent Places remains success-only
and unchanged by twelve such navigation-only folders. The current Linux store
has only Where folders and saved raw input; a separate target history is still
required. General history capacity, suggestion ranking and unavailable-target
handling remain pending.

The [owned location checkpoint](../evidence/development/file-input-location-20261017/validation.json)
adds a Where menu with the current folder, its ancestors and Recent
Places in a separate menu window. Choosing the current folder preserves file
selection and history. Ancestor/recent navigation clears selection and enters
Back/Forward history without calling the owner. Escape closes only this menu;
removing the input owner also removes its menu. The opener exposes the visible
menu as its accessible child, with the corresponding parent relationship,
expanded state, item actions and focus. This relationship is scoped to the owned
chooser classes rather than changing unrelated Qt controls.

Recent Places uses the per-user `Avelino/FileChooser` QSettings store, shared by
Avelino consumers. On Linux this follows XDG configuration paths; the default is
`~/.config/Avelino/FileChooser.conf`. Successful acceptance promotes the visible
folder, removes duplicates and retains ten entries. Browsing, cancellation and
history navigation do not update the pool. A separate short-lived lock covers
the read/promote/write transaction, in addition to QSettings' own atomic-write
lock. Invalid or unsupported settings remain intact and produce a visible menu
error; missing saved folders remain visible but disabled. Native equivalence for
unavailable mounts, symlink identity and storage errors is still pending.

The pinned Qt 6.8.3 Wayland implementation requires a native input serial when
opening a grabbing popup. Assistive actions provide no new serial: the earlier
runs show an unanchored first window and a later grab dismissed by the compositor.
The owned adapter uses Qt's non-grabbing `xdg_popup` surface path, then restores
the logical Popup window type and Qt's popup stack for keyboard and pointer
routing. It explicitly focuses an enabled menu item and closes the menu when
the application becomes inactive. The window guard only applies to the menu's
own popup window. These private Qt interfaces are version-asserted; revalidate
them before upgrading Qt. The [pinned shell implementation](https://raw.githubusercontent.com/qt/qtwayland/v6.8.3/src/plugins/shellintegration/xdg-shell/qwaylandxdgshell.cpp)
and [Qt popup input routing](https://raw.githubusercontent.com/qt/qtbase/v6.8.3/src/gui/kernel/qguiapplication.cpp)
explain the distinction between surface grabs and logical popup input delivery.

The focused Qt tests cover the actual menu controls, selection/history, recent
reload after remount, owner removal and outside clicks. Backend tests separately
exercise fresh processes, concurrent writers, ten-entry promotion and invalid
settings preservation. Installed-consumer checks use a fresh independent consumer
build, with its source bytes checked before reuse against later library builds.
Virtual display profiles and reader transport are recorded separately. The
Wayland reader test explicitly focuses the X11 host of the nested compositor;
Xvfb PointerRoot is not a valid destination for its XTest keys. Reader child exits,
raw ChildrenChanged signature warnings and failed attempts remain diagnostic
evidence. Physical input/display, native reader hierarchy and speech-engine audio
acceptance remain pending.

The complete native panel also has a sidebar, search, selection preview and
group/sort controls. These remain missing from the Linux
implementation. Its path field and columns must not be reported as the
complete native presentation. Location-menu artwork, the separate Go to Folder
sheet and its path-selected file rules also remain pending. Direct two-axis sizing, type conformance, source input and
callback timing, strict raster, physical display/input and independent-machine
acceptance also remain pending.
