# Button candidate checkpoint

Source: `efb2a90d04233b7ea023215ec78917811ca44688`.
Reference: `fe8a1d462fbd793d883fb92086a16aa2947e32c9`.
[CI run](https://github.com/gaulatti/avelino/actions/runs/38273039988).

All 112 Linux candidate PNGs and metadata are preserved here. Candidate pixels
match on x86_64 and ARM64. Both raw reports fail every case at zero tolerance.
The environment record includes source/resource hashes, dependencies, compiler,
and Qt version. The eight X11/Wayland configurations preserve window and entire
display captures with renderer, scaling, input, capture-tool, and compositor data.
They use virtual displays and synthetic input; hardware and accessibility remain
unverified. These files are candidate evidence, not new expected images.

From the repository root, with `tools/visual-requirements.txt` installed:

```sh
python3 scripts/verify-references.py
python3 scripts/compare-captures.py --reference reference/captures/desktop/buttons \
  --candidate evidence/checkpoints/efb2a90 --output artifacts/replay-efb2a90
```

The comparison returns status 1. Its 112 hashes, changed-pixel counts, error
bounds, and maximum-channel errors reproduce the CI results. Reference files
remain unchanged. `geometry-change.json` retains per-case improvements and
regressions relative to `75cb37a`; it does not accept any difference.
