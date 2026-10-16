qt_add_executable(AvelinoComponentTests main.cpp)
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
    NATIVE_SIDEBAR_BRAND_FILE="${PROJECT_SOURCE_DIR}/evidence/reference-investigations/sidebar-brand-20261015/captures.json"
    NATIVE_SPINNER_FILE="${PROJECT_SOURCE_DIR}/evidence/geometry/native-spinner.json"
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
