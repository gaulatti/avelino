# Linux TV target baseline

Status: decision record for issue #9. It selects a documentation baseline only;
the 46 TV inventory entries stay pending and no TV acceptance is claimed.

Assumption recorded: the owner has not named hardware, so the baseline is the
conservative generic-PC target that matches the verified desktop stack.

## Baseline

| Area | Choice |
| --- | --- |
| OS / toolkit | Ubuntu 24.04, Qt 6.8.3 (same as desktop) |
| Architecture | x86_64 primary, arm64 build/runtime evidence as for desktop |
| Display | Fullscreen Wayland session (EGLFS is out of scope for the baseline) |
| Graphics / decode | Mesa with VA-API hardware decode, software decode as the fallback of last resort |
| Playback stack | Qt Multimedia with the GStreamer backend |
| Remote / input | HID keyboard-class remotes and HDMI-CEC delivered as key events; arrow, select, back, play/pause, channel up/down mapped to Qt keys |
| Stream formats | HLS first; raw TS, DASH and RTMP only when a ticket for the selected device requires them |
| Errors | Visible playback error state with retry and return-to-guide; no silent channel skip |

## Not decided (needs a real device)

- A concrete SoC/board and its decoder driver.
- The physical remote model and its CEC behavior.
- Sustained-playback duration and thermal limits.

## Acceptance still required

- [ ] Real remote navigation on the chosen hardware.
- [ ] Sustained playback of each supported format on that hardware.
- [ ] Scoped implementation tickets per area (chrome, guide, playback, input).

Desktop and TV acceptance remain separate. The TV reference pin
`f5ac479bfceaa7eab23c1716ac47420ac53dae25` is unchanged.
