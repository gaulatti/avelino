#pragma once
#include <QColor>
#include <QFont>
#include <QPointer>
#include <QQuickItem>
#include <QUrl>
#include <QtQml/qqmlregistration.h>

class DropdownLabel : public QQuickItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QObject* root READ root WRITE setRoot NOTIFY rootChanged)
    Q_PROPERTY(QFont defaultFont READ defaultFont WRITE setDefaultFont NOTIFY defaultFontChanged)
    Q_PROPERTY(QString text READ text NOTIFY metadataChanged)
    Q_PROPERTY(bool hasText READ hasText NOTIFY metadataChanged)
    Q_PROPERTY(QFont textFont READ textFont NOTIFY metadataChanged)
    Q_PROPERTY(QColor textColor READ textColor NOTIFY metadataChanged)
    Q_PROPERTY(int textFormat READ textFormat NOTIFY metadataChanged)
    Q_PROPERTY(QUrl imageSource READ imageSource NOTIFY metadataChanged)
    Q_PROPERTY(qreal imageWidth READ imageWidth NOTIFY metadataChanged)
    Q_PROPERTY(qreal imageHeight READ imageHeight NOTIFY metadataChanged)
public:
    using QQuickItem::QQuickItem;
    QObject *root() const{return m_root;}
    QFont defaultFont() const{return m_defaultFont;}
    QString text() const{return m_text;}
    bool hasText() const{return m_hasText;}
    QFont textFont() const{return m_font;}
    QColor textColor() const{return m_color;}
    int textFormat() const{return m_format;}
    QUrl imageSource() const{return m_image;}
    qreal imageWidth() const{return m_imageWidth;}
    qreal imageHeight() const{return m_imageHeight;}
    void setRoot(QObject *value);
    void setDefaultFont(const QFont &value);
    Q_INVOKABLE void refresh();
    Q_INVOKABLE QFont systemFont(int pixelSize) const;
    Q_INVOKABLE int controlFontSize(const QString &size) const;
public slots:
    void scheduleRefresh(){polish();}
signals:
    void rootChanged();
    void defaultFontChanged();
    void metadataChanged();
protected:
    void updatePolish() override{refresh();}
private:
    void observe(QQuickItem *item);
    void visit(QQuickItem *item);
    QPointer<QQuickItem> m_root;
    QFont m_defaultFont,m_font;
    QString m_text;
    QColor m_color=Qt::black;
    QUrl m_image;
    qreal m_imageWidth=0,m_imageHeight=0;
    int m_format=0;
    bool m_hasText=false;
    QList<QMetaObject::Connection> m_connections;
};
