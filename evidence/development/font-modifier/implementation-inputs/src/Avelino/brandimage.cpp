#include "brandimage.h"
#include <QPainter>
#include <algorithm>
#include <cmath>

BrandImage::BrandImage(QQuickItem *parent):QQuickPaintedItem(parent),
    m_source(QStringLiteral(":/qt/qml/Avelino/brand/BleeckerLogo.png")) {
    if(m_source.isNull())qFatal("Pinned Bleecker logo resource is missing");
    m_source=m_source.convertToFormat(QImage::Format_ARGB32);
    setAntialiasing(true);
}
void BrandImage::setColor(QColor value) {
    if(m_color==value)return;m_color=value;m_tinted=QImage();update();emit colorChanged();
}
void BrandImage::paint(QPainter *painter) {
    if(width()<=0||height()<=0)return;
    if(m_tinted.isNull()) {
        m_tinted=QImage(m_source.size(),QImage::Format_ARGB32_Premultiplied);
        for(int y=0;y<m_source.height();++y) {
            const auto source=reinterpret_cast<const QRgb*>(m_source.constScanLine(y));
            auto output=reinterpret_cast<QRgb*>(m_tinted.scanLine(y));
            for(int x=0;x<m_source.width();++x)
                output[x]=qPremultiply(qRgba(m_color.red(),m_color.green(),m_color.blue(),qRound(qAlpha(source[x])*m_color.alphaF())));
        }
    }
    const auto extent=QSizeF(m_tinted.size()).scaled(QSizeF(width(),height()),Qt::KeepAspectRatio);
    const auto scale=std::hypot(painter->deviceTransform().m11(),painter->deviceTransform().m12());
    const QSize target(std::max(1,qRound(extent.width()*scale)),std::max(1,qRound(extent.height()*scale)));
    QImage sampled(target,QImage::Format_ARGB32_Premultiplied);
    if(sampled.isNull())qFatal("Brand image render target cannot be allocated");
    // Sample the original mask bilinearly. Area reduction would introduce
    // coverage where the recorded native one-point samples are clear.
    for(int y=0;y<target.height();++y) {
        const auto sy=(y+0.5)*m_tinted.height()/target.height()-0.5;
        const auto y0=int(std::floor(sy));const auto fy=sy-y0;
        const auto upper=reinterpret_cast<const QRgb*>(m_tinted.constScanLine(std::clamp(y0,0,m_tinted.height()-1)));
        const auto lower=reinterpret_cast<const QRgb*>(m_tinted.constScanLine(std::clamp(y0+1,0,m_tinted.height()-1)));
        auto out=reinterpret_cast<QRgb*>(sampled.scanLine(y));
        for(int x=0;x<target.width();++x) {
            const auto sx=(x+0.5)*m_tinted.width()/target.width()-0.5;
            const auto x0=int(std::floor(sx));const auto fx=sx-x0;
            const auto a=upper[std::clamp(x0,0,m_tinted.width()-1)],b=upper[std::clamp(x0+1,0,m_tinted.width()-1)];
            const auto c=lower[std::clamp(x0,0,m_tinted.width()-1)],d=lower[std::clamp(x0+1,0,m_tinted.width()-1)];
            auto channel=[&](int shift){return qRound((((a>>shift)&255)*(1-fx)+((b>>shift)&255)*fx)*(1-fy)+(((c>>shift)&255)*(1-fx)+((d>>shift)&255)*fx)*fy);};
            out[x]=qRgba(channel(16),channel(8),channel(0),channel(24));
        }
    }
    painter->setRenderHint(QPainter::SmoothPixmapTransform,false);
    painter->drawImage(QRectF((width()-extent.width())/2,(height()-extent.height())/2,extent.width(),extent.height()),sampled);
}
