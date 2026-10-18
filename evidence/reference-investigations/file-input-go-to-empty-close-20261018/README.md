# Native empty-field Close and excluded input trial

The reused pinned helper starts a native Go to Folder sheet with an empty field.
Clicking its observed CloseButton dismisses that nested sheet and returns to the
still-open file chooser, without an owner result. The before/after AX states have
PID/time/count/raw-hash receipts. Together with the earlier nonempty-field clear
observation, this establishes the conditional clear/dismiss behavior.

The intended relative-path investigation does not establish its starting folder.
Its first setup assumes that Close always clears, so the following text partly
lands outside the dismissed sheet before a partial path appears in a reopened
prompt. These relative observations are excluded. A later retry records the full
intended absolute proposal, but Return does not produce a verified destination;
a subsequent capture has `/` in the field. This retry also remains diagnostic.
No new relative-resolution or keyboard-delivery rule is asserted.

All seventeen AX states and completed receipts, launch inputs, trace, terminal
result and log are preserved. The process exits 0 with no callback. AX copies
omit the unrelated sidebar, retain original indices and remove trailing blank
lines. The four JPEGs show excluded setup/retry states and remain external with
raw paths, byte counts and hashes; they are not presented as destination captures.
No expected image, reference pin, tolerance or exception changes.

Run `python3 scripts/verify-file-input-go-to-close.py`. The only positive claim is
the initial empty-field Close transition. Independent source rebuild, complete
contexts, native reader, physical input/display, raster and general input timing
remain pending. This record does not alter earlier sealed observations.
