# -*- coding: utf-8 -*-
"""Surgically patch slide 1 of the 13-slide deck: replace the ⑤ one-liner
with a 3-box pipeline and update the ⑥ implications. Slides 2-13 untouched."""
import hashlib, io, shutil, zipfile
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.oxml.ns import qn

SRC = "community-issue-pr-io-issue.pptx"
OUT = "community-issue-pr-io-issue.page1-v2.pptx"
FONT = "微软雅黑"
INK, TEAL, GRAY, LIGHT, TRACK, WHITE = "16191E", "0F766E", "6B7380", "9AA1AC", "EEF1F3", "FFFFFF"


def set_font(run, name=FONT):
    run.font.name = name
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = rPr.makeelement(qn("a:ea"), {})
        rPr.append(ea)
    ea.set("typeface", name)


def add_text(slide, x, y, w, h, paras, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.0):
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


def add_rect(slide, x, y, w, h, color):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = RGBColor.from_string(color)
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def dump_texts(path):
    prs = Presentation(path)
    out = []
    for slide in prs.slides:
        buf = []
        def rec(shapes):
            for sh in shapes:
                if sh.has_text_frame:
                    buf.append(sh.text_frame.text)
                if sh.shape_type == 6:
                    rec(sh.shapes)
        rec(slide.shapes)
        out.append("\n".join(buf))
    return out


def media_hashes(path):
    z = zipfile.ZipFile(path)
    return {n: hashlib.sha256(z.read(n)).hexdigest()
            for n in z.namelist() if n.startswith("ppt/media/") and not n.endswith("/")}


base_texts = dump_texts(SRC)
base_media = media_hashes(SRC)
assert len(base_texts) == 13, len(base_texts)

shutil.copyfile(SRC, OUT)
prs = Presentation(OUT)
slide = prs.slides[0]

# ---- remove the ⑤ one-liner ----
removed = False
for sh in list(slide.shapes):
    if sh.has_text_frame and "五维标签 + 决策五门 + 执行四门" in sh.text_frame.text:
        sh._element.getparent().remove(sh._element)
        removed = True
assert removed, "one-liner not found"

# ---- ⑤ 3-box pipeline ----
BY, BH = 3.80, 0.46
created = []

add_rect(slide, 6.19, BY, 1.70, BH, TRACK)
created.append(add_text(slide, 6.27, BY, 1.54, BH, [
    [("模型", 9.5, True, INK)],
    [("只读评审 → decision", 8, False, GRAY)]], anchor=MSO_ANCHOR.MIDDLE))

created.append(add_text(slide, 7.92, BY, 0.16, BH, [[("→", 11, False, LIGHT)]],
                        align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE))

add_rect(slide, 8.11, BY, 2.40, BH, TEAL)
created.append(add_text(slide, 8.21, BY, 2.20, BH, [
    [("代码", 9.5, True, WHITE)],
    [("schema → 证据门 → 执行门", 8, False, WHITE)],
    [("唯一写入口 · 缺一即拒", 8, False, "D7EFED")]], anchor=MSO_ANCHOR.MIDDLE))

created.append(add_text(slide, 10.53, BY, 0.16, BH, [[("→", 11, False, LIGHT)]],
                        align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE))

add_rect(slide, 10.73, BY, 1.56, BH, TRACK)
created.append(add_text(slide, 10.81, BY, 1.40, BH, [
    [("人", 9.5, True, INK)],
    [("否决 / 复活", 8, False, GRAY)]], anchor=MSO_ANCHOR.MIDDLE))

created.append(add_text(slide, 6.19, 4.29, 6.10, 0.14, [[
    ("五维标签：路由 / 复现 / 评级 / 优先级 / 影响", 8, False, LIGHT)]]))

# ---- ⑥ implications ----
lines = [
    "先建分流，再叠评分：两层正交，不合成总分",
    "先立证据契约，再开自动动作",
    "模型只提议，代码执行，人可否决",
]
tb = None
for sh in slide.shapes:
    if sh.name == "TextBox 47" or (sh.has_text_frame and "先建分流，再叠评分" in sh.text_frame.text):
        tb = sh
        break
assert tb is not None, "implications box not found"
ps = tb.text_frame.paragraphs
for i, line in enumerate(lines):
    p = ps[i]
    for r in list(p.runs):
        r._r.getparent().remove(r._r)
    r = p.add_run()
    r.text = line
    r.font.size = Pt(12)
    r.font.bold = False
    r.font.color.rgb = RGBColor.from_string(INK)
    set_font(r)

prs.save(OUT)

# ---- verify ----
new_texts = dump_texts(OUT)
new_media = media_hashes(OUT)
print("SLIDES:", len(new_texts))
print("SLIDES 2-13 TEXT UNCHANGED:", new_texts[1:] == base_texts[1:])
print("MEDIA UNCHANGED:", new_media == base_media)

prs2 = Presentation(OUT)
s2 = prs2.slides[0]
bad = []
for sh in created:
    if sh.left < 0 or sh.top < 0 or sh.left + sh.width > prs2.slide_width \
       or sh.top + sh.height > prs2.slide_height:
        bad.append(sh.name)
print("NEW SHAPES OUT OF BOUNDS:", bad or "none")
print("NEW SHAPES:", len(created))
print("ONE-LINER GONE:", not any("决策五门 + 执行四门" in (sh.text_frame.text if sh.has_text_frame else "")
                                 for sh in s2.shapes))
print("IMPL LINES OK:", all(l in new_texts[0] for l in lines))
