cmake_minimum_required(VERSION 3.24)
project(AvelinoInstalledConsumer LANGUAGES CXX)
find_package(Avelino 0.1 REQUIRED)
find_package(Qt6 6.8.3 EXACT REQUIRED COMPONENTS Test)
qt_standard_project_setup(REQUIRES 6.8)
qt_add_executable(InstalledConsumer main.cpp)
qt_add_qml_module(InstalledConsumer URI InstalledConsumer VERSION 0.1
    OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/qml/InstalledConsumer
    QML_FILES FontModifier.qml FontModifierCase.qml ButtonStyle.qml ButtonStyleCase.qml Tooltip.qml TooltipCase.qml Modal.qml ModalCase.qml ActivityItem.qml ActivityItemCase.qml ActivityCaseGlyph.qml OTPInput.qml OTPInputCase.qml RadioGroup.qml RadioGroupCase.qml Stepper.qml StepperCase.qml DataMetrics.qml DataMetricsCase.qml DataMetricGlyph.qml Main.qml Controls.qml Composition.qml Selection.qml Checkbox.qml SecureField.qml SearchField.qml CollectionFilters.qml Slider.qml Tabs.qml Pagination.qml PaginationIntegers.qml Accordion.qml PresentationStates.qml Spinner.qml Alert.qml Clipping.qml Navigation.qml NavigationCase.qml BreadcrumbHouse.qml SidebarBrandCase.qml SidebarGlyph.qml SidebarBrand.qml AccordionText.qml NavigationIcon.qml SearchGlyph.qml)
qt_add_resources(InstalledConsumer "consumer_fixture_assets" PREFIX "/avelino/fixtures"
    BASE "${CMAKE_CURRENT_SOURCE_DIR}" FILES native-font-modifier-witnesses.json native-button-style-witnesses.json avatar-wide.ppm native-metric-formatting.json native-stepper-witnesses.json native-radio-witnesses.json native-otp-witnesses.json native-activity-witnesses.json native-modal-witnesses.json)
target_link_libraries(InstalledConsumer PRIVATE Avelino::Avelino Qt6::Quick Qt6::Test)
target_compile_definitions(InstalledConsumer PRIVATE AVELINO_INSTALLED_IMPORT_PATH="${Avelino_QML_IMPORT_PATH}")
