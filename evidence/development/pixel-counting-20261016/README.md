# Exact pixel-counting equivalence

The comparator now computes RGB diagnostic counts from a per-pixel maximum-channel
histogram. Zero entries count unchanged pixels; the largest entry is the maximum
channel error. Alpha and every source, color, metadata, dimension, geometry and
pass/fail check retain their existing implementation.

The complete 1,048-case data-display comparison produced identical JSON, HTML,
raw differences, overlays and image pairs: all 3,146 output files matched byte for
byte. [The record](comparison-equivalence.json) identifies both tool hashes and
the preserved candidate/report from `f7cd6896`. Its native result remains zero
exact pixel matches; this optimization provides no visual acceptance.

The [metric benchmark](metric-benchmark.json) covers 16 synthetic checks and ten
preserved frames spanning all five APIs at both DPRs. Counting took 4.85 seconds
with the earlier method and 0.068 seconds with the histogram method on that host.
These timings cover diagnostic counting; capture and PNG writing have their own
costs. The boundary tests also cover overlapping channel changes, every 8-bit
channel value, transparent RGB data and independent alpha changes.

With `tools/visual-requirements.txt` installed, reproduce the metric check from a
full checkout:

```sh
python3 evidence/development/pixel-counting-20261016/benchmark.py
```

The report is written under `artifacts/pixel-counting/`; `--output PATH` selects
a separate report for another machine. The preserved reference/candidate images
are read directly from this checkout.
