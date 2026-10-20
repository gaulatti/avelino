#include "inheritedcontrol.h"
#include "radiogroupbase.h"
#include "proposalrow.h"
#include "proposalcolumn.h"
#include "proposaloverlay.h"
#include "apptabrow.h"
#include "chartrenderer.h"
#include "spotlightrows.h"
#include "medialibrarybase.h"
#include "softwarecontentmask.h"
#include <QGuiApplication>
#include <QQuickWindow>
#include <QQmlEngine>
#include <QQmlComponent>
#include <cstdlib>
int main(int argc,char **argv){
 QGuiApplication app(argc,argv);QQmlEngine engine;
 engine.addImportPath("/work/artifacts/resumed-avelino-20261016/file-input-build/build/qml");
 QQmlComponent import(&engine);import.setData("import QtQuick; import Avelino; Item {}",QUrl());
 auto root=import.create();if(!root)return 90;
 QQuickWindow window;QQuickControl parent(window.contentItem());
 const QString name=argc>1?QString::fromUtf8(argv[1]):QStringLiteral("inherited");
 const int mode=argc>2?std::atoi(argv[2]):0;
 if(mode&1)parent.setEnabled(false);
 auto font=parent.font();font.setPointSizeF(28);parent.setFont(font);
 QQuickItem *control=nullptr;
 if(name=="inherited")control=new InheritedControl(&parent);
 else if(name=="radio")control=new RadioGroupBase(&parent);
 else if(name=="row")control=new ProposalRow(&parent);
 else if(name=="column")control=new ProposalColumn(&parent);
 else if(name=="overlay")control=new ProposalOverlay(&parent);
 else if(name=="tabs")control=new AppTabRow(&parent);
 else if(name=="charts")control=new ChartRenderer(&parent);
 else if(name=="spotlight")control=new SpotlightRows(&parent);
 else if(name=="media")control=new MediaLibraryBase(&parent);
 else if(name=="mask")control=new SoftwareContentMask(&parent);
 else return 91;
 if(mode&2)new QQuickItem(control);
 delete control;delete root;return 0;
}
