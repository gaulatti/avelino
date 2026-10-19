# Qt software opacity regression

The Qt 6.8.3 software renderer can leave transparent pixels in an opaque window
when an opaque scene node has fractional bounds. In the retained DateRangePicker
case, selecting the Arabic year produces twelve transparent pixels along one
selection edge. A separator click changes those pixels while selection, focus,
calendar visibility and model values remain equal. The existing strict window
comparison remains unchanged.

The source patch in [qt-software-opacity.patch](../tools/qt-software-opacity.patch)
applies the conservative classification inside Qt's software renderer. It
preserves geometry, colors, input, clipping and comparison rules. The
[paired source-built evidence](../evidence/development/qt-software-source-patch-20261019/result.json)
validates that change on Linux ARM64 with the SDK's QML libraries retained.
The supported toolchain installer and fresh image still require validation.

## Paired source validation

The unpatched source build reproduces nine failed opacity frames out of ninety
attempted frames; its nine Canvas2D frames pass. The real consumer then fails
the same Arabic-year/end literal check with twelve changed pixels, equal model
values and equal selection/focus/calendar state. The strict script stops at
that failure.

After applying the source patch without fuzz, only the staged Qt Quick library
changes between the paired runs. All 120 opacity frames and twelve Canvas2D
frames pass across X11/Wayland at DPR 1 and 2. The unchanged consumer ELF passes
all sixteen literal checks and eight native-derived value comparisons. All 84
cold date/Chinese-calendar PNGs remain byte-identical.

Run `python3 scripts/verify-qt-software-source-patch.py` to audit the retained
source diff, commands, effective features, linkage and raw captures. The verifier
independently decodes the PNGs and checks the twelve-pixel failure, opacity,
fixture paint, stable frames and all 84 cold pairs. This validates the source
repair, with native geometry, raster, physical displays, readers and overall
mirror acceptance still pending.

The source is the [official Qt 6.8.3 archive](https://download.qt.io/archive/qt/6.8/6.8.3/submodules/qtdeclarative-everywhere-src-6.8.3.tar.xz),
SHA-256 `1f03a2b8f5588b4face7da87926e9b2c1372b3a32157c52df07a75067a9db1af`.
The Linux ARM64 SDK enables QML JIT. All 49 effective QML/Quick feature definitions
match the source build, using the target C++ preprocessor to resolve conditional
definitions. The software-node private header is byte-identical to the source
release. Adding the matching ShaderTools build dependency changes none of the
existing SDK files.

## Standalone regression

Run `bash tools/check-qt-software-opacity.sh <fresh-evidence-directory>` in the
Linux verification environment with Qt 6.8.3, CMake, Ninja, Xvfb and Weston.
The optional second argument supplies the Qt prefix; its default is `/opt/qt`.
This probe uses Qt Quick directly, without Avelino or native fixture inputs.

The probe moves plain and clipped rectangles through five fractional positions
on an opaque window, preserving the original captures. It requires opaque
pixels, visible fixture color and three stable frames per position across
X11/Wayland software rendering at DPR 1 and 2. The complete matrix contains
120 frames. It rejects preloading so diagnostic interposition cannot supply a
passing toolchain result.

Each profile also renders three frames from a separate Canvas2D window. These
twelve additional captures check the private QML-engine boundary used by real
components, after the opacity captures have already been saved. They require
the expected opaque Canvas color and stable frames.

The paired source runs above pass this complete matrix after patching.
DateRangePicker initial-selection and RTL glyph behavior require separate native
observations.

The original SDK control has now run successfully as a reproducer: X11 DPR 1
and 2 each produced thirty opaque, stable frames. Wayland DPR 1 produced thirty
rendered frames, nine with alpha corruption, and returned failure. The strict
script stopped there; Wayland DPR 2 was not run in that attempt.

The [Linux CI run for `a946db525`](https://github.com/gaulatti/avelino/actions/runs/39208237227)
also reproduces the Arabic-year/end literal pixel failure on both x86-64 and
ARM64. Both core build/test steps passed; both independent installed-consumer
steps failed with equal state and models but different pixels.

## Toolchain preparation

The candidate installer verifies archive and patch hashes, derives QML JIT from
the installed SDK, and checks all 49 effective QML/Quick feature definitions
before compilation. It stages only Qt Quick, checks runtime linkage, and requires
the complete opacity/Canvas2D regression before replacing that library. The SDK
audit requires exactly that one existing library to change. Source-built QML
libraries are excluded from the installed payload. A fresh Docker image is
building through that installer; it has not passed end-to-end validation yet.

Qt Quick's source build also requires the matching ShaderTools SDK module and
Vulkan development headers. The first unpatched build stopped because those
headers were absent while the existing Qt Gui Vulkan feature was enabled.
Installing `libvulkan-dev` changed no existing packages, and the corrected
unpatched build completed. The failed attempt remains separate from renderer
regression results.

The first source baseline used the incorrect JIT-off setting selected by the
literal-header audit. Its simple rectangles reproduced the alpha defect, but
the date consumer crashed in Canvas2D. GDB and disassembly showed the private
engine extension table at offset 680 in that build and 688 in the SDK. The target
preprocessor confirms JIT is enabled; the private header's final literal
definition belongs to an inactive macOS ARM fallback. The incorrect literal
audit is excluded from binary-compatibility evidence. The corrected source build
uses offset 688, and both paired Qt Quick builds pass the Canvas2D checks against
the SDK's QML libraries. The Canvas2D guard prevents a rectangle-only pass from
overlooking that runtime boundary.
