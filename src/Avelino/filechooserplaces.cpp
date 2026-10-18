#include "filechooserplaces.h"
#include <QDir>
#include <QFileInfo>
#include <QLockFile>
#include <QSettings>
#include <QSet>
#include <QStorageInfo>
#include <QUrl>

namespace {
constexpr int recentLimit=10;
struct SavedPlaces {QStringList folders;QString input;bool hasInput=false;};
void configure(QSettings &settings){settings.setFallbacksEnabled(false);settings.sync();}
QString settingsError(QSettings &settings){
    return settings.status()==QSettings::NoError?QString():QStringLiteral("Recent places could not be read.");
}
QString localPath(const QUrl &url){
    if(!url.isValid()||!url.isLocalFile()||url.hasQuery()||url.hasFragment()||!QDir::isAbsolutePath(url.toLocalFile()))return {};
    return QDir::cleanPath(url.toLocalFile());
}
QString load(QSettings &settings,SavedPlaces &saved){
    if(const auto error=settingsError(settings);!error.isEmpty())return error;
    if(settings.contains("version")){
        bool valid=false;const auto version=settings.value("version").toInt(&valid);
        if(!valid||version!=1)return QStringLiteral("Saved recent places have an unsupported format.");
    }
    const auto value=settings.value("recentFolders");
    if(value.isValid()){
        if(value.metaType().id()!=QMetaType::QStringList&&value.metaType().id()!=QMetaType::QString)
            return QStringLiteral("Saved recent places are invalid.");
        saved.folders=value.toStringList();
        if(saved.folders.size()>recentLimit)return QStringLiteral("Saved recent places are invalid.");
        QSet<QString> seen;
        for(auto &folder:saved.folders){
            const auto path=localPath(QUrl(folder));
            if(path.isEmpty()||seen.contains(path))return QStringLiteral("Saved recent places are invalid.");
            seen.insert(path);folder=QUrl::fromLocalFile(path).toString(QUrl::FullyEncoded);
        }
    }
    saved.hasInput=settings.contains("lastPathInput");
    if(saved.hasInput){
        const auto input=settings.value("lastPathInput");
        if(input.metaType().id()!=QMetaType::QString)return QStringLiteral("The saved folder input is invalid.");
        saved.input=input.toString();
    }
    return {};
}
QString label(const QString &path){
    return path==QDir::rootPath()?QStorageInfo(path).displayName():QFileInfo(path).fileName();
}
QVariantMap entry(const QString &path,bool recent){
    return {{"label",label(path)},{"url",QUrl::fromLocalFile(path)},{"path",path},
            {"available",QFileInfo(path).isDir()},{"recent",recent},{"heading",false}};
}
}
void FileChooserPlaces::refresh(const QString &currentFolder){
    m_currentFolder=currentFolder;
    QSettings settings(QSettings::NativeFormat,QSettings::UserScope,"Avelino","FileChooser");configure(settings);
    SavedPlaces saved;m_readError=load(settings,saved);m_hasPathInput=m_readError.isEmpty()&&saved.hasInput;
    m_lastPathInput=m_hasPathInput?saved.input:QString();m_entries.clear();
    if(QDir::isAbsolutePath(currentFolder)){
        auto path=QDir::cleanPath(currentFolder);
        for(;;){
            m_entries.append(entry(path,false));QDir parent(path);
            if(!parent.cdUp()||parent.absolutePath()==path)break;path=parent.absolutePath();
        }
    }
    if(!saved.folders.isEmpty()||!error().isEmpty()){
        m_entries.append(QVariantMap{{"label","Recent Places"},{"available",false},{"heading",true},{"recent",true}});
        if(m_readError.isEmpty())for(const auto &folder:saved.folders)m_entries.append(entry(localPath(QUrl(folder)),true));
        if(!error().isEmpty())m_entries.append(QVariantMap{{"label",error()},{"available",false},{"heading",true},{"recent",true}});
    }
    emit changed();
}
bool FileChooserPlaces::save(const QString *folder,const QString *input){
    QSettings settings(QSettings::NativeFormat,QSettings::UserScope,"Avelino","FileChooser");
    settings.setFallbacksEnabled(false);
    const QFileInfo location(settings.fileName());
    if(!QDir().mkpath(location.absolutePath())){
        m_writeError="Recent places could not be saved.";refresh(m_currentFolder);return false;
    }
    // QSettings has its own atomic-write lock. This different lock serializes
    // the complete read/promote/write operation across consumer processes.
    QLockFile lock(settings.fileName()+".recent.lock");
    if(!lock.tryLock(250)){
        m_writeError="Recent places are being updated by another application.";refresh(m_currentFolder);return false;
    }
    configure(settings);SavedPlaces saved;const auto error=load(settings,saved);
    if(!error.isEmpty()){m_readError=error;lock.unlock();refresh(m_currentFolder);return false;}
    if(folder){
        const auto encoded=QUrl::fromLocalFile(*folder).toString(QUrl::FullyEncoded);
        saved.folders.removeAll(encoded);saved.folders.prepend(encoded);
        if(saved.folders.size()>recentLimit)saved.folders.resize(recentLimit);
        settings.setValue("recentFolders",saved.folders);
    }
    if(input)settings.setValue("lastPathInput",*input);
    settings.setValue("version",1);settings.sync();
    const bool success=settings.status()==QSettings::NoError;
    m_writeError=success?QString():QStringLiteral("Recent places could not be saved.");
    lock.unlock();refresh(m_currentFolder);return success;
}
bool FileChooserPlaces::rememberAcceptedFolder(const QString &folder){
    const QFileInfo info(folder);const auto path=info.canonicalFilePath();
    if(!info.isDir()||path.isEmpty()){
        m_writeError="The accepted folder is no longer available.";refresh(m_currentFolder);return false;
    }
    return save(&path,nullptr);
}
bool FileChooserPlaces::rememberPathInput(const QString &input){return save(nullptr,&input);}
