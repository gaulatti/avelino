qt_add_executable(AvelinoCatalog main.cpp)
qt_add_qml_module(AvelinoCatalog URI AvelinoCatalog VERSION 0.1 QML_FILES Main.qml ButtonFixture.qml)
target_link_libraries(AvelinoCatalog PRIVATE Avelino Qt6::Quick)
install(TARGETS AvelinoCatalog RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
