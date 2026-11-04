# Assistive path replacement lifetime

The unchanged path editor crashes when a caller synchronously destroys it from
ten selection or commit notifications. Four selection callbacks also demonstrate
stale replacements after disable, read-only, text or cursor changes. The retained
baseline records these failures independently. Qt history, validation/length and
actual chooser-owner removal already passed; those passing controls remain.

The path field now shares the existing DateRange Qt text-input notification
wrapper. Qt completes selection/IME work before changed properties are published;
each notification checks lifetime, and selection callbacks can cancel a stale
replacement. Qt owns text commands, validation and Undo/Redo. The pinned Undo
cursor is observed only. The DateRange extraction retains the original behavior.
No presentation recipe, font, expected image, tolerance, mask or exception changes.

Source4 passes all38 FileInput and48 DateRange UI checks at each DPR1/2. This is
172 scoped Qt checks, not a rerun of the full58-group suite. The catalog installs,
and an independent consumer builds from an empty directory. Consumer2 adds public
Qt callback assertions in three separately frozen consumer files, using a clone
of that fresh independent build. It is not relabelled as an empty-directory build.
The library/catalog remain source4; consumer2 changes no source used by them.

Four actual source-free X11/software runs cover FileInput and DateRange in light
DPR1 and dark/text1.5/DPR2 profiles. FileInput checks ten installed destruction
notifications, four real GoTo callback vetoes, replacement/insert/delete and native
keyboard Undo/Redo. DateRange checks six endpoint/owner edits per profile. Actual
loaded-module maps and hashes identify the installed library. Every run captures
the full Xvfb session before acknowledging the unchanged10second application
deadline. Neither product nor consumer source/build projects are mounted.

Two real21phase GoTo and two12phase DateRange AT-SPI/Orca runs pass on X11/software
and nested Wayland/OpenGL/softwareGL/dark/text1.5/DPR2. GoTo14 assertions and their
10second waits are retained with an output-root adaptation. Bounded Date6 session,
bootstrap and diagnostic code supplies isolated buses and local output copying.
The prefix/probe inputs remain unchanged. Speech commands use null ALSA audio;
native reader comparison and physical listening/input remain pending.

The old c32/e2 Docker images were missing after restart. A new pinned Qt6.8.3
image was built from the unchanged b938 tools recipe; the new reader overlay
preserves five Qt module hashes. The failed incomplete VM boot image is retained
externally by full hash; no raw OS image or compiled binary is embedded here.
First baseline125 never reached Qt. The next baseline hit ENOSPC before the app
and failed to save its normal result; its qualification and partial logs remain.
Only baseline3 executed the ten SIGSEGV cases. The prepared -pipe runner was never
executed; actual baseline3/fix4 compiler flags are unchanged.

FileInput retains native frame metadata mismatches29/32, with32/32 contract states;
both DateRange strict-observation results remain false. These are retained failures,
not native raster acceptance. Desktop coverage stays78/80 candidates and0/80
accepted, with46 TV entries pending. Prior31532 protected inventory fields remain
unchanged; two additional cases are verification-pending. The historical binding
uses b938 Git blobs plus seven retained Linux runtime files. It keeps the580-file
library execution and separately expanded581-file consumer candidate distinct.
Native fonts, full hierarchy/timing/reader/raster, physical and independent-machine
acceptance remain open. Default audits must remain independent of future ROOT
runtime/inventory edits; --current adds a candidate comparison before publication.
