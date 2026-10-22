# Atomic search expressions: observations and integration work

The candidate represents search as ordered raw-text segments and independent
token objects. The editor stores token metadata in Qt document object formats;
the controller, cancellable Tracker requests and browser history carry the full
expression. The [integrated candidate checkpoint](../evidence/development/file-input-search-atomic-integration-20261021/README.md)
records the actual source47 product and installed-runtime checks. Native
acceptance remains pending. The isolated prototype receipts below retain their
mechanism scope.

The internal expression is a list of `{kind: "text", text: "draft"}` and
`{kind: "token", mode: "filename" | "everything", query: "term"}` objects.
Raw runs retain their positions between tokens. Adjacent raw segments are
rejected because they must be one document run; malformed expressions are not
silently converted into a different query. Each request joins independently
bound segment groups. An Everything/raw group combines name containment and a
literal content phrase; a Filename group uses name containment. The controlled
native conjunction below informs this candidate; arbitrary native matching and
unfinished-draft readiness remain pending.

Each token has a stable row keyed to its document object identity. Changing its
mode updates its existing button/menu and accessible object. In the first
integration attempt a QVariantList-backed Repeater recreated those objects;
a retained accessibility interface then crashed on the next Press. The captured
trace identifies that lifetime failure. The model now uses row updates, insertion,
removal and moves. It does not reset retained delegates when a mode changes.

Token commits publish their settled document and Undo baseline after Qt completes
the edit. Notification delivery checks for synchronous control destruction.
Qt owns text command creation and grouping; supplemental selection metadata
restores a selected token when Undo brings it back. External expression loading
clears that metadata and starts a new baseline. Suggestions refer to the current
raw run. Escape first dismisses visible suggestions; the existing candidate
clear action applies after that dismissal or when no suggestions are visible.
The full native Escape sequence remains unaccepted.

Source47 passes23 indexed input cases with one expected separate-provider skip,
nine focused Qt groups, normal build/install and14 independent-consumer phases.
Two actual AT-SPI/Orca runs pass26 phases each on X11/software and scaled dark
Wayland/OpenGL; the latter uses software GL. Both production projects are absent
in those runs. Eight portable display profiles pass15 phases each with both
projects and the build absent. All256 prior closed PNG/frame/state pairs remain
exact. The ordinary package consumer contains its copied consumer project;
its library project and product build are absent. Source45's inaccurate legacy
scope flag is qualified by a separate receipt without changing its raw result.

The full58-group suite passed on source45. Source46 changes three selected
noncompiled inputs while all158 installed prefix files match45. A visual review
of its dark selected token found white text on light blue. Source47 binds that
caption to the editor's selectedTextColor, adds actual light/dark selection
assertions and diagnostic captures, and repeats the relevant current checks.
The source45 full-suite result is not relabeled as47. Build and installed module
hashes differ only by CMake's exact zero-padded RPATH replacement from
`/opt/qt/lib:` to `$ORIGIN`; measured receipts preserve both hashes and the
unchanged remaining bytes. Runtime evidence identifies the installed module.

The checkpoint preserves the three red source41 atomic regressions, source42's
stale token accessibility-interface crash and debugger trace, source43's anonymous
final-model registration failure, and source44's empty assistive-deletion failure.
The debugger exits0 after recording SIGSEGV; that is not a passing application.
The stable token model and normal Qt removal command resolve those two runtime
failures in the subsequent checks. Selected-token Undo, partial assistive deletion,
Unicode IME, external history resets, independent menus and synchronous destruction
are exercised through their respective Qt, consumer and reader paths.

Native active-field geometry, clipboard behavior, general
matching/readiness, complete hierarchy/timing, raster and reader equivalence,
physical input and independent-machine acceptance remain open. Actual reader logs
retain ChildrenChanged signature warnings also seen before this integration;
complete accessibility event delivery is unaccepted. Speech-dispatcher commands
use null audio, so physical listening is unverified. No expected image, tolerance,
mask, reference pin, exception or acceptance field changes.

Run `python3 scripts/verify-file-input-search-atomic-integration.py` to audit the
content-addressed records, exact41-47 source reconstruction, distinct execution
identities, module/prefix bindings, compound semantics, speech windows, display
captures, all256 closed pairs, current runtime sources and31503 preexisting
protected inventory fields. Its contracts reject relabeled full-suite evidence,
broadened conjunction, lost token/selection metadata, changed raw bytes and scope
or acceptance promotion. The verifier reads saved evidence; it does not rerun
the application or approve native parity.

The source47 runtime binding is checked against published commit
`6f16b95ad9f9d4e54f8be6c2fb82777d13e8d31a`. Later component or consumer repairs
retain that checkpoint's exact source and execution identity; they do not
relabel its old consumer binary as a newly built one.

Fresh regular/light native observations on macOS 27.0.1 show separate compact
mode and query cells: Filename displays `NAME` with a dropdown before the query;
Everything displays `ANY` with a dropdown. Full accessible names remain
`Filename: query` and `Everything: query`, and each token occupies U+FFFC in the
field. The search magnifier remains visible. Two short tokens already scroll
horizontally; moving to the leading caret reveals the first token and clips the
trailing one. These JPEG captures support presentation and scrolling observations,
not a lossless raster baseline or exact AX geometry. The external caller reuses
the unchanged pinned native library; it is not an independent library rebuild.

The Linux candidate now paints those compact mode/query cells with a gap between
tokens, retains the fixed magnifier and empty `Search` placeholder, and leaves
queries at their full document width for Qt scrolling. Its full menu names,
stable token identities, expression semantics, Undo and assistive editing remain
unchanged. Light/dark Qt tests exercise mode changes, accessible names, leading
and trailing scroll positions and selected captions. Exact field/cell geometry,
native dark/scaled presentation and the remaining acceptance gates stay pending.
The full source50 suite retains one failing group: its new DPR2 scrolling test
expects overflow although the responsive field is 309 units wide and its content
is only 260 units wide. A logging-only source51 diagnostic confirms that geometry.
Source52 explicitly checks a fitting cell and a query that exceeds either layout;
both DPR groups pass. Only the search-test executable changes among 14 test/module
binaries; all 158 installed files match50. The earlier full-suite failure remains
failed. Its other 57 passing groups and the corrected source52 groups have
separate execution identities. The source50 display, reader and closed runtime
evidence retains its original identity on those unchanged installed bytes.
The fresh52 consumer passes its normal flows. Its source matches50; its binary
differs in a generated Qt qmldir resource timestamp and the GNU build ID only.
The measured 23-byte difference is recorded without rewriting either binary.
The presentation capsule's 578 runtime inputs bind to published commit
`4f720b5eee7623e57f0dc263514eba85c464cffb`. Later input repairs keep those old
source52 tests and source50 runtime executions under their original identities.
The [presentation checkpoint](../evidence/development/file-input-search-presentation-20261022/README.md)
binds the scoped native captures, original failing test and subsequent Linux
executions to their exact sources. Run
`python3 scripts/verify-file-input-search-presentation.py` to audit those records.

A fresh build of the pinned Sabella source, on the same Mac, supplies the later
regular/light pointer witness. Clicking a token's query selects its U+FFFC object
without opening the mode menu; clicking its mode label or arrow opens the menu.
Double-clicking the query expands it into selected raw text. Undo restores and
selects the token; Redo leaves the caret after the inserted text. A neighboring
token retains its mode/query. At each adjacent raw-text boundary, expansion adds
one ASCII space even when that boundary already contains a space. It adds no
space at a token boundary. Thus `oak <object> cedar` becomes `oak  pine  cedar`.
The suffix case becomes `pine cedar`; typing `X` after Redo yields `pine Xcedar`.
The initial coordinate calibration missed the query and is explicitly excluded.
Stale native suggestions after Undo remain an observation, not a readiness rule.

The Linux query hit region selects the object; its double-click path commits the
raw replacement through Qt's document command. Supplemental Undo metadata keeps
the restored token selected. Focus-return callbacks revalidate object identity,
and notification delivery permits synchronous editor destruction. The popup is
anchored to the mode segment so a query click uses Qt's normal outside-press
closure. Read-only/disabled rejection, external history reset, eight observed
boundary cases, neighbor accessibility identity and actual query/mode clicks have
regression coverage. [Qt 6.8.3 text control](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quick/items/qquicktextcontrol.cpp)
owns selection removal, commit insertion and grouping into one Undo command.

The [pointer checkpoint](../evidence/development/file-input-search-pointer-20261022/README.md)
retains the initial missing behavior and the later uppercase key-helper failure
under their original source identities. Source56 passes42 indexed cases with
one expected separate-provider skip at each DPR. Its installed consumer adds
seven query-selection/expansion phases while retaining the previous flows.
General Unicode/IME expansion, clipboard/drag, native hierarchy/events/timing,
exact geometry/raster, native reader, physical and independent-machine acceptance
remain pending. The fresh native build is independent of the old build cache;
it does not constitute independent-machine acceptance. Run
`python3 scripts/verify-file-input-search-pointer.py` to audit the saved evidence.

The [native capsule](../evidence/reference-investigations/file-input-search-atomic-20261021/README.md)
contains 31 scoped projections bound to a captured CUA JSON export. First
Backspace selects an adjacent U+FFFC token; second Backspace removes it. Left
and Right select an adjacent token before crossing it. Forward Delete removes
an adjacent object immediately. A draft commit inserts a separate token at its
position. In the observed leading-draft case, the caret ends after the tokens.
Replacing one selected token retains another token and its mode/query. Menu
Undo restores and selects the original object; Redo restores the draft.

In the controlled folder, Everything(avelinoulnacerulean) shows a name-only file
and pine-only.txt. Adding Filename(pine), then changing that second token to
Everything(pine), leaves only pine-only.txt. Those projections have no busy
indicator. This supports conjunction for that fixture. It does not establish
general matching, query readiness, ranking or scope exclusion. Cmd+Z did not
restore a deleted token in this caller; enabled menu Undo did. Keyboard shortcut
routing remains unestablished. The unchanged cached pinned Sabella library was
reused, not independently rebuilt. The caller was normally cancelled and closed
with no owner result. Apple helper code and broad-draft result listings remain
external. No raster baseline or native acceptance is created.

The [Linux mechanism capsule](../evidence/development/file-input-search-atomic-20261021/README.md)
retains three isolated Qt 6.8.3 attempts. Inline document objects retain each
token's mode/query through Qt's text commands. Both plain-text and rich-text
variants pass 14 phases in attempts1/2 and24 in attempt3. Attempt1's bare C++
item has no accessible interface. Attempt2's QML host exposes text access but
lacks editable access; restored selection and scrolling are unresolved there.
Attempt3 adds editable access, restored token selection and an owned horizontal
viewport. It verifies assistive replacement/Undo/Redo, read-only/disabled rejection,
and Unicode IME preedit/commit between tokens without losing either token.
Plain-text mode exposes U+FFFC through its text property. Qt owns text command
creation and grouping; the prototype stores selection metadata at public document
Undo positions. The diagnostic PNGs were visually inspected for attempt3 and are
not native comparisons.

The integration contract covers the complete path:

1. Represent ordered tokens and raw segments in the editor and controller. Keep
   token metadata in document object formats, expose the current draft for
   suggestions, and retain the observed selection/deletion/commit behavior.
   A Backspace-only change to the scalar editor cannot satisfy this contract.
2. Give every token its own Filename/Everything menu, in that order, including
   owned presentation, Press actions, accessible children and focus behavior.
   Preserve token metadata across supported keyboard, assistive and IME paths.
   Clipboard behavior still needs native evidence; do not infer it from Qt.
3. Carry the expression into each immutable, cancellable Tracker request. Bind
   every term and preserve controlled conjunction, current-folder scope,
   notification refresh, stale-generation rejection and visible provider errors.
   Do not change indexing locations or substitute a filesystem crawl.
4. Save and restore expressions in browser navigation. Preserve result identity,
   eligibility, selection revalidation, browsing restoration, cancellation and
   callback ordering. Verify synchronous owner removal and control destruction
   across the new document/notification paths.
5. Exercise the integrated installed consumer with both development projects
   absent at runtime. Repeat X11/Wayland, display and text scaling, keyboard and
   pointer, actual AT-SPI/Orca, and closed-capture checks. Preserve existing
   images, reference pins and strict comparisons. Native raster, hierarchy,
   timing, reader, physical and independent-machine gates remain open.

Attempt3 does not yet prove external-history resets, clipboard behavior, every
command path, complete pointer/menu interaction or reentrant lifetime safety.
It runs offscreen/software without either production project mounted and is not
registered in Avelino. It provides no installed-consumer, X11/Wayland, actual
reader or native acceptance. Existing product build/runtime receipts retain their
original source identity; none are relabeled as atomic-expression verification.

Run `python3 scripts/verify-file-input-search-atomic.py` to check manifests,
source hashes, raw projection bindings, native controlled membership, prototype
reports and unchanged preexisting protected inventory values. The contracts also
reject missing restored selection, broader compound membership and promotion of
a mechanism pass to native acceptance. These integrity checks do not perform
product integration or approve equivalence.
