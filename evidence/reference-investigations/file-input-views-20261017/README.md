# Native FileInput view and hierarchy observations

This supplement uses the pinned desktop FileInput and its recorded source-built
library. The helper, Apple sources, executable and fixtures remain outside
Avelino. It is not a fresh independent behavior-source rebuild. Linux FileInput
remains pending and candidate coverage stays 75/80. No expected capture, reference
pin, tolerance or exception changes.

The controlled fixture has three text files, an extension-ineligible PNG and a
folder containing one text file. Normal CUA input navigates to this directory;
the helper's cached directory property alone is not used as location proof.
Original AX text, five unmodified CUA JPEGs, helper trace and fixture hashes are
retained. OS-generated `.DS_Store` bytes stay outside the repository; only their
hash and size are recorded. Host sidebar labels and configured sort preferences
are observations of this host rather than Linux defaults.

List shows Name, Size, Kind and Date Added. Clicking Name produces ascending
ordering, with directories interleaved by name. The initial Date Added descending
order is this host's configuration. List permits multiple selected files across
the root listing and an expanded child folder. Right expands the folder inline
without changing the location. Collapsing drops selected descendants, preserving
other selected rows; collapsing the only selected child leaves Open disabled.
View mode and the expanded branch persist on the measured reopen, while file
selection and navigation history clear.

Switching List to Icons preserves two selected root files. Switching with a root
file and an expanded child selected retains only the root file; the callback
confirms the hidden child is excluded. A selected child alone becomes no
selection, with Open disabled and location unchanged. Icons to Columns retains
the selected root file. A single Icons click on a folder selects it without
navigating; Open then enters that folder without returning it to the owner.
Command-clicking that noneligible folder while a file is selected leaves the
existing file selection unchanged in the observed case.

Four callbacks are preserved in their original order. The cross-level List
selection returns `[Folder/Child.txt, Alpha.txt]`; reverse-order column clicks
still return `[Alpha.txt, Bravo.txt]`. These do not establish a general ordering
rule for selections spanning directories. That requirement stays pending.

The second callback follows an extra Return after a view-menu action. It is not
evidence that changing view alone submits a result. Native remote-panel AX can
temporarily retain the old view/menu after an action; the later screenshot and
full AX observations establish the settled view without another acceptance key.
The immediate and settled snapshots remain separate. Failed REPL helper lookups
performed no UI actions; the actual callback trace is authoritative.

The helper exits normally after final Cancel and restoration of Columns mode.
These observations require a hierarchy-aware List implementation and shared
selection across views. The current Linux column-only presentation is unchanged.
Full keyboard/modifier behavior, all sorts/metadata, folder-eligible contexts,
cross-directory ordering, input timing, exact raster, physical input/display,
native readers and independent-machine acceptance remain pending. CUA JPEGs are
not lossless strict-comparison baselines.

Run `python3 scripts/verify-file-input-views.py` to audit this record.
