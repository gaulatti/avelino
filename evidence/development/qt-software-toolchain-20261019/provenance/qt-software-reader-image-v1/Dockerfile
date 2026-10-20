FROM avelino-toolchain:qt-software-opacity-v4-20261019-qt6.8.3
RUN apt-get update && apt-get install -y --no-install-recommends \
    at-spi2-core=2.52.0-1build1 orca=46.1-1ubuntu1 python3-pyatspi=2.46.1-1 \
    speech-dispatcher=0.12.0~rc2-2build3 speech-dispatcher-espeak-ng=0.12.0~rc2-2build3 \
    && rm -rf /var/lib/apt/lists/*
