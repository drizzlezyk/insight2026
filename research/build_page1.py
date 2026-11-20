# -*- coding: utf-8 -*-
"""Rebuild slide 1 of community-issue-pr-io-issue.pptx. Only slide 1 is touched."""
import hashlib, io, os, shutil, sys, zipfile
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.oxml.ns import qn

SRC = "community-issue-pr-io-issue.pptx"
OUT = "community-issue-pr-io-issue.page1.pptx"
FONT = "微软雅黑"
PX = 9525  # EMU per px on a 1280x720 canvas

INK, TEAL, GRAY, LIGHT, TRACK, BORDER, AMBER, WHITE = (
    "16191E", "0F766E", "6B7380", "9AA1AC", "EEF1F3", "C9D0D6", "B45309", "FFFFFF")


def emu(px):
    return int(round(px * PX))


def set_font(run, name=FONT):
    run.font.name = name
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = rPr.makeelement(qn("a:ea"), {})
        rPr.append(ea)
    ea.set("typeface", name)


def add_text(slide, x, y, w, h, paras, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
             spacing=1.0):
    tb = slide.shapes.add_textbox(emu(x), emu(y), emu(w), emu(h))
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


def add_rect(slide, x, y, w, h, color, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, emu(x), emu(y), emu(w), emu(h))
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


# ---- baseline before touching anything ----
base_texts = dump_texts(SRC)
base_media = media_hashes(SRC)
assert len(base_texts) == 12, len(base_texts)

shutil.copyfile(SRC, OUT)
prs = Presentation(OUT)
slide = prs.slides[0]

# ---- clear slide 1 ----
for shp in list(slide.shapes):
    shp._element.getparent().remove(shp._element)

# ================= 标题 =================
add_text(slide, 34, 16, 1200, 44,
         [[("证据优先、模型判断、代码守门", 26, True, INK)]])
add_text(slide, 36, 60, 1200, 20,
         [[("openClaw 社区 issue 治理实践 · 对我们基础设施的三点启示", 12, False, GRAY)]])
add_rect(slide, 34, 96, 1212, 1, "E2E6EA")

# ================= 左：漏斗 =================
add_text(slide, 38, 106, 586, 20, [[
    ("①", 10.5, True, TEAL), (" 怎么管 ", 10.5, True, INK),
    ("· 量在哪一关掉", 9, False, LIGHT)]])

rows = [
    # label, count, bar_px, drop, hot
    ("全部 issue",    "11,468", 252, "", False),
    ("完成分流评级",  "9,497",  209, "−1,971 分流未过", False),
    ("仍在流程中",    "7,855",  173, "−1,642 自动关闭", False),
    ("证据可复现",    "5,221",  115, "▲ −2,634 最大流失", True),
    ("已合并关闭",    "2,769",   61, "−2,452 未合并", False),
]
for i, (label, count, barw, drop, hot) in enumerate(rows):
    y = 142 + i * 62
    add_text(slide, 38, y + 7, 112, 20, [[(label, 10.5, False, INK)]])
    add_rect(slide, 152, y, 252, 34, TRACK)
    add_rect(slide, 152, y, barw, 34, GRAY if i == 4 else TEAL)
    if i == 4:
        add_text(slide, 408, y + 1, 56, 32, [
            [("2,769", 11, True, INK)],
            [("24.1%", 8, False, LIGHT)]], align=PP_ALIGN.RIGHT)
    else:
        add_text(slide, 408, y + 7, 56, 20, [[(count, 11, True, INK)]],
                 align=PP_ALIGN.RIGHT)
    if drop:
        add_text(slide, 470, y + 8, 154, 18,
                 [[(drop, 9, hot, AMBER if hot else GRAY)]])

# ================= 右：② 为什么 =================
add_text(slide, 658, 106, 586, 20, [[
    ("②", 10.5, True, TEAL), (" 为什么 ", 10.5, True, INK),
    ("· 策略与理念", 9, False, LIGHT)]])

principles = [
    ("证据优先", "缺证据只补证，不判无效"),
    ("模型判断、代码守门", "AI 不直接改状态"),
    ("关闭即解释", "处置留痕、可复活"),
]
for i, (head, sub) in enumerate(principles):
    add_text(slide, 658, 136 + i * 32, 586, 20, [[
        (head, 11, True, INK), ("　" + sub, 9.5, False, GRAY)]])

# ================= 右：③④ 谁受益 =================
add_rect(slide, 658, 228, 586, 1, TRACK)
add_text(slide, 658, 238, 586, 20, [[
    ("③④", 10.5, True, TEAL), (" 谁受益 ", 10.5, True, INK),
    ("· 每条到达时都已带判断依据", 9, False, LIGHT)]])

benef = [
    ("maintainer", "到达时已带去向与证据，只判断不筛选", "98.5%", 270, 266, None),
    ("contributor", "每条都有回应、理由与下一步；可补证复活", "100%", 308, 304, "设计保证"),
]
for role, text, num, ty, ny, tag in benef:
    add_text(slide, 658, ty, 86, 18, [[(role, 8.5, False, LIGHT)]])
    add_text(slide, 744, ty, 344, 18, [[(text, 9.5, False, INK)]])
    add_text(slide, 1090, ny, 154, 24, [[(num, 15, True, TEAL)]],
             align=PP_ALIGN.RIGHT)
    if tag:
        add_text(slide, 1090, ny + 25, 154, 13, [[(tag, 8, False, LIGHT)]],
                 align=PP_ALIGN.RIGHT)

# ================= 左下：⑤ 怎么做 =================
add_text(slide, 38, 428, 586, 18, [[
    ("⑤", 10.5, True, TEAL), (" 怎么做 ", 10.5, True, INK),
    ("· 设计与实现", 9, False, LIGHT)]])

BY, BH = 448, 44
add_rect(slide, 38, BY, 160, BH, TRACK)
add_text(slide, 46, BY, 144, BH, [
    [("模型", 9.5, True, INK)],
    [("只读评审", 8, False, GRAY)],
    [("产出 decision", 8, False, GRAY)]], anchor=MSO_ANCHOR.MIDDLE)
add_text(slide, 200, BY, 18, BH, [[("→", 11, False, LIGHT)]],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

add_rect(slide, 220, BY, 226, BH, TEAL)
add_text(slide, 228, BY, 210, BH, [
    [("代码", 9.5, True, WHITE)],
    [("schema → 证据门 → 执行门", 8, False, WHITE)],
    [("唯一写入口 · 缺一即拒", 8, False, "D7EFED")]], anchor=MSO_ANCHOR.MIDDLE)
add_text(slide, 448, BY, 18, BH, [[("→", 11, False, LIGHT)]],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

add_rect(slide, 468, BY, 156, BH, TRACK)
add_text(slide, 476, BY, 140, BH, [
    [("人", 9.5, True, INK)],
    [("否决 / 复活", 8, False, GRAY)],
    [("一条评论可重开", 8, False, GRAY)]], anchor=MSO_ANCHOR.MIDDLE)

add_text(slide, 38, 494, 586, 14, [[
    ("五维标签：路由 / 复现 / 评级 / 优先级 / 影响", 8, False, LIGHT)]])

# ================= 右：⑥ 启示 =================
add_rect(slide, 658, 354, 586, 136, TEAL)
add_text(slide, 672, 362, 558, 18, [[
    ("⑥", 10, True, WHITE), (" 所以 · 对我们基建的启示", 10, True, WHITE)]])
add_text(slide, 672, 386, 558, 14, [[
    ("从零起步的三条建设顺序", 8.5, False, "CFE3E1")]])
impl = [
    "先建分流，再叠评分：两层正交，不合成总分",
    "先立证据契约，再开自动动作",
    "模型只提议，代码执行，人可否决",
]
for i, t in enumerate(impl):
    add_text(slide, 672, 410 + i * 26, 558, 18, [[(t, 10, False, WHITE)]])

# ================= 底：6 步条 =================
add_text(slide, 38, 510, 586, 20, [[
    ("同一流程", 9.5, True, INK), (" · 谁在做、多久、在哪分叉", 9.5, False, GRAY)]])
add_rect(slide, 60, 548, 1160, 1.5, BORDER)

steps = [
    (112,  "规则分流",           "bot · 秒级",              TEAL,  180, 30),
    (312,  "Agent 复现 + 标签",  "bot · ~3min",             TEAL,  180, 230),
    (512,  "证据判定",           "bot · ~9min",             TEAL,  180, 430),
    (712,  "维护者定夺",         "人 · 小时–天",            AMBER, 180, 630),
    (912,  "开 PR",              "人 / bot",                AMBER, 180, 830),
    (1112, "校验合并",           "人 99.2% · bot 0.8%",     AMBER, 200, 1020),
]
for node, l1, l2, color, lw, lx in steps:
    add_rect(slide, node, 541, 15, 15, color, MSO_SHAPE.OVAL)
    add_text(slide, lx, 560, lw, 16, [[(l1, 9, False, INK)]], align=PP_ALIGN.CENTER)
    add_text(slide, lx, 576, lw, 14, [[(l2, 8, False, LIGHT)]], align=PP_ALIGN.CENTER)

add_text(slide, 500, 594, 240, 30, [
    [("├ 3a 证据不足 → 补证据 / 带理由关闭", 8, False, TEAL)],
    [("└ 3b 证据齐 → 生成 fixPrompt", 8, False, TEAL)]], spacing=1.1)

# ================= 脚注 =================
add_text(slide, 38, 648, 1204, 14, [[
    ("口径：漏斗为现有第 1 页口径（窗口 2026-09-11–11-11，n=11,468，completed 且带合并 PR）"
     "· 待与附件 P12（11,147 / 09-13–11-13）对齐后替换", 8, False, LIGHT)]])

prs.save(OUT)

# ================= 校验 =================
new_texts = dump_texts(OUT)
new_media = media_hashes(OUT)
print("SLIDES:", len(new_texts))
print("SLIDES 2-12 TEXT UNCHANGED:", new_texts[1:] == base_texts[1:])
print("MEDIA UNCHANGED:", new_media == base_media)

prs2 = Presentation(OUT)
s2 = prs2.slides[0]
min_pt, chars, out_of_bounds = 99, 0, []
for sh in s2.shapes:
    if sh.left is None:
        continue
    if sh.left < 0 or sh.top < 0 or sh.left + sh.width > prs2.slide_width \
       or sh.top + sh.height > prs2.slide_height:
        out_of_bounds.append(sh.name)
    if sh.has_text_frame:
        chars += len(sh.text_frame.text.replace("\n", ""))
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                if r.font.size and len(r.text.strip()):
                    min_pt = min(min_pt, r.font.size.pt)
print("SHAPES:", len(s2.shapes))
print("OUT OF BOUNDS:", out_of_bounds or "none")
print("MIN FONT PT:", min_pt)
print("BODY CHARS:", chars)
print("SIX LABELS:", all(k in new_texts[0] for k in ["①", "②", "③④", "⑤", "⑥"]))
