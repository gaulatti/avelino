#pragma once
#include <QtQuickTemplates2/private/qquicktextarea_p.h>
#include <QtQml/qqmlregistration.h>
#include "filechoosersearchtokens.h"
#include <QMap>
#include <QTextCharFormat>
#include <QVariantList>
#include <functional>
#include <memory>

class FileChooserSearchHistory;

// Qt owns document commands, selection, composition and layout. Token metadata
// lives in inline object formats. Scoped native history and restored selection
// supplement the public Qt document commands.
class FileChooserSearchText : public QQuickTextArea {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QString text READ text WRITE setText NOTIFY textChanged)
    Q_PROPERTY(QVariantList expression READ expression WRITE setExpression NOTIFY expressionChanged)
    Q_PROPERTY(FileChooserSearchTokens *tokens READ tokens CONSTANT)
    Q_PROPERTY(QString draft READ draft NOTIFY draftChanged)
public:
    explicit FileChooserSearchText(QQuickItem *parent=nullptr);
    ~FileChooserSearchText()override;
    QVariantList expression()const;
    void setExpression(const QVariantList &value);
    void setText(const QString &value);
    FileChooserSearchTokens *tokens()const{return m_tokens;}
    QString draft()const;
    Q_INVOKABLE void commitDraft(const QString &mode);
    Q_INVOKABLE void setTokenModeAt(int position,const QString &mode);
    Q_INVOKABLE void selectTokenAt(int position);
    Q_INVOKABLE void editTokenAt(int position);
    Q_INVOKABLE void undo();
    Q_INVOKABLE void redo();
    Q_INVOKABLE void cut();
    Q_INVOKABLE void paste();
    Q_INVOKABLE void insert(int position,const QString &text);
    Q_INVOKABLE void remove(int start,int end);
    Q_INVOKABLE void append(const QString &text);
    Q_INVOKABLE void clear();
signals:
    void expressionChanged();
    void tokenLayoutChanged();
    void draftChanged();
protected:
    void keyPressEvent(QKeyEvent *event)override;
    void inputMethodEvent(QInputMethodEvent *event)override;
private:
    enum {ModeProperty=QTextFormat::UserProperty+1,QueryProperty};
    struct EditState {int undo,revision,start,end,cursor;bool selectedToken;};
    struct Selection {int start,end;};
    struct QtState {
        QString text,selected;
        int cursor,start,end,lines;
        QRectF rectangle;
        QSizeF content;
        bool undo,redo;
    };
    QList<FileChooserSearchTokens::Row> tokenRows()const;
    QTextDocument *editDocument()const;
    QTextCharFormat formatAt(int position)const;
    bool tokenAt(int position)const;
    QTextImageFormat tokenFormat(const QString &mode,const QString &query,const QString &identity={});
    QPair<int,int> draftRange()const;
    EditState editState()const;
    QtState qtState()const;
    bool publishQtChanges(const QtState &before);
    void finishHistory(const EditState &before,bool replay);
    void performEdit(const std::function<void()> &operation,bool replay=false);
    void performTokenEdit(const std::function<void()> &operation);
    void documentChanged();
    void markLayoutChanged();
    void markDraftChanged();
    void publishChanges();
    void reportError(const QString &message);
    FileChooserSearchTokens *m_tokens;
    QMap<int,Selection> m_selections;
    QMap<int,int> m_redoCursors;
    std::unique_ptr<FileChooserSearchHistory> m_history;
    QVariantList m_reportedExpression;
    int m_editDepth=0,m_resource=0;
    bool m_contentsDirty=false,m_tokensDirty=false,m_draftDirty=false,m_publishing=false;
};
