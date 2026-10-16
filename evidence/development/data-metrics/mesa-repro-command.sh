set -euo pipefail
docker --context colima-centinela run --rm --read-only --cpus 2 --memory 2g --tmpfs /tmp:rw,exec,size=512m --tmpfs /run:rw,size=8m \
 -v "$PWD/artifacts/package:/input:ro" -v "$PWD/artifacts/data-metrics-implementation/mesa-repro:/evidence-root" avelino-toolchain:local-qt6.8.3 bash -c '
 set -eu
 cp -R /input /tmp/package
 cd /tmp/package
 python3 - <<'"'"'PY'"'"'
from pathlib import Path
p=Path("consumer/datametricschecks.h");s=p.read_text();needle="window->setProperty(\"showDelta\",false);QTest::qWait(20);"
assert needle in s
s=s.replace(needle,needle+"qInfo(\"delta at20 visible=%d card=%g\",delta->isVisible(),card->property(\"presentationItem\").value<QQuickItem*>()->height());QTest::qWait(500);qInfo(\"delta at520 visible=%d card=%g\",delta->isVisible(),card->property(\"presentationItem\").value<QQuickItem*>()->height());")
p.write_text(s)
p=Path("check-display-sessions.sh");s=p.read_text().replace("for protocol in xcb wayland; do","for protocol in wayland; do").replace("for backend in software opengl; do","for backend in opengl; do").replace("for configuration in standard scaled; do","for configuration in standard; do")
start=s.index("    for fixture in base ");end=s.index("; do",start);s=s[:start]+"    for fixture in data-metrics"+s[end:];p.write_text(s)
PY
 cmake -S consumer -B consumer-build -G Ninja -DCMAKE_PREFIX_PATH="$PWD/install;/opt/qt"
 cmake --build consumer-build --parallel 2
 bash check-display-sessions.sh /evidence-root/sessions'
