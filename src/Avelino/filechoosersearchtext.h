#pragma once
#include "filechooserpathinput.h"
#include <QMap>

// Qt owns text, composition, selection and undo commands. Token creation marks
// a Qt edit boundary; token metadata follows the resulting native undo cursor.
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
    State editState()const;
    void finishEdit(const State &before,bool wholeReplacement,bool replay);
    void observeTextChange();
    void remember();
    QString m_mode="general";
    QMap<int,QString> m_modes;
    int m_editDepth=0;
};
