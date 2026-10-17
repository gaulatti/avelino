# Dense surface path diagnostic

This rejects the prior analytic-containment prototype. The library is unchanged and remains unaccepted. All 32 geometries, 6,355,228 dense samples and complete indexed critical queries are preserved. Each corner uses step 0.125 within half the extent capped at 40 units. Raw path containment has no caller-frame hit clipping.

The prototype differs from SwiftUI in 38,308 dense samples when given native stroke outlines; sparse curved-outline agreement did not generalize. Qt containment on native outlines differs in 38,318; Qt containment on Linux-generated stroked outlines differs in 37,670. Generic SwiftUI paths constructed from the native CGPath match every native dense sample, while CoreGraphics containment differs in 60,063. These observations do not establish the internal cause.

A clean same-host SDK source-only replay reproduces every native data byte. Both Linux runs reproduce every dense method mask; the second also retains complete critical masks and indices. All 995 previous sparse classifications and their native paths remain unchanged. No expected image, source pin, tolerance or exception changes. SDK-only tooling is distinct from rebuilding the pinned Sabella module or delivering actual native pointer events.

Apple source and its checksummed source-only replay archive remain outside this Linux repository. Only data, logs and the Linux probe enter this directory.
