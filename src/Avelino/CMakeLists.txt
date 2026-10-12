set(qml_files BleeckerTokens.qml BleeckerTheme.qml BleeckerButton.qml BleeckerLoadingSpinner.qml BleeckerTextField.qml ContinuousSurface.qml continuouscorners.js)
set_source_files_properties(BleeckerTokens.qml BleeckerTheme.qml PROPERTIES QT_QML_SINGLETON_TYPE TRUE)
set_source_files_properties(ContinuousSurface.qml PROPERTIES QT_QML_INTERNAL_TYPE TRUE)
file(GLOB font_resources CONFIGURE_DEPENDS "${PROJECT_SOURCE_DIR}/assets/fonts/*.ttf")
foreach(font_file IN LISTS font_resources)
    get_filename_component(font_name "${font_file}" NAME)
    set_source_files_properties("${font_file}" PROPERTIES QT_RESOURCE_ALIAS "fonts/${font_name}")
endforeach()
qt_add_library(Avelino SHARED)
qt_add_qml_module(Avelino URI Avelino VERSION 0.1
    OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/qml/Avelino
    QML_FILES ${qml_files}
    SOURCES bleeckerfonts.h bleeckerfonts.cpp pixelalignment.h pixelalignment.cpp buttonlabel.h buttonlabel.cpp
    RESOURCES ${font_resources})
target_link_libraries(Avelino PUBLIC Qt6::Core Qt6::Gui Qt6::Qml Qt6::Quick Qt6::QuickControls2)
target_include_directories(Avelino PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
install(TARGETS Avelino Avelinoplugin EXPORT AvelinoTargets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}/qml/Avelino)
install(FILES ${CMAKE_BINARY_DIR}/qml/Avelino/qmldir ${CMAKE_BINARY_DIR}/qml/Avelino/Avelino.qmltypes
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/qml/Avelino)
install(FILES ${qml_files} DESTINATION ${CMAKE_INSTALL_LIBDIR}/qml/Avelino)
