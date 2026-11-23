# Native date-field idle completion

The retained source-built public DateRangePicker helper was reused with its
executable bytes unchanged. The source remains pinned at
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`. Only the app bundle identity changed
to isolate this run. The runtime was macOS 27.0.1, SDK 27.0, field style, regular
size, en_US/Gregorian/UTC, light, text scale 1, logical DPR 1 and backing DPR 2.

CUA clicked each endpoint, selected its year and typed `2` without Return, Tab
or focus loss. The model stayed unchanged during initial entry, then received
one request after about one second idle. The From request was
`-62098387199.375`; the To request was `-62097523199.875`. The original hidden
time/fraction and independent peer value survived. In a third field-style
observation, Escape left the pending entry intact and the same idle request
followed. `observations.json` retains before/after model states, observer elapsed
times, executable/journal hashes and six unmodified owned-view images. Observer
times are not exact action-delivery timestamps or an accepted timing tolerance.

A separately compiled literal selected-source helper added standard Undo/Redo
menu actions. Those actions were disabled after committed date changes, its
window undo manager stayed empty, and the shortcuts did not change dates. This
probe used a system inherited font and is not a full Sabella module rebuild.
It does not justify adding date history beyond the source contract.

A fresh full-source helper rebuild failed while checking out unrelated FFmpeg
dependencies because disk space was exhausted. Only that newly created failed
scratch directory was removed; probe source, journals and captures remain. No
new source-only replay is claimed. The original helper reuse and literal menu
probe are distinguished in the metadata. A later popup attempt selected a day
instead of a year and remains in the external journal; it is not an oracle here.

These observations add no accepted component, reference-pin change, mask,
resizing, tolerance or exception. Full input contexts, native raster and physical
reader/device acceptance remain pending.
