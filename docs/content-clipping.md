# Generic content clipping candidate

Continuous surfaces, circular alerts and capsule filter chips now mask arbitrary
children on Qt 6.8.3's software renderer as well as the RHI CurveRenderer.
This closes the software implementation gap; complete native equivalence remains
verification-pending. Source contours, expected captures, tolerances and approved
exceptions are unchanged.

| Outline | Producers | Consumers |
| --- | --- | --- |
| Source continuous curve | `RoundedContent`, `continuouscorners.js` | Card, Panel, Surface, AttentionSurface, LoadingOverlay, Accordion |
| Circular corners | `CircularContent` | Alert |
| Capsule | `CapsuleContent` | FilterChip, CollectionFilters |

The software mask reads the same `ShapePath` as the curve renderer. It therefore
keeps continuous and circular geometry distinct. A `ShaderEffectSource` retains
the actual child controls in a Qt-owned effect root. `SoftwareContentMask` uses
Qt's software node dispatcher to render that borrowed root into an explicitly
alpha-capable CPU image, applies a cached antialiased mask, and presents the
result with a Qt scene-graph texture node. The adapter never reparents or owns
Qt's child nodes. It restores the software context's active painter and invalidates
the borrowed root's cached projection around layer rendering. Transparent corners reveal the actual
background, including patterns and translucent/nested content. There is no
asynchronous GUI snapshot, image encoding or GPU readback. Source, outline and
size changes refresh the raster; removing a source clears the preceding image.
Each changed image is painted completely so unchanged opaque islands survive
updates elsewhere; unchanged frames reuse the preceding masked texture.
A pixel-aligned raster origin, transparent gutter and one-to-one texture rectangle
preserve fractional-position child text. Only this renderer's placement records
are offset and restored; Qt's scene-graph nodes stay untouched. Visibility changes
invalidate the paint node, and the adapter retains/releases its source effect
reference so initially hidden controls synchronize when revealed. The RHI
implementation continues to use the existing Shape texture fill.

`SoftwareContentMask` is a renderer-support type, not another Bleecker desktop API.
It is software-only and rejects visible use on another backend or an invalid
source. Empty or not-yet-created effect roots remain transparent until the Qt
scene graph supplies content. Inactive RHI items produce no software node.
Its private path/item/effect-root and software-renderer interfaces are tied to
the repository's existing exact Qt **6.8.3** requirement. Only the library build links QuickPrivate;
installed consumers require the exported public dependencies. The toolchain adds
`libxkbcommon-dev`, needed by Qt's private CMake dependency graph. A Qt upgrade must
revalidate the adapter and both renderer paths before changing the pin.

The initial `QSGLayer::toImage()` prototype was rejected after regression captures
showed black holes around sparse opaque children. In Qt 6.8.3,
`QSGAbstractSoftwareRenderer::optimizeRenderList()` uses `QRegion::contains(rect)`
to decide whether opaque nodes cover the complete target; that API reports any
overlap. Consequently the pixmap layer can remain RGB even when it needs alpha.
The adapter uses an ARGB32 premultiplied image from allocation through painting,
so it does not infer missing alpha from pixel colors, change child opacity or
patch Qt. Sparse-content regression checks exercise the actual installed path.

The pinned source declares `clipShape` on these surfaces without a separate
content hit shape. Qt 6.8.3 traverses clipped descendants using `clipRect`, so a
transparent corner can still receive child input. This change preserves existing
pointer delivery. It does not claim native corner-hit equivalence or introduce
a new input policy. Keyboard focus, editing, disabled actions and real Qt
accessibility interfaces still use the original controls; actual reader output
and physical input remain separate gates.

Run `AvelinoCatalog --fixture clipping` for the shared visual fixture and
`InstalledConsumer --clipping` for pixel, source/path/resize/empty/visibility and
normal input checks through the installed package. The fixture is also captured
in light/dark at DPR 1/2 and checked in each independent X11/nested-Wayland,
software/Mesa OpenGL and standard/scaled session. QuickTest covers three outlines,
initially empty sources, nested masks, sparse opaque islands with transparent
holes and unchanged islands across other edits, translucent content
and parent opacity, live content, fractional and
zero sizes, and unchanged rectangular descendant pointer delivery at DPR 1/2.

Thirty-two software text-invariance rows check opaque-button glyph interiors
and complete transparent-text frames before/after masking at fractional positions,
widths, parent movement and reveal, at DPR 1/2. They provide 64 position comparisons
and 32 complete transparent-frame identity witnesses. Opaque-button outline
compositing remains in the separate zero-tolerance native audit. This assertion
covers the software adapter; it is explicitly skipped on RHI, whose text-raster
equivalence remains unaccepted. The RHI functional contour/lifecycle/input checks
run independently.

The complete evidence and regression audit are recorded under
[`evidence/development/software-clipping`](../evidence/development/software-clipping).
Strict native pixels, broader generic/font/script/fractional-scale contexts,
physical display/input, reader output and corner-hit equivalence remain pending.
This native library change has no backend, authentication, configuration-secret,
observability or TV behavior impact.

Qt 6.8.3 implementation references:
[software layer](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quick/scenegraph/adaptations/software/qsgsoftwarelayer.cpp),
[software node dispatcher](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quick/scenegraph/adaptations/software/qsgabstractsoftwarerenderer.cpp),
[region overlap semantics](https://doc.qt.io/qt-6.8/qregion.html#contains-1),
[path contract](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quick/util/qquickpath_p.h),
[descendant pointer delivery](https://github.com/qt/qtdeclarative/blob/v6.8.3/src/quick/util/qquickdeliveryagent.cpp).

Final verification: 4,608 Qt checks, 84 contracts,
136 virtual installed window/output pairs and
79 independent catalog captures pass. The complete
3,518-pair audit preserves 3,202 pairs;
296 native comparisons lose no geometry/exact pass. Fourteen cases have at most
four additional differing native pixels; these remain visible, unaccepted and
inside the existing zero-tolerance comparison. No exception is approved.
