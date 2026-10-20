#include <QApplication>
#include <QWidget>
#include <QDialog>
#include <QToolTip>
#include <QTimer>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
int main(int argc,char **argv){
    QApplication app(argc,argv);QWidget window;
    const bool tooltip=app.arguments().contains("--tooltip");
    window.setWindowTitle(tooltip?"Stock Qt tooltip owner":"Stock Qt second client");
    window.resize(500,400);window.show();
    QDialog dialog(&window);dialog.setWindowTitle("Stock Qt modal dialog");dialog.resize(400,300);dialog.setWindowModality(Qt::ApplicationModal);if(tooltip)dialog.show();
    if(tooltip){
        QTimer::singleShot(500,&app,[&]{QToolTip::showText(dialog.mapToGlobal(QPoint(50,50)),"Stock Qt tooltip",&dialog,QRect(),60000);});
        QTimer::singleShot(1000,&app,[]{QFile out("/probe/stock-tooltip-ready.json");out.open(QIODevice::WriteOnly);out.write(QJsonDocument(QJsonObject{{"stockQtTooltipVisible",QToolTip::isVisible()}}).toJson());});
    }
    return app.exec();
}
