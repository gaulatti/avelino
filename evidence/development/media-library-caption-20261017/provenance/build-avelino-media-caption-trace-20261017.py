from pathlib import Path
import hashlib,json,shutil,subprocess,time
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';Q=B/'media-library-reflow-build-v5';P=B/'media-library-caption-trace-build-v1';assert not P.exists();P.mkdir()
shutil.copytree(Q/'source',P/'source');shutil.copytree(Q/'build',P/'build',ignore=shutil.ignore_patterns('Testing'));(P/'qt-artifacts').mkdir()
p=P/'source/tests/consumer/MediaLibraryTile.qml';s=p.read_text();s=s.replace('    FontMetrics {id:captionMetrics;', '''    Timer {
        interval:100;repeat:true;running:tile.kind==="button" &&tile.tileActive
        property string previous:""
        function geometry(item) {
            if(!item)return null
            const point=item.mapToItem(null,0,0)
            return {x:item.x,y:item.y,width:item.width,height:item.height,implicitWidth:item.implicitWidth,implicitHeight:item.implicitHeight,scene:[point.x,point.y]}
        }
        onTriggered:{
            const renderer=caption.textRenderer
            if(!renderer)return
            const transform=renderer.transform.length ? renderer.transform[0]:null
            const value={id:tile.tileData.id,title:tile.tileData.title,definition:tile.fixture.definition.id,
                offered:tile.fixture.definition.width,minimum:tile.fixture.definition.minimumTileWidth,rtl:tile.fixture.definition.rtl,
                dark:BleeckerTheme.dark,textScale:BleeckerTheme.textScale,disabled:tile.fixture.definition.disabled,scroll:tile.fixture.definition.scroll,
                tile:geometry(tile),caption:geometry(caption),renderer:geometry(renderer),
                offeredCaption:caption.offeredWidth,naturalCaption:caption.naturalWidth,measuredCaption:caption.measuredWidth,
                measuredBaseline:caption.measuredBaseline,maximumLineCount:caption.maximumLineCount,
                horizontalAlignment:caption.horizontalAlignment,mirrored:caption.mirrored,
                contentWidth:renderer.contentWidth,contentHeight:renderer.contentHeight,lineCount:renderer.lineCount,
                rendererAlignment:renderer.horizontalAlignment,effectiveAlignment:renderer.effectiveHorizontalAlignment,
                rendererFamily:renderer.font.family,rendererPoints:renderer.font.pointSize,rendererPixels:renderer.font.pixelSize,
                rendererWeight:renderer.font.weight,renderType:renderer.renderType,
                translation:transform ? [transform.x,transform.y]:null}
            const encoded=JSON.stringify(value)
            if(encoded!==previous){previous=encoded;console.log("MEDIA_CAPTION_TRACE "+encoded)}
        }
    }
    FontMetrics {id:captionMetrics;''');p.write_text(s)
inputs={str(p.relative_to(P/'source')):hashlib.sha256(p.read_bytes()).hexdigest()for p in(P/'source').rglob('*')if p.is_file()};(P/'inputs.json').write_text(json.dumps(dict(scope='Isolated diagnostic timer only; canonical producer source copied unchanged otherwise',baseRevision='1691bbff68b2cd6ac063f09f23aeb5afc0635b4d',sourceFiles=inputs),indent=2)+'\n')
command=['docker','--context','colima-avelino-verify','run','--rm','--init','--name','avelino-media-caption-trace-build-v1','-v',str(P/'source')+':/work:ro','-v',str(P)+':/result:rw','-v',str(P/'qt-artifacts')+':/work/artifacts:rw','-w','/work','avelino-toolchain:data-metrics-qt6.8.3','bash','-lc','cmake -S /work -B /result/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DCMAKE_PREFIX_PATH=/opt/qt && cmake --build /result/build --target AvelinoCatalog --parallel 2 && cmake --install /result/build --prefix /result/install']
start=time.monotonic()
with(P/'run.log').open('w')as log:p=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(P/'result.json').write_text(json.dumps(dict(command=command,exitCode=p.returncode,seconds=time.monotonic()-start),indent=2)+'\n');print('Caption trace build',p.returncode);print((P/'run.log').read_text()[-1500:]);raise SystemExit(p.returncode)
