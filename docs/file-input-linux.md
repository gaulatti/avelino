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

The complete native panel also has a sidebar, back/forward and view controls,
location menu, search and selection preview. These are missing from this Linux
checkpoint. Its path field and columns must not be reported as the complete
native presentation. Direct two-axis sizing, type conformance, source input and
callback timing, strict raster, physical display/input and independent-machine
acceptance also remain pending.
