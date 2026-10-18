# Ubuntu's application formatter uses system ICU74; Qt's separate ICU73 must
# not be combined with the system headers by FindICU's prefix search.
find_library(ICU_I18N_LIBRARY_RELEASE NAMES libicui18n.so.74 REQUIRED)
find_library(ICU_UC_LIBRARY_RELEASE NAMES libicuuc.so.74 REQUIRED)
find_package(ICU 74.2 EXACT REQUIRED COMPONENTS i18n uc)
include(CheckCXXSourceCompiles)
include(CMakePushCheckState)
cmake_push_check_state(RESET)
set(CMAKE_REQUIRED_LIBRARIES ICU::i18n ICU::uc)
check_cxx_source_compiles("#include <unicode/locid.h>
int main(){icu::Locale locale(\"en_US\");return locale.isBogus();}" AVELINO_ICU_ABI_COHERENT)
cmake_pop_check_state()
if(NOT AVELINO_ICU_ABI_COHERENT)
    message(FATAL_ERROR "ICU74 headers and libraries must resolve to the same system installation")
endif()
set(qml_files BleeckerHeroCarousel.qml BleeckerFileInput.qml FileChooserDialog.qml FileChooserGoTo.qml FileChooserLocationMenu.qml FileChooserViews.qml FileChooserNewFolder.qml FileChooserButton.qml FileChooserGlyph.qml BleeckerDropdownMenu.qml BleeckerCommandSpotlight.qml BleeckerAppTabBar.qml BleeckerMediaLibrary.qml ChartBase.qml BleeckerLineChart.qml BleeckerBarChart.qml BleeckerPieChart.qml BleeckerScatterChart.qml BleeckerSparkline.qml BleeckerSurfaceModifier.qml SurfaceModifierPart.qml BleeckerFont.qml BleeckerText.qml BleeckerButtonStyle.qml ButtonStylePart.qml BleeckerTooltip.qml TooltipHost.qml BleeckerModalDialog.qml BleeckerModal.qml ModalCloseGlyph.qml BleeckerActivityItem.qml ActivityGlyph.qml BleeckerMetric.qml BleeckerStatCard.qml BleeckerIconBadge.qml BleeckerKbd.qml BleeckerTokens.qml BleeckerTheme.qml BleeckerButton.qml
    BleeckerOTPInput.qml BleeckerRadioGroup.qml RadioGlyph.qml BleeckerLoadingSpinner.qml BleeckerStepper.qml StepperGlyph.qml BleeckerAlert.qml AlertGlyph.qml CircularContent.qml BleeckerEmptyState.qml BleeckerErrorState.qml BleeckerLoadingOverlay.qml StateGlyph.qml BleeckerTextField.qml BleeckerSeparator.qml
    BleeckerSkeleton.qml BleeckerBauhausBackground.qml BleeckerProgress.qml
    BleeckerButtonGroup.qml BleeckerHeader.qml BleeckerPanelLayout.qml
    BleeckerCard.qml BleeckerPanel.qml BleeckerAttentionSurface.qml
    BleeckerStatusBadge.qml BleeckerNotificationBadge.qml BleeckerEyebrow.qml BleeckerPill.qml PillModifierPart.qml
    BleeckerAvatar.qml BleeckerDataList.qml BleeckerTimelineItem.qml BleeckerSurface.qml
    BleeckerField.qml BleeckerSwitch.qml BleeckerToggleButton.qml BleeckerSegmentedControl.qml BleeckerTabs.qml BleeckerIconButton.qml BleeckerPagination.qml BleeckerAccordion.qml NavigationGlyph.qml BleeckerTextArea.qml
    BleeckerBrandMark.qml BleeckerBrandLockup.qml BleeckerSidebarItem.qml BleeckerPageHeader.qml BleeckerBreadcrumb.qml BleeckerSectionHeader.qml BleeckerDashboardSection.qml BleeckerDashboardGrid.qml
    BleeckerFooter.qml BleeckerAppShell.qml BleeckerFeedItem.qml BleeckerProgressStack.qml
    BleeckerSelect.qml SelectionGlyph.qml BleeckerCheckbox.qml CheckboxGlyph.qml BleeckerSecureField.qml SecureEyeGlyph.qml BleeckerSearchField.qml InputGlyph.qml
    BleeckerFilterChip.qml BleeckerCollectionFilters.qml CapsuleContent.qml BleeckerSlider.qml
    OwnedText.qml RoundedContent.qml SurfaceShadow.qml attentioncolors.js
    ContinuousSurface.qml continuouscorners.js spinnerpresentation.js)
set_source_files_properties(BleeckerTokens.qml BleeckerTheme.qml TooltipHost.qml PROPERTIES QT_QML_SINGLETON_TYPE TRUE)
set_source_files_properties(FileChooserDialog.qml FileChooserGoTo.qml FileChooserLocationMenu.qml FileChooserViews.qml FileChooserNewFolder.qml FileChooserButton.qml FileChooserGlyph.qml ChartBase.qml PillModifierPart.qml PROPERTIES QT_QML_INTERNAL_TYPE TRUE)
set_source_files_properties(SurfaceModifierPart.qml ButtonStylePart.qml ModalCloseGlyph.qml ActivityGlyph.qml ContinuousSurface.qml OwnedText.qml RoundedContent.qml SurfaceShadow.qml SelectionGlyph.qml CheckboxGlyph.qml SecureEyeGlyph.qml InputGlyph.qml CapsuleContent.qml NavigationGlyph.qml StateGlyph.qml CircularContent.qml StepperGlyph.qml RadioGlyph.qml PROPERTIES QT_QML_INTERNAL_TYPE TRUE)
file(GLOB font_resources CONFIGURE_DEPENDS "${PROJECT_SOURCE_DIR}/assets/fonts/*.ttf")
foreach(font_file IN LISTS font_resources)
    get_filename_component(font_name "${font_file}" NAME)
    set_source_files_properties("${font_file}" PROPERTIES QT_RESOURCE_ALIAS "fonts/${font_name}")
endforeach()
set(brand_logo "${PROJECT_SOURCE_DIR}/assets/brand/BleeckerLogo.png")
set_source_files_properties("${brand_logo}" PROPERTIES QT_RESOURCE_ALIAS "brand/BleeckerLogo.png")
qt_add_library(Avelino SHARED)
# Source plot-proxy arithmetic rounds each Double operation independently.
# Fused multiply-add changes observable coordinates on supported Linux CPUs.
set_source_files_properties(chartrenderer.cpp medialibrarybase.cpp PROPERTIES COMPILE_OPTIONS "-ffp-contract=off")
qt_add_qml_module(Avelino URI Avelino VERSION 0.1
    OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/qml/Avelino
    QML_FILES ${qml_files}
    SOURCES filechooserpaths.h filechooserpaths.cpp filechooserbuttonbase.h filechooserbuttonbase.cpp filechooserplaces.h filechooserplaces.cpp filechooserrow.h filechooserrow.cpp filechooserlisting.h filechooserlisting.cpp filechooserdialogbase.h filechooserdialogbase.cpp filechooserbrowser.h filechooserbrowser.cpp filechoosermodel.h filechoosermodel.cpp dropdowninput.h dropdowninput.cpp menuitems.h menuitems.cpp dropdownlabel.h dropdownlabel.cpp spotlightrows.h spotlightrows.cpp apptabbutton.h apptabbutton.cpp apptaboptions.h apptaboptions.cpp apptabrow.h apptabrow.cpp medialibrarybase.h medialibrarybase.cpp chartrenderer.h chartrenderer.cpp surfaceborderinput.h surfaceborderinput.cpp surfacedecorator.h surfacedecorator.cpp proposaloverlay.h proposaloverlay.cpp tooltipaccess.h tooltipaccess.cpp proposalcolumn.h proposalcolumn.cpp inheritedcontrol.h inheritedcontrol.cpp otptools.h otptools.cpp otpunicode.h selectionidentity.h selectionidentity.cpp radiooptions.h radiooptions.cpp radiogroupbase.h radiogroupbase.cpp bleeckerfonts.h bleeckerfonts.cpp pixelalignment.h pixelalignment.cpp buttonlabel.h buttonlabel.cpp texttools.h texttools.cpp valuetools.h valuetools.cpp softwarecontentmask.h softwarecontentmask.cpp proposalrow.h proposalrow.cpp brandimage.h brandimage.cpp numbertools.h numbertools.cpp
    SOURCES filechooserpathinput.h filechooserpathinput.cpp filechoosersuggestions.h filechoosersuggestions.cpp
    SOURCES herocarouselbase.h herocarouselbase.cpp
    RESOURCES ${font_resources} ${brand_logo} unicode-normalization-17.json)
target_link_libraries(Avelino PUBLIC Qt6::Core Qt6::Gui Qt6::Qml Qt6::Quick Qt6::QuickControls2)
target_link_libraries(Avelino PRIVATE Qt6::QuickPrivate Qt6::QuickTemplates2Private ICU::i18n ICU::uc)
target_include_directories(Avelino PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
install(TARGETS Avelino Avelinoplugin EXPORT AvelinoTargets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}/qml/Avelino)
install(FILES ${CMAKE_BINARY_DIR}/qml/Avelino/qmldir ${CMAKE_BINARY_DIR}/qml/Avelino/Avelino.qmltypes
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/qml/Avelino)
install(FILES ${qml_files} DESTINATION ${CMAKE_INSTALL_LIBDIR}/qml/Avelino)
