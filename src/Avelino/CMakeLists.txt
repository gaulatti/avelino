set(qml_files BleeckerTokens.qml BleeckerTheme.qml BleeckerButton.qml
    BleeckerLoadingSpinner.qml BleeckerAlert.qml AlertGlyph.qml CircularContent.qml BleeckerEmptyState.qml BleeckerErrorState.qml BleeckerLoadingOverlay.qml StateGlyph.qml BleeckerTextField.qml BleeckerSeparator.qml
    BleeckerSkeleton.qml BleeckerBauhausBackground.qml BleeckerProgress.qml
    BleeckerButtonGroup.qml BleeckerHeader.qml BleeckerPanelLayout.qml
    BleeckerCard.qml BleeckerPanel.qml BleeckerAttentionSurface.qml
    BleeckerStatusBadge.qml BleeckerNotificationBadge.qml BleeckerEyebrow.qml
    BleeckerAvatar.qml BleeckerDataList.qml BleeckerTimelineItem.qml BleeckerSurface.qml
    BleeckerField.qml BleeckerSwitch.qml BleeckerToggleButton.qml BleeckerSegmentedControl.qml BleeckerTabs.qml BleeckerIconButton.qml BleeckerPagination.qml BleeckerAccordion.qml NavigationGlyph.qml BleeckerTextArea.qml
    BleeckerBrandMark.qml BleeckerBrandLockup.qml BleeckerSidebarItem.qml BleeckerPageHeader.qml BleeckerBreadcrumb.qml BleeckerSectionHeader.qml BleeckerDashboardSection.qml BleeckerDashboardGrid.qml
    BleeckerFooter.qml BleeckerAppShell.qml BleeckerFeedItem.qml BleeckerProgressStack.qml
    BleeckerSelect.qml SelectionGlyph.qml BleeckerCheckbox.qml CheckboxGlyph.qml BleeckerSecureField.qml SecureEyeGlyph.qml BleeckerSearchField.qml InputGlyph.qml
    BleeckerFilterChip.qml BleeckerCollectionFilters.qml CapsuleContent.qml BleeckerSlider.qml
    OwnedText.qml RoundedContent.qml SurfaceShadow.qml attentioncolors.js
    ContinuousSurface.qml continuouscorners.js spinnerpresentation.js)
set_source_files_properties(BleeckerTokens.qml BleeckerTheme.qml PROPERTIES QT_QML_SINGLETON_TYPE TRUE)
set_source_files_properties(ContinuousSurface.qml OwnedText.qml RoundedContent.qml SurfaceShadow.qml SelectionGlyph.qml CheckboxGlyph.qml SecureEyeGlyph.qml InputGlyph.qml CapsuleContent.qml NavigationGlyph.qml StateGlyph.qml CircularContent.qml PROPERTIES QT_QML_INTERNAL_TYPE TRUE)
file(GLOB font_resources CONFIGURE_DEPENDS "${PROJECT_SOURCE_DIR}/assets/fonts/*.ttf")
foreach(font_file IN LISTS font_resources)
    get_filename_component(font_name "${font_file}" NAME)
    set_source_files_properties("${font_file}" PROPERTIES QT_RESOURCE_ALIAS "fonts/${font_name}")
endforeach()
set(brand_logo "${PROJECT_SOURCE_DIR}/assets/brand/BleeckerLogo.png")
set_source_files_properties("${brand_logo}" PROPERTIES QT_RESOURCE_ALIAS "brand/BleeckerLogo.png")
qt_add_library(Avelino SHARED)
qt_add_qml_module(Avelino URI Avelino VERSION 0.1
    OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/qml/Avelino
    QML_FILES ${qml_files}
    SOURCES bleeckerfonts.h bleeckerfonts.cpp pixelalignment.h pixelalignment.cpp buttonlabel.h buttonlabel.cpp texttools.h texttools.cpp valuetools.h valuetools.cpp softwarecontentmask.h softwarecontentmask.cpp proposalrow.h proposalrow.cpp brandimage.h brandimage.cpp
    RESOURCES ${font_resources} ${brand_logo})
target_link_libraries(Avelino PUBLIC Qt6::Core Qt6::Gui Qt6::Qml Qt6::Quick Qt6::QuickControls2)
target_link_libraries(Avelino PRIVATE Qt6::QuickPrivate)
target_include_directories(Avelino PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
install(TARGETS Avelino Avelinoplugin EXPORT AvelinoTargets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}/qml/Avelino)
install(FILES ${CMAKE_BINARY_DIR}/qml/Avelino/qmldir ${CMAKE_BINARY_DIR}/qml/Avelino/Avelino.qmltypes
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/qml/Avelino)
install(FILES ${qml_files} DESTINATION ${CMAKE_INSTALL_LIBDIR}/qml/Avelino)
