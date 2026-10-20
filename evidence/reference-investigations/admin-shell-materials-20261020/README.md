# Native AdminShell material and divider observations

Four existing standard controls cover both appearances and initial visibility
values. All three observation versions retain the same 12 before/after/chrome
images byte-for-byte against the prior colour-input record. Geometry, requests,
owner state and colour inputs remain unchanged. The 36 original paths share eight
exact PNG blobs. The 53-file library object is reused; Apple helpers stay outside
this Linux repository.

The native view hierarchy exposes sidebar glass, a 12-point split shadow, 52-point
titlebar scroll pockets, and the divider. At actual backing DPR 2, the divider view
measures 0.5 by 500 at x=299.5; it is hidden with collapsed navigation. The public
split-view thickness getter returns 1, which remains a separate observation.
These four contexts do not establish complete material or display-scale behavior.

Version 2 initially resolved the public divider colour outside its drawing
appearance, returning the ambient white colour even for a light control. Version
3 resolves it inside the view's effective drawing appearance: black or white,
respectively, at alpha 25/255. Both versions and all original controls are retained.
Changing only the owned window appearance for the additional property query does
not override the split view's explicit light/dark environment. That property query
is separate from the original Aqua-window images.

The Linux candidate now adds the visible divider using the existing separator
colour and one device pixel, preserving zero layout extent and its input mask.
The generated native witnesses drive four regular component cases. The sidebar
glass, shadow and titlebar-pocket rendering remain unresolved. ICC conversion
review, native raster, complete toolbar/caller behavior, readers, physical input
and independent-machine acceptance remain pending.

```sh
python3 scripts/generate-admin-divider-witnesses.py --check
python3 scripts/verify-admin-shell-materials.py
```
