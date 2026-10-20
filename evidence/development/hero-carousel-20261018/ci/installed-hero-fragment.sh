#!/usr/bin/env bash
set -euo pipefail
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software consumer-build/InstalledConsumer --hero-carousel --hero-carousel-observe
hero_checks_dir="$(mktemp -d "$PWD/hero-carousel-installed.XXXXXX")"
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software consumer-build/InstalledConsumer --hero-carousel --hero-carousel-gallery --hero-carousel-report "$hero_checks_dir/gallery"
