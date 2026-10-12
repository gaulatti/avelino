FROM ubuntu:24.04@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55
ARG TARGETARCH
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake ninja-build python3 python3-venv ca-certificates git \
    libgl1 libegl1 libopengl0 libgl-dev libegl-dev libopengl-dev libdbus-1-3 libfontconfig1 libxkbcommon0 \
    libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 libxcb-shape0 libxcb-xinerama0 \
    libxcb-randr0 libxcb-render-util0 libxcb-xkb1 libxkbcommon-x11-0 \
    libxcb-image0 libxcb-sync1 libxcb-xfixes0 libxcb-util1 libx11-xcb1 \
    xvfb xauth x11-utils x11-apps xdotool weston dbus-x11 imagemagick \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /opt/aqt && /opt/aqt/bin/pip install --no-cache-dir aqtinstall==3.3.0
RUN case "$TARGETARCH" in \
      arm64) qt_host=linux_arm64; qt_arch=linux_gcc_arm64 ;; \
      amd64) qt_host=linux; qt_arch=linux_gcc_64 ;; \
      *) exit 1 ;; \
    esac && /opt/aqt/bin/aqt install-qt "$qt_host" desktop 6.8.3 "$qt_arch" \
      --outputdir /opt/Qt --archives icu qtbase qtdeclarative qttools qtsvg qtwayland \
    && ln -s /opt/Qt/6.8.3/* /opt/qt
ENV PATH=/opt/qt/bin:$PATH
ENV LD_LIBRARY_PATH=/opt/qt/lib
ENV CMAKE_PREFIX_PATH=/opt/qt
WORKDIR /work
