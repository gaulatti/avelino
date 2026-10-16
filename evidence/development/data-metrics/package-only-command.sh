# Reproduction of the package-only run: input package read-only, source absent.
docker --context colima-centinela run --rm --read-only --cpus 2 --memory 2g \
 --tmpfs /tmp:rw,exec,size=512m --tmpfs /run:rw,size=8m \
 -v "$PWD/artifacts/package:/input:ro" \
 -v "$PWD/artifacts/data-metrics-implementation/package-only:/evidence-root" \
 avelino-toolchain:local-qt6.8.3 bash -c '
 set -eu
 cp -R /input /tmp/package
 cd /tmp/package
 bash check-installed.sh > /evidence-root/installed-check.log 2>&1
 cp -R catalog-evidence /evidence-root/catalog
 set +e
 QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software consumer-build/InstalledConsumer --data-metrics --format-diagnostics /evidence-root/number-formatting.json
 format_status=$?
 QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software consumer-build/InstalledConsumer --data-metrics --sidebar-brand
 mode_status=$?
 set -e
 test "$format_status" = 244
 test "$mode_status" = 58
 dpkg-query -W libicu74
 test ! -d /usr/include/unicode
 bash check-display-sessions.sh /evidence-root/sessions'
