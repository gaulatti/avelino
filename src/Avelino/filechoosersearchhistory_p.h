#pragma once
#include <QList>
#include <QMap>
#include <QPointer>
#include <QTextCursor>
#include <QTextDocument>
#include <QTextDocumentFragment>
#include <algorithm>
#include <optional>
#include <utility>

// Keep Qt's earlier commands. After a token materializes between raw runs,
// native Undo retains the query as text; Redo must restore the span actually
// removed by each earlier command, rather than that command's old payload.
class FileChooserSearchHistory {
public:
    struct Cursor {int start=0,end=0,position=0;};
    struct Delta {
        bool seen=false;
        int position=0,removed=0,added=0;
        void record(int at,int oldLength,int newLength){
            if(!seen){seen=true;position=at;removed=oldLength;added=newLength;return;}
            const int shift=added-removed;
            const int oldStart=at<=position?at:at>=position+added?at-shift:position;
            const int end=at+oldLength;
            const int oldEnd=end<=position?end:end>=position+added?end-shift:position+removed;
            const int start=std::min(position,oldStart),finish=std::max(position+removed,oldEnd);
            removed=finish-start;added=removed+shift+newLength-oldLength;position=start;
        }
    };
    struct Entry {
        Delta delta;
        QTextDocumentFragment before,after;
        Cursor undoCursor;
        std::optional<Cursor> redoCursor;
    };
    explicit FileChooserSearchHistory(QTextDocument *document):m_document(document){}
    bool active()const{return m_active;}
    bool hasRecordedRedo()const{return !m_pending.isEmpty();}
    const Entry &nextRedo()const{return m_pending.first();}
    std::optional<Entry> applied(int depth)const{
        auto found=m_applied.constFind(depth);
        return found==m_applied.cend()?std::nullopt:std::optional<Entry>{found.value()};
    }
    void reset(){m_active=false;m_pending.clear();m_applied.clear();}
    void newEdit(int depth){m_pending.clear();trimApplied(depth);}
    static QTextDocumentFragment fragment(QTextDocument *document,int position,int length){
        QTextCursor cursor(document);cursor.setPosition(position);
        cursor.setPosition(position+length,QTextCursor::KeepAnchor);return QTextDocumentFragment(cursor);
    }
    QTextDocumentFragment whole()const{return fragment(m_document,0,m_document->characterCount()-1);}
    void expandBetweenRawRuns(int position,const QString &query){
        m_active=true;m_document->appendUndoItem(new Expansion(m_document,position,query));
        // Execute the first change inside Qt's own command replay. The initial
        // Undo is a no-op; no private undo flag or earlier history is changed.
        m_document->undo();m_document->redo();
    }
    void recordUndo(const QTextDocumentFragment &before,const Delta &delta,
                    Cursor undoCursor,std::optional<Cursor> redoCursor,int depth){
        QTextDocument previous;QTextCursor cursor(&previous);cursor.insertFragment(before);
        Entry entry{delta,fragment(&previous,delta.position,delta.removed),
            fragment(m_document,delta.position,delta.added),undoCursor,redoCursor};
        m_pending.prepend(entry);trimApplied(depth);
        // Every pending command is retained as an exact rich inverse span.
        // Rebuild only Redo; the earlier Qt Undo commands remain untouched.
        m_document->clearUndoRedoStacks(QTextDocument::RedoStack);
        for(const auto &value:m_pending)m_document->appendUndoItem(new Replay(m_document,value));
        for(qsizetype index=0;index<m_pending.size();++index)m_document->undo();
    }
    void recordedRedoCompleted(int depth){m_applied.insert(depth,m_pending.takeFirst());}
private:
    class Expansion final:public QAbstractUndoItem {
        QPointer<QTextDocument> document;
        int position;
        QString query;
        bool bootstrap=true,firstRedo=true;
        void replace(int length,const QString &text){
            if(!document)return;QTextCursor cursor(document);cursor.setPosition(position);
            cursor.setPosition(position+length,QTextCursor::KeepAnchor);cursor.insertText(text,QTextCharFormat());
        }
    public:
        Expansion(QTextDocument *document,int position,QString query):document(document),position(position),query(std::move(query)){}
        void undo()override{if(bootstrap){bootstrap=false;return;}replace(query.size()+2,query);}
        void redo()override{replace(firstRedo?1:query.size(),QStringLiteral(" ")+query+QStringLiteral(" "));firstRedo=false;}
    };
    class Replay final:public QAbstractUndoItem {
        QPointer<QTextDocument> document;
        Entry state;
        bool bootstrap=true;
        void replace(int length,const QTextDocumentFragment &value){
            if(!document)return;QTextCursor cursor(document);cursor.setPosition(state.delta.position);
            cursor.setPosition(state.delta.position+length,QTextCursor::KeepAnchor);
            cursor.removeSelectedText();if(document)cursor.insertFragment(value);
        }
    public:
        Replay(QTextDocument *document,Entry state):document(document),state(std::move(state)){}
        void undo()override{if(bootstrap){bootstrap=false;return;}replace(state.delta.removed,state.after);}
        void redo()override{replace(state.delta.added,state.before);}
    };
    void trimApplied(int depth){auto later=m_applied.upperBound(depth);while(later!=m_applied.end())later=m_applied.erase(later);}
    QPointer<QTextDocument> m_document;
    QList<Entry> m_pending;
    QMap<int,Entry> m_applied;
    bool m_active=false;
};
