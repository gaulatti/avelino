# Atomic search expressions: observations and integration work

The native search field holds independent token objects, with raw draft text
before, after or between them. The current production editor, search request and
browser history still hold one scalar query/mode. They cannot represent these
states. This checkpoint publishes observations and an isolated Qt mechanism;
it does not claim an integrated compound-search feature.

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

Production integration must cover the complete path:

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
