# AdminShell padded-sidebar background checkpoint

The pinned desktop source applies its card background after padding the caller
and extending its height. It does not extend that background across the entire
split column. The candidate now centres the caller-width-plus-32 background.
The standard 180-point caller has a 212-point card at x=44 in its 300-point column.
The unchanged native controls also show the card span at backing columns 88..511.

Both DPR 1 and DPR 2 pass 264 source-interpreted component cases, including the
background bounds and visibility for the native caller profiles. Two additional
capture cases per scale retain raw light/dark standard bodies. The light images
are byte-identical to the prior package; the dark change affects only the two
44-point side strips. Caller, detail and layout geometry remain unchanged.
The retained base library is reused; this is not a fresh compiled-module result.

The exposed side strips currently reveal the white diagnostic caller background.
Native sidebar glass remains unimplemented. The native encoded-pixel row samples
also place the composed edge at column 600, distinct from the earlier isolated
divider-view bounds. These observations do not accept the candidate divider.
Source colour integration, ICC conversion review, native raster, screen readers,
physical input and complete display-session verification remain open. Expected
images, comparison policy and source revisions are unchanged.

```sh
python3 scripts/verify-admin-sidebar-background.py
```
