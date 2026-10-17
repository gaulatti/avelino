#include "texttools.h"
#include <QTextDocument>
#include <QTextImageFormat>
#include <QThread>
#include <QtQuick/private/qquicktext_p.h>
#include <QtQuick/private/qquicktext_p_p.h>
#include <cmath>

QFont BleeckerTextTools::spacedFont(const QFont &font,qreal spacing) const {
    if(!std::isfinite(spacing))qFatal("Text spacing must be finite");
    auto copy=font;
    if(spacing!=0)copy.setLetterSpacing(QFont::AbsoluteSpacing,spacing);
    return copy;
}
bool BleeckerTextTools::textResourcesReady(QObject *item) const {
    const auto text=qobject_cast<QQuickText*>(item);
    if(!text)qFatal("Text resource readiness requires the owned Qt text renderer");
    if(QThread::currentThread()!=text->thread())qFatal("Text resources must be prepared on the owning GUI thread");
    const auto state=QQuickTextPrivate::get(text);
    if(state->extra.isAllocated() &&state->extra->doc) {
        // An image with explicit width/height need not be fetched during text
        // layout. Fetch on the GUI thread before scene-graph text nodes paint.
        for(const auto &format:state->extra->doc->allFormats())if(format.isImageFormat())
            state->extra->doc->resource(QTextDocument::ImageResource,QUrl(format.toImageFormat().name()));
    }
    return text->resourcesLoading()==0;
}
QString BleeckerTextTools::plainText(const QString &text,int format) const {
    if(format==Qt::PlainText)return text;
    QTextDocument document;
    if(format==Qt::MarkdownText)document.setMarkdown(text);
    else if(format==Qt::RichText ||format==4 ||(format==Qt::AutoText &&Qt::mightBeRichText(text)))document.setHtml(text);
    else if(format==Qt::AutoText)return text;
    else qFatal("Unsupported text format");
    return document.toPlainText();
}
#include <algorithm>

qreal BleeckerTextTools::proposedWidth(qreal maximumWidth, qreal insets) const {
    if (!std::isfinite(maximumWidth) || (maximumWidth < 0 && maximumWidth != -1)
        || !std::isfinite(insets) || insets < 0)
        qFatal("Text maximum width must be nonnegative or -1, with finite nonnegative insets");
    return maximumWidth == -1 ? -1 : std::max(qreal(0), maximumWidth-insets);
}
#include <QTextBoundaryFinder>

QString BleeckerTextTools::avatarInitials(const QString &name) const {
    QString result;
    const auto words = name.split(QLatin1Char(' '), Qt::SkipEmptyParts);
    for (int i = 0; i < std::min(2, int(words.size())); ++i) {
        QTextBoundaryFinder finder(QTextBoundaryFinder::Grapheme, words[i]);
        const auto end = finder.toNextBoundary();
        if (end > 0) result += words[i].left(end);
    }
    return result.toUpper();
}
