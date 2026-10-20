# Native HeroCarousel investigation

This records the unmodified Sabella desktop reference
`fe8a1d462fbd793d883fb92086a16aa2947e32c9`. It does not accept a Linux mirror.
Desktop coverage stays at 75/80 candidates and 0/80 accepted; television remains
the separate later phase. No expected capture, pin, mask, tolerance or exception
is changed.

The public API accepts identifiable items and a caller-supplied slide builder.
The pinned body uses a horizontal ScrollView, LazyHStack with a 16-point gap,
horizontal container-relative frames, a scroll target layout, view-aligned
behavior with `.always` limit behavior, and hidden scroll indicators. The exact
per-interaction limit remains pending. Apple's
[`.always` documentation](https://developer.apple.com/documentation/swiftui/viewalignedscrolltargetbehavior/limitbehavior/always)
does not specify a single-view limit; that guarantee belongs to the separately
documented [`.alwaysByOne` setting](https://developer.apple.com/documentation/swiftui/viewalignedscrolltargetbehavior/limitbehavior/alwaysbyone).
The pinned source uses `.always`. It supplies no autoplay, navigation buttons or
page indicators.

Twenty fixtures cover empty/single/multiple/dense lists, fill/fixed/text/button
slides, narrow/zero dimensions, inherited font/foreground, disabled content,
right-to-left layout and Unicode. Each is recorded under light/dark, text-scale
1/1.5 and DPR 1/2 settings: 160 contexts and 480 PNGs. Public, transparently
instrumented and literal pinned-layout versions match in every context. The
instrumented and literal geometry agrees; all three versions report the same
normalized caller lifecycle. These are native witness comparisons, not Linux
pixel comparisons. The fixture's requested DPR is separate from the recorded
window backing DPR.

Fixed-width slide content centers within a viewport-width allocation. Empty and
zero-width views create no slide instances in the recorded closed observations.
The control fills a bounded offered height; unbounded sizing depends on layout
history. There are 7,200 direct sizing queries across the three versions. Window
diagnostics and placement diagnostics add 1,080 queries. Varying window width
320/640/900 leaves the measured ideal width unchanged after a 200-point placement.
Varying the actual prior placement to 160/200/337 changes a three-slide control's
unspecified-width result to 512/632/1,043. Those values equal three prior viewport
widths plus two gaps. Therefore 632 is an observation after a particular layout,
not a fixed default to encode in Linux. Other histories remain pending.

The interactive native probe reports a 337-point viewport and a 1,043-point
document. Its accessibility scroll-to-bottom action reaches offset 706, and
scroll-to-top restores offset zero. The first slide retains its caller state
instance across disappearance and reappearance. A CUA right-page request produced
three Right key events without moving the viewport. No wheel event was delivered;
wheel, momentum and settling behavior are unverified. Two `noWindowsAvailable`
observation/coordinate-action errors are recorded. The app was closed through its
Quit menu and its process was verified absent; `open` does not provide its exit
code. The interactive probe uses the earlier verified source build and does not
suppress animations. It does not establish reader or physical-input acceptance.

The automated collector builds all 89 immutable source files from a fresh source
archive. A source-only package then repeats that build and reproduces all 482
capture/sizing files byte-for-byte. Both builds leave source inputs unchanged.
Native helper sources, compiled products, bundles and source archives stay outside
the Linux repository. The local candidate package's hash and path are recorded in
`provenance/source-only-artifact.json`; independent-machine download/replay
availability remains pending. That package covers the automated closed/sizing
collector. Supplementary diagnostic and interactive helper availability also
remains pending. The initial pilot's missing-resource-bundle failure and its
successful corrected rerun are retained.

`files.json` seals all members. Linux CI can validate the recorded data and raw
replay equality using `python3 scripts/verify-hero-carousel-source.py`, without an
Apple toolchain, sibling checkout or local native helper. Linux implementation,
catalog, installed consumer, display/accessibility/input checks, dynamic identity
and lazy timing, other sizing histories, generic IDs, reader comparison, physical
display/input and independent-machine acceptance all remain pending.
