# Pill modifier

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
by this capture. Native raster/fonts/symbols, input/timing, physical displays/input,
readers and independent-machine replay availability remain pending. No expected
image, source pin, tolerance or exception changes.

## Linux candidate

`BleeckerPill` retains one `BleeckerText` caller, provides the fixed bold mono 9
font and sea palette, and measures a muted capsule with 7 horizontal and 4 vertical
padding. A non-Text caller, an empty content slot, or multiple callers fails with
an explicit diagnostic. Caller fonts/colors and rich spans keep their own values.

```qml
BleeckerPill {
    BleeckerText { text: "Ready" }
}
```

`BleeckerText` defaults to plain text and now exposes explicit Qt `textFormat`,
`maximumLineCount`, `tracking`, `kerning`, `baselineShift` and `accessibleText`
properties. Plain text keeps the existing source-font renderer; formatted text
allocates independent unwrapped measurement and displayed Qt text with the
resolved caller font and palette. Empty plain
text keeps the measured 14-unit line box and baseline 11 for all tested fonts.
Inline images settle through the pinned private `QQuickText::resourcesLoading()`
bridge before capture. The private integration stays inside the library.

Formatting follows Qt 6.8.3's supported HTML/Markdown subset. In particular, its
rich-text renderer does not implement finite line limits or elision; combined
rich-text/line-limit equivalence remains unresolved. The exact-version
[Qt Text source](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quick/items/qquicktext.cpp)
documents those boundaries. Inline checkmarks in the fixture use proposed portable
SVG artwork at the inherited nominal font size; this is an unapproved replacement
for the native system symbol. Image callers can supply explicit `accessibleText`.

Open `AvelinoCatalog --fixture pill-modifier` to change text, formatting, parent
layout, width offer, RTL, theme, scale, visibility and enabled state. Isolated
`Text.bleeckerPill` definitions use the same `PillModifierCase` and reject malformed
or incomplete inputs. The installed consumer uses `--pill-modifier`; its default
mode fails on native frame/guide differences. `--pill-observe` records every
difference while keeping structural failures fatal.

The complete matrix contains 2,112 images: 888 public, 888 bare, and all 336 steps
of the 56 retained histories. Strict comparison finds 224 exact pixel/frame/guide
cases, all bare; 236 pixel matches, 888 frame matches and 1,616 guide matches.
All 2,112 caller state observations pass. Zero public or history cases pass the
complete strict comparison. These are candidate measurements, with no visual
exceptions, changed expectations or accepted mirror parity.

The full Qt suite passes all 29 targets, including 5,330 component checks at DPR
one and 5,558 at DPR two. The final fixture-only rectangle change passes the three
affected catalog/configuration targets; the other 126 installed files and the
component test executable remain byte-identical to that full-suite producer.
The installed package passes 32 modes and 131 catalog captures. All 127 earlier
gallery PNGs and their complete metadata remain byte-identical. Actual XTest
input through Xvfb/X11 reaches 18 toolbar controls across 22 clicks and 23 states;
each complete caller viewport matches a separate installed Qt fixture exactly.
This is virtual UI evidence, with native pixels and physical/reader acceptance
remaining separate.

Run `python3 scripts/generate-pill-witnesses.py --check` to verify the complete
projection. Capture with `scripts/capture-pill-modifier-cases.py <consumer> <new-dir>`
and compare with `scripts/compare-pill-modifier-captures.py <captures> <new-dir>`.
Every attempt uses a fresh directory and keeps its actual exit code.


The [candidate record](../evidence/development/pill-modifier-20261017/candidate.json)
keeps every compiler, package, runtime and observer attempt. Cold GPU capsule
paths now use asynchronous tessellation; the original stale first frame and
rejected texture-sizing experiment remain diagnostic. Explicitly sized rich
images load on the GUI thread, avoiding the preserved render-thread QObject
warning. A separately measured unwrapped text item avoids natural-width binding
loops without constructing a formatted renderer for plain callers.

The [native marker audit](../evidence/development/pill-modifier-20261017/native-marker-raster.json)
checks 1,024 physical-pixel observations: 928 fully visible and 96 clipped by the
viewport. Native sharp rectangles paint at the nearest physical pixel while
retaining fractional emitted frames. The fixture applies that measured policy
to its diagnostic rectangles; aligning their lower right corner also preserves
negative half-pixel origins at the viewport edge. An alpha-capable painted item
also makes the software renderer clear the background beside fractional parent
frames. These changes remove the preserved Wayland software readback's transparent
marker-edge pixels at both DPRs without changing
caller frames, guides or expected images. The inline-image test checks actual
window pixels, including at DPR two, rather than an already hidden texture child.

Desktop coverage is 66/80 verification-pending candidates and 14 pending entries;
zero are accepted. Television remains separate with 46 pending entries.

Pill callers with rich text or a line limit share the formatted `BleeckerText`
width-update policy described in [font modifiers](font-modifier.md). Growing
a fractional offer requests a complete wrapped-text layout before rendering.
The closed and retained native corpora remain strict; this correction does not
establish native font or pill acceptance.

The [formatted-text correction replay](../evidence/development/media-library-caption-20261017/candidate.json)
keeps all 2,112 pill PNGs byte-identical to the earlier candidate. No previously
passing frame, baseline or state observation regressed.
