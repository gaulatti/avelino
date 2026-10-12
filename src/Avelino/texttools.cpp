#include "texttools.h"
#include <QTextBoundaryFinder>
#include <algorithm>

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
