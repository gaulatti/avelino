cmake_minimum_required(VERSION 3.24)
project(AvelinoInstalledConsumer LANGUAGES CXX)
find_package(Avelino 0.1 REQUIRED)
find_package(Qt6 6.8.3 EXACT REQUIRED COMPONENTS Test)
qt_standard_project_setup(REQUIRES 6.8)
qt_add_executable(InstalledConsumer main.cpp)
qt_add_qml_module(InstalledConsumer URI InstalledConsumer VERSION 0.1
    OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/qml/InstalledConsumer
    SOURCES sharprectangle.h mediatilefill.h
    QML_FILES AdminShell.qml AdminShellCase.qml MobileShell.qml MobileShellCase.qml MobileShellGlyph.qml DateRangePicker.qml DateRangePickerCase.qml HeroCarousel.qml HeroCarouselCase.qml HeroCarouselSlide.qml FileInput.qml FileInputCase.qml DropdownMenu.qml DropdownMenuCase.qml DropdownMenuImage.qml CommandSpotlight.qml CommandSpotlightCase.qml CommandSpotlightRow.qml AppTabs.qml AppTabsCase.qml AppTabGlyph.qml apptabfixturemetrics.js MediaLibrary.qml MediaLibraryCase.qml MediaLibraryTile.qml Charts.qml ChartsCase.qml PillModifier.qml PillModifierCase.qml SurfaceSupplement.qml SurfaceInputCase.qml SurfaceModifier.qml SurfaceModifierCase.qml FontModifier.qml FontModifierCase.qml ButtonStyle.qml ButtonStyleCase.qml Tooltip.qml TooltipCase.qml Modal.qml ModalCase.qml ActivityItem.qml ActivityItemCase.qml ActivityCaseGlyph.qml OTPInput.qml OTPInputCase.qml RadioGroup.qml RadioGroupCase.qml Stepper.qml StepperCase.qml DataMetrics.qml DataMetricsCase.qml DataMetricGlyph.qml Main.qml Controls.qml Composition.qml Selection.qml Checkbox.qml SecureField.qml SearchField.qml CollectionFilters.qml Slider.qml Tabs.qml Pagination.qml PaginationIntegers.qml Accordion.qml PresentationStates.qml Spinner.qml Alert.qml Clipping.qml Navigation.qml NavigationCase.qml BreadcrumbHouse.qml SidebarBrandCase.qml SidebarGlyph.qml SidebarBrand.qml AccordionText.qml NavigationIcon.qml SearchGlyph.qml)
qt_add_resources(InstalledConsumer "consumer_fixture_assets" PREFIX "/avelino/fixtures"
    BASE "${CMAKE_CURRENT_SOURCE_DIR}" FILES native-admin-shell-witnesses.json native-mobile-shell-witnesses.json native-mobile-shell-input-witnesses.json native-date-range-witnesses.json native-date-chinese-witnesses.json native-date-literal-input-witnesses.json native-hero-carousel-witnesses.json native-file-input-witnesses.json native-dropdown-menu-witnesses.json native-command-spotlight-witnesses.json native-app-tabs-witnesses.json native-app-tab-icon-metrics.json native-media-library-witnesses.json native-chart-witnesses.json native-pill-witnesses.json native-surface-supplement-witnesses.json native-surface-modifier-witnesses.json native-font-modifier-witnesses.json native-button-style-witnesses.json avatar-wide.ppm native-metric-formatting.json native-stepper-witnesses.json native-radio-witnesses.json native-otp-witnesses.json native-activity-witnesses.json native-modal-witnesses.json)
qt_add_resources(InstalledConsumer "dropdown_menu_images" PREFIX "/qt/qml/InstalledConsumer"
    BASE "${CMAKE_CURRENT_SOURCE_DIR}" FILES menu-symbols/folder-light.svg menu-symbols/folder-dark.svg
    menu-symbols/ellipsis-light.svg menu-symbols/ellipsis-dark.svg)
target_link_libraries(InstalledConsumer PRIVATE Avelino::Avelino Qt6::Quick Qt6::Test)
target_include_directories(InstalledConsumer PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
file(RELATIVE_PATH AVELINO_CONSUMER_IMPORT_PATH "${CMAKE_CURRENT_BINARY_DIR}" "${Avelino_QML_IMPORT_PATH}")
target_compile_definitions(InstalledConsumer PRIVATE AVELINO_INSTALLED_IMPORT_PATH="${AVELINO_CONSUMER_IMPORT_PATH}")
