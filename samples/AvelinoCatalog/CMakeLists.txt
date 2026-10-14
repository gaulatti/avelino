qt_add_executable(AvelinoCatalog main.cpp)
set(search_glyph "${PROJECT_SOURCE_DIR}/tests/consumer/SearchGlyph.qml")
set_source_files_properties("${search_glyph}" PROPERTIES QT_RESOURCE_ALIAS "SearchGlyph.qml")
qt_add_qml_module(AvelinoCatalog URI AvelinoCatalog VERSION 0.1
    OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/qml/AvelinoCatalog
    QML_FILES Main.qml ButtonFixture.qml FoundationsFixture.qml SurfacesFixture.qml DataDisplayFixture.qml ControlsFixture.qml ReferenceCaseFixture.qml CompositionFixture.qml SelectionFixture.qml CheckboxFixture.qml SecureFieldFixture.qml SearchFieldFixture.qml CollectionFiltersFixture.qml ${search_glyph})
qt_add_resources(AvelinoCatalog "catalog_fixture_assets" PREFIX "/avelino/fixtures"
    BASE "${PROJECT_SOURCE_DIR}/tests/consumer" FILES "${PROJECT_SOURCE_DIR}/tests/consumer/avatar-wide.ppm")
target_link_libraries(AvelinoCatalog PRIVATE Avelino Qt6::Quick)
install(TARGETS AvelinoCatalog RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
