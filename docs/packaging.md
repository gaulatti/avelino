# Installed package checks

The core ships a shared library, QML plugin, qmldir/type metadata, QML source,
embedded static font resources, font license notices, and asset provenance.
`find_package(Avelino 0.1 REQUIRED)` exposes `Avelino::Avelino` and
`Avelino_QML_IMPORT_PATH`. Set the engine's import path to that installed directory.
Desktop has no media-decoder dependency.

The independent consumer is copied outside the repository and built against a
temporary installation. Its public import comes from the installed package;
it does not use a source QML directory or build-tree module import. Runtime checks
must additionally hide build/source trees to prove there is no accidental lookup.
Open overlays and internal controls will be required as those APIs are implemented.

No package release or complete mirror acceptance is claimed by these checkpoints.
Release acceptance requires every desktop gate in the parity inventory to pass.
