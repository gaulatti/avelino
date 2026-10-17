# Portable media evidence replay

The original References run failed because the historical producer binding included generated Python bytecode absent from a clean checkout. The corrected checker binds all critical inputs to the frozen manifest and continues validating complete bytes from Git and archived overlays. It preserves every cache entry and checksum in the original evidence.

Linux Python 3.12 with Pillow 12.1.1 verifies the complete frozen candidate and all 19 focused contracts while the cache directory is replaced by an empty temporary filesystem. Native images, comparison outcomes, source pins and acceptance gates remain unchanged. Remote CI confirmation is separate from this local replay.
