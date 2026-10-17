# Native Text.bleeckerPill investigation

The public Text extension applies a 9-point bold monospaced font, horizontal/vertical padding 7/4, sea foreground, muted background and a Capsule clip. Caller-owned fonts, colors and rich runs survive. It does not use the pill radius token or the custom text-scale environment. Its private modifier type is not a public constructor; a non-Text caller fails typechecking.

All 111 fixtures span 888 closed appearance/scale/DPR contexts. Public, probed and literal-witness pixels match in all 888. The 440 baseline groups retain requested guides and raw dimension queries; center/ordinary stack guides remain unrequested. Twenty empty-font fixtures show a zero-width, 14-unit label and a 14-by-22 padded capsule in the measured contexts, independent of the tested caller/parent font.

Seven fixture histories cover 56 contexts and six steps each. The corrected concat run consumes the changed text; every text step changes actual full-view pixels. All public/probed/witness images agree and all final pixels, geometry and emitted guides restore. Wrapper instances stay one, with one appearance and no disappearance. This does not claim native Text object identity.

The original concat helper changed an unused string. Its 24 ineffective branch traces, the original exact 4,419-file replay, pilot and receipts remain diagnostic. All closed/empty images and all 720 non-concat history images remain unchanged. The corrected clean source-only replay reproduces all 4,563 outputs exactly. All 53 pinned Package/Sources files and the full 89-file snapshot are unchanged. Apple source and source-only replay archives stay outside Linux.

No expected image, pin, tolerance or exception changes. Linux implementation, native raster/fonts/symbols, actual pointer/timing, physical displays/input, readers and independent-machine replay availability remain pending. The desktop and TV acceptance counts are unchanged.
