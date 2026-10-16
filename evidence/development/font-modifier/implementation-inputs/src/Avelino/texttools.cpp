#include "texttools.h"
#include <algorithm>
#include <cmath>

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
