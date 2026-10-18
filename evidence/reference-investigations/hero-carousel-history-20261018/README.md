# HeroCarousel native history supplement

This supplements the [first investigation](../hero-carousel-20261018/README.md)
at desktop reference `fe8a1d462fbd793d883fb92086a16aa2947e32c9`.
Nothing here accepts a Linux mirror, changes expected images or grants a tolerance.

The helper wraps the unchanged public control and its transparent/literal
witnesses in `ScrollViewReader`. Typed in-process calls select the first or last
slide; these are layout observations, not mouse, wheel, touchpad or remote input.
Animations are suppressed. Coverage is light appearance, text scale 1, DPR 1,
on macOS 27.0 build 26A428 with the recorded Swift 6.4 / SDK 27.0 toolchain.
The compiler's macOS 26 deployment floor is not the running OS version.

Attempt 1 preserves a failed helper compile (optional numeric conversion).
Attempt 2 succeeds with two 12-step histories and 72 images. Attempt 3 extends
both histories to 16 steps, adding consecutive 1-second and 3-second empty-data
idle intervals and scrolling after restoration: 32 observations and 96 images.
Each public/probed/literal image triple is byte-identical. Command exit codes,
helper input hashes and the previously rebuilt library object hash are retained.
The native helper sources and executable stay outside the Linux tree. They are
not included in the first investigation's source-only replay package;
independent availability of this supplementary helper remains pending.

Observed behavior:

- The fitted carousel stays 80 points high after visiting a 120-point slide and
  after changing that later slide to 200 points. Moving the 200-point slide to
  logical index zero changes fitted height to 200. Empty data fits to zero;
  restoration returns to 80. The explicitly bounded history remains 180 high.
- Caller instance 1 for each identifier survives removal, empty data, both idle
  intervals, restoration and subsequent first/last scrolling. This observation
  does not establish an unlimited retention guarantee under memory pressure.
- Expanding width from 160 to 337 transiently realizes identifier `1`, even
  though it is inactive at the final observation. Lazy realization timing must
  be compared separately from final visible frames.
- Geometry preferences cache frames for hidden and removed slides. The portable
  projection preserves that complete raw map and separately labels an active
  slide projection. The helper did not measure the caller wrapper frame. Neither
  filtering stale entries nor omitting an unobserved frame proves full geometry.

The separate safe `limit-value` probe only reads and reflects public limit
values. On this host `.always` and `.alwaysByOne` have the same reflected value;
`.alwaysByFew` differs. This supports investigating Qt's `SnapOneItem` policy,
but does not establish equivalent gesture limits, momentum, settling, timing or
behavior on another Apple runtime. The original source still spells `.always`.

`files.json` seals every member except itself. Run
`python3 scripts/verify-hero-carousel-history.py` and
`python3 scripts/generate-hero-carousel-witnesses.py --check` from the repo root.
Other appearance/scaling histories, actual gestures, complete sizing histories,
reader behavior, physical displays/input and independent-machine replay remain open.
