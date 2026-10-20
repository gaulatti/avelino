# Chinese-calendar editor presentation

The pinned desktop library is unchanged. The external fixture adapter adds the
Chinese Calendar identifier; the 89-file library remains byte-identical to the
existing pinned archive. Three initial locale cases are expanded into 36 source
configurations: en_US, zh_CN and ko_KR, ordinary/leap-month/new-year dates, and
regular/small/mini/large controls. All 72 source endpoints match isolated plain
AppKit controls in intrinsic size, cell size and insets. All before/after source
images are identical. Ordinary regular images also equal the initial captures.

The source's English presentation ends in a literal r. The Chinese presentation
uses lunar month/day names; Korean shows numeric month/day. These observations
come from the source images. Separately labelled diagnostics on calibrated bare
cells identify patterns M/d/'r', MMMddd and M. d.; they also retain full leap-month
labels and fixed field rectangles. No private selector or class mutation is
applied to the source controls. Private metadata is not a public API, renderer,
input, accessibility or physical acceptance oracle.

Public Calendar, DateFormatter, font measurements and NSDatePicker properties
validate all 864 raw cell and intrinsic width predictions exactly. The three
positive-era sampling strategies give the same widths in these contexts. Public
formatter text agrees with the isolated-cell logical strings at all 72 source
dates, including 2bis, 闰二月 and 윤2 leap-month labels. A longer logical label can
exceed a native reserved slot; full strings do not prove rendered clipping or
selection geometry. Source PNGs are retained unmodified.

The Linux probe records ICU 74.2's ordinary ddd output 029 and the corrected
per-day-field hanidays output 廿九. CLDR's algorithmic numbering system supplies
the lunar labels; no hand-written numeral table is introduced. Field-specific
number formatting leaves the other date fields and locales under their existing
number-format contracts. The product resource binds these observed patterns and
the zh_CN day-number override separately.

The 99-file external source-only archive contains the unchanged pinned library,
the Chinese-aware fixture adapter, public helpers, input JSON and diagnostic
source. A fresh extraction and library/helper build reproduces all 153 public
initial, source-sample and validation files exactly on this Mac. Diagnostic
address-bearing outputs are not included in that replay oracle. All Apple code,
archives, bundles and binaries remain external. Independent-machine availability,
native OS input, complete field layout, font/raster, readers and physical-device
acceptance remain pending. No reference, mask, resize, tolerance or exception is
changed. DateRangePicker and the complete desktop/TV goal remain unaccepted.
