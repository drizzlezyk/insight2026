# -*- coding: utf-8 -*-
"""Add the 'not auto-closed by bot' stage to the slide-1 funnel.

Window 2026-09-11..11-11: 11,468 issues.
  bot-closed (clawsweeper / barnacle / roboclaw / other bots): 3,613
  not auto-closed: 7,855 (68.5%)

The new band goes between 'Agent 筛选后打标签' (9,497) and
'获得源码级可复现标签' (5,221), so the funnel stays monotonic:
  11,468 -> 9,497 -> 7,855 -> 5,221 -> 2,769
"""
import os
import shutil
import sys
from copy import deepcopy
from datetime import datetime

from lxml import etree
from pptx import Presentation
from pptx.oxml.ns import qn

PPTX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'community-issue-pr-io-issue.pptx')
BACKUP = PPTX.replace('.pptx', '.backup-%s.pptx' % datetime.now().strftime('%Y%m%d-%H%M%S'))

NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}

NEW_LAYER_ID = 176
NEW_CONN_ID = 177
NEW_TEXT_ID = 178


def find_child(group, shape_id):
    for el in group:
        cnv = el.find('.//p:cNvPr', NS)
        if cnv is not None and cnv.get('id') == str(shape_id):
            return el
    raise KeyError(shape_id)


def get_cnv(el):
    return el.find('.//p:cNvPr', NS)


def set_identity(el, shape_id, name):
    cnv = get_cnv(el)
    cnv.set('id', str(shape_id))
    cnv.set('name', name)


def set_xfrm(el, x=None, y=None, cx=None, cy=None):
    xfrm = el.find('.//a:xfrm', NS)
    off = xfrm.find('a:off', NS)
    ext = xfrm.find('a:ext', NS)
    if x is not None:
        off.set('x', str(x))
    if y is not None:
        off.set('y', str(y))
    if cx is not None:
        ext.set('cx', str(cx))
    if cy is not None:
        ext.set('cy', str(cy))


def set_y(el, y):
    set_xfrm(el, y=y)


def set_path(el, w, h, points):
    path = el.find('.//a:path', NS)
    path.set('w', str(w))
    path.set('h', str(h))
    pts = path.findall('.//a:pt', NS)
    assert len(pts) == 4, len(pts)
    for pt, (x, y) in zip(pts, points):
        pt.set('x', str(int(round(x))))
        pt.set('y', str(int(round(y))))


def set_fill(el, lum_mod, lum_off):
    scheme = el.find('.//a:solidFill/a:schemeClr', NS)
    for tag, val in (('a:lumMod', lum_mod), ('a:lumOff', lum_off)):
        node = scheme.find(tag, NS)
        if node is None:
            node = etree.SubElement(scheme, qn(tag))
        node.set('val', str(val))


def set_text(tb_el, line1, count, pct):
    paras = tb_el.findall('.//p:txBody/a:p', NS)
    assert len(paras) >= 2, len(paras)
    runs0 = paras[0].findall('a:r', NS)
    runs0[0].find('a:t', NS).text = line1
    runs1 = paras[1].findall('a:r', NS)
    runs1[0].find('a:t', NS).text = count
    runs1[-1].find('a:t', NS).text = '%s of 原始  ' % pct


def main():
    if not os.path.exists(PPTX):
        raise SystemExit('missing ' + PPTX)
    shutil.copy2(PPTX, BACKUP)
    print('backup ->', BACKUP)

    prs = Presentation(PPTX)
    slide = prs.slides[0]
    group = None
    for sh in slide.shapes:
        if sh.shape_id == 7:
            group = sh._element
            break
    if group is None:
        raise SystemExit('funnel group (id 7) not found')

    layer1 = find_child(group, 2)   # 11,468
    layer2 = find_child(group, 4)   # 9,497
    layer3 = find_child(group, 5)   # 5,221
    layer4 = find_child(group, 6)   # 2,769
    conn1 = find_child(group, 122)
    conn2 = find_child(group, 123)
    conn3 = find_child(group, 124)
    conn4 = find_child(group, 125)
    text1 = find_child(group, 126)
    text2 = find_child(group, 127)
    text3 = find_child(group, 128)
    text4 = find_child(group, 129)

    # --- new band: top width 2,979 (7,855), bottom width 1,980 (5,221) ---
    new_layer = deepcopy(layer2)
    set_identity(new_layer, NEW_LAYER_ID, 'Freeform 6')
    set_xfrm(new_layer, x=1275, y=6836, cx=2979, cy=1237)
    set_path(new_layer, 2979000, 785241,
             [(0, 0), (2979000, 0), (2479500, 785241), (499500, 785241)])
    set_fill(new_layer, 50000, 50000)
    layer2.addnext(new_layer)

    # --- layer 2 now funnels down to the new band (bottom 2,979, not 1,980) ---
    set_path(layer2, 2286873, 785241,
             [(0, 0), (2286873, 0), (2089318, 785241), (197555, 785241)])

    # --- shift the two lower bands by one slot ---
    set_y(layer3, 8152)
    set_y(layer4, 9468)
    set_y(text3, 8338)
    set_y(text4, 9654)
    set_y(conn3, 8770)
    set_y(conn4, 10086)

    # --- new connector ---
    new_conn = deepcopy(conn2)
    set_identity(new_conn, NEW_CONN_ID, 'Connector 125')
    set_xfrm(new_conn, x=4340, y=7455, cx=844, cy=0)
    conn2.addnext(new_conn)

    # --- new label ---
    new_text = deepcopy(text2)
    set_identity(new_text, NEW_TEXT_ID, 'TextBox 176')
    set_xfrm(new_text, y=7023)
    set_text(new_text, ' 未被 bot 自动关闭', '7,855', '68.5%')
    text2.addnext(new_text)

    # --- extend the group; keep bottom inside the white card ---
    gxfrm = group.find('p:grpSpPr/a:xfrm', NS)
    goff = gxfrm.find('a:off', NS)
    gext = gxfrm.find('a:ext', NS)
    chext = gxfrm.find('a:chExt', NS)
    goff.set('y', '2575000')
    gext.set('cy', '2131427')
    chext.set('cy', '6500')

    prs.save(PPTX)
    print('saved', PPTX)

    # --- verify on reopen ---
    prs2 = Presentation(PPTX)
    g2 = None
    for sh in prs2.slides[0].shapes:
        if sh.shape_id == 7:
            g2 = sh._element
    print('group xfrm:', etree.tostring(g2.find('p:grpSpPr/a:xfrm', NS), encoding='unicode'))
    for sid in (2, 4, NEW_LAYER_ID, 5, 6):
        el = find_child(g2, sid)
        xfrm = el.find('.//a:xfrm', NS)
        print(sid, get_cnv(el).get('name'), 'off', xfrm.find('a:off', NS).attrib,
              'ext', xfrm.find('a:ext', NS).attrib)
    for sid in (126, 127, NEW_TEXT_ID, 128, 129):
        el = find_child(g2, sid)
        txt = ''.join(t.text or '' for t in el.findall('.//a:t', NS))
        print(sid, repr(txt), 'y', el.find('.//a:off', NS).get('y'))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
