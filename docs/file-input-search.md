# FileInput indexed search candidate

Search remains part of the pending FileInput implementation. Native acceptance,
complete chooser presentation, native hierarchy/reader behavior and physical
verification remain open. The candidate uses the pinned desktop observations;
it does not change their images, tolerances, references or approval gates.

The owned Search field opens results from the existing session index. Raw text
matches filenames and indexed contents. Down/Return selects Name Contains and
creates a Filename token. The Content Contains suggestion instead creates an
Everything token that still matches both filenames and contents: the native
single-word fixture exposes its name-only file and `pine-only.txt` in that mode.
It must not be implemented as a body-only filter. These source observations are
controlled AX projections; general query-completion and owner-delivery acceptance
remain pending. A later [controlled native investigation](../evidence/reference-investigations/file-input-search-owner-menu-20261021/README.md)
records five successful callbacks across AppKit and SwiftUI caller hosts, including
normal owner removal during the last Filename result. Public NSOpenPanel visibility
is true at each callback; private importing state and exact visual ordering remain
unverified. Both helpers use the same unchanged cached pinned library object;
only their callers were rebuilt. The actual runtime is macOS 27.0.1 (26A434), with
SDK 27.0; the minimum compilation target macOS 26.0 is a separate fact.

The Linux candidate has three presentation states: raw `general`, `filename`
and tokenized `everything`. General/Everything combine case-insensitive filename
containment with a bound literal full-text phrase in Tracker; Filename uses only
filename containment. Arbitrary native phrase/punctuation, normalization,
stemming, ranking and additional criteria remain unverified. Token editing and
menu artwork/hierarchy are also pending native equivalence. From either token,
the native menu offers exactly Filename and Everything, in that order. The Linux
menu follows those two choices; raw general search remains available by typing.
Some CUA projections duplicate the native menu, so complete object identity is
not established. The saved CUA screenshots have elided JPEG bytes and cannot
serve as raster baselines.

The owned candidate toolbar keeps Search on a second row when the available
logical width is below 640. Its suggestions then open below the scope controls;
at ordinary widths the suggestions align inside the chooser's right edge.
This keeps location and scope controls reachable on the 400-point offscreen
desktop used by the DPR2 input tests. The compact layout is Linux functional
evidence; corresponding native layout and raster equivalence remain unverified.

The default scope is the session's system index. Current-folder scope uses an
encoded, trailing-slash directory URI, includes descendants and excludes a
similarly prefixed sibling, including an outside content-only match. Native
repository copies observed globally were absent in initial controlled folder
projections. Later Everything projections include two v24 snapshot copies outside
the root despite the selected folder radio. Stable native membership, general
exclusion and query completion remain unverified; this unexplained result does
not change the Linux scope policy.
The application never changes the user's indexed
locations or substitutes a directory crawl. Unindexed files remain subject to
the system provider's policy. The `This Computer` label is a Linux candidate;
OS presentation acceptance has not been approved.

Queries run through cancellable public Tracker 3.7.1 APIs on a private worker
context. Index notifications refresh the active query. Changing query, mode or
scope cancels earlier work and ignores older generations. Closing or removing
the owner cancels its work and suppresses late results. Indexing locations,
permissions, extraction configuration and service installation remain outside
the chooser's mutation path.

Results retain filesystem identity and expose the existing filename-only MIME
type adapter. Eligible selection is revalidated before delivery; a vanished or
changed item produces a visible chooser error and no owner result. A sole
noneligible selected directory navigates into it. Successful callbacks occur
while the chooser is still active and may synchronously remove the owner.
Cancel sends no result. Icons and flat result presentations share selection.
A C++ owner observer cancels the chooser when its control leaves its window or
is destroyed. This also covers Loader removal after QML callbacks have been
disconnected but before deferred object deletion, preventing a result during
that interval. A C++-owned browser may also be deleted from a selection callback.
Search results use the chooser's shared accessible result view, backed by the
same private row/selection contract as directory results. Assistive clients can
query, add, remove and clear selections, including rows outside the viewport.
The mode token exposes its owned menu and Press action through that same menu
relationship used by the location control. These Qt interfaces do not establish
native hierarchy, screen-reader or physical acceptance.
The query field also reuses the chooser's editable-text adapter. Assistive text
replacement follows Qt input-method commits, preserving the field's normal
query updates, read-only checks and undo behavior. Restoring browsing for an
empty query leaves an already focused editor active, so typing and native Qt
undo/redo can continue. Qt owns the grouping of consecutive input-method edits.
The [search accessibility checkpoint](../evidence/development/file-input-search-accessibility-20261021/README.md)
retains actual AT-SPI/Orca runs on X11/software and scaled dark Wayland/OpenGL.
Each covers twelve phases, including offscreen and multiple selection, token
Press/menu actions, selected-result speech before Return, editable query text,
native undo/redo, owner delivery and cancellation. Speech-dispatcher commands are
observed with null audio output; physical listening and native reader comparison
remain pending. Earlier failures and the invalid manual Loader-deletion test are
retained separately from the corrected Loader-unmount regression.

The [token-menu checkpoint](../evidence/development/file-input-search-menu-20261021/README.md)
adds fourteen-phase reader runs 7/8, including both token menus with exactly two
choices. Its portable consumer repeats three flows and eight display profiles;
all 256 closed PNG/frame/state pairs are unchanged. These runs execute source 26.
All 158 installed prefix files are byte-identical on source 27, which independently
passes all nine focused Qt groups. Source 27 changes only the test fixture: the
vanished-selection case creates its own valid temporary image instead of deleting
and restoring the shared canonical image needed by later selection tests.
Source 26's earlier two-scale failure and the passing direct-provider diagnostic
are retained; the precise provider timing cause is unproven. The full 58-group
result belongs to the historical source 24 checkpoint.

The search-specific editable adapter also keeps token metadata with Qt's undo
positions. Replacing a complete token by keyboard or the editable-text interface
returns to raw input; Undo and Redo restore the associated token presentation.
Committing a Filename or Everything token starts a new Undo baseline: earlier
literal edits become unavailable, and Undo leaves the committed token unchanged.
Qt retains its normal grouping for subsequent edits. The adapter uses the undo
cursor, history reset and cached availability properties in the
[pinned Qt 6.8.3 implementation](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quick/items/qquicktextinput.cpp);
an exact-version compile guard requires revalidation before upgrading. Qt owns
text command creation and grouping. Restoring token metadata during Undo/Redo
preserves the remaining history. Availability and mode notifications allow the
control to be synchronously destroyed by their observers. Read-only replacement is rejected, identical
literal replacement still removes the token, and changing the query externally
clears the text undo history through Qt. The shared Go To editor is unchanged.

The [token-editing checkpoint](../evidence/development/file-input-search-token-editing-20261021/README.md)
retains the failing regressions and source repairs. Source 34 passes all nine
focused groups, and its 158 installed files are byte-identical to source 36.
Its installed consumer passes three flows, including replacement,
Undo and Redo. A separate runtime with both development projects absent passes
all eight display profiles with ten search phases each. Two actual AT-SPI/Orca
runs pass 17 phases each on the identical module, and all 256 closed FileInput
PNG/frame/state pairs are exact in eight source-free contexts. These results
remain candidate evidence; they do not replace the historical full 58-group
result or close any native, physical or independent-machine gate. The final
source 37 build renames the private edit helper to preserve Qt's inherited
`state` getter and repeats the focused groups, consumer, reader, portable and
closed comparisons on that new binary. `current-candidate.json` identifies
that checkpoint's source 37 executions; the source 34/36 records remain historical evidence.

The [token-baseline checkpoint](../evidence/development/file-input-search-token-baseline-20261021/README.md)
preserves source 38's two new regression failures. Applied source 40 passes all
nine focused Qt groups and the independent consumer. Its 4,116 selected inputs
and all 158 installed files exactly match isolated source 39. That explicit
identity binds source 39's eight portable display profiles, two 17-phase
AT-SPI/Orca runs, 256 exact closed capture/state pairs and three synchronous
control-lifetime cases. Those remain source 39 executions. The full 58-group
suite remains historical source 24 evidence.

The [native baseline control](../evidence/reference-investigations/file-input-search-token-baseline-20261021/README.md)
shows Undo disabled on the selected committed Everything token while Cut, Copy
and Delete are enabled. Backspace clears it and enables Undo; menu Undo restores
the token with Undo disabled and Redo enabled; menu Redo clears it again. The
original caller was still running and was not relaunched. It was then normally
cancelled and quit, with process absence verified. Result membership after Undo
initially remains stale, so general query readiness and native parity stay open.

The [fresh native history investigation](../evidence/reference-investigations/file-input-search-history-20261021/README.md)
observes whole-token replacement returning to a raw field and a later Undo
restoring the old Filename token. It does not establish a single atomic Undo
step: the first key Undo leaves the field unchanged, then the enabled menu Undo
restores the token. Suggestions and result membership initially remain stale.
Changing folder scope refilters the restored token. The candidate's reversible
presentation is scoped behavior; complete native edit/commit, predicate, reader
and raster equivalence remain pending.

Escape from a nonempty field clears search to the preceding browse location.
Back/Forward retain the query/token and scope while clearing selection; a new
query after Back replaces the forward branch. The native Forward diagnostic
restored its token but exposed inconsistent membership, so complete native
history, readiness, focus and timing equivalence remain unverified. The fresh
native run repeats the discrepancy in both complete serialized text and the
displayed chooser: Forward restores Filename/folder scope but shows eight
recursive files instead of the preceding single name match. Back clears selection
and returns to browsing; a different query after Back resets scope to This Mac
and replaces the Forward branch in that controlled case. The unexplained result
membership does not define a new Linux query rule.

Building requires Ubuntu 24.04's `libtracker-sparql-3.0-dev` 3.7.1 and pkg-config.
Runtime search uses `org.freedesktop.Tracker3.Miner.Files` on the session bus,
with Tracker's filesystem miner and extractors. The library adds no playback
backend. Missing index service or query failure stays visible; there is no
filename-only fallback. Existing system indexing policy is authoritative.

`tests/components/run-file-search.py` creates only a fresh controlled tree under
the current home, private XDG/GSettings directories and a private session bus.
It preserves an existing GUI runtime directory so Wayland/accessibility sockets
stay connected, and creates a private runtime only when none is supplied.
It does not override HOME or edit host index settings. `/tmp` is unsuitable for
these fixture files because Tracker excludes it even when listed explicitly.
The private bus and its activated indexer/extractor share an owned process group.
The wrapper stops and waits for that group before deleting its controlled tree,
preserving the client exit status and leaving other sessions' processes alone.
The unavailable-provider variant uses a real private bus without service
activation directories. No fabricated index or mocked search response is used.

The Qt input suite exercises names/contents, Filename/Everything, scopes,
recursive inclusion, live updates, quotes, validation, history, cancellation,
reopening and owner removal. The independent installed consumer uses public
QML properties and real Qt input through `--file-input --file-input-search`;
the wrapper supplies `--file-input-search-root`. Its missing-provider variant
checks the visible error and cancellation. New reports/captures remain scoped
runtime evidence, with strict raster and native/physical/reader acceptance false.

From the independent installed-package directory,
`bash check-display-sessions-file-search.sh "$PWD/display-search"` runs eight
X11/Wayland, software/OpenGL and display/text-scale profiles. The consumer checks
the owner result and cancellation, then reopens a selected Everything search and
keeps it mapped until the full-output capture writes the usual `.captured`
acknowledgement. These are virtual-session checks with synthetic Qt input; native
visual, physical display/input and reader acceptance remain pending.
