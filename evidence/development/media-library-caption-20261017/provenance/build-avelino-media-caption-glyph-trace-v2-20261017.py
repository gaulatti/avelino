from pathlib import Path
import hashlib,json,shutil,subprocess,time
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';Q=B/'media-library-caption-trace-build-v1';P=B/'media-library-caption-glyph-trace-build-v2';assert not P.exists();P.mkdir()
shutil.copytree(Q/'source',P/'source');shutil.copytree(B/'media-library-caption-glyph-trace-build-v1/build',P/'build',ignore=shutil.ignore_patterns('Testing'));(P/'qt-artifacts').mkdir()
(P/'source/tests/consumer/captionlayoutprobe.h').write_text(r'''#pragma once
#include <QObject>
#include <QVariantMap>
#include <QCryptographicHash>
#include <QTextLayout>
#include <QQuickItem>
#include <QtQuick/private/qquicktext_p_p.h>
#include <QtQml/qqmlregistration.h>
class CaptionLayoutProbe : public QObject {
    Q_OBJECT
    QML_ELEMENT
    QML_SINGLETON
public:
    using QObject::QObject;
    static QVariantMap font(const QFont &font){return {{"key",font.key()},{"family",font.family()},{"style",font.styleName()},{"points",font.pointSizeF()},{"pixels",font.pixelSize()},{"hinting",font.hintingPreference()},{"strategy",int(font.styleStrategy())}};}
    static QVariantMap layout(QTextLayout &layout){
        QVariantList lines,runs;
        for(int i=0;i<layout.lineCount();++i){auto line=layout.lineAt(i);lines.append(QVariantMap{{"position",QVariantList{line.x(),line.y()}},{"width",line.width()},{"naturalWidth",line.naturalTextWidth()},{"advance",line.horizontalAdvance()},{"height",line.height()},{"ascent",line.ascent()},{"descent",line.descent()},{"start",line.textStart()},{"length",line.textLength()}});}
        for(const auto &run:layout.glyphRuns()){
            QVariantList indexes,positions;for(auto index:run.glyphIndexes())indexes.append(index);for(auto point:run.positions())positions.append(QVariantList{point.x(),point.y()});
            const auto raw=run.rawFont();
            runs.append(QVariantMap{{"indexes",indexes},{"positions",positions},{"flags",int(run.flags())},{"family",raw.familyName()},{"style",raw.styleName()},{"pixels",raw.pixelSize()},{"hinting",raw.hintingPreference()},{"headSha256",QString::fromLatin1(QCryptographicHash::hash(raw.fontTable("head"),QCryptographicHash::Sha256).toHex())}});
        }
        const auto option=layout.textOption();
        return {{"text",layout.text()},{"font",font(layout.font())},{"lines",lines},{"runs",runs},{"designMetrics",option.useDesignMetrics()},{"alignment",int(option.alignment())},{"wrap",option.wrapMode()},{"direction",option.textDirection()},{"flags",int(option.flags())}};
    }
    Q_INVOKABLE QVariantMap snapshot(QQuickItem *item){
        auto text=qobject_cast<QQuickText*>(item);if(!text)return {};
        auto d=QQuickTextPrivate::get(text);
        QVariantMap result{{"layout",layout(d->layout)},{"font",font(d->font)},{"sourceFont",font(d->sourceFont)},{"lineWidth",d->lineWidth},{"elideMode",d->elideMode},{"updateType",d->updateType},{"truncated",bool(d->truncated)},{"textHasChanged",bool(d->textHasChanged)},{"needToUpdateLayout",bool(d->needToUpdateLayout)},{"polishSize",bool(d->polishSize)},{"layoutTextElided",bool(d->layoutTextElided)}};
        if(d->elideLayout)result.insert("elided",layout(*d->elideLayout));return result;
    }
};
''')
p=P/'source/tests/consumer/MediaLibraryTile.qml';s=p.read_text().replace('offeredCaption:caption.offeredWidth,','layout:CaptionLayoutProbe.snapshot(renderer),offeredCaption:caption.offeredWidth,');p.write_text(s)
p=P/'source/samples/AvelinoCatalog/CMakeLists.txt';s=p.read_text().replace('${PROJECT_SOURCE_DIR}/tests/consumer/mediatilefill.h','${PROJECT_SOURCE_DIR}/tests/consumer/mediatilefill.h ${PROJECT_SOURCE_DIR}/tests/consumer/captionlayoutprobe.h');s+='\ntarget_link_libraries(AvelinoCatalog PRIVATE Qt6::QuickPrivate)\n';p.write_text(s)
(P/'inputs.json').write_text(json.dumps(dict(baseRevision='1691bbff68b2cd6ac063f09f23aeb5afc0635b4d',scope='Isolated Qt 6.8.3 private text layout snapshots. No product changes.',sourceFiles={str(p.relative_to(P/'source')):hashlib.sha256(p.read_bytes()).hexdigest()for p in(P/'source').rglob('*')if p.is_file()}),indent=2)+'\n')
command=['docker','--context','colima-avelino-verify','run','--rm','--init','--name','avelino-media-caption-glyph-trace-build-v2','-v',str(P/'source')+':/work:ro','-v',str(P)+':/result:rw','-v',str(P/'qt-artifacts')+':/work/artifacts:rw','-w','/work','avelino-toolchain:data-metrics-qt6.8.3','bash','-lc','cmake -S /work -B /result/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DCMAKE_PREFIX_PATH=/opt/qt && cmake --build /result/build --target AvelinoCatalog --parallel 2 && cmake --install /result/build --prefix /result/install'];start=time.monotonic()
with(P/'run.log').open('w')as log:p=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(P/'result.json').write_text(json.dumps(dict(exitCode=p.returncode,command=command,seconds=time.monotonic()-start),indent=2)+'\n');print('Glyph trace build',p.returncode);print((P/'run.log').read_text()[-1400:]);raise SystemExit(p.returncode)
