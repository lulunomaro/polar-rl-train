"""Side-by-side: SJTU RM2025 open-source doc figures vs our MuJoCo plant."""
import os, numpy as np
from PIL import Image, ImageDraw
ROOT = r"D:\claude2\fangzhen"
A = os.path.join(ROOT, "docs", "audit")
S = os.path.join(ROOT, "docs", "sjtu")
W = 900
def crop_frac(path, box, w):
    im = Image.open(path).convert("RGB")
    x0, y0 = int(im.width * box[0]), int(im.height * box[1])
    x1, y1 = int(im.width * box[2]), int(im.height * box[3])
    c = im.crop((x0, y0, x1, y1))
    return c.resize((w, max(1, int(c.height * w / c.width))), Image.LANCZOS)
def load(path, w):
    im = Image.open(path).convert("RGB")
    return im.resize((w, max(1, int(im.height * w / im.width))), Image.LANCZOS)
def caption(im, txt, h=40):
    out = Image.new("RGB", (im.width, im.height + h), (16, 18, 22))
    out.paste(im, (0, h))
    d = ImageDraw.Draw(out)
    for i, line in enumerate([txt[:96], txt[96:]]):
        if line:
            d.text((10, 6 + i * 16), line, fill=(238, 241, 245))
    return out
ROWS = [
    (crop_frac(os.path.join(S, "pg09.png"), (0.50, 0.02, 1.00, 0.44), W),
     "REFERENCE  |  SJTU RM2025 serial-leg doc, p.9: 串联腿平衡底盘腿部整体结构示意图",
     load(os.path.join(A, "hero_F_leg_closeup.png"), W),
     "OURS (fixed)  |  same similar-link closed chain: hip crank + four-bar + thigh/shank + "
     "chain sprockets + nitrogen spring, rendered from the STEP"),
    (crop_frac(os.path.join(S, "pg14.png"), (0.05, 0.38, 0.99, 0.82), W),
     "REFERENCE  |  SJTU doc p.14: 车体框架 - hip machined parts on both sides of the frame, "
     "gimbal above",
     load(os.path.join(A, "hero_A_side_left.png"), W),
     "OURS (fixed)  |  733/733 CAD solids now rendered: armour plates, 4x DM-J8009 hip motors, "
     "slip rings, gas springs, guide wheels"),
]
tiles = []
for ref, rcap, ours, ocur in ROWS:
    ai = np.asarray(caption(ref, rcap)); bi = np.asarray(caption(ours, ocur))
    h = min(ai.shape[0], bi.shape[0], 760)
    tiles.append(np.concatenate([ai[:h], np.full((h, 10, 3), 8, dtype=np.uint8), bi[:h]], 1))
grid = np.concatenate(tiles, 0)
out = os.path.join(A, "compare_sjtu.png")
Image.fromarray(grid).save(out)
print("wrote", out, grid.shape)
