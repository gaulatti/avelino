# Complete display run with the patched compositor

The unchanged check-display-sessions.sh passes all304 records:38 fixtures in each
X11/Wayland, software/OpenGL, standard/scaled profile. Every record retains its
raw window and complete-output capture with independently checked SHA-256 values.
All eight tooltip profiles complete20 visible-owner remounts, totaling160 frames;
all eight FileInput profiles pass, including the previously missing scaled
Wayland/OpenGL record. No compositor core is produced.

This completes the display gate that was still running when97fe54c was sealed.
The module and independent consumer are unchanged from fede040 (604 core inputs,
149 consumer inputs); the image uses97fe54c's patched Weston13.0.4. The original
253-record EGL failure,303-record capture failure and stock compositor crash
remain preserved in their earlier checkpoints. This successful complete run does
not prove a permanent cause/fix for the intermittent FileInput capture failure.

The subsequent date-literal source607 change is not part of this run and has its
own compiled and package verification. No current-source claim is inferred from
this historical source binding. Virtual software-rendered sessions, synthetic
input and Qt accessibility assertions do not close physical display/input,
hardware acceleration, reader or strict native appearance acceptance. Desktop
coverage remains76/80 candidates and0/80 accepted. Reference pins, comparisons,
masks, resizing, tolerances and approved exceptions are unchanged.
