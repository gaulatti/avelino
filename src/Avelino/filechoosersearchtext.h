#pragma once
#include "filechooserpathinput.h"
#include <QMap>

// Qt owns text, composition, selection and undo commands. Token commits start
// an undo baseline; later edits preserve token metadata at Qt undo positions.
class FileChooserSearchText : public FileChooserPathInput {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QString tokenMode READ tokenMode WRITE setTokenMode NOTIFY tokenModeChanged)
public:
    explicit FileChooserSearchText(QQuickItem *parent=nullptr);
    QString tokenMode()const{return m_mode;}
    void setTokenMode(const QString &mode);
signals:
    void tokenModeChanged();
protected:
    void keyPressEvent(QKeyEvent *event)override;
    void inputMethodEvent(QInputMethodEvent *event)override;
private:
    struct State {int cursor;QString text,mode;};
    void applyTokenMode(const QString &mode,bool restoring);
    State editState()const;
    void finishEdit(const State &before,bool wholeReplacement,bool replay);
    void observeTextChange();
    void remember();
    QString m_mode="general";
    QMap<int,QString> m_modes;
    int m_editDepth=0;
};
