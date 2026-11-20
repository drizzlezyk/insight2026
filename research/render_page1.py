# -*- coding: utf-8 -*-
"""Rough PIL render of slide 1 for visual sanity checking (not a PowerPoint render)."""
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

REG = "C:/Windows/Fonts/msyh.ttc"
BOLD = "C:/Windows/Fonts/msyhbd.ttc"
EMU = 9525

prs = Presentation("community-issue-pr-io-issue.page1.pptx")
s = prs.slides[0]
W, H = 1280, 720
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)
fcache = {}


def fnt(pt, bold):
    k = (round(pt, 1), bold)
    if k not in fcache:
        fcache[k] = ImageFont.truetype(BOLD if bold else REG, max(1, round(pt * 4 / 3)))
    return fcache[k]


def hexrgb(c):
    return tuple(int(str(c)[i:i + 2], 16) for i in (0, 2, 4))


for sh in s.shapes:
    x, y = sh.left / EMU, sh.top / EMU
    w, h = sh.width / EMU, sh.height / EMU
    if sh.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
        try:
            rgb = hexrgb(sh.fill.fore_color.rgb)
        except Exception:
            continue
        if "OVAL" in str(sh.auto_shape_type):
            d.ellipse([x, y, x + w, y + h], fill=rgb)
        else:
            d.rectangle([x, y, x + w, y + h], fill=rgb)
    elif sh.shape_type == MSO_SHAPE_TYPE.TEXT_BOX:
        cy = y
        for p in sh.text_frame.paragraphs:
            runs = [r for r in p.runs if r.text]
            if not runs:
                continue
            size = max((r.font.size.pt if r.font.size else 11) for r in runs)
            ls = p.line_spacing if isinstance(p.line_spacing, float) else 1.0
            widths = [fnt(r.font.size.pt if r.font.size else 11, bool(r.font.bold)).getlength(r.text)
                      for r in runs]
            tw = sum(widths)
            if str(p.alignment).startswith("CENTER"):
                cx = x + (w - tw) / 2
            elif str(p.alignment).startswith("RIGHT"):
                cx = x + w - tw
            else:
                cx = x
            for r, rw in zip(runs, widths):
                rgb = hexrgb(r.font.color.rgb) if r.font.color and r.font.color.rgb else (0, 0, 0)
                d.text((cx, cy), r.text,
                       font=fnt(r.font.size.pt if r.font.size else 11, bool(r.font.bold)),
                       fill=rgb)
                cx += rw
            cy += size * 4 / 3 * 1.2 * ls

img.save("page1_render.png")
small = img.resize((820, 461), Image.LANCZOS)
small.save("page1_render.jpg", quality=42, optimize=True)
import os
print(os.path.getsize("page1_render.jpg"))
