find_package(Qt6 6.8.3 EXACT REQUIRED COMPONENTS Test)
qt_add_executable(AvelinoCatalog main.cpp)
set(navigation_icon "${PROJECT_SOURCE_DIR}/tests/consumer/NavigationIcon.qml")
set_source_files_properties("${navigation_icon}" PROPERTIES QT_RESOURCE_ALIAS "NavigationIcon.qml")
set(search_glyph "${PROJECT_SOURCE_DIR}/tests/consumer/SearchGlyph.qml")
set_source_files_properties("${search_glyph}" PROPERTIES QT_RESOURCE_ALIAS "SearchGlyph.qml")
set(accordion_text "${PROJECT_SOURCE_DIR}/tests/consumer/AccordionText.qml")
set_source_files_properties("${accordion_text}" PROPERTIES QT_RESOURCE_ALIAS "AccordionText.qml")
qt_add_qml_module(AvelinoCatalog URI AvelinoCatalog VERSION 0.1
    OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/qml/AvelinoCatalog
    QML_FILES Main.qml ButtonFixture.qml FoundationsFixture.qml SurfacesFixture.qml DataDisplayFixture.qml ControlsFixture.qml ReferenceCaseFixture.qml CompositionFixture.qml SelectionFixture.qml CheckboxFixture.qml SecureFieldFixture.qml SearchFieldFixture.qml CollectionFiltersFixture.qml SliderFixture.qml TabsFixture.qml PaginationFixture.qml PaginationIntegerFixture.qml AccordionFixture.qml PresentationStatesFixture.qml SpinnerFixture.qml ${accordion_text} ${navigation_icon} ${search_glyph})
qt_add_resources(AvelinoCatalog "catalog_fixture_assets" PREFIX "/avelino/fixtures"
    BASE "${PROJECT_SOURCE_DIR}/tests/consumer" FILES "${PROJECT_SOURCE_DIR}/tests/consumer/avatar-wide.ppm")
target_link_libraries(AvelinoCatalog PRIVATE Avelino Qt6::Quick Qt6::Test)
install(TARGETS AvelinoCatalog RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})

# Match the exported package's QML directory while keeping the executable relocatable.
file(RELATIVE_PATH avelino_catalog_qml_from_bin
    "${CMAKE_INSTALL_FULL_BINDIR}" "${CMAKE_INSTALL_FULL_LIBDIR}/qml")
target_compile_definitions(AvelinoCatalog PRIVATE
    AVELINO_QML_IMPORT_FROM_BIN="${avelino_catalog_qml_from_bin}")
