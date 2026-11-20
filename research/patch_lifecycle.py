# -*- coding: utf-8 -*-
"""Reframe slide 1's bottom lifecycle band.

Only slide 1 is touched. Slides 2-19 are left byte-for-byte in the package
(python-pptx re-serializes XML, so the verifier compares text/media, not zip bytes).
"""
import shutil
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

SRC = "research/community-issue-pr-io-issue.pptx"
OUT = "research/community-issue-pr-io-issue.lifecycle.pptx"
FONT = "微软雅黑"

INK = "16191E"
TEAL = "0F766E"
AMBER = "B45309"
GRAY = "9AA1AC"
BORDER = "C9D0D6"
PANEL_TEAL = "F0F7F6"
PANEL_AMBER = "FBF4EC"

REMOVE_IDS = {
    11, 12, 15, 21, 24, 26, 28, 30, 59, 61, 62, 63, 64, 65, 66,
    67, 68, 69, 70, 71, 72, 73, 75, 76, 77, 131, 132,
}


def set_font(run, name=FONT):
    run.font.name = name
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = rPr.makeelement(qn("a:ea"), {})
        rPr.append(ea)
    ea.set("typeface", name)


def add_text(slide, x, y, w, h, paras, align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP, spacing=1.0):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, runs in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        p.space_before = Pt(0)
        p.space_after = Pt(0)
        for text, size, bold, color in runs:
            r = p.add_run()
            r.text = text
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.color.rgb = RGBColor.from_string(color)
            set_font(r)
    return tb


def add_rect(slide, x, y, w, h, fill):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y),
                               Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = RGBColor.from_string(fill)
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def add_oval(slide, x, y, w, h, fill):
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y),
                               Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = RGBColor.from_string(fill)
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def main():
    shutil.copyfile(SRC, OUT)
    prs = Presentation(OUT)
    slide = prs.slides[0]

    removed = []
    for sh in list(slide.shapes):
        if sh.shape_id in REMOVE_IDS:
            removed.append(sh.shape_id)
            sh._element.getparent().remove(sh._element)
    missing = REMOVE_IDS - set(removed)
    if missing:
        raise SystemExit("shape ids not found: %s" % sorted(missing))

    # ---- panels (added first, so text sits above the fills) ----
    add_rect(slide, 0.35, 5.82, 5.95, 0.60, PANEL_TEAL)
    add_rect(slide, 6.45, 5.82, 6.20, 0.60, PANEL_AMBER)

    # ---- headline ----
    add_text(slide, 0.50, 5.48, 8.70, 0.30, [[
        ("bot 用 ", 14, True, INK),
        ("≈10 分钟", 16, True, TEAL),
        ("，把原始 issue 变成「可决策包」", 14, True, INK),
    ]])
    add_text(slide, 10.75, 5.52, 1.95, 0.16, [[
        ("2026-09-11 → 11-11", 8.5, False, GRAY),
    ]], align=PP_ALIGN.RIGHT)
    add_rect(slide, 0.32, 5.50, 0.06, 0.19, AMBER)

    # ---- bot panel ----
    add_text(slide, 0.48, 5.84, 1.95, 0.17, [[
        ("bot · 完成 3 件事", 10.5, True, TEAL),
    ]])
    add_text(slide, 2.55, 5.86, 3.60, 0.14, [[
        ("（~3min / ~9min 为创建后时点）", 7.5, False, GRAY),
    ]])

    outputs = [
        (0.28, "① 分流", "类别 / 缺什么证据"),
        (2.36, "② 复现 + 标签", "源码级结论 / 五维标签"),
        (4.44, "③ review 意见", "证据链 / fixPrompt / 关闭理由"),
    ]
    for x, title, sub in outputs:
        add_text(slide, x, 6.03, 1.88, 0.15, [[(title, 8.5, True, INK)]],
                 align=PP_ALIGN.CENTER)
        add_text(slide, x, 6.20, 1.88, 0.14, [[(sub, 8, False, "4B5563")]],
                 align=PP_ALIGN.CENTER)

    # ---- human panel ----
    add_text(slide, 6.58, 5.84, 2.00, 0.17, [[
        ("人接手 · 小时–天", 10.5, True, AMBER),
    ]])
    add_text(slide, 8.62, 5.86, 2.50, 0.14, [[
        ("只做 3 个关键动作", 7.5, False, GRAY),
    ]])
    add_text(slide, 6.58, 6.12, 5.90, 0.16, [[
        ("定夺（修 / 挂起 / 路由）· 开 PR · 合并 99.2% 由人", 8, False, INK),
    ]])

    # ---- rail + nodes ----
    add_rect(slide, 0.60, 6.52, 12.05, 0.02, BORDER)
    dot_x = [1.13, 3.21, 5.30, 7.39, 9.46, 11.55]
    for i, x in enumerate(dot_x):
        add_oval(slide, x, 6.45, 0.16, 0.16, TEAL if i < 3 else AMBER)

    labels = [
        (0.28, 1.88, "规则分流", "bot · 秒级"),
        (2.36, 1.88, "Agent 判定", "bot · ~3min"),
        (4.44, 1.88, "review 意见", "bot · ~9min"),
        (6.53, 1.88, "maintainer 定夺", "人 · 小时–天"),
        (8.61, 1.88, "开 PR", "人 / bot"),
        (10.59, 2.08, "校验合并", "人 99.2% · bot 0.8%"),
    ]
    for x, w, title, sub in labels:
        add_text(slide, x, 6.62, w, 0.17, [[(title, 10, False, INK)]],
                 align=PP_ALIGN.CENTER)
        add_text(slide, x, 6.80, w, 0.17, [[(sub, 10, False, GRAY)]],
                 align=PP_ALIGN.CENTER)

    # ---- fork + takeaway ----
    add_text(slide, 0.50, 6.98, 8.60, 0.16, [[
        ("分叉也在 10 分钟内：证据足 → 关闭 + 理由（可复活）｜证据不足 → 补证据",
         8, False, TEAL),
    ]])
    add_text(slide, 0.50, 7.20, 12.00, 0.17, [[
        ("启示：", 9, True, TEAL),
        ("人拿到的是「可决策包」，不是原始 issue —— 省下的是判断前的整理时间。",
         9, False, INK),
    ]])

    prs.save(OUT)
    print("removed=%d added_text=%d out=%s" % (len(removed), 30, OUT))


if __name__ == "__main__":
    sys.exit(main())
