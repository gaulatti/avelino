# Native Go to Folder recent-history lifecycle

Three processes use the unchanged pinned helper and a controlled tree with twelve
folders. They finish with exit 0 and no owner callbacks. The two consumer bundle
identifiers are distinct. This supplements the earlier path-sheet lifecycle
record; neither sealed record, reference pin nor expected image is changed.

The first process navigates through History-01 to History-12 using Go to Folder,
verifying each proposed absolute target and resulting chooser folder. No file is
selected or accepted. The empty path field then shows exactly History-12 through
History-08 in Recents. A History- query returns those same five paths. History-01
instead produces five approximate recent suggestions and does not include the
existing History-01 folder. Other.png, a distinct prior path from the preceding
process, has no proposal here. These are bounded presentation/search results;
the underlying storage capacity and general ranking algorithm remain pending.

Cancelling these queries preserves the successful literal History-12 input.
Where Recent Places still starts with Navigator Root and contains none of the
twelve navigation-only destinations. Its current-folder/ancestor section does
contain History-12; the two sections are checked separately.

The second consumer starts with the same saved History-12 input and empty-field
five-path pool. Single-clicking History-10 then pressing Return navigates there,
with the field still empty before submission and no owner callback. Reopening
has an empty field and promotes History-10 without duplication, followed by
History-12, History-11, History-09 and History-08.

A fresh original consumer sees that exact promoted pool and empty input. It
cancels the nested sheet, chooses the parent from Where, and double-clicks the
ordinary History-01 folder row. The chooser reaches History-01 while the next
Go to Folder opening retains the same five paths and empty field. This observed
ordinary browsing does not promote Go to Folder history.

The earlier twelve-row path prompt has the heading "Go to:", not "Recents".
Its twelve controlled sibling suggestions cannot establish a twelve-entry
recent-history pool. The verifier reads that unchanged older capture as well.
The implementation needs separate raw successful input, selected-target history
and success-only Where recent folders; they have different update boundaries.

All 76 AX captures have PID/time/count/raw-hash receipts. Filtered copies omit
the sidebar subtree, unrelated URL rows and unrelated menu ancestors, preserve
original indices, and remove trailing blank lines. Ten original CUA JPEGs are
copied byte for byte; none is resized, cropped, masked or re-encoded. Apple source
and binaries remain external, and no global preference reset is used.
Their original dimensions vary: 920x690, 920x430 and 920x494. This record preserves
that variation and does not establish a fixed native sheet height or sizing rule.

Run `python3 scripts/verify-file-input-go-to-history.py`. These are same-host,
reused-helper observations under public.plain-text. General history capacity,
ranking, relative resolution, unavailable targets, timing, independent source
rebuild, native reader, physical input/display, complete context and strict
raster acceptance remain pending. Linux Go to Folder is not implemented yet.
Desktop coverage remains 75/80 candidates and 0/80 accepted.
