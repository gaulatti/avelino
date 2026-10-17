# Pill modifier native contract

The pinned `Text.bleeckerPill()` extension applies a 9-point bold monospaced font,
horizontal padding 7, vertical padding 4, the resolved sea foreground and muted
background, followed by a `Capsule()` clip. It does not read the custom text-scale
environment or use the pill radius token. The modifier type is private; the
public entry point accepts `Text`. Compiler probes preserve the successful
extension call and the expected private-type/non-Text failures.

The [source investigation](../evidence/reference-investigations/pill-modifier-20261016/investigation.json)
keeps 111 fixtures across 888 appearance/text-scale/requested-DPR contexts. Each
context has public unprobed, public probed, literal-body/label probed and bare
Text images. All 888 public/probed/witness triples match exactly. The unchanged
53 pinned Package/Sources files are part of the unchanged 89-file snapshot used
for the fresh reference-module build.

Cases include empty/space/newline/multiline/long/Unicode/bidi/emoji text, explicit
primary/secondary/monospaced/system fonts, colors, bold/italic/underline/strike,
tracking, kerning, baseline offset, concatenated and attributed runs, Markdown,
inline system images, width offers 0 through 800, line limits, parent fonts/colors,
RTL, ordinary stacks, first-baseline parents, disabled state and outer opacity zero.
Caller-owned fonts and colors survive the modifier; mixed runs retain their own
attributes. The Linux implementation must preserve those caller properties.

The probed label sits at offset 7,4 inside the styled frame, which adds 14,8 to
its measured extent. All 440 first-baseline groups associate emitted guides with
the exact final width/height; the styled guide adds 4 to the label guide and
reaches the 3-by-30 reference marker. Center and ordinary stack layouts retain
unrequested guides. The raw query sets include intermediate proposals.

At requested DPR one, plain `Ready` measures 42 by 19 after padding. Twenty
additional empty-font fixtures measure a zero-width, 14-unit label and a 14-by-22
padded capsule throughout the measured contexts, independent of the tested
caller/parent font. This is an observed empty-text layout behavior, not a
14-point typography declaration. Width offers remain separate outer frames;
an offer of zero retains a 14-unit padded surface around the zero-width label.
The 444 public text-scale pairs remain byte-identical.

Seven fixtures retain public/probed/literal wrappers through 56 six-step histories:
initial, text, appearance, text scale, direction and restore. Every text step
changes actual full-view pixels, every public/probed/witness image agrees, and
every final image, frame set and emitted guide restores. One wrapper instance,
one appearance and zero disappearances remain observed throughout. This does not
claim identity for a native Text object.

The first concat helper used a constant string and changed an unused input.
Its 24 ineffective branch traces, pilot, receipts and exact 4,419-file source
replay remain diagnostic. The corrected helper consumes the changing text and
adds a baseline concat history. All 3,552 closed/empty images and 720 non-concat
history images remain unchanged. The corrected clean source-only replay rebuilds
the unchanged reference and reproduces all 4,563 outputs exactly.

Run `python3 scripts/verify-pill-modifier-source.py`. Integrity contracts reject
missing contexts, changed probe pixels, invented/dropped guides, collapsed padding,
ineffective text steps, recreated wrappers, skipped stages, changed pinned source,
partial replays, false API exposure and forged acceptance.

Apple source, tooling and source-only archives remain outside the Linux tree.
The application was prohibited/inactive, with offscreen hosted windows at actual
backing DPR two and requested bitmap DPR one/two. No pointer events were delivered
by this capture. Linux implementation, native raster/fonts/symbols, input/timing,
physical displays/input, readers and independent-machine replay availability
remain pending. No expected image, source pin, tolerance or exception changes.
Desktop coverage remains 65/80 candidates, 15 pending and zero accepted; TV stays
separate with 46 pending entries.
