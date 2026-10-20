# CI artifact directory ownership

The x86-64 job at revision `3a93a7fdb6f14ba4cf2ed1b02f0d4ddd96021b41`
built the patched Qt toolchain successfully, then failed before the core checks:
`mkdir artifacts/package` was denied. Docker had created the absent `artifacts`
bind source as root during toolchain evidence extraction.

The workflow now creates `artifacts/linux/toolchain` as the runner user before
mounting that specific directory for the root copy. Package seeding can then
create its sibling directories. The copied evidence retains its original bytes.

The raw remote job log and exact before/after workflows are retained here.
`probe.py` reproduces the same ownership boundary using real Linux user IDs and
kernel permissions: the old seed fails, the repaired seed succeeds, and the
root-owned copied evidence is checksummed. This local probe does not run the
whole GitHub workflow or establish a green remote result.

The Qt toolchain verifier binds its original workflow to immutable commit
`53606010b9e8f7c804275da3f57b543f875afb93`. The installer and build-check inputs
remain checked against their current bytes. The live orchestration repair is
checked by `scripts/verify-ci-artifact-ownership.py` against this new evidence.
