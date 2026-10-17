#pragma once
#include "filechoosermodel.h"

class FileChooserBrowser : public QAbstractListModel {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QVariantList allowedContentTypes READ allowedContentTypes WRITE setAllowedContentTypes NOTIFY allowedContentTypesChanged)
    Q_PROPERTY(bool active READ active NOTIFY activeChanged)
    Q_PROPERTY(int count READ count NOTIFY countChanged)
    Q_PROPERTY(int focusedColumn READ focusedColumn NOTIFY metadataChanged)
    Q_PROPERTY(int selectionColumn READ selectionColumn NOTIFY metadataChanged)
    Q_PROPERTY(QString folderPath READ folderPath NOTIFY metadataChanged)
    Q_PROPERTY(QString error READ error NOTIFY metadataChanged)
    Q_PROPERTY(bool canAccept READ canAccept NOTIFY metadataChanged)
    Q_PROPERTY(QVariantList selectedUrls READ selectedUrls NOTIFY metadataChanged)
public:
    using QAbstractListModel::QAbstractListModel;
    enum Role {ModelRole=Qt::UserRole+1,BranchRole};
    int rowCount(const QModelIndex &parent={}) const override{return parent.isValid()?0:m_columns.size();}
    QVariant data(const QModelIndex &index,int role) const override;
    QHash<int,QByteArray> roleNames() const override{return {{ModelRole,"directoryModel"},{BranchRole,"navigationUrl"}};}
    QVariantList allowedContentTypes() const{return m_types;}
    void setAllowedContentTypes(const QVariantList &value);
    bool active() const{return m_active;}
    int count() const{return m_columns.size();}
    int focusedColumn() const{return m_focus;}
    int selectionColumn() const{return m_selection;}
    QString folderPath() const;
    QString error() const;
    bool canAccept() const;
    QVariantList selectedUrls() const;
    Q_INVOKABLE QUrl defaultFolder() const;
    Q_INVOKABLE FileChooserModel *modelAt(int column) const;
    Q_INVOKABLE bool open(const QUrl &initialFolder);
    Q_INVOKABLE void cancel();
    Q_INVOKABLE void choose(int column,int row,int modifiers=0);
    Q_INVOKABLE void chooseFromInput(int column,int row);
    Q_INVOKABLE void activate(int column,int row);
    Q_INVOKABLE void move(int offset,int modifiers=0);
    Q_INVOKABLE void moveFromInput(int offset);
    Q_INVOKABLE void focusLeft();
    Q_INVOKABLE void focusRight();
    Q_INVOKABLE void selectAll();
    Q_INVOKABLE bool navigatePath(const QString &path);
    Q_INVOKABLE bool goUp();
    Q_INVOKABLE void acceptSelection();
signals:
    void allowedContentTypesChanged();
    void activeChanged();
    void countChanged();
    void metadataChanged();
    void focusRequested(int column);
    void result(const QVariantMap &value);
private:
    struct Column {FileChooserModel *model;QUrl branch;};
    void append(const QUrl &folder);
    void trimAfter(int column);
    void branch(int column,const QUrl &url);
    void clearOtherSelections(int column);
    FileChooserModel *selectionModel() const{return modelAt(m_selection);}
    QList<Column> m_columns;
    QVariantList m_types;
    QString m_typeError;
    QUrl m_lastFolder;
    int m_focus=-1,m_selection=-1;
    bool m_active=false,m_completing=false;
};
