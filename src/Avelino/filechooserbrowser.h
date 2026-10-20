#pragma once
#include "filechoosermodel.h"
#include "filechooserlisting.h"
#include "filechooserplaces.h"

class FileChooserBrowser : public QAbstractListModel {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QVariantList allowedContentTypes READ allowedContentTypes WRITE setAllowedContentTypes NOTIFY allowedContentTypesChanged)
    Q_PROPERTY(bool active READ active NOTIFY activeChanged)
    Q_PROPERTY(int count READ count NOTIFY countChanged)
    Q_PROPERTY(int focusedColumn READ focusedColumn NOTIFY metadataChanged)
    Q_PROPERTY(int selectionColumn READ selectionColumn NOTIFY metadataChanged)
    Q_PROPERTY(QString folderPath READ folderPath NOTIFY metadataChanged)
    Q_PROPERTY(QString folderLabel READ folderLabel NOTIFY metadataChanged)
    Q_PROPERTY(QString error READ error NOTIFY metadataChanged)
    Q_PROPERTY(bool canAccept READ canAccept NOTIFY metadataChanged)
    Q_PROPERTY(QVariantList selectedUrls READ selectedUrls NOTIFY metadataChanged)
    Q_PROPERTY(bool canGoBack READ canGoBack NOTIFY metadataChanged)
    Q_PROPERTY(bool canGoForward READ canGoForward NOTIFY metadataChanged)
    Q_PROPERTY(bool canCreateFolder READ canCreateFolder NOTIFY metadataChanged)
    Q_PROPERTY(QString newFolderError READ newFolderError NOTIFY newFolderErrorChanged)
    Q_PROPERTY(QString viewMode READ viewMode WRITE setViewMode NOTIFY viewModeChanged)
    Q_PROPERTY(FileChooserListing *listing READ listing CONSTANT)
    Q_PROPERTY(FileChooserPlaces *places READ places CONSTANT)
public:
    explicit FileChooserBrowser(QObject *parent=nullptr);
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
    QString folderLabel() const;
    QString error() const;
    bool canAccept() const;
    QVariantList selectedUrls() const;
    bool canGoBack() const{return m_active&&m_historyIndex>0;}
    bool canGoForward() const{return m_active&&m_historyIndex>=0&&m_historyIndex+1<m_history.size();}
    bool canCreateFolder() const;
    QString newFolderError() const{return m_newFolderError;}
    QString viewMode()const{return m_viewMode;}
    void setViewMode(const QString &mode);
    FileChooserListing *listing()const{return m_listing;}
    FileChooserPlaces *places()const{return m_places;}
    Q_INVOKABLE void refreshPlaces();
    Q_INVOKABLE bool chooseLocation(const QUrl &url);
    Q_INVOKABLE bool choosePath(const QUrl &url);
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
    Q_INVOKABLE void goBack();
    Q_INVOKABLE void goForward();
    Q_INVOKABLE QString suggestedFolderName() const;
    Q_INVOKABLE QString folderNameError(const QString &name) const;
    Q_INVOKABLE bool createFolder(const QString &name,const QString &parentPath);
    Q_INVOKABLE void clearNewFolderError();
    Q_INVOKABLE void acceptSelection();
signals:
    void allowedContentTypesChanged();
    void activeChanged();
    void countChanged();
    void metadataChanged();
    void newFolderErrorChanged();
    void viewModeChanged();
    void focusRequested(int column);
    void result(const QVariantMap &value);
private:
    struct Column {FileChooserModel *model;QUrl branch;};
    struct SavedColumn {QUrl folder,branch;};
    struct Location {QList<SavedColumn> columns;};
    Location location() const;
    void rememberNavigation(const Location &before);
    void restoreLocation(int index);
    void setNewFolderError(const QString &message);
    void append(const QUrl &folder);
    void trimAfter(int column);
    void branch(int column,const QUrl &url);
    void clearOtherSelections(int column);
    void completeResult(const QVariantMap &value);
    FileChooserModel *selectionModel() const{return modelAt(m_selection);}
    QList<Column> m_columns;
    QList<Location> m_history;
    int m_historyIndex=-1;
    QVariantList m_types;
    QString m_typeError;
    QString m_newFolderError;
    QString m_viewMode="columns";
    FileChooserListing *m_listing;
    FileChooserPlaces *m_places;
    QUrl m_lastFolder;
    int m_focus=-1,m_selection=-1;
    bool m_active=false,m_completing=false;
};
