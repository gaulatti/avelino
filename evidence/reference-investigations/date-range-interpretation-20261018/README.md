# DateRange graphical time interpretation correction
+
+The first input metadata incorrectly described native timestamp 1710345600 as
+UTC midnight. It is 2024-03-13 16:00:00 UTC. Right-arrow navigation in the observed
+graphical style preserves hour/minute/second and drops the .625 fractional second;
+Space commits that whole-second preview. Pointer selection retains the fraction.
+No midnight reset is observed in that native input path.
+
+The first Linux backend regression exposed the mistake: its midnight operation
+returned 1710288000 (2024-03-13 00:00:00 UTC), while the native captured timestamp
+was 1710345600. The failed test log and original interpretation metadata remain
+here. The source records, event journal, PNGs, reference pins, source-only archives
+and acceptance rules are unchanged. Only three interpretive input members and
+their membership hash file are corrected; docs and the verifier now check the
+UTC hour/minute/second and fractional-second semantics explicitly.
+
+This is a correction to the meaning of existing observations, not new native or
+Linux acceptance. All component/runtime, reader, physical and complete native
+input gates remain pending. The Linux backend remains work in progress.
+
A follow-up native session begins at 13:27:41.625 UTC. Graphical Right previews
the next day at 13:27:41, and Space commits it. This directly tests nonzero hour,
minute and second values rather than extrapolating from 16:00:00.625. The reused
helper is unchanged; its new fixture, event journal, images, annotations and clean
CUA window closure are retained under nonzero-time. No reader/physical acceptance
is claimed. The host system time zone is recorded as America/New_York; the fixture
and native date picker explicitly use UTC/GMT.
