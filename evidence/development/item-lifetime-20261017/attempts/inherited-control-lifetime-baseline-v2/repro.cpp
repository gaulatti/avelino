#include "inheritedcontrol.h"
#include <QGuiApplication>
#include <QQuickWindow>
#include <cstdlib>
int main(int argc,char **argv){
 QGuiApplication app(argc,argv);QQuickWindow window;
 const int mode=argc>1?std::atoi(argv[1]):0;
 auto parent=new InheritedControl(window.contentItem());
 if(mode&1)parent->setEnabled(false);
 if(mode&2){auto font=parent->font();font.setPointSizeF(28);parent->setFont(font);}
 auto control=new InheritedControl(parent);
 delete control;delete parent;return 0;
}
