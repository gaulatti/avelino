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
negative spacing and reserves at least the widest child. When the available
width fits all ideal sizes in a row without expanding children, it preserves
intrinsic label proposals; allocating
equal shares prematurely can wrap a larger button and leave unused space.
Its positive
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

The [compiled checkpoint](../evidence/development/button-group-layout-20261019/result.json)
matches all 184 component/child frame profiles. Label frames match 170/184;
128/184 raw image comparisons are pixel-exact. The 48 button profiles and eight
fractional-block profiles retain visible raster differences. Three diagnostic
side-by-side views are retained separately from the unchanged comparison inputs.
The eight canonical catalog controls improve in two contexts, remain unchanged
in six, and worsen in none; none is yet pixel-exact.

The shared library passes all 55 Linux core targets and the 792 Python contracts.
After that full run, two catalog-only integrations add the canonical `default`
alias and an explicit empty-case contract. The final catalog passes all 184
expanded contexts and eight canonical contexts; four missing, false, nonboolean
or inappropriate empty flags are rejected. Empty declarations are derived from
the source's fitted frames. The fitted presentation is measured independently
of a caller's zero-width outer frame.

The fresh independent consumer was compiled in producer v5; the catalog repair
in v6 reuses the identical consumer ELF. Eight source-free composition contexts
exercise five bare group cases plus pointer/keyboard activation. Eight virtual
X11/Wayland, software/OpenGL and standard/scaled profiles pass. All 42 existing
installed-consumer smoke commands pass without project sources. Cold replay
preserves all 437 date/navigation image bytes and 128 literal-input checks.
All 120 footer images retain their previous bytes. The original failed attempts
and the consumer build-label clarification are retained, with the raw receipts.

Run `python3 scripts/verify-button-group-candidate.py` to independently decode
the raw pixels, measurements, package/display records and historical controls.
The checkpoint does not close native font/raster, baseline/lifecycle coverage,
physical input/display or reader gates. Desktop acceptance remains 0/80.
