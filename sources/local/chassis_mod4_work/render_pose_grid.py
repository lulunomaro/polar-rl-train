"""Render a side-view grid to visually match a SolidWorks configuration."""
import sys
from pathlib import Path

import mujoco
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import simulate_folded_pose as sim

sim.model.jnt_limited[:] = 0
hips = [-1.4, -1.2, -1.0, -0.8, -0.6]
diffs = [-0.8, -0.5, -0.2, 0.1, 0.4]
width, height = 440, 300
renderer = mujoco.Renderer(sim.model, height=height, width=width)
sheet = Image.new("RGB", (width * len(diffs), height * len(hips)), (30, 30, 30))
draw = ImageDraw.Draw(sheet)
camera = mujoco.MjvCamera()
camera.type = mujoco.mjtCamera.mjCAMERA_FREE
camera.distance = 1.1
camera.azimuth = 90
camera.elevation = 0

for row, hip in enumerate(hips):
    for col, difference in enumerate(diffs):
        origin = (col * width, row * height)
        try:
            result = sim.set_pose(hip, difference, 0.0, 0.0)
            mujoco.mj_forward(sim.model, sim.data)
            camera.lookat[:] = sim.data.xpos[sim.CHASSIS]
            renderer.update_scene(sim.data, camera=camera)
            sheet.paste(Image.fromarray(renderer.render()), origin)
            label = "hip %+.1f diff %+.1f leg %.0fmm" % (
                hip, difference, result["leg_height_m"] * 1000
            )
            draw.text((origin[0] + 8, origin[1] + 8), label, fill=(255, 220, 50))
        except Exception as exc:
            draw.text((origin[0] + 8, origin[1] + 8), str(exc), fill=(255, 80, 80))

renderer.close()
output = sim.OUT / "pose_grid.png"
sheet.save(output)
print(output)
