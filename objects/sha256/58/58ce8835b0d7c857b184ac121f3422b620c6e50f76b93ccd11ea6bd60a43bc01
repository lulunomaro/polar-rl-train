# -*- coding: utf-8 -*-
"""Pull labelled still frames out of rendered skill videos and tile them into one
contact sheet, so the demos can be inspected without a player.

  python scripts/vid_stills.py docs/videos/a.mp4 docs/videos/b.mp4 --out docs/crops/fig_F.png
"""
import argparse
import os

import imageio.v2 as iio
import numpy as np
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument("videos", nargs="+")
ap.add_argument("--out", default=r"D:/claude2/fangzhen/docs/crops/fig_F_video_stills.png")
ap.add_argument("--per-video", type=int, default=3)
ap.add_argument("--scale", type=float, default=0.62)
a = ap.parse_args()

tiles = []
for vp in a.videos:
    rdr = iio.get_reader(vp)
    n = rdr.count_frames()
    idxs = [int(round(f)) for f in np.linspace(0.10, 0.93, a.per_video) * (n - 1)]
    for i in idxs:
        fr = np.asarray(rdr.get_data(i))
        im = Image.fromarray(fr)
        im = im.resize((int(im.width * a.scale), int(im.height * a.scale)))
        dr = ImageDraw.Draw(im)
        dr.rectangle([0, 0, im.width, 16], fill=(20, 20, 20))
        dr.text((5, 2), "%s  frame %d/%d" % (os.path.basename(vp), i, n), fill=(255, 255, 255))
        tiles.append(im)
    rdr.close()

cols = 3
rows = (len(tiles) + cols - 1) // cols
w = max(t.width for t in tiles)
h = max(t.height for t in tiles)
sheet = Image.new("RGB", (cols * w + 10, rows * h + 10), (18, 18, 18))
for i, t in enumerate(tiles):
    sheet.paste(t, (5 + (i % cols) * w, 5 + (i // cols) * h))
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
sheet.save(a.out)
print("wrote", a.out, sheet.size, "tiles:", len(tiles))
