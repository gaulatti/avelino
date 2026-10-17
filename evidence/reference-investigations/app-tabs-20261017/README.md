# Native desktop app tab bar investigation

See [the contract and limits](../../../docs/app-tabs.md) and
[investigation.json](investigation.json). The unmodified public reference,
transparent outer probe and literal pinned body are captured separately. The
full source and native tooling live in checksummed external artifacts; this
directory contains Linux-readable observations and provenance.

The record preserves 344 closed contexts, 15,480 sizing queries and 864 retained
history steps. The fresh pinned-source replay reproduces all 3,627 output files byte
for byte. Public/probed/literal pixels agree in every closed context and history
step; sizing agrees in all 344 contexts. Requested bitmap/display scales are 1/2; actual window backing
scale is two. Local pointer events are synthetic. Native accessibility button
children were unavailable, so their absence does not establish accessibility or
reader equivalence. Geometry probes retain their last values after view removal;
consumer projection excludes removed views using current tab data.

`python3 scripts/verify-app-tabs-source.py` audits the sealed record.
`python3 scripts/generate-app-tabs-witnesses.py --check` verifies its consumer
projection. Neither command runs a native build on Linux or accepts the mirror.
