# Native FileInput controls supplement

This supplement records owned-fixture observations of the pinned desktop source
through normal CUA input. It reuses the already source-built helper/library;
it is not an independent behavior-source replay or physical-input acceptance.
Apple source and executables stay outside the Linux repository.

The controls run covers Columns/List/Icons, sidebar visibility choices, group and
Option-sort menu entries, the location menu, and a deliberately unique no-match
search through This Mac/current-folder scopes and clearing search. It does not
establish positive search semantics, indexing equivalence or menu artwork.
The menu screenshot attempt is retained separately as unverified.

New Folder opens a nested prompt. An empty name disables Create. The history run
starts with an existing `untitled folder`, observes `untitled folder 2` as the
selected default, and sees immediate disabled Create with “This name is already
taken.” for an existing directory and file. Return creates `untitled folder 2`
and navigates inside it. Actual Back and Forward return to the parent and the
new folder. Command+Shift+N opens another nested prompt; Escape closes only that
prompt. Final chooser cancellation sends no owner callback. The controls run
also creates `Created by probe`; both directories are independently verified
empty, and the nested Escape creates no child directory.

The helper's cached directory property is not proof of the visible folder.
Go to Folder and controlled AX URL rows establish the actual location. Filtered
AX excerpts remove URL rows outside the controlled fixtures; some excerpts are
CUA diffs and do not establish a complete native accessibility hierarchy.
Sidebar labels, configured list ordering, ancestors and recent places are host
observations and must not be hard-coded as Linux defaults.

JPEGs are original CUA bytes with dimensions recorded in `investigation.json`.
They are not resized, cropped, masked or re-encoded. Lossless capture, strict
native raster, full state/context coverage, physical input/display, readers and
independent-machine behavior replay remain pending. These files add diagnostic
source evidence; they do not approve Linux mirror parity or replace baselines.

The history-selection run supplies a native counterexample to restoring selected
files: after selecting a+b or b alone, entering `folder` and pressing Back clears
the file selection and disables Open. Forward also clears a previously selected
child file. Shift-clicking c after Back selects a,b,c in this controlled alphabetic
fixture. This source evidence supersedes the initial Linux history prototype's
selection-restoration assumption. No owner result is sent.
