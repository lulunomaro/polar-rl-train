"""Extract circular landmarks from the user's SolidWorks side screenshot.

This first stage only estimates guide-wheel and drive-wheel centres from image
edges. It keeps the supplied image read-only.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates, sobel


IMAGE = Path(r"C:\Users\lulu\AppData\Local\Temp\codex-clipboard-d7cecd84-1371-415b-9a05-8a5a28fc6cec.png")
OUT = Path(__file__).resolve().parent / "folded_pose_sim" / "solidworks_circle_fit.json"

gray = np.asarray(Image.open(IMAGE).convert("L"), dtype=float) / 255.0
gx = sobel(gray, axis=1)
gy = sobel(gray, axis=0)
mag = np.hypot(gx, gy)


def circle_score(cx: float, cy: float, radius: float, samples: int = 180) -> float:
    theta = np.linspace(0, 2 * math.pi, samples, endpoint=False)
    ct, st = np.cos(theta), np.sin(theta)
    xs = cx + radius * ct
    ys = cy + radius * st
    coords = np.vstack((ys, xs))
    edge = map_coordinates(mag, coords, order=1, mode="constant")
    sx = map_coordinates(gx, coords, order=1, mode="constant")
    sy = map_coordinates(gy, coords, order=1, mode="constant")
    radial = np.abs(sx * ct + sy * st)
    return float(np.mean(edge + 0.5 * radial))


def fit(box, radii, coarse=2):
    x0, x1, y0, y1 = box
    best = (-1.0, None)
    for cy in np.arange(y0, y1 + 1, coarse):
        for cx in np.arange(x0, x1 + 1, coarse):
            for radius in radii:
                score = circle_score(cx, cy, radius, 120)
                if score > best[0]:
                    best = (score, (float(cx), float(cy), float(radius)))
    _, (bcx, bcy, br) = best
    for cy in np.arange(bcy - 3, bcy + 3.01, 0.5):
        for cx in np.arange(bcx - 3, bcx + 3.01, 0.5):
            for radius in np.arange(br - 3, br + 3.01, 0.5):
                score = circle_score(cx, cy, radius, 360)
                if score > best[0]:
                    best = (score, (float(cx), float(cy), float(radius)))
    return {"score": best[0], "cx_px": best[1][0], "cy_px": best[1][1], "radius_px": best[1][2]}


result = {
    "image": str(IMAGE),
    "size_px": [int(gray.shape[1]), int(gray.shape[0])],
    "front_guide": fit((190, 245, 415, 465), np.arange(10, 27, 2)),
    "rear_guide": fit((920, 975, 415, 465), np.arange(10, 27, 2)),
    "drive_wheel": fit((555, 685, 385, 465), np.arange(52, 92, 2)),
}
front = result["front_guide"]
rear = result["rear_guide"]
drive = result["drive_wheel"]
scale_centres = abs(rear["cx_px"] - front["cx_px"]) / (2 * 0.259)
scale_radius = 0.5 * (front["radius_px"] + rear["radius_px"]) / 0.015
chassis_x_px = 0.5 * (front["cx_px"] + rear["cx_px"])
chassis_roller_y_px = 0.5 * (front["cy_px"] + rear["cy_px"])
result["derived"] = {
    "scale_from_guide_centres_px_per_m": scale_centres,
    "scale_from_guide_radius_px_per_m": scale_radius,
    "chassis_origin_x_px": chassis_x_px,
    "guide_centre_y_px": chassis_roller_y_px,
    "drive_centre_relative_m": [
        (drive["cx_px"] - chassis_x_px) / scale_centres,
        (chassis_roller_y_px - drive["cy_px"]) / scale_centres - 0.135,
    ],
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, indent=2), encoding="utf8")
print(json.dumps(result, indent=2))
