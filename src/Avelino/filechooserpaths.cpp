#include "filechooserpaths.h"
#include <QCollator>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <algorithm>
#include <cerrno>
#include <cstring>
#include <dirent.h>

namespace {
struct Candidate {QString path,name;bool available=true;int group=0,score=0;};
int distance(const QString &a,const QString &b){
    QList<int> previous(b.size()+1),current(b.size()+1);
    for(int j=0;j<=b.size();++j)previous[j]=j;
    for(int i=1;i<=a.size();++i){
        current[0]=i;
        for(int j=1;j<=b.size();++j)current[j]=std::min({previous[j]+1,current[j-1]+1,previous[j-1]+int(a[i-1]!=b[j-1])});
        previous.swap(current);
    }
    return previous.last();
}
bool match(Candidate &candidate,const QString &query){
    const auto name=candidate.name.toCaseFolded(),needle=query.toCaseFolded();
    if(name==needle){candidate.group=0;return true;}
    if(name.startsWith(needle)){candidate.group=1;candidate.score=name.size()-needle.size();return true;}
    int common=0;while(common<std::min(name.size(),needle.size())&&name[common]==needle[common])++common;
    if(!needle.isEmpty()&&name.contains(needle)){candidate.group=2;candidate.score=name.size()-needle.size();return true;}
    if(needle.size()>=2&&common>=std::max(2,int(needle.size()/2))){candidate.group=3;candidate.score=distance(name,needle);return true;}
    return false;
}
QVariantMap row(const Candidate &value){
    return {{"heading",false},{"label",value.name},{"path",value.path},
        {"url",QUrl::fromLocalFile(value.path)},{"available",value.available}};
}
}
void FileChooserPaths::begin(const QString &folder,const QString &input,const QVariantList &targets,const QString &storageError){
    m_folder=folder;m_recent=targets;m_storageError=storageError;m_input=input;
    rebuild();emit inputChanged();
}
void FileChooserPaths::setInput(const QString &input){if(input==m_input)return;m_input=input;rebuild();emit inputChanged();}
void FileChooserPaths::refresh(){rebuild();}
void FileChooserPaths::rebuild(){
    m_entries.clear();m_error=m_storageError;m_completion=m_input;m_index=-1;
    QList<Candidate> files,recents;
    QString directory,needle,prefix;
    auto expanded=m_input;
    if(expanded=="~"||expanded.startsWith("~/"))expanded=QDir::homePath()+expanded.mid(1);
    const bool absolute=QDir::isAbsolutePath(expanded);
    if(absolute){
        const auto slash=expanded.lastIndexOf('/');directory=expanded.left(slash+1);needle=expanded.mid(slash+1);prefix=m_input.left(m_input.lastIndexOf('/')+1);
    }else if(!m_input.isEmpty()&&!m_input.contains('/')){
        directory=m_folder;needle=m_input;
    }else if(m_input=="../"||m_input=="./"){
        // These measured current-location proposals are not POSIX cd semantics.
        // General native relative-component resolution remains unproven.
        directory=m_folder;
    }
    if(!directory.isEmpty()&&QDir::isAbsolutePath(directory)){
        const auto path=QFile::encodeName(directory);DIR *handle=opendir(path.constData());
        if(handle){
            if(needle.isEmpty())files.append({QDir::cleanPath(directory),QFileInfo(QDir::cleanPath(directory)).fileName(),true,-1});
            while(auto entry=readdir(handle)){
                const auto name=QFile::decodeName(entry->d_name);
                if(name=="."||name==".."||(name.startsWith('.')&&!needle.startsWith('.')))continue;
                QFileInfo info(QDir(directory).filePath(name));
                if(needle.isEmpty()&&!info.isDir())continue;
                Candidate candidate{info.absoluteFilePath(),name,info.exists()};
                if(!needle.isEmpty()&&!match(candidate,needle))continue;
                files.append(candidate);
            }
            closedir(handle);
        }else if(QFileInfo(directory).isDir())m_error=QString::fromLocal8Bit(std::strerror(errno));
    }
    QCollator collator;collator.setCaseSensitivity(Qt::CaseInsensitive);collator.setNumericMode(true);
    std::stable_sort(files.begin(),files.end(),[&](const Candidate &a,const Candidate &b){
        if(a.group!=b.group)return a.group<b.group;
        if(a.score!=b.score)return a.score<b.score;
        const auto order=collator.compare(a.name,b.name);return order?order<0:a.path<b.path;
    });
    for(const auto &value:m_recent){
        const auto target=value.toMap();const auto path=target["path"].toString();
        if(path.isEmpty())continue;
        Candidate candidate{path,QFileInfo(path).fileName(),QFileInfo::exists(path)};
        if(!m_input.isEmpty()&&!match(candidate,m_input))continue;
        if(std::any_of(files.begin(),files.end(),[&](const Candidate &file){return file.path==path;}))continue;
        recents.append(candidate);
    }
    auto group=[&](const QString &title,const QList<Candidate> &values){
        if(values.isEmpty())return;
        m_entries.append(QVariantMap{{"heading",true},{"label",title},{"available",false}});
        for(const auto &value:values)m_entries.append(row(value));
    };
    group(absolute?QStringLiteral("Go to:"):QStringLiteral("Go to folder in current location"),files);
    group(QStringLiteral("Recents"),recents);
    if(!m_input.isEmpty())for(int i=0;i<m_entries.size();++i)if(m_entries[i].toMap()["available"].toBool()){m_index=i;break;}
    if(!files.isEmpty()&&!needle.isEmpty()){
        auto common=files.first().name;
        for(const auto &file:files){int length=0;while(length<std::min(common.size(),file.name.size())&&common[length].toCaseFolded()==file.name[length].toCaseFolded())++length;common.truncate(length);}
        if(common.size()>needle.size())m_completion=prefix+common;
        else if(files.size()==1&&files.first().name.compare(needle,Qt::CaseInsensitive)==0)
            m_completion=prefix+files.first().name+(QFileInfo(files.first().path).isDir()?QStringLiteral("/"):QString());
    }
    emit entriesChanged();emit currentIndexChanged();
}
QUrl FileChooserPaths::selectedUrl()const{
    if(m_index<0||m_index>=m_entries.size())return {};
    const auto entry=m_entries[m_index].toMap();return entry["available"].toBool()?entry["url"].toUrl():QUrl();
}
void FileChooserPaths::select(int index){
    if(index<0||index>=m_entries.size()||!m_entries[index].toMap()["available"].toBool()||index==m_index)return;
    m_index=index;emit currentIndexChanged();
}
void FileChooserPaths::move(int offset){
    if(!offset)return;const auto step=offset>0?1:-1;
    int index=m_index<0?(step>0?0:m_entries.size()-1):m_index+step;
    for(;index>=0&&index<m_entries.size();index+=step)if(m_entries[index].toMap()["available"].toBool()){select(index);return;}
}
QString FileChooserPaths::completion()const{return m_completion;}
