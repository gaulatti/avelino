qt_add_executable(AvelinoComponentTests main.cpp)
target_link_libraries(AvelinoComponentTests PRIVATE Qt6::QuickTest Avelino)
target_compile_definitions(AvelinoComponentTests PRIVATE QUICK_TEST_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}")
add_test(NAME components COMMAND AvelinoComponentTests -import ${CMAKE_BINARY_DIR}/qml)
