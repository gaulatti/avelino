# Native DateRangePicker investigation

This is source observation, not a Linux implementation or mirror acceptance.
Desktop candidate coverage remains 76/80 and accepted desktop entries remain zero.
The reference is fe8a1d462fbd793d883fb92086a16aa2947e32c9,
Sources/Sabella/Extended.swift:63-68. Original source, Apple helper source,
compiled outputs and the source-only archive stay outside the Linux repository.
provenance records their identities and external locators.

Forty-eight fixtures cover eight appearance/text-scale/DPR contexts each. All
384 public/probed/literal image triples, model values, and observed outer geometry
agree. The 1,152 images retain their original bytes. The direct proposal queries
retain the actual outer probe and agree across all three branches: 384 contexts,
three branches, 15 proposals, totaling 17,280 results. These windows are visible
but offscreen, inactive and non-key; actual backing DPR is 2, independently of
the requested logical display scale. Inactive accessibility snapshots do not
establish focused navigation, reader announcements or native input behavior.

Seventeen typed data/range/environment history steps produce 51 images. All
three branches agree in images, model values, native picker properties and weak
instance identities. Turning a nil range into a supplied range, or clearing it,
recreates the inner native pickers while retaining the wrapper; changing bounds
within the supplied-range branch retains the native pickers. Switching styles
changes the helper's outer ViewBuilder branch and remounts its wrapper, so that
observation is not an intrinsic dynamic-style lifecycle guarantee.

A fresh build of the unmodified 89-file reference succeeds. A deterministic
source-only package is extracted and rebuilt without sibling or prebuilt inputs.
All 1,206 cold, sizing and history files replay byte-for-byte on this machine.
The full source tree remains byte-identical before and after. Independent-machine
availability remains pending; the archive itself is outside this repository.

Failed attempts remain visible. native-v1 omitted the resource bundle: compilation
succeeded, then both pilot runs exited -5 before measuring component behavior.
native-v2 fixed resources, but its sizing pilot did not retain the actual outer
probe; native-v3 fixes that instrumentation. native-v4 preserves an initial failed
history compilation due to a missing actor annotation; history-v1 corrects it.
Interactive v1 compiled but its passive fingerprint included its changing status
label. Interactive v2 removes that feedback and launches through Launch Services.
Both apps exposed an owned visible NSWindow but stayed inactive/non-key, and CUA
returned cgWindowNotFound. No keyboard, pointer, stepper, calendar, owner-response
or reader evidence is claimed. Both test processes were terminated and confirmed
absent. Their source hashes, raw journals, images, compiler logs and routing
failure receipts remain in attempts. The final visible inactive AX getters retain
From/To date-time area labels despite the source's labelsHidden modifier.

All scripts, matrices and raw observations are bound by files.json. Recompute
the checks with python3 scripts/verify-date-range-source.py. No reference pin,
expected image, mask, tolerance or exception has changed. The public Linux
component, catalog, independent consumer and all Linux runtime gates are pending.
