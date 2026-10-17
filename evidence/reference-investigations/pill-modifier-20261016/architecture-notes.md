# Installed text inheritance probes

These exploratory probes use the existing installed package. No Pill implementation is present. Raw Qt Text and raw rich Text keep their application font and color. BleeckerText inherits the control font; setting the scope palette supplies its inherited color. A rich Qt Text with explicit scope font/palette bindings receives that scope while retaining the supplied styled spans.

The metadata identifies the font/color boundary the implementation must handle. It is not a native frame, pixel, accessibility or reader acceptance result. Both complete attempts, Linux sources, exact installed-file hashes and actual exits are preserved.
