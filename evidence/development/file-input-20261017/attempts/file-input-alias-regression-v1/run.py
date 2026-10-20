from pathlib import Path
import hashlib,json,shutil,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];source=p/'source';source.mkdir();prior=p.parent/'file-input-qt-v3/source';current=p.parent/'file-input-qt-v4/source'
for name in ['filechoosermodel.h','filechoosermodel.cpp']:shutil.copy2(prior/'src/Avelino'/name,source/name)
shutil.copy2(current/'tests/components/filechoosermodel.cpp',source/'tests.cpp')
(source/'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.24)
project(FileInputAliasRegression LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
find_package(Qt6 6.8.3 EXACT REQUIRED COMPONENTS Qml Test)
qt_standard_project_setup(REQUIRES 6.8)
qt_add_executable(Regression tests.cpp filechoosermodel.h filechoosermodel.cpp)
target_link_libraries(Regression PRIVATE Qt6::Qml Qt6::Test)
target_include_directories(Regression PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
''')
# The copied unit source includes the original basename's moc output.
(source/'tests.cpp').rename(source/'filechoosertests.cpp');s=(source/'filechoosertests.cpp').read_text().replace('#include "filechoosermodel.moc"','#include "filechoosertests.moc"');(source/'filechoosertests.cpp').write_text(s);c=source/'CMakeLists.txt';c.write_text(c.read_text().replace('Regression tests.cpp','Regression filechoosertests.cpp'))
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'inputs.json').write_text(json.dumps(dict(accepted=False,priorModel=str(prior),currentTests=str(current),files={f.name:sha(f)for f in source.iterdir()}),indent=2)+'\n');base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(r)+':/work','-w','/work/'+str(source.relative_to(r)),'avelino-toolchain:data-metrics-qt6.8.3'];steps=[]
for name,cmd in [('configure',['cmake','-S','.','-B','../build','-G','Ninja','-DCMAKE_BUILD_TYPE=Debug']),('build',['cmake','--build','../build','--parallel','2']),('regression',['../build/Regression'])]:
 start=time.monotonic()
 with(p/(name+'.log')).open('w')as log:result=subprocess.run(base+cmd,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=base+cmd,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,result.returncode,flush=True)
 if result.returncode and name!='regression':raise SystemExit(result.returncode)
 if name=='regression':
  text=(p/'regression.log').read_text();assert result.returncode!=0 and ('Broken filename'in text or 'Compared values are not the same'in text);(p/'result.json').write_text(json.dumps(dict(accepted=False,status='old model rejected by new navigation regression',exitCode=result.returncode),indent=2)+'\n')
