from pathlib import Path
import difflib,json,hashlib
p=Path(__file__).resolve().parent
cpp=(p/'original/qsgsoftwareinternalrectanglenode.cpp').read_text()
header=(p/'original/qsgsoftwareinternalrectanglenode_p.h').read_text()
def replace_once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)
cpp=replace_once(cpp,"""    QRect alignedRect = rect.toAlignedRect();
    if (m_rect != alignedRect) {
        m_rect = alignedRect;
        markDirty(DirtyMaterial);
    }""","""    if (m_exactRect != rect) {
        m_exactRect = rect;
        m_rect = rect.toAlignedRect();
        markDirty(DirtyMaterial);
    }""")
cpp=replace_once(cpp,"""    if (painter->transform().isRotating()) {
        //Rotated rectangles""","""    if (isPlainRect()) {
        painter->save();
        if (painter->transform().isRotating()) {
            painter->setPen(Qt::NoPen);
            painter->setBrush(m_brush);
            painter->drawRect(m_exactRect);
        } else {
            painter->setRenderHint(QPainter::Antialiasing, false);
            painter->fillRect(m_exactRect, m_brush);
        }
        painter->restore();
        return;
    }

    if (painter->transform().isRotating()) {
        //Rotated rectangles""")
cpp=replace_once(cpp,"""QRectF QSGSoftwareInternalRectangleNode::rect() const
{
    //TODO: double check that this is correct.
    return m_rect;
}""","""bool QSGSoftwareInternalRectangleNode::isPlainRect() const
{
    return m_penWidth == 0 && m_radius == 0
        && m_topLeftRadius <= 0 && m_topRightRadius <= 0
        && m_bottomLeftRadius <= 0 && m_bottomRightRadius <= 0
        && m_stops.isEmpty();
}

QRectF QSGSoftwareInternalRectangleNode::rect() const
{
    return isPlainRect() ? m_exactRect : QRectF(m_rect);
}""")
header=replace_once(header,'private:\n    void paintRectangle(', 'private:\n    bool isPlainRect() const;\n    void paintRectangle(')
header=replace_once(header,'    QRect m_rect;\n','    QRect m_rect;\n    QRectF m_exactRect;\n')
(p/'patched').mkdir(exist_ok=True)
patch=[]
for name,text in [('qsgsoftwareinternalrectanglenode.cpp',cpp),('qsgsoftwareinternalrectanglenode_p.h',header)]:
    (p/'patched'/name).write_text(text)
    original=(p/'original'/name).read_text()
    relative='src/quick/scenegraph/adaptations/software/'+name
    patch.extend(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile='a/'+relative,tofile='b/'+relative))
(p/'fractional-rectangle.patch').write_text(''.join(patch))
(p/'patch-scope.json').write_text(json.dumps(dict(qt='6.8.3',plainRectOnly=True,bordersRoundedGradientsUnchanged=True,privateHeaderLayoutChanges=True,productSdkChanged=False,sourcePinsChanged=False,comparisonPolicyChanged=False,accepted=False),indent=2)+'\n')
print(''.join(patch))
