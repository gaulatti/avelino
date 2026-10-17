from pathlib import Path
import hashlib,json,shutil,subprocess,time
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';Q=B/'media-library-reflow-build-v5';P=B/'media-library-caption-offset-build-v1';assert not P.exists();P.mkdir()
shutil.copytree(Q/'source',P/'source');shutil.copytree(B/'media-library-caption-trace-build-v1/build',P/'build',ignore=shutil.ignore_patterns('Testing'));(P/'qt-artifacts').mkdir()
(P/'source/samples/AvelinoCatalog/ReferenceCaseFixture.qml').write_text('''import QtQuick
import Avelino
Window {
    visible:true;width:1120;height:820;color:BleeckerTheme.palette.background
    title:"Avelino diagnostic fresh caller offset"
    readonly property real fixtureTextScale:BleeckerTheme.textScale
    Component.onCompleted:{BleeckerTheme.dark=captureDark;BleeckerTheme.textScale=captureTextScale;BleeckerTheme.reducedMotion=true}
    MediaLibraryCase {
        objectName:"referenceCaseComponent";x:24;y:200
        definition:Object.assign({},captureDefinition,{width:captureDefinition.libraryWidth,height:captureDefinition.libraryHeight})
    }
}
''')
(P/'inputs.json').write_text(json.dumps(dict(baseRevision='1691bbff68b2cd6ac063f09f23aeb5afc0635b4d',scope='Fresh caller placed at the gallery scene offset; no retained updates and no tracing timer',sourceFiles={str(p.relative_to(P/'source')):hashlib.sha256(p.read_bytes()).hexdigest()for p in(P/'source').rglob('*')if p.is_file()}),indent=2)+'\n')
command=['docker','--context','colima-avelino-verify','run','--rm','--init','--name','avelino-media-caption-offset-build-v1','-v',str(P/'source')+':/work:ro','-v',str(P)+':/result:rw','-v',str(P/'qt-artifacts')+':/work/artifacts:rw','-w','/work','avelino-toolchain:data-metrics-qt6.8.3','bash','-lc','cmake -S /work -B /result/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DCMAKE_PREFIX_PATH=/opt/qt && cmake --build /result/build --target AvelinoCatalog --parallel 2 && cmake --install /result/build --prefix /result/install'];start=time.monotonic()
with(P/'run.log').open('w')as log:p=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(P/'result.json').write_text(json.dumps(dict(exitCode=p.returncode,command=command,seconds=time.monotonic()-start),indent=2)+'\n');print('Fresh scene-offset build',p.returncode);print((P/'run.log').read_text()[-700:]);raise SystemExit(p.returncode)
