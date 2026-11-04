#pragma once
#include <QObject>
#include <QPointer>
#include <QScopedPointer>
#include <QVariant>

// Independent caller callbacks use only Qt's public object/property interfaces.
class ConsumerPathInputObserver:public QObject {
    Q_OBJECT
public:
    QScopedPointer<QObject> ownedInput;
    QPointer<QObject> target;
    QByteArray property;
    QVariant value;
    QString lastText;
    int calls=0;
public slots:
    void apply(){
        QObject::disconnect(target,nullptr,this,nullptr);
        ++calls;lastText=target->property("text").toString();
        if(ownedInput)ownedInput.reset();else target->setProperty(property.constData(),value);
    }
};
