qt_add_executable(AvelinoComponentTests main.cpp)
target_link_libraries(AvelinoComponentTests PRIVATE Qt6::QuickTest Avelino)
target_compile_definitions(AvelinoComponentTests PRIVATE
    QUICK_TEST_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}"
    NATIVE_GEOMETRY_FILE="${PROJECT_SOURCE_DIR}/evidence/geometry/native-rounded-rectangle.json"
    NATIVE_WRAPPING_FILE="${PROJECT_SOURCE_DIR}/evidence/geometry/native-wrapping.json"
    NATIVE_TYPOGRAPHY_FILE="${PROJECT_SOURCE_DIR}/evidence/geometry/native-typography.json")
add_test(NAME components COMMAND AvelinoComponentTests -import ${CMAKE_BINARY_DIR}/qml)
add_test(NAME components-dpr2 COMMAND AvelinoComponentTests -import ${CMAKE_BINARY_DIR}/qml)
set_tests_properties(components-dpr2 PROPERTIES ENVIRONMENT "QT_SCALE_FACTOR=2")

add_test(NAME slider-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-slider.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)

add_test(NAME pagination-invalid-config COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/check-invalid-pagination.py
    $<TARGET_FILE:AvelinoComponentTests> ${CMAKE_BINARY_DIR}/qml)
