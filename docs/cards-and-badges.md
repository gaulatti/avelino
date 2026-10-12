# Cards and badges candidates

Six desktop APIs now have Linux candidates. Every entry remains
verification-pending; the pinned native reference images for these cases,
complete comparisons, accessibility, scaling, and session acceptance are missing.

| Reference API | Linux interface and presentation |
| --- | --- |
| `BleeckerCard` | Default content slot; `paddingSize` none/sm/md/lg = 0/16/24/32; surface/elevated/subtle/transparent variants; continuous radius 12, border, and light-only surface/elevated shadows |
| `BleeckerPanel` | Card composition with optional `title`, explicit `hasTitle` for a present empty title, title/content gap 16, default content slot |
| `BleeckerAttentionSurface` | Required `hue` and `intensity`; pinned finite-value defaults, hue wrapping, urgency clamp 0–10, accent/label colors, theme gradient and border; padding 16 |
| `BleeckerStatusBadge` | Required `text`; default/live/offline/warning/info; dot 6, gap 6, horizontal padding 9, minimum height 24, foreground-tinted capsule |
| `BleeckerNotificationBadge` | Required integer-valued `count`; localized display through 99, `99+` above it, full count accessibility name, padding 6, minimum height 18, pinned light destructive background in both themes |
| `Text.bleeckerEyebrow` | `BleeckerEyebrow` preserves text case, bold Encode Sans at 10 px, tracking 1.15, desert color |

Status text follows the reference's explicit text-scale modifier (11 px times
the text scale). Panel titles, notification labels, and eyebrows use fixed
logical sizes of 16/10/10, as their reference declarations do. This distinction
does not resolve OS accessibility text scaling; that remains a separate gate.
Logical tracking is applied at design-unit scale before Qt glyph rasterization
to avoid QFont's initial 1.15-to-1.140625 px quantization. Font metrics, wrapping,
tracking geometry, fallback, and cross-architecture pixels still require native
comparisons. OwnedText currently provides explicit lines without automatic wrapping.

Content clipping is deliberately reported by backend. Qt 6.8.3's software Shape
renderer ignores texture fills. Its candidate content therefore has rectangular
clipping, and `roundedContentClipping` is false. The CurveRenderer uses a
ShaderEffectSource texture inside the continuous outline. GPU clipping and pointer
containment require complete geometry and interaction comparisons. This is an
unfinished implementation gap, not an approved platform exception. Canvas shadow
blur and edge rasterization likewise remain uncalibrated against native captures.

Tests cover 32 card theme/padding/variant combinations, slot dimensions and resize,
optional/empty panel titles, eight accent boundary/wrapping/default cases, ten
status theme/variant combinations, six notification count boundaries, and eyebrow
case/weight/tracking. Run `AvelinoCatalog --fixture surfaces` for the gallery;
the check script captures light/dark at DPR 1 and 2. Installed consumption embeds
real buttons and an editable text field inside a card, the existing foundation
composition inside a panel, and attention/status/notification/eyebrow examples.
Its metadata records card/badge checks and the clipping backend separately.

Remaining cases include constrained/wrapping content, all shadow geometries,
rounded clipping of opaque and interactive slots on every renderer, locale and
count-domain differences, screen-reader output, scale combinations, and complete
native comparisons. All cases and runtime gates remain pending in the
[parity inventory](parity-inventory.json); no exception is approved.

Pinned sources: `Sources/Sabella/Surfaces.swift`, `Feedback.swift`, and
`Tokens.swift` at `fe8a1d462fbd793d883fb92086a16aa2947e32c9`.
Qt mechanisms: [ShapePath texture fills](https://doc.qt.io/qt-6.8/qml-qtquick-shapes-shapepath.html#fillItem-prop)
and [Canvas shadows](https://doc.qt.io/qt-6.8/qml-qtquick-context2d.html#shadowBlur-prop).
