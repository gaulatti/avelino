# Qt item teardown

Qt base-item teardown can change window membership and inherited enabled, font
or palette values. Self-connections to a derived class must be disconnected
before that derived state ends. Window-frame and owned-caller observers must
also stop before their receiver's member state is destroyed. QObject's eventual
automatic disconnection happens later in the destruction chain.

The installed MediaLibrary consumer exposed this in InheritedControl when a
tile under a disabled parent was removed. A standalone control reproduces the
same assertion without MediaLibrary or FileInput. A 40-case matrix also exposes
teardown assertions in RadioGroupBase, ChartRenderer, SpotlightRows and
SoftwareContentMask. ProposalRow, ProposalColumn, ProposalOverlay, AppTabRow and
the corrected MediaLibraryBase survive the same cases.

The regression matrix covers attached items under enabled/disabled parents,
inherited font configuration and destruction with/without a live child. A QML
regression separately removes an inherited control from a disabled parent.
Control cases also assert that no derived style notification is forwarded during
destruction, independently of Qt's Debug-only dynamic-type assertions.
Mask teardown disconnects source and outline callbacks before releasing its
effect reference. These changes affect teardown, not presentation or layout.

Raw baseline and corrected process results remain separate development evidence.
Passing these checks does not accept native visual parity, physical input,
display hardware or reader behavior.
