#pragma once
#include <QtQuickTemplates2/private/qquickitemdelegate_p.h>
#include <QtQuick/private/qquicklistview_p.h>
#include <QtQuick/private/qquickgridview_p.h>
#include <QtQml/qqmlregistration.h>
#include "filechooserlisting.h"

class FileChooserTree : public QQuickListView {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(FileChooserListing *directoryModel READ directoryModel WRITE setDirectoryModel NOTIFY directoryModelChanged)
    Q_PROPERTY(QVariantList columnWidths MEMBER m_columnWidths NOTIFY columnWidthsChanged)
public:
    explicit FileChooserTree(QQuickItem *parent=nullptr);
    FileChooserListing *directoryModel()const{return m_directory;}
    void setDirectoryModel(FileChooserListing *model);
    QVariantList m_columnWidths;
signals:
    void directoryModelChanged();
    void columnWidthsChanged();
private:
    QPointer<FileChooserListing> m_directory;
    QList<QMetaObject::Connection> m_connections;
};

class FileChooserGrid : public QQuickGridView {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(FileChooserRows *directoryModel READ directoryModel WRITE setDirectoryModel NOTIFY directoryModelChanged)
public:
    explicit FileChooserGrid(QQuickItem *parent=nullptr);
    FileChooserRows *directoryModel()const{return m_directory;}
    void setDirectoryModel(FileChooserRows *model);
signals:
    void directoryModelChanged();
private:
    QPointer<FileChooserRows> m_directory;
    QList<QMetaObject::Connection> m_connections;
};

class FileChooserRow : public QQuickItemDelegate {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(bool hierarchical MEMBER m_hierarchical NOTIFY disclosureChanged)
    Q_PROPERTY(bool folder MEMBER m_folder NOTIFY disclosureChanged)
    Q_PROPERTY(bool expanded MEMBER m_expanded NOTIFY disclosureChanged)
    Q_PROPERTY(QQuickItem *view READ view WRITE setView NOTIFY positionChanged)
    Q_PROPERTY(int listingIndex MEMBER m_index NOTIFY positionChanged)
public:
    explicit FileChooserRow(QQuickItem *parent=nullptr);
    QQuickItem *view()const{return m_view;}
    void setView(QQuickItem *view){if(m_view==view)return;m_view=view;emit positionChanged();}
    bool m_hierarchical=false,m_folder=false,m_expanded=false;
    int m_index=-1;
signals:
    void disclosureChanged();
    void disclosureRequested();
    void positionChanged();
private:
    QPointer<QQuickItem> m_view;
};
