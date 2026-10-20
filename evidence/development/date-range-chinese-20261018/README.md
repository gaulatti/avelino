# Chinese-calendar editor checkpoint

The owned editor preserves the source's locale-specific year presentation and
uses ICU's per-day-field hanidays numbering for Chinese lunar labels. It parses
and round-trips all 72 source dates, including leap-month labels and hidden
calendar/year/time/fractions. Calendar sizing samples use the current era rather
than the astronomical maximum. The gallery exposes all three captured locales.
The native source supplement retains 36 configurations, 864 exact public sizing
observations and 153 exact source-only replay files; source pins are unchanged.

Producer24 retains the old related-year formatting failure. Producer25 passes
presentation/parsing and both UI runs but retains the width-sample failure.
Producer26 passes the semantic checks; producer27 reproduces missing CJK glyphs.
The recorded font dependency layer adds Noto CJK and fontconfig. Producer28 passes
all three final Qt runs, including glyph-run coverage for all 72 source strings, including 72 new endpoint presentation,
parsing and font-reservation checks, 72 live endpoint checks per DPR and three
synthetic input-method commits per DPR. Existing calendar/owner/input/teardown,
retained-width, fresh-width and chrome checks still pass. Native OS-input and
reader/physical acceptance remain separate.

Consumer9 is freshly configured and compiled from its 149 input files
against producer28's installed prefix. Runtime mounts contain neither project
source tree. All eight package and eight gallery profiles pass. Each package
profile checks all 36 Chinese source cases for models, padded field strings,
editable roles and calendar parts. Eight virtual X11/Wayland software/OpenGL
profiles and four installed catalog captures also pass. These are distinct from
physical display/input, acceleration and screen-reader gates.

All 384 legacy model/date observations and all 17 history model, editor identity,
calendar and environment observations remain exact. All 401 legacy whole-image
comparisons execute and fail (0 lower, 0 higher,
401 unchanged changed-pixel counts against the width checkpoint).
The 36 new light/text1/DPR1 whole-image comparisons retain every result; see
chinese-comparison.json and chinese-result.json. Intrinsic sizes, complete frame
geometry, logical strings and pixels are recorded separately. No mask, resize,
reference/pin update, tolerance or approved exception is introduced.

Native reserved slots can clip longer leap-month labels; the current joined-text
editor does not establish native per-field clipping or selection geometry. Font,
bezel, full geometry/raster, native input histories, readers, physical displays,
the remaining desktop entries and the separate 46-entry TV phase stay pending.
Coverage is 76/80 desktop candidates and 0/80 accepted. Run
scripts/verify-date-chinese-checkpoint.py. Source specs bind the compiled inputs,
fresh consumer, native evidence, font environment and all integration edits.
