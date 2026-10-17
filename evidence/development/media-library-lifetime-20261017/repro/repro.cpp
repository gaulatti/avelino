#include "medialibrarybase.h"
#include <QGuiApplication>
#include <QQuickWindow>
int main(int argc,char **argv){QGuiApplication app(argc,argv);QQuickWindow window;auto library=new MediaLibraryBase(window.contentItem());delete library;return 0;}
