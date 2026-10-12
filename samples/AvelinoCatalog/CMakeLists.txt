qt_add_executable(AvelinoCatalog main.cpp)
qt_add_qml_module(AvelinoCatalog URI AvelinoCatalog VERSION 0.1
    OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/qml/AvelinoCatalog
    QML_FILES Main.qml ButtonFixture.qml FoundationsFixture.qml SurfacesFixture.qml DataDisplayFixture.qml)
qt_add_resources(AvelinoCatalog "catalog_fixture_assets" PREFIX "/avelino/fixtures"
    BASE "${PROJECT_SOURCE_DIR}/tests/consumer" FILES "${PROJECT_SOURCE_DIR}/tests/consumer/avatar-wide.ppm")
target_link_libraries(AvelinoCatalog PRIVATE Avelino Qt6::Quick)
install(TARGETS AvelinoCatalog RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
