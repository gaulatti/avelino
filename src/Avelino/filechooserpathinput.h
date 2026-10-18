#pragma once
#include <QtQuickTemplates2/private/qquicktextfield_p.h>
#include <QtQml/qqmlregistration.h>

// Qt keeps input, selection, composition and undo; this field adds the missing
// editable-text accessibility interface used by Linux assistive clients.
class FileChooserPathInput : public QQuickTextField {
    Q_OBJECT
    QML_ELEMENT
public:
    explicit FileChooserPathInput(QQuickItem *parent=nullptr);
};
