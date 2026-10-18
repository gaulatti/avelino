# Native FileInput recent-policy and path-input supplement

This record extends the earlier location investigation without modifying any
sealed record, reference pin, expected image, tolerance or exception. It uses the
unchanged pinned component and an externally built helper with normal Edit/Quit
responder menus, timestamped observations and no programmatic panel-directory
assignment. The source library object and resource bundle are reused. Apple
source, build products and capture tooling remain outside Avelino.

Two files selected across a root and expanded child return together, while
Recent Places records the visible `Mixed Root`, not each selected file's parent.
Twelve subsequent successful folder locations leave exactly the latest ten,
newest first (`Recent-12` through `Recent-03`). A second app with a different
bundle identifier sees that same pool before making any selection. Selecting a
directory in List returns the directory URL but records the unchanged visible
parent. With no row selected, a directory chooser can accept its current folder.
All fifteen callbacks in those two processes retain their exact controlled URLs.

Normal Command+A now replaces the path field. A verified missing path remains
in its own prompt; Escape preserves the underlying selected file. Submitting an
existing file path closes the prompt and selects that file without calling the
owner. Submitting the current folder preserves its selected file. An explicitly
typed hidden folder can be reached. Successful path input persists across openings and these consumer processes.
Cancelling the invalid input leaves the previous saved path intact.

The text-only process exposes a distinct source behavior: Go to Folder selects
`Blocked.png`, Open is enabled, and acceptance returns that exact URL. Ordinary
pointer selection of the same PNG remains disabled. Both routes use the same
unchanged `public.plain-text` configuration. This does not establish the path
selection rule for every other type array. Its sixteenth callback is retained.
The relative-input trial `../Recent-12` has a Recent Child suggestion and
navigates there. It does not establish relative normalization or whether
suggestion updates had settled; those input/timing gates remain pending.

The first startup failure lacks the required source-library resource bundle and
exits -5. It is preserved separately; corrected launches copy the existing bundle
unchanged. Each successful run receives its own capture object/output path and
records timestamps and recorder PID/count receipts, avoiding the earlier snapshot
helper's captured-directory problem. AX records omit unrelated URL rows and
configured recent-place names. Initial Documents views retain panel controls and controlled recent entries only.
Per-file raw hashes and filtering scope are recorded. The single JPEG is copied
as original CUA bytes without resizing, cropping, masking or re-encoding.

This is same-host diagnostic source evidence, not a fresh independent source
behavior rebuild, complete hierarchy, reader, physical input/display, menu/raster
acceptance or a portable statement about every macOS configuration. General type
conformance, relative input, callback ordering and timing remain pending. Linux
location controls are in progress; desktop coverage remains 75/80 candidates and
0/80 accepted entries. Run `python3 scripts/verify-file-input-location-policy.py`
to audit the record.
