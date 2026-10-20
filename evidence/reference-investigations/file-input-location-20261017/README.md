# Native FileInput location-menu investigation

This diagnostic supplement records the unchanged pinned desktop component through
its existing source-built helper. It approves no Linux implementation or native
parity. Reference pins, expected captures, tolerances and exceptions are unchanged.
Apple source and executables remain outside the Linux repository.

The corrected run starts with a complete controlled fixture root. The location
menu lists the current folder, its ancestors, and Recent Places. Choosing the
current folder preserves the selected file and leaves Back disabled in a fresh
history. Choosing an ancestor clears file selection and adds a navigation step;
Back and Forward restore locations with file selection cleared. Menu-only Escape
leaves the chooser open. Those menu/navigation actions send no owner result.

Accepting `Menu Parent/Parent.txt` adds `Menu Parent` to Recent Places. Visiting
`Alternate/Leaf` and cancelling retains that visible location on reopening but
does not add it to Recent Places. Accepting `Menu Parent/Leaf/First.txt` puts
`Leaf` before `Menu Parent`. Browsing the older recent parent leaves that order
unchanged. Accepting Parent.txt again promotes its folder without a duplicate.
These are three single-file cases. Recent updates for cross-directory or directory
selections remain pending. Three successful callbacks retain exact controlled URLs and report the panel
visible during the callback. Final cancellation adds no fourth result.

A separately started process preserves the order `Menu Parent`, `Leaf`, and its
recent Leaf entry navigates to the expected controlled directory. This establishes
same-bundle process persistence on this configured host. General capacity,
cross-application sharing, unavailable volumes and independent-machine behavior
remain pending; unrelated configured recent-place names are not Linux defaults.

Go to Folder appears as a separate GoToWindow sheet with a path field and
suggestions. Return on a verified missing path leaves the prompt open without a
candidate row; Escape returns to the selected First.txt without an owner callback.
The file-path experiments are diagnostic: Command+A did not reliably replace text
in the minimal helper, and AX value/selection plus keyboard retries gave
inconsistent prompt observations. After dismissing the remaining prompt, the
stable main chooser shows Parent.txt selected and no owner result. General file
submission/dismissal and timing are unresolved; these attempts are not grounds
for silently accepting a guessed file-path behavior.

The first attempt had a helper redaction root that was too narrow for its parent
navigation; its callback URL was therefore hidden. Its launch, trace, result and
limitation are retained separately. Corrected callbacks are all inside their
complete controlled root. The first REPL snapshot helper also retained its original
output directory binding. Corrected/fresh-process phase files are copied from their
actual storage paths, recorded with raw source hashes. Some earlier same-name
snapshots were overwritten; unavailable bytes are not reconstructed. Transient AX
states can show a new location with old selected rows or an exposed old menu;
settled observations and callbacks remain distinct.

AX excerpts omit unrelated URL rows and configured recent-place names. Every
filter and raw source hash is recorded. Five JPEGs are copied as original CUA
bytes at their recorded dimensions, without resizing, cropping, masking or
re-encoding. The menu artwork and all JPEG/raster equivalence remain unverified.
This is a single-host observation using a reused source-built library, not a
fresh independent behavior-source rebuild, full accessibility hierarchy, physical
input/display, reader or strict native acceptance.

Run `python3 scripts/verify-file-input-location.py` to audit the retained records.
Desktop coverage remains 75/80 candidates and 0/80 accepted entries; FileInput,
the Linux location menu and native path presentation remain pending.
