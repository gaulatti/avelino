# CI runtime contract repair

This checkpoint repairs validation and artifact access. Application sources,
reference pins, images, comparison thresholds and mirror acceptance are unchanged.
The desktop inventory remains 76 candidates of 80, with none accepted.

On c1b7946, References passed and both Linux architectures passed all 52 Qt tests.
The Linux workflow then failed because the installed catalog produced 159 valid
captures while the validator still required 155. The older 463f327 package run
also exposed stale FileInput counters: its 49 images, 30 owner/input phases,
62 synthetic pointer deliveries and 164 synthetic key deliveries were checked
against the previous 44/24/54/40 trace. Both runs failed artifact upload when the
host reader encountered root-owned 0700 Qt evidence directories. Byte-exact raw
CI logs are preserved under ci-logs as deterministic gzip files.

The existing sealed FileInput trace reproduces all eight old-validator failures
and passes all eight repaired checks. The relocated, source-absent HeroCarousel
runtime produces all 159 catalog images and metadata. Missing and unexpected
capture mutations each fail the repaired catalog validator. The catalog derives
its exact expected filename set from the gallery list instead of a stale total.

The first permission probe used the macOS-shared mount and failed its denied-read
precondition; its script, failed receipt and log remain under attempts/v1. The
second probe creates private root-owned directories on the container's Linux
filesystem. An unprivileged nobody reader fails with PermissionError for each of
the three workflow evidence trees, then reads unchanged bytes after the workflow
chmod loop. The container is already root and lacks sudo, so the probe omits only
that privilege prefix. The workflow itself retains sudo on the GitHub runner.

commands.json aggregates the 18 successful baseline/current-profile/catalog
commands from attempt v1 and the syntax, Linux permission and negative-catalog
checks from attempt v2. The complete v1 receipt retains its failed nineteenth
command separately. run.py and the attempt scripts document the original local
paths; generated evidence is copied here and bound by files.json. input-reports
binds the eight input reports in the existing sealed FileInput checkpoint.

These checks prove local validator and artifact-readability behavior. Full remote
CI for the repair remains pending. They grant no strict raster, physical input,
screen-reader, deployment or mirror acceptance.
