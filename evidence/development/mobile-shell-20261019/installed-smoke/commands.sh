set -euo pipefail
mkdir -p /output/date /output/hero
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --controls
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --composition
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --mobile-shell
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --selection
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --checkbox
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --secure-field
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --search-field
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --collection-filters
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --slider
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --tabs
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --pagination
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --pagination-integers
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --accordion
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --presentation-states
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --spinner
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --alert
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --clipping
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --navigation
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --sidebar-brand
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --data-metrics
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --stepper
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --radio-group
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --otp-input
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --activity-item
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --modal
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --tooltip
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --button-style
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --font-modifier
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --surface-modifier
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --pill-modifier --pill-observe
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --charts --charts-observe
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --media-library --media-library-observe
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --date-range --date-range-observe
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --date-range --date-range-gallery --date-range-report "/output/date/gallery"
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --hero-carousel --hero-carousel-observe
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --hero-carousel --hero-carousel-gallery --hero-carousel-report "/output/hero/gallery"
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --command-spotlight --command-spotlight-observe
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --dropdown-menu --dropdown-menu-observe
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --app-tabs --app-tabs-observe
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --surface-baseline --surface-supplement-observe
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --surface-input --surface-supplement-observe
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /package/consumer-build/InstalledConsumer --file-input --file-input-observe
