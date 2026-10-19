# Button group layout

The pinned Sabella button group preserves fractional child widths, flattens
content groups, retains hidden children in layout, and centers its fitted stack
inside an explicitly offered width. The source investigation retains 23 cases
across light/dark appearance, text scale 1/1.5 and DPR 1/2: 184 bare captures and
184 transparent measurement captures. Every measurement pair has identical PNG
bytes. Source frames include both buttons and their text labels.

The cases cover absent, zero-size, conditional, hidden and grouped children;
fixed and fractional blocks; mixed-size buttons; zero, fractional, negative and
very large spacing; RTL; and offered widths 0, 20, 110 and 300. With spacing
`-200`, fixed children of widths 80/40 produce a fitted width of 80 while the
second child starts at -120. The layout can paint outside its own fitted extent.

The Linux candidate uses the existing proposal layout system. A button group
exposes its content and spacing, reports minimum/ideal widths, and centers its
fitted presentation inside the caller's width. The shared row accepts finite
negative spacing and reserves at least the widest child. Its existing positive
spacing, baseline and proposal behavior remains subject to the full core suite.
The catalog and component checks share `tests/consumer/ButtonGroupCase.qml`;
the independent consumer also constructs bare public groups and exercises
pointer and keyboard activation without the catalog fixture.

The source helpers reuse the previously verified pinned Sabella library object;
this is not another independent library rebuild. The original capture helper,
run in the original full fixture order, reproduces all eight retained canonical
button-group images byte for byte. Its isolated filter reproduces six, and the
expanded slot helper has small raster differences. All attempts and their raw
captures are retained separately. Expanded measurements establish slot geometry;
they do not replace canonical expected images or prove broad raster equivalence.

Run `python3 scripts/verify-button-group-source.py` with
`tools/visual-requirements.txt` installed to verify inventories, source bindings,
raw geometry, transparent measurement identity and the unchanged canonical
controls. See `evidence/reference-investigations/button-group-slots-20261019`.
Apple capture tooling remains outside the Linux tree. Source pins, expected
images, pixel tolerances and acceptance exceptions are unchanged. Full native
pixels, physical input/display and reader acceptance remain pending.
