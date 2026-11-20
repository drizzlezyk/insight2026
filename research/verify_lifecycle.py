# -*- coding: utf-8 -*-
"""Verify the slide-1 lifecycle reframe without opening PowerPoint.

Usage:
  python verify_lifecycle.py <pptx> [--write-baseline]
"""
import hashlib, io, json, os, sys, zipfile
from PIL import ImageFont
from pptx import Presentation

BASE = os.path.dirname(os.path.abspath(__file__))
BASELINE = os.path.join(BASE, "implement", "lifecycle-baseline.json")
REG = "C:/Windows/Fonts/msyh.ttc"
BOLD = "C:/Windows/Fonts/msyhbd.ttc"
EMU = 914400
CANVAS_W, CANVAS_H = 12192000, 6858000

NEW_STRINGS = [
    "bot 用 ≈10 分钟，把原始 issue 变成「可决策包」",
    "bot · 完成 3 件事",
    "① 分流",
    "② 复现 + 标签",
    "③ review 意见",
    "人接手 · 小时–天",
    "只做 3 个关键动作",
    "分叉也在 10 分钟内：证据足 → 关闭 + 理由（可复活）｜证据不足 → 补证据",
    "启示：人拿到的是「可决策包」，不是原始 issue —— 省下的是判断前的整理时间。",
]
OLD_STRINGS = ["谁在做、多久、在哪分叉", "work lane", "clawsweeper触发只在创建和人工@"]

_font_cache = {}


def font(pt, bold):
    key = (round(pt, 1), bold)
    if key not in _font_cache:
        px = max(1, round(pt * 4 / 3))
        _font_cache[key] = ImageFont.truetype(BOLD if bold else REG, px)
    return _font_cache[key]


def slide_texts(prs):
    out = []
    for slide in prs.slides:
        buf = []
        def walk(shapes):
            for sh in shapes:
                if sh.has_text_frame and sh.text_frame.text.strip():
                    buf.append(sh.text_frame.text)
                if sh.shape_type == 6:
                    walk(sh.shapes)
        walk(slide.shapes)
        out.append("\n".join(buf))
    return out


def media_hashes(path):
    z = zipfile.ZipFile(path)
    return {n: hashlib.sha256(z.read(n)).hexdigest()
            for n in z.namelist() if n.startswith("ppt/media/") and not n.endswith("/")}


def main():
    path = sys.argv[1]
    write = "--write-baseline" in sys.argv
    prs = Presentation(path)
    texts = slide_texts(prs)
    media = media_hashes(path)
    if write:
        os.makedirs(os.path.dirname(BASELINE), exist_ok=True)
        with io.open(BASELINE, "w", encoding="utf-8") as f:
            json.dump({"texts": texts, "media": media}, f, ensure_ascii=False)
        print("baseline written:", BASELINE)
        return 0

    with io.open(BASELINE, encoding="utf-8") as f:
        base = json.load(f)

    problems = []
    if len(texts) != 19:
        problems.append("slide count %d != 19" % len(texts))
    if texts[1:] != base["texts"][1:]:
        problems.append("slides 2-19 text changed")
    if media != base["media"]:
        problems.append("media bytes changed")
    for s in NEW_STRINGS:
        if s not in texts[0]:
            problems.append("missing: " + s)
    for s in OLD_STRINGS:
        if s in texts[0]:
            problems.append("old string still present: " + s)

    slide = prs.slides[0]
    text_boxes = []
    for sh in slide.shapes:
        l, t, w, h = sh.left, sh.top, sh.width, sh.height
        if None in (l, t, w, h):
            continue
        if l < -1 or t < -1 or l + w > CANVAS_W + 1 or t + h > CANVAS_H + 1:
            problems.append("out of canvas: %s (%.2f, %.2f, %.2f, %.2f)" %
                            (sh.name, l / EMU, t / EMU, w / EMU, h / EMU))
        if not sh.has_text_frame or not sh.text_frame.text.strip():
            continue
        box_w, box_h = w / 9525, h / 9525
        measured_w = 0.0
        measured_h = 0.0
        for p in sh.text_frame.paragraphs:
            runs = [r for r in p.runs if r.text]
            if not runs:
                continue
            measured_w = max(measured_w, sum(
                font(r.font.size.pt if r.font.size else 11, bool(r.font.bold)).getlength(r.text)
                for r in runs))
            size = max((r.font.size.pt if r.font.size else 11) for r in runs)
            ls = p.line_spacing if isinstance(p.line_spacing, float) else 1.0
            measured_h += size * 4 / 3 * 1.2 * ls
        if t / EMU > 5.35:
            if measured_w > box_w + 2:
                problems.append("WIDE %.0f>%.0f :: %s" % (measured_w, box_w, sh.text_frame.text[:32]))
            if measured_h > box_h + 2:
                problems.append("TALL %.0f>%.0f :: %s" % (measured_h, box_h, sh.text_frame.text[:32]))
        if t / EMU > 5.35:
            text_boxes.append((l / 9525, t / 9525, w / 9525, h / 9525,
                               sh.text_frame.text[:20]))
    for i in range(len(text_boxes)):
        for j in range(i + 1, len(text_boxes)):
            ax, ay, aw, ah, at = text_boxes[i]
            bx, by, bw, bh, bt = text_boxes[j]
            ox = max(0, min(ax + aw, bx + bw) - max(ax, bx))
            oy = max(0, min(ay + ah, by + bh) - max(ay, by))
            if ox * oy > 6:
                problems.append("OVERLAP %.0fx%.0f :: %s x %s" % (ox, oy, at, bt))

    if problems:
        print("FAIL")
        for p in problems:
            print("  -", p)
        return 1
    print("OK slides=%d media=%d boxes=%d" % (len(texts), len(media), len(text_boxes)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
