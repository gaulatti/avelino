# Installed package checks

The core ships a shared library, QML plugin, qmldir/type metadata, QML source,
embedded static font resources, font license notices, and asset provenance.
`find_package(Avelino 0.1 REQUIRED)` exposes `Avelino::Avelino` and
`Avelino_QML_IMPORT_PATH`. Set the engine's import path to that installed directory.
Desktop has no media-decoder dependency.

The independent consumer is copied outside the repository and built against a
temporary installation. Its public import comes from the installed package;
it does not use a source QML directory or build-tree module import. CI then builds
and runs it again in a fresh container whose only mount contains the installed
package and the independent consumer fixture. The original product source and
build trees are absent. This also checks relocating the CMake/QML package prefix.
Open overlays and internal controls will be required as those APIs are implemented.

No package release or complete mirror acceptance is claimed by these checkpoints.
Release acceptance requires every desktop gate in the parity inventory to pass.
