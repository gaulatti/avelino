#pragma once
#include "filechooserpaths.h"
#include <QtQuick/private/qquicklistview_p.h>
#include <QtQuickTemplates2/private/qquickitemdelegate_p.h>
#include <QPointer>

class FileChooserSuggestionRow : public QQuickItemDelegate {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(int choiceIndex MEMBER m_choiceIndex NOTIFY choiceIndexChanged)
public:
    explicit FileChooserSuggestionRow(QQuickItem *parent=nullptr):QQuickItemDelegate(parent){}
    int m_choiceIndex=-1;
signals:
    void choiceIndexChanged();
};

class FileChooserSuggestions : public QQuickListView {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(FileChooserPaths *pathModel READ pathModel WRITE setPathModel NOTIFY pathModelChanged)
public:
    explicit FileChooserSuggestions(QQuickItem *parent=nullptr);
    ~FileChooserSuggestions()override;
    FileChooserPaths *pathModel()const{return m_model;}
    void setPathModel(FileChooserPaths *model);
signals:
    void pathModelChanged();
private:
    void scheduleSelectionUpdate();
    void updateSelection();
    QPointer<FileChooserPaths> m_model;
    QPointer<QQuickItem> m_previous;
    QString m_previousPath;
    QList<QMetaObject::Connection> m_connections;
    bool m_scheduled=false;
};
