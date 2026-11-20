# -*- coding: utf-8 -*-
"""Measure every text box on slide 1 against real Microsoft YaHei metrics."""
import io
from PIL import ImageFont
from pptx import Presentation

REG = "C:/Windows/Fonts/msyh.ttc"
BOLD = "C:/Windows/Fonts/msyhbd.ttc"
PRES_PX = 9525  # EMU per px

prs = Presentation("community-issue-pr-io-issue.page1.pptx")
s = prs.slides[0]
cache = {}


def font(sz_pt, bold):
    key = (round(sz_pt, 1), bold)
    if key not in cache:
        px = max(1, round(sz_pt * 4 / 3))
        cache[key] = ImageFont.truetype(BOLD if bold else REG, px)
    return cache[key]


def measure(run):
    f = font(run.font.size.pt if run.font.size else 11, bool(run.font.bold))
    return f.getlength(run.text)


issues, total_lines, overlap_candidates = [], 0, []
boxes = []
for sh in s.shapes:
    if not sh.has_text_frame or not sh.text_frame.text.strip():
        continue
    w = sh.width / PRES_PX
    h = sh.height / PRES_PX
    lines_h = 0.0
    for p in sh.text_frame.paragraphs:
        runs = [r for r in p.runs if r.text]
        if not runs:
            continue
        total_lines += 1
        tw = sum(measure(r) for r in runs)
        if tw > w + 1:
            issues.append("WIDE  %-5.0fpx > %-5.0fpx :: %s" % (tw, w, p.text[:34]))
        size = max((r.font.size.pt if r.font.size else 11) for r in runs)
        ls = p.line_spacing if isinstance(p.line_spacing, float) else 1.0
        lines_h += size * 4 / 3 * 1.2 * ls
    if lines_h > h + 2:
        issues.append("TALL  %.0fpx > %.0fpx :: %s" % (lines_h, h, sh.text_frame.text[:34]))
    boxes.append((sh.left / PRES_PX, sh.top / PRES_PX, w, h, sh.text_frame.text[:16]))

for i in range(len(boxes)):
    for j in range(i + 1, len(boxes)):
        ax, ay, aw, ah, at = boxes[i]
        bx, by, bw, bh, bt = boxes[j]
        ox = max(0, min(ax + aw, bx + bw) - max(ax, bx))
        oy = max(0, min(ay + ah, by + bh) - max(ay, by))
        if ox * oy > 6:
            overlap_candidates.append("OVER  %.0fx%.0f :: %s x %s" % (ox, oy, at, bt))

out = ["PARAGRAPHS: %d  TEXT BOXES: %d" % (total_lines, len(boxes))]
out += issues or ["NO WIDTH/HEIGHT OVERFLOW"]
out += overlap_candidates or ["NO TEXT-BOX OVERLAP"]
io.open("page1_verify.txt", "w", encoding="utf-8").write("\n".join(out))
print("done", len(issues), len(overlap_candidates))
