# Native search history and token replacement investigation

This fresh SwiftUI caller uses the unchanged cached pinned Sabella library object.
Only the external helper is rebuilt. Actual runtime macOS27.0.1/26A434, SDK27.0
and minimum compilation target26.0 remain separate facts. Apple helper code,
apps, objects and executable CUA actions remain outside this Linux repository.
The helper is cancelled and closed; no owner result is recorded.

Back from a selected Filename folder search restores browsing, clears selection
and enables Forward. Forward restores the token and selected folder scope, but
both a complete CUA projection and the displayed screenshot show eight recursive
files, including unrelated names, instead of the previous single name match.
This reproduces the older inconclusive history trial. No loading indicator is
exposed in those two Forward snapshots; general query readiness is still not
established, and no guessed Linux predicate or acceptance rule follows from it.
Starting a different query after Back disables Forward and resets scope to This
Mac, matching the current Linux branch/scope behavior in this controlled case.

Selecting the complete Filename token with Cmd+A and typing a different literal
removes the token presentation and exposes raw-field suggestions. The observed
result list initially retains filename-only membership; predicate completion and
commit semantics are not established by the changed field presentation. A first
Cmd+Z leaves that presentation unchanged. The following enabled Edit > Undo
restores the original Filename token, while suggestions initially retain the new
raw query. Changing to folder scope then exposes the three old Filename matches.
The four field projections in interaction17 explicitly do not retain complete
AX text. No single atomic Undo step is inferred. The candidate repair targets
whole-token replacement and reversible token metadata while retaining Qt's own
editing, composition and undo grouping; it does not emulate unexplained native
result-membership behavior.

Original CUA outputs and the deliberately limited edit projections identify their
capture times and action-argument hashes. Some output is diffed; some is full
serialized text. These are not complete native AX attribute/identity archives.
The displayed screenshot is JPEG with base64 bytes elided in the session log;
complete image bytes are unavailable and no raster baseline is derived. Prior
investigations remain unchanged. All native, reader, physical and raster gates
remain pending.
