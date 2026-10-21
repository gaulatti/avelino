#pragma once
#include <QAbstractListModel>
#include <QVariantMap>
#include <QtQml/qqmlregistration.h>

// The chooser's directory and indexed result views share selection and row
// identity. Their query/navigation policies stay in the concrete models.
class FileChooserRows : public QAbstractListModel {
    Q_OBJECT
    QML_ANONYMOUS
public:
    using QAbstractListModel::QAbstractListModel;
    virtual int count()const=0;
    virtual int currentIndex()const=0;
    virtual QVariantMap entry(int row)const=0;
    virtual QVariantList selection()const=0;
    virtual void setSelection(const QVariantList &urls)=0;
    virtual void select(int row,int modifiers=0)=0;
    virtual void selectFromInput(int row)=0;
    virtual void selectAll()=0;
};
