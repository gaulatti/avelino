FROM avelino-toolchain:recovered-20261017-qt6.8.3
RUN apt-get update && apt-get install -y --no-install-recommends gdb at-spi2-core python3-pyatspi libglib2.0-bin orca speech-dispatcher-espeak-ng && rm -rf /var/lib/apt/lists/*
