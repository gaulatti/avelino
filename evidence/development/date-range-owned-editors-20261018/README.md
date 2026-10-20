# Owned DateRangePicker implementation checkpoint

This adds the ICU calendar backend, owned field/stepper/overlay/graphical editors,
caller gallery and installed-consumer route. The desktop inventory remains 76/80
candidates, 0/80 accepted; DateRangePicker stays pending. Registration is 80.

Three final Qt test runs pass: calendar components and owned input at DPR 1/2.
They cover exact native dates, calendar properties, localized segments, grid and
parsing; actual synthetic Qt input covers owner echo/ignore/delay, graphical
preview/commit, owned popup input, disabled/caller overflow, range-presence editor
lifetimes, delayed/external updates, owner removal, independent endpoints, exact
bounds and numeric year entry. These are not physical/native OS input proof.

A fresh installed consumer runs with project sources absent in eight light/dark,
text-scale-1/1.5, DPR-1/2 profiles. All 384 native model/displayed-date observations
match; complete geometry matches in 8. All 384 original-image comparisons execute
and fail strict pixel equality. No mask, resize, tolerance or baseline/pin change
is used. The default Linux row is 232 wide versus 222 in the native reference.
Fonts, native date segmentation, raster presentation and broader behavior remain
unresolved. Diagnostic pairs/differences are retained under strict/.

The gallery exercises 17 actual operators in each of eight profiles. Four
installed catalog captures pass startup/metadata checks. Eight X11/Wayland,
software/OpenGL, standard/scaled display profiles pass structural/input checks
with full virtual-session captures. They use Xvfb and Weston with software
rendering; physical display/input, hardware acceleration and reader acceptance
remain pending.

The first virtual-session run exposes a missing QML module after changing the
runtime mount path: the consumer embedded its build-time absolute import path.
CMake now computes the import relationship to the consumer executable. The fresh
consumer runs under /relocated-check and display sessions under /display-check,
with /consumer-check absent. All 560 repeated package output files match the
before-repair output exactly. The failed run and both package command streams
remain retained. Earlier comparator/check scaffolding failures are preserved too.

The source-specs file binds the final compiled core and consumer sources. Copies
of changed product/integration files preserve this checkpoint independently of
later edits. Command receipts and failed/successful Qt attempts retain their
original bytes. No complete native history replay, parsing/cancellation/traversal
acceptance, extreme-value behavior, strict geometry/raster parity, reader or
physical acceptance is claimed. TV's 46 entries remain pending in the later phase.

Verify with scripts/verify-date-range-owned-editors.py using the pinned visual
Python requirements. This is an implementation checkpoint, not accepted parity.
