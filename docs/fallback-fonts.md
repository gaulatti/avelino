# Fallback-font contract for Unicode and RTL text

Status: decision record for issue #13. It authorizes no capture, reference-pin,
tolerance or exception change. Implementation is a follow-up (see "Delivery").

## Decision

Avelino bundles one fallback family per script that Encode Sans and Libre
Franklin do not cover, from the Noto family under the SIL Open Font License 1.1:

| Script | Family | Weights shipped | Subset |
| --- | --- | --- | --- |
| Arabic | Noto Sans Arabic | Regular, Medium, Bold | U+0600-06FF, U+0750-077F, U+08A0-08FF, U+FB50-FDFF, U+FE70-FEFF |
| Japanese/CJK | Noto Sans CJK JP | Regular, Medium, Bold | U+3000-30FF, U+31F0-31FF, U+4E00-9FFF, U+FF00-FFEF |

Encode Sans and Libre Franklin keep every glyph they already provide. Fallback
applies per run and only for code points those fonts lack. No fixture-specific,
per-title or per-script offsets are allowed.

## Subsetting

- Tool: `pyftsubset` from a pinned fonttools release recorded in
  `assets/provenance.json` with the source font version, source URL and SHA-256 of
  both the upstream and the subset file.
- Keep layout features required for correct shaping: `ccmp`, `locl`, `kern`,
  `mark`, `mkmk`, `calt`, `liga`, `rlig`, plus `init`, `medi`, `fina`, `isol` for
  Arabic. Keep hinting off; drop name records not required by OFL attribution.
- Output goes to `assets/fonts/` next to a copy of the OFL text; the font files
  are registered through the existing font-registration path.
- Distribution: OFL permits bundling and subsetting. Reserved font names apply,
  so subset files must be renamed if the license of the chosen release declares
  a Reserved Font Name (Noto does not); the check is recorded in provenance.

## Constraints that change

1. The "unchanged bundled fonts only" restriction in #4 is relaxed solely for
   code points outside Encode Sans and Libre Franklin coverage.
2. Reference captures stay unchanged. The macOS references use GeezaPro and
   PingFangSC-Medium, whose advances differ from Noto (issue #13 measured 136.24
   vs 142.68 at size 14). Exact width parity for these titles is therefore not a
   goal; the retained differences stay recorded as open, un-excepted mirror
   failures until the owner approves a specific difference.
3. Latin text must remain byte-identical in layout to the current output.

## Acceptance for the follow-up implementation

- [ ] Arabic and Japanese FileInput titles render without missing-glyph boxes in
      the installed consumer on Ubuntu 24.04 (Qt 6.8.3), light/dark, scale 1/1.5.
- [ ] The full title remains the accessible name regardless of painted truncation.
- [ ] Latin cases in the 32-case matrix are unchanged.
- [ ] Measured Noto widths for the #13 titles are recorded in docs, not hidden.
- [ ] Provenance and license entries exist for every shipped font file.

## Delivery

Font files are binary assets that must be downloaded from the upstream Noto
release; that step and the shaping/fallback wiring are the follow-up work.
