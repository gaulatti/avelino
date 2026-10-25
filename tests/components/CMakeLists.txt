qt_add_executable(AvelinoComponentTests main.cpp)
qt_add_executable(AvelinoDateRangeToolsTests daterangetools.cpp)
qt_add_executable(AvelinoDateRangeUiTests daterangeui.cpp)
qt_add_resources(AvelinoDateRangeUiTests date_range_fixtures PREFIX "/date-range-tests" FILES date-range-fixture.qml)
target_link_libraries(AvelinoDateRangeUiTests PRIVATE Avelino Qt6::Quick Qt6::Test)
target_compile_definitions(AvelinoDateRangeUiTests PRIVATE
    AVELINO_DATE_IMPORT_PATH="${CMAKE_BINARY_DIR}/qml"
    DATE_RANGE_CASE_FILE="${PROJECT_SOURCE_DIR}/tests/consumer/DateRangePickerCase.qml"
    NATIVE_DATE_WITNESSES="${PROJECT_SOURCE_DIR}/tests/consumer/native-date-range-witnesses.json"
    NATIVE_DATE_WIDTH_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/date-range-width-20261018"
    NATIVE_DATE_CHINESE_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/date-range-chinese-20261018")
add_dependencies(AvelinoDateRangeUiTests Avelinoplugin)
add_test(NAME date-range-owned-input COMMAND AvelinoDateRangeUiTests)
add_test(NAME date-range-owned-input-dpr2 COMMAND AvelinoDateRangeUiTests)
set_tests_properties(date-range-owned-input-dpr2 PROPERTIES ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_QUICK_BACKEND=software;QT_SCALE_FACTOR=2")
set_tests_properties(date-range-owned-input PROPERTIES ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_QUICK_BACKEND=software")
target_link_libraries(AvelinoDateRangeToolsTests PRIVATE Avelino Qt6::Gui Qt6::Test)
target_include_directories(AvelinoDateRangeToolsTests PRIVATE ${PROJECT_SOURCE_DIR}/src/Avelino)
target_compile_definitions(AvelinoDateRangeToolsTests PRIVATE
    NATIVE_DATE_RANGE_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/date-range-20261018"
    NATIVE_DATE_INPUT_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/date-range-input-20261018"
    NATIVE_DATE_FONT_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/date-range-font-20261018"
    NATIVE_DATE_WIDTH_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/date-range-width-20261018"
    NATIVE_DATE_RESERVATION_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/date-range-reservation-20261018"
    NATIVE_DATE_CHINESE_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/date-range-chinese-20261018")
add_test(NAME date-range-calendar-components COMMAND AvelinoDateRangeToolsTests)
set_tests_properties(date-range-calendar-components PROPERTIES ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_QUICK_BACKEND=software")
qt_add_executable(AvelinoHeroCarouselTests herocarousel.cpp)
qt_add_resources(AvelinoHeroCarouselTests hero_carousel_fixtures PREFIX "/hero-carousel-tests" FILES herocarousel-fixture.qml)
target_link_libraries(AvelinoHeroCarouselTests PRIVATE Avelino Qt6::Quick Qt6::Test)
target_include_directories(AvelinoHeroCarouselTests PRIVATE ${PROJECT_SOURCE_DIR}/src/Avelino)
target_compile_definitions(AvelinoHeroCarouselTests PRIVATE AVELINO_HERO_IMPORT_PATH="${CMAKE_BINARY_DIR}/qml")
add_dependencies(AvelinoHeroCarouselTests Avelinoplugin)
add_test(NAME hero-carousel-retained-slides COMMAND AvelinoHeroCarouselTests)
add_test(NAME hero-carousel-retained-slides-dpr2 COMMAND AvelinoHeroCarouselTests)
set_tests_properties(hero-carousel-retained-slides PROPERTIES ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_QUICK_BACKEND=software;QT_SCALE_FACTOR=1")
set_tests_properties(hero-carousel-retained-slides-dpr2 PROPERTIES ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_QUICK_BACKEND=software;QT_SCALE_FACTOR=2")
target_link_libraries(AvelinoComponentTests PRIVATE Qt6::QuickTest Avelino)
target_compile_definitions(AvelinoComponentTests PRIVATE
    QUICK_TEST_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}"
    NATIVE_GEOMETRY_FILE="${PROJECT_SOURCE_DIR}/evidence/geometry/native-rounded-rectangle.json"
    NATIVE_WRAPPING_FILE="${PROJECT_SOURCE_DIR}/evidence/geometry/native-wrapping.json"
    NATIVE_CENTERED_TEXT_FILE="${PROJECT_SOURCE_DIR}/evidence/geometry/native-presentation-states.json"
    NATIVE_HOSTED_LOADING_FILE="${PROJECT_SOURCE_DIR}/evidence/geometry/native-loading-hosted.json"
    NATIVE_PROSE_BOUNDARIES_FILE="${PROJECT_SOURCE_DIR}/evidence/geometry/native-prose-boundaries.json"
    NATIVE_ALERT_TEXT_FILE="${PROJECT_SOURCE_DIR}/evidence/geometry/native-alert-text-layout.json"
    NATIVE_ALERT_FILE="${PROJECT_SOURCE_DIR}/evidence/geometry/native-alert.json"
    NATIVE_NAVIGATION_FILE="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/navigation-layout-20261015/captures.json"
    NATIVE_NAVIGATION_TEXT_FILE="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/navigation-layout-20261015/text-layout/measurements.json"
    NATIVE_NUMERIC_TEXT_FILE="${PROJECT_SOURCE_DIR}/evidence/geometry/native-numeric-text.json"
    NATIVE_DATA_METRICS_FILE="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/data-metrics-20261015/captures.json"
    NATIVE_DATA_METRICS_INPUT_FILE="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/data-metrics-inputs-20261015/fixture-inputs.json"
    NATIVE_FOOTER_FILE="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/footer-slots-20261019/captures.json"
    NATIVE_ADMIN_SHELL_FILE="${PROJECT_SOURCE_DIR}/tests/consumer/native-admin-shell-witnesses.json"
    NATIVE_MOBILE_SHELL_FILE="${PROJECT_SOURCE_DIR}/tests/consumer/native-mobile-shell-witnesses.json"
    NATIVE_BUTTON_GROUP_FILE="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/button-group-slots-20261019/captures.json"
    NATIVE_SIDEBAR_BRAND_FILE="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/sidebar-brand-20261015/captures.json"
    NATIVE_SPINNER_FILE="${PROJECT_SOURCE_DIR}/evidence/geometry/native-spinner.json"
    NATIVE_RADIO_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/radio-20261016"
    NATIVE_ACTIVITY_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/activity-item-20261016"
    NATIVE_MODAL_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/modal-20261016"
    NATIVE_MODAL_INPUT_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/modal-input-20261016"
    NATIVE_MEDIA_LIBRARY_FILE="${PROJECT_SOURCE_DIR}/tests/consumer/native-media-library-witnesses.json"
    NATIVE_BUTTON_STYLE_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/button-style-20261016"
    NATIVE_FONT_MODIFIER_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/font-modifier-20261016"
    NATIVE_SURFACE_MODIFIER_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/surface-modifier-20261016"
    NATIVE_FONT_BASELINE_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/font-baseline-20261016"
    NATIVE_ACTIVITY_LAYOUT_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/activity-layout-mechanics-20261016"
    NATIVE_ACTIVITY_ALIGNMENT_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/activity-text-alignment-20261016"
    NATIVE_OTP_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/otp-20261016"
    OTP_TRACE_OUTPUT_DIRECTORY="${PROJECT_SOURCE_DIR}/artifacts/otp-editor-traces"
    NATIVE_STEPPER_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/stepper-20261016"
    NATIVE_TYPOGRAPHY_FILE="${PROJECT_SOURCE_DIR}/evidence/geometry/native-typography.json")
add_test(NAME components COMMAND AvelinoComponentTests -import ${CMAKE_BINARY_DIR}/qml)
add_test(NAME components-dpr2 COMMAND AvelinoComponentTests -import ${CMAKE_BINARY_DIR}/qml)
set_tests_properties(components-dpr2 PROPERTIES ENVIRONMENT "QT_SCALE_FACTOR=2")

add_test(NAME slider-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-slider.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)

add_test(NAME pagination-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-pagination.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)

add_test(NAME presentation-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-presentation.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)

add_test(NAME navigation-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-navigation.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)

add_test(NAME sidebar-brand-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-sidebar-brand.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)

add_test(NAME data-metrics-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-data-metrics.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)

add_test(NAME stepper-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-stepper.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)

add_test(NAME radio-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-radio.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)

add_test(NAME radio-catalog-metadata COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-radio-catalog.py
    $<TARGET_FILE:AvelinoCatalog> ${CMAKE_BINARY_DIR}/qml ${PROJECT_SOURCE_DIR})

qt_add_executable(AvelinoOTPSemanticsTests otptools.cpp)
target_link_libraries(AvelinoOTPSemanticsTests PRIVATE Qt6::Test Avelino)
target_include_directories(AvelinoOTPSemanticsTests PRIVATE ${PROJECT_SOURCE_DIR}/src/Avelino)
target_compile_definitions(AvelinoOTPSemanticsTests PRIVATE
    NATIVE_OTP_DIRECTORY="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/otp-20261016")
add_test(NAME otp-native-transformation COMMAND AvelinoOTPSemanticsTests)
add_test(NAME otp-invalid-transformation COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-otp.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)
add_test(NAME otp-invalid-input COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-otp-input.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)
add_test(NAME otp-catalog-metadata COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-otp-catalog.py
    $<TARGET_FILE:AvelinoCatalog> ${CMAKE_BINARY_DIR}/qml ${PROJECT_SOURCE_DIR})
add_test(NAME activity-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-activity.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)
add_test(NAME activity-catalog-metadata COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-activity-catalog.py
    $<TARGET_FILE:AvelinoCatalog> ${CMAKE_BINARY_DIR}/qml ${PROJECT_SOURCE_DIR})

add_test(NAME modal-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-modal.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)
add_test(NAME modal-catalog-metadata COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-modal-catalog.py
    $<TARGET_FILE:AvelinoCatalog> ${CMAKE_BINARY_DIR}/qml ${PROJECT_SOURCE_DIR})

add_test(NAME tooltip-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-tooltip.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)
add_test(NAME tooltip-catalog-metadata COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-tooltip-catalog.py
    $<TARGET_FILE:AvelinoCatalog> ${CMAKE_BINARY_DIR}/qml ${PROJECT_SOURCE_DIR})

add_test(NAME button-style-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-button-style.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)
add_test(NAME button-style-catalog-metadata COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-button-style-catalog.py
    $<TARGET_FILE:AvelinoCatalog> ${CMAKE_BINARY_DIR}/qml ${PROJECT_SOURCE_DIR})

add_test(NAME font-modifier-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-font-modifier.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)
add_test(NAME font-modifier-catalog-metadata COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-font-modifier-catalog.py
    $<TARGET_FILE:AvelinoCatalog> ${CMAKE_BINARY_DIR}/qml ${PROJECT_SOURCE_DIR})

add_test(NAME surface-modifier-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-surface-modifier.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)

add_test(NAME surface-modifier-catalog-metadata COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-surface-modifier-catalog.py
    $<TARGET_FILE:AvelinoCatalog> ${CMAKE_BINARY_DIR}/qml ${PROJECT_SOURCE_DIR})

add_test(NAME pill-modifier-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-pill-modifier.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)

add_test(NAME pill-modifier-catalog-metadata COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-pill-modifier-catalog.py
    $<TARGET_FILE:AvelinoCatalog> ${CMAKE_BINARY_DIR}/qml ${PROJECT_SOURCE_DIR})

add_test(NAME charts-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-charts.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)
add_test(NAME charts-catalog-metadata COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-charts-catalog.py
    $<TARGET_FILE:AvelinoCatalog> ${CMAKE_BINARY_DIR}/qml ${PROJECT_SOURCE_DIR})

add_test(NAME media-library-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-media-library.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)
add_test(NAME media-library-catalog-metadata COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-media-library-catalog.py
    $<TARGET_FILE:AvelinoCatalog> ${CMAKE_BINARY_DIR}/qml ${PROJECT_SOURCE_DIR})
add_test(NAME hero-carousel-catalog-metadata COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-hero-carousel-catalog.py
    $<TARGET_FILE:AvelinoCatalog> ${CMAKE_BINARY_DIR}/qml ${PROJECT_SOURCE_DIR})

add_test(NAME app-tabs-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-app-tabs.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)
add_test(NAME app-tabs-catalog-metadata COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-app-tabs-catalog.py
    $<TARGET_FILE:AvelinoCatalog> ${CMAKE_BINARY_DIR}/qml ${PROJECT_SOURCE_DIR})

qt_add_executable(AvelinoAppTabRasterTests app-tabs-raster.cpp)
set(app_tab_raster_qml)
foreach(name AppTabs.qml AppTabsCase.qml AppTabGlyph.qml apptabfixturemetrics.js)
    set(path "${PROJECT_SOURCE_DIR}/tests/consumer/${name}")
    set_source_files_properties("${path}" PROPERTIES QT_RESOURCE_ALIAS "${name}")
    list(APPEND app_tab_raster_qml "${path}")
endforeach()
qt_add_qml_module(AvelinoAppTabRasterTests URI AvelinoAppTabRasterTests VERSION 0.1
    OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/qml/AvelinoAppTabRasterTests QML_FILES ${app_tab_raster_qml})
qt_add_resources(AvelinoAppTabRasterTests app_tab_raster_metrics PREFIX "/avelino/fixtures"
    BASE "${PROJECT_SOURCE_DIR}/tests/consumer" FILES "${PROJECT_SOURCE_DIR}/tests/consumer/native-app-tab-icon-metrics.json")
qt_add_resources(AvelinoAppTabRasterTests app_tab_raster_sequence PREFIX "/avelino/fixtures"
    BASE "${CMAKE_CURRENT_SOURCE_DIR}" FILES app-tabs-raster-sequence.json)
target_link_libraries(AvelinoAppTabRasterTests PRIVATE Avelino Qt6::Quick Qt6::Test)
target_compile_definitions(AvelinoAppTabRasterTests PRIVATE
    AVELINO_APP_TABS_IMPORT_PATH="${CMAKE_BINARY_DIR}/qml"
    AVELINO_APP_TABS_RASTER_EVIDENCE_ROOT="${PROJECT_SOURCE_DIR}/artifacts/linux/app-tabs-raster")
add_test(NAME app-tabs-retained-raster COMMAND AvelinoAppTabRasterTests)
add_test(NAME app-tabs-retained-raster-dpr2 COMMAND AvelinoAppTabRasterTests)
set_tests_properties(app-tabs-retained-raster PROPERTIES ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_QUICK_BACKEND=software;QT_SCALE_FACTOR=1")
set_tests_properties(app-tabs-retained-raster-dpr2 PROPERTIES ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_QUICK_BACKEND=software;QT_SCALE_FACTOR=2")

add_test(NAME command-spotlight-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-command-spotlight.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)

add_test(NAME command-spotlight-catalog-metadata COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-command-spotlight-catalog.py
    $<TARGET_FILE:AvelinoCatalog> ${CMAKE_BINARY_DIR}/qml ${PROJECT_SOURCE_DIR})

add_test(NAME dropdown-menu-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-dropdown-menu.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)

add_test(NAME dropdown-menu-catalog-metadata COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-dropdown-menu-catalog.py
    $<TARGET_FILE:AvelinoCatalog> ${CMAKE_BINARY_DIR}/qml ${PROJECT_SOURCE_DIR})

qt_add_executable(AvelinoFileChooserTests filechoosermodel.cpp
    ${PROJECT_SOURCE_DIR}/src/Avelino/filechoosermodel.cpp
    ${PROJECT_SOURCE_DIR}/src/Avelino/filechoosermodel.h)
target_link_libraries(AvelinoFileChooserTests PRIVATE Qt6::Qml Qt6::Test)
target_include_directories(AvelinoFileChooserTests PRIVATE ${PROJECT_SOURCE_DIR}/src/Avelino)
add_test(NAME file-chooser-filesystem COMMAND AvelinoFileChooserTests)

qt_add_executable(AvelinoFileBrowserTests filechooserbrowser.cpp
    ${PROJECT_SOURCE_DIR}/src/Avelino/filechooserrows.h
    ${PROJECT_SOURCE_DIR}/src/Avelino/filechoosersearch.cpp
    ${PROJECT_SOURCE_DIR}/src/Avelino/filechoosersearch.h
    ${PROJECT_SOURCE_DIR}/src/Avelino/filechooserplaces.cpp
    ${PROJECT_SOURCE_DIR}/src/Avelino/filechooserplaces.h
    ${PROJECT_SOURCE_DIR}/src/Avelino/filechooserlisting.cpp
    ${PROJECT_SOURCE_DIR}/src/Avelino/filechooserlisting.h
    ${PROJECT_SOURCE_DIR}/src/Avelino/filechooserbrowser.cpp
    ${PROJECT_SOURCE_DIR}/src/Avelino/filechooserbrowser.h
    ${PROJECT_SOURCE_DIR}/src/Avelino/filechoosermodel.cpp
    ${PROJECT_SOURCE_DIR}/src/Avelino/filechoosermodel.h)
target_link_libraries(AvelinoFileBrowserTests PRIVATE Qt6::Gui Qt6::Qml Qt6::Test PkgConfig::Tracker)
target_include_directories(AvelinoFileBrowserTests PRIVATE ${PROJECT_SOURCE_DIR}/src/Avelino)
add_test(NAME file-chooser-columns COMMAND AvelinoFileBrowserTests)

qt_add_executable(AvelinoFilePlacesTests filechooserplaces.cpp
    ${PROJECT_SOURCE_DIR}/src/Avelino/filechooserplaces.cpp
    ${PROJECT_SOURCE_DIR}/src/Avelino/filechooserplaces.h)
target_link_libraries(AvelinoFilePlacesTests PRIVATE Qt6::Qml Qt6::Test)
target_include_directories(AvelinoFilePlacesTests PRIVATE ${PROJECT_SOURCE_DIR}/src/Avelino)
add_test(NAME file-chooser-places COMMAND AvelinoFilePlacesTests)

qt_add_executable(AvelinoFilePathTests filechooserpaths.cpp
    ${PROJECT_SOURCE_DIR}/src/Avelino/filechooserpaths.cpp
    ${PROJECT_SOURCE_DIR}/src/Avelino/filechooserpaths.h)
target_link_libraries(AvelinoFilePathTests PRIVATE Qt6::Qml Qt6::Test)
target_include_directories(AvelinoFilePathTests PRIVATE ${PROJECT_SOURCE_DIR}/src/Avelino)
add_test(NAME file-chooser-paths COMMAND AvelinoFilePathTests)

qt_add_executable(AvelinoFileInputUiTests fileinput-ui.cpp)
qt_add_resources(AvelinoFileInputUiTests file_input_ui_fixtures PREFIX "/file-input-tests"
    FILES fileinput-fixture.qml)
target_link_libraries(AvelinoFileInputUiTests PRIVATE Avelino Qt6::Quick Qt6::Test)
target_include_directories(AvelinoFileInputUiTests PRIVATE ${PROJECT_SOURCE_DIR}/src/Avelino)
target_compile_definitions(AvelinoFileInputUiTests PRIVATE AVELINO_FILE_INPUT_IMPORT_PATH="${CMAKE_BINARY_DIR}/qml")
if(NOT DEFINED AVELINO_FILE_INPUT_EVIDENCE_DIR)
    set(AVELINO_FILE_INPUT_EVIDENCE_DIR "${CMAKE_CURRENT_BINARY_DIR}/file-input-evidence")
endif()
target_compile_definitions(AvelinoFileInputUiTests PRIVATE AVELINO_FILE_INPUT_EVIDENCE_DIR="${AVELINO_FILE_INPUT_EVIDENCE_DIR}")
add_dependencies(AvelinoFileInputUiTests Avelinoplugin)
add_test(NAME file-input-owned-ui COMMAND AvelinoFileInputUiTests)
set_tests_properties(file-input-owned-ui PROPERTIES ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_QUICK_BACKEND=software;XDG_RUNTIME_DIR=/tmp/avelino-file-input-runtime")
add_test(NAME file-input-owned-ui-dpr2 COMMAND AvelinoFileInputUiTests)
set_tests_properties(file-input-owned-ui-dpr2 PROPERTIES ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_QUICK_BACKEND=software;QT_SCALE_FACTOR=2;XDG_RUNTIME_DIR=/tmp/avelino-file-input-runtime")

# Teardown regression for attached derived items, including disabled ancestry.
qt_add_executable(AvelinoItemLifetimeTests itemlifetime.cpp)
target_include_directories(AvelinoItemLifetimeTests PRIVATE "${PROJECT_SOURCE_DIR}/src/Avelino")
target_link_libraries(AvelinoItemLifetimeTests PRIVATE Avelino Qt6::Test Qt6::QuickPrivate Qt6::QuickTemplates2Private)
target_compile_definitions(AvelinoItemLifetimeTests PRIVATE AVELINO_LIFETIME_IMPORT_PATH="${CMAKE_BINARY_DIR}/qml")
add_test(NAME item-lifetime COMMAND AvelinoItemLifetimeTests)
add_test(NAME item-lifetime-dpr2 COMMAND AvelinoItemLifetimeTests)
set_tests_properties(item-lifetime PROPERTIES ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_QUICK_BACKEND=software;QT_SCALE_FACTOR=1")
set_tests_properties(item-lifetime-dpr2 PROPERTIES ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_QUICK_BACKEND=software;QT_SCALE_FACTOR=2")

qt_add_executable(AvelinoFileSearchTests filesearch.cpp)
qt_add_resources(AvelinoFileSearchTests file_search_ui_fixtures PREFIX "/file-input-tests" FILES fileinput-fixture.qml)
target_link_libraries(AvelinoFileSearchTests PRIVATE Avelino Qt6::Quick Qt6::Test)
target_include_directories(AvelinoFileSearchTests PRIVATE ${PROJECT_SOURCE_DIR}/src/Avelino)
target_compile_definitions(AvelinoFileSearchTests PRIVATE AVELINO_FILE_INPUT_IMPORT_PATH="${CMAKE_BINARY_DIR}/qml"
    AVELINO_FILE_SEARCH_EVIDENCE_DIR="${CMAKE_CURRENT_BINARY_DIR}/file-search-evidence")
add_dependencies(AvelinoFileSearchTests Avelinoplugin)
foreach(scale RANGE 1 2)
    add_test(NAME file-input-indexed-search-dpr${scale} COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/run-file-search.py $<TARGET_FILE:AvelinoFileSearchTests>)
    set_tests_properties(file-input-indexed-search-dpr${scale} PROPERTIES ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_QUICK_BACKEND=software;QT_SCALE_FACTOR=${scale}")
endforeach()
add_test(NAME file-input-search-missing-index COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/run-file-search.py --no-index $<TARGET_FILE:AvelinoFileSearchTests> unavailableIndexIsVisibleAndCancels)
set_tests_properties(file-input-search-missing-index PROPERTIES ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_QUICK_BACKEND=software")
