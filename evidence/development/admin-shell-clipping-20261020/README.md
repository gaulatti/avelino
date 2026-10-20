# AdminShell split-root clipping

The pinned source's NSSplitView masks its contents to its own bounds. A separate
small caller puts a 1400-point yellow overlay in its 90-by-36 header, with a
30-point purple margin around the 360-by-180 shell. Both native captures keep
all changed pixels inside the split root. All twelve ordinary native control
paths remain byte-identical to the published material controls. The source
library object is reused unchanged; native helper source and Apple products stay
outside this Linux repository. This caller experiment is not an expected-image
update or a native raster approval.

The prior Linux implementation lets that caller paint into the surrounding
margin. Final negative attempt6 records 265 passes and that one failure using
the exact pre-change module source. The split root now enables clipping. Final
source-interpreted attempts5 and7 pass all266 component cases at DPR1 and2,
including caller identity, geometry, binding states and actual margin pixels.

Initial attempt1's failure and attempt3/4 intermediate passes remain external.
Attempt2 is retained here as invalid clipping evidence: the test inferred DPR
from the returned image dimensions and sampled inside the component. The final
case uses window DPR and keeps its samples inside Qt Quick Test's image crop.
The native helper's missing-resource failure is also retained; it captured no
images. Corrected native runs use the verified original27-file resource bundle.

Only clipping at the split root changes. The source's overflowing minimum body
geometry remains intact; clipping is not applied to the outer caller frame.
Historical265-case colour receipts stay bound to their original producer for
the evolved module/test files. Raw receipts, pins, images and comparison policy
are unchanged. Fresh compiled/package/display execution, native material and
raster, ICC review, physical input, readers and independent-machine replay remain
pending. The previous eight-context package evidence belongs to source4a0a06b.
