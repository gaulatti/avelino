# Surface paint and async capture checkpoint

`validation.json` seals all evidence and implementation inputs. Native mirror
acceptance remains false. The source investigation and pending generic modifier
layout are documented in [the surface contract](../../../docs/surface-modifier.md).

The old surface paints its border behind opaque caller content. The final
implementation clips the background and caller together, then paints one border
above them. The original [before](before.png) and final [after](after.png) probes
show an opaque red caller beside a clear caller. At `(70,30)` the opaque edge
changes from RGBA `(255,0,0,255)` to `(235,0,0,255)`; the clear edge at `(170,30)`
stays `(235,235,235,255)`. The full unedited images are retained. Component tests
cover both appearances, radius zero/twelve, opaque/clear content and DPR one/two,
plus caller pointer/keyboard actions, local state, focus and actual Qt names.

The final producer passes all 25 CTest targets: 5,184 checks at DPR one and 5,412
at DPR two, with no failures or skips. The independent consumer passes all 28
modes. Its catalog produces 123 original captures and refuses a missing module.
All 123 metadata files and 119 PNGs are byte-identical to the prior package; only
the four Data Display PNGs change. The eight executable-only virtual profiles
pass with the same 123 installed files as the final tested producer.

The prior two build attempts remain in `qt-builds.tar.gz`. The first read-only
source mount prevented OTP trace output. Both early snapshots omitted native
PNGs needed by the font-catalog validator. The final snapshot has a separate
writable trace directory and complete native inputs. The focused catalog replay
also passes its 207 states and 21 malformed definitions. Actual outer exits,
signals and the host setup locator error are retained. No attempt was restarted
because observation expired.

The source-only Python contracts pass all 396 tests, including 14 new surface
integrity contracts. The final producer's frozen snapshot contains the final
library and component tests. The independently built consumer additionally
contains the later capture-readiness correction; its source hashes are separate
from the producer's manifest. `final-runtime.tar.gz` contains just captures,
logs, input hashes and the replay script; its runtime container mounts the
consumer executable and installed package without source/build trees.

## Async shape readiness

A repeated OpenGL capture exposed an old loading-button width still painted
after its logical width changed. A diagnostic occupies the single async worker
for 250 ms before that change. The original 50 ms capture takes a [pending
shape](pending-shape.png): logical button and surface widths are 224, while the
Shape status remains Processing before and after capture. The pixel at
`(490,100)` is the underlying card `(24,37,51,255)` where the updated button should
extend. All prior functional assertions still passed, so those assertions alone
did not prove the captured geometry was current.

The corrected consumer observes async shapes through displayed frames and
requires two unchanged, non-processing path/geometry observations. It fails
explicitly if that barrier times out. Under the identical worker delay, the
[ready shape](ready-shape.png) has status Ready before and after capture, zero
processing shapes, and button fill `(54,93,138,255)` at that point.
`readiness-fault-proof.json` retains every measured phase. The display validator
also requires the new `asyncShapeFrameChecks` result. Existing pixel, geometry,
state, focus and accessibility assertions remain intact.

`opengl-repeats.tar.gz` retains five fresh processes per protocol/scale for both
old and new libraries with the same original consumer executable. The unchanged
old builds already vary by one to three channel levels in a few timeline-text
pixels. One new-library run also captured the unfinished loading geometry
described above. Raw whole images, session images and complete comparisons are
preserved; no region is masked or tolerated in native comparison. Exact OpenGL
and native raster acceptance remains pending.

| Archive | Evidence |
| --- | --- |
| `qt-builds.tar.gz` | All three producer attempts, source inputs, actual exits, full CTest logs and trace outputs |
| `earlier-packages.tar.gz` | Both earlier package attempts and complete gallery outputs |
| `final-package.tar.gz` | Canonical consumer build/check receipts, all 123 galleries and missing-module refusal |
| `paint-and-readiness.tar.gz` | Before/after pixels, failing/passing regressions, caller input, delayed-worker traces and catalog setup/replay |
| `opengl-repeats.tar.gz` | Forty original repeated OpenGL sessions and raw pixel comparisons |
| `early-runtime.tar.gz` | Earlier executable-only runtime matrix |
| `final-runtime.tar.gz` | Final eight profiles with Shape readiness required |

Every archive has a complete member hash/size manifest. Each extracted member
was checked against the original bytes. Compiled executables and installations
are identified by hash. No Apple source/tooling archive is included.
