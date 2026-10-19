#!/usr/bin/env bash
set -euo pipefail
# Ubuntu 24.04's Weston 13.0.0 crashes when activation walks a non-grabbing
# popup. Keep the upstream 13.x ABI and use its fixed patch release.
apt-get update
apt-get install -y --no-install-recommends \
    meson pkg-config patch libwayland-dev wayland-protocols libpixman-1-dev \
    libinput-dev libudev-dev libdrm-dev libgbm-dev libegl-dev libgles-dev \
    libcairo2-dev libpango1.0-dev libjpeg-dev libwebp-dev liblcms2-dev \
    libx11-xcb-dev libxcb-composite0-dev libxcursor-dev libxcb-xfixes0-dev \
    libxcb-shm0-dev libxcb-xkb-dev libxcb-render0-dev libxcb-xinput-dev \
    libxcb-xinerama0-dev libxcb-randr0-dev libxkbcommon-dev \
    libxkbcommon-x11-dev libpng-dev libglib2.0-dev
rm -rf /var/lib/apt/lists/*
weston_build_root="$(mktemp -d)"
trap 'rm -rf "$weston_build_root"' EXIT
python3 - "$weston_build_root" "${AVELINO_WESTON_ARCHIVE:-}" <<'PY'
import hashlib
from pathlib import Path
import sys
import urllib.request

url = 'https://gitlab.freedesktop.org/wayland/weston/-/releases/13.0.4/downloads/weston-13.0.4.tar.xz'
if sys.argv[2]:
    raw = Path(sys.argv[2]).read_bytes()
else:
    with urllib.request.urlopen(url, timeout=60) as response:
        raw = response.read()
assert hashlib.sha256(raw).hexdigest() == '66252c9c5bbc45ab402e2518b76e6d824f09ebc1d0040ee2f51b096a1bc585b1'
(Path(sys.argv[1]) / 'weston-13.0.4.tar.xz').write_bytes(raw)
PY
tar -xf "$weston_build_root/weston-13.0.4.tar.xz" -C "$weston_build_root"
# A parent may commit between get_popup and the popup's first commit. Until
# that first popup commit, its view has no transform parent to position against.
weston_patch="$(cd "$(dirname "$0")" && pwd)/weston-popup-parent.patch"
python3 - "$weston_patch" <<'PY'
import hashlib
from pathlib import Path
import sys
assert hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest() == '18587d7496f73dbd6fb61717acf1cfb3af98a8d873f8594dafd984aff4cb32e0'
PY
patch --batch --fuzz=0 -p1 -d "$weston_build_root/weston-13.0.4" -i "$weston_patch"
meson setup "$weston_build_root/build" "$weston_build_root/weston-13.0.4" \
    --prefix=/opt/weston-13.0.4 --libdir=lib --buildtype=release \
    -Dbackend-drm=false -Dbackend-drm-screencast-vaapi=false \
    -Dbackend-pipewire=false -Dbackend-rdp=false -Dbackend-vnc=false \
    -Dbackend-default=headless -Dscreenshare=false -Dxwayland=false \
    -Dsystemd=false -Dremoting=false -Dpipewire=false \
    -Dshell-fullscreen=false -Dshell-ivi=false -Dshell-kiosk=false \
    -Dcolor-management-lcms=false -Dtools=[] -Ddemo-clients=false \
    -Dsimple-clients=[] -Dwcap-decode=false -Dtest-junit-xml=false -Ddoc=false
meson compile -C "$weston_build_root/build" -j2
meson install -C "$weston_build_root/build"
mkdir -p /opt/weston-13.0.4/share/avelino
cp "$weston_patch" /opt/weston-13.0.4/share/avelino/weston-popup-parent.patch
LD_LIBRARY_PATH=/opt/weston-13.0.4/lib /opt/weston-13.0.4/bin/weston --version
