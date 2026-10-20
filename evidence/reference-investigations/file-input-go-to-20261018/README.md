# Native FileInput Go to Folder lifecycle

The unchanged pinned helper from the previous location-policy investigation ran
against a new controlled folder tree. It completed with exit 0 and one successful
owner callback for `Navigator Root/Other.png`. The source library and helper
executable are reused, not independently rebuilt. Apple source and binaries stay
outside Avelino. No global recent-place preferences were reset.

The sheet's AX `CloseButton` clears its path field and shows Recents while leaving
the sheet open. An absolute Alpha path opens that folder without submitting the
owner. `Child` proposes the child of the currently visible Alpha folder and
Return navigates there; the next opening retains the literal `Child`. In that
new folder, the retained input proposes `Child.txt`. The displayed heading still
says "Go to folder in current location" for that file proposal.

From Alpha/Child, `..` has no proposal and Return leaves the sheet open. `../`
proposes that same current folder and Return leaves the chooser there. `../A.txt`
has no proposal despite the controlled A.txt existing in the parent. These exact
observations do not establish a general relative-path algorithm. A missing
absolute path also remains in the prompt; Escape preserves the selected
Child.txt and the previous successful raw input `../`.

Single-clicking the Alpha recent row selects it while the field stays empty.
A completed pointer double-click navigates to Alpha, and the next opening has
an empty field. A separate AX double-click attempt failed partway through a UI
change; its resulting Alpha/ field is diagnostic, not proof of that gesture's
full behavior. `operations.json` identifies the completed trial.

An absolute `Al` input presents Alpha, Alpine and Alphabet in that order. Down
selects Alpine without changing the field. Return navigates there, and the next
opening still contains literal `Al`. With the Edit menu closed, Tab extends it
to the common prefix `Alp`. Ordering for other inputs and the completion/search
algorithm remain pending. Go to Folder Recents and Where Recent Places must not
be assumed to have the same pool, capacity or ordering.

The PNG ordinary-row click leaves Open disabled under `public.plain-text`. The
same file entered through Go to Folder becomes selected with Open enabled,
without an owner callback. Clicking Open then returns that exact URL. Other type
arrays and the complete native selection-conformance rule remain pending.

Two atomic-paste attempts produced no field change. Command+A after Tab did not
replace the field, and the attempted root text appended instead. Those attempts
are retained without a successful input claim; clicking the measured clear
control then typing provides the corrected root trial. An Edit menu inspection
showed disabled Paste. Two screenshot API failures left partial AX captures
without completed receipts; the menu-context Tab attempt is excluded. This record
does not turn the earlier normal-menu observation into a universal Command+A or
paste guarantee.

There are 57 AX captures: 55 completed PID/time/count/hash receipts and two partial
captures. AX copies omit unrelated sidebar subtrees and retain original indices;
their raw source hashes and filtering are recorded. Trailing blank lines in these
filtered text copies are removed. Twenty original CUA JPEGs
are copied byte for byte. Nine whole open-panel images are omitted to avoid
publishing unrelated sidebar names; their source hashes remain recorded. No
image is cropped, resized, masked or re-encoded. Screenshot omission is not a
strict raster comparison or an approved exception.

Run `python3 scripts/verify-file-input-go-to.py`. This is same-host diagnostic UI
evidence, not native reader, physical input/display, independent source rebuild,
complete context, input timing, general path resolution or strict raster
acceptance. FileInput remains pending; desktop coverage stays 75/80 candidates
and 0/80 accepted. The Linux Go to Folder sheet is still to be implemented.
