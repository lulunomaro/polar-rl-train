"""Manual WASD controller for the R4 MuJoCo arena."""
from argparse import ArgumentParser
import json
from pathlib import Path
import time

import numpy as np
import torch

from jump360_r3_policy import R3Control, load_policy
from jump360_scene import COMMAND_DT, HERE, json_save, mujoco, sha
from jump380_r4_evaluate import trial_from
from jump380_r4_replay import run_trial
from jump380_r4_scene import KINDS, RUN, Jump380Plant

LABELS = ("平地", "380 mm 实体台面", "360 mm 实体台面", "380 mm 实体高栏")


def play(policy, checkpoint, starting_scene, examples):
    import tkinter as tk
    from tkinter import ttk
    from PIL import Image, ImageTk

    plant = Jump380Plant(visual=True)
    renderer = mujoco.Renderer(plant.m, width=896, height=504)
    camera = mujoco.MjvCamera()
    camera.distance, camera.elevation, camera.azimuth = 2.8, -13., 113.
    view = mujoco.MjvOption()
    view.geomgroup[3] = 0

    root = tk.Tk()
    root.title(f"MOD4v3 R4 跑动跳 · {sha(checkpoint)[:8]}")
    panel = ttk.Frame(root, padding=10)
    panel.grid()
    display = ttk.Label(panel)
    display.grid(row=0, columnspan=2)
    keys = set()
    speed, stance = tk.DoubleVar(), tk.DoubleVar()
    scene = tk.StringVar(value=starting_scene)
    status, operating_hint = tk.StringVar(), tk.StringVar()
    speed_label, height_label = tk.StringVar(), tk.StringVar()
    vx = yaw_rate = accumulator = 0.

    def reset(change_scene=False):
        nonlocal vx, yaw_rate, accumulator
        kind = scene.get()
        example = examples.get(kind, {})
        if change_scene:
            speed.set(example.get("speed", 1.4))
            stance.set(example.get("height", .32))
        seed = example.get("seed", 0)
        rng = np.random.default_rng(seed)
        y, yaw = rng.uniform(-.012, .012), rng.uniform(-.010, .010)
        plant.rng = np.random.default_rng(seed + 94887)
        plant.setup(stance.get(), example.get("dr", 0.), (0., float(y), float(yaw)))
        plant.wall(kind, example.get("wall_at") or 3.3)
        policy.reset_history()
        keys.clear()
        vx = yaw_rate = accumulator = 0.
        cue = example.get("front_gap_on_press_m")
        duration = example.get("hold_ticks", 38)*COMMAND_DT
        if cue is not None and example.get("obstacle_pass_physical"):
            operating_hint.set(f"复现参考  车头距墙 {cue:.2f} m 时按键约 {duration:.2f} s")
        else:
            operating_hint.set("")
        root.focus_set()

    scenes = ttk.Frame(panel)
    scenes.grid(row=1, column=0, sticky="w", pady=(8, 3))
    for kind, label in zip(KINDS, LABELS):
        ttk.Radiobutton(scenes, text=label, value=kind, variable=scene,
                        command=lambda: reset(True)).pack(side="left")
    ttk.Button(panel, text="复位 R", command=reset, takefocus=False).grid(row=1, column=1, sticky="e")

    sliders = ttk.Frame(panel)
    sliders.grid(row=2, columnspan=2, sticky="ew", pady=3)
    ttk.Label(sliders, textvariable=speed_label, width=20).grid(row=0, column=0)
    ttk.Scale(sliders, from_=.8, to=2., variable=speed, length=245, takefocus=False).grid(row=0, column=1)
    ttk.Label(sliders, textvariable=height_label, width=20).grid(row=0, column=2)
    ttk.Scale(sliders, from_=.24, to=.42, variable=stance, length=210, takefocus=False).grid(row=0, column=3)
    ttk.Label(panel, text="W/S 前后行驶    A/D 转向    Space/J 跳跃").grid(row=3, columnspan=2, sticky="w")
    ttk.Label(panel, textvariable=operating_hint).grid(row=4, columnspan=2, sticky="w")
    ttk.Label(panel, textvariable=status).grid(row=5, columnspan=2, sticky="w")

    def press(event):
        name = event.keysym.lower()
        if name == "r" and name not in keys:
            reset()
        keys.add(name)

    root.bind("<KeyPress>", press)
    root.bind("<KeyRelease>", lambda event: keys.discard(event.keysym.lower()))
    root.bind("<FocusOut>", lambda _: keys.clear())
    reset(True)
    previous, last_draw = time.perf_counter(), 0.

    def tick():
        nonlocal previous, last_draw, accumulator, vx, yaw_rate
        now = time.perf_counter()
        accumulator += min(.10, now - previous)
        previous = now
        for _ in range(int(accumulator / COMMAND_DT)):
            accumulator -= COMMAND_DT
            if plant.tilt_fault:
                break
            target = float(("w" in keys) - ("s" in keys))*speed.get()
            turn = float(("a" in keys) - ("d" in keys))*1.35
            vx += (target - vx)/12.
            yaw_rate += (turn - yaw_rate)/12.
            key = "space" in keys or "j" in keys
            obs = plant.command(vx, stance.get(), key, yaw_rate)
            plant.advance(policy(plant, obs))
        if now - last_draw >= .038:
            last_draw = now
            camera.lookat[:] = [plant.d.qpos[0] + .27, 0., .32]
            renderer.update_scene(plant.d, camera, scene_option=view)
            frame = plant.frame()
            if plant.tilt_fault:
                status.set("已失稳 · 按 R 复位")
            else:
                gap = f"   车头距墙 {plant.wall_edge - frame.max_x:+.2f} m" if scene.get() != "flat" else ""
                status.set(f"实际速度 {frame.vx:+.2f} m/s{gap}")
            speed_label.set(f"速度命令 {speed.get():.2f} m/s")
            height_label.set(f"站高命令 {stance.get():.3f} m")
            photo = ImageTk.PhotoImage(Image.fromarray(renderer.render()))
            display.configure(image=photo)
            display.image = photo
        root.after(5, tick)

    root.after(5, tick)
    try:
        root.mainloop()
    finally:
        renderer.close()


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--scene", choices=KINDS, default="platform_380")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    torch.set_num_threads(1)
    config = json.loads((RUN/"EXPERIENCE.json").read_text(encoding="utf-8"))
    checkpoint = HERE/Path(config["checkpoint"])
    checksum = sha(checkpoint)
    if checksum != config["sha256"]:
        raise ValueError("R4 WASD checkpoint SHA-256 mismatch")
    actor = R3Control(load_policy(checkpoint))
    if args.smoke:
        if args.scene not in config["examples"]:
            parser.error("Select a scene with a recorded smoke replay")
        example = config["examples"][args.scene]
        row, _ = run_trial(Jump380Plant(), actor, trial_from(example))
        if row["key_observed_ticks"] != example["hold_ticks"]:
            raise RuntimeError("WASD jump key did not reach obs[30] for the expected duration")
        if row["qualified"] != example["qualified"] or row["strict_direct"] != example["strict_direct"]:
            raise RuntimeError("WASD checkpoint replay disagrees with its recorded result")
        json_save(RUN/f"PLAYER_{args.scene.upper()}.json", dict(checkpoint_sha256=checksum, case=row))
        print(f"R4 WASD {checksum[:8]}  {args.scene}  obs[30] {row['key_observed_ticks']} ticks  "
              f"peak {row['flight_peak_all_m']:.4f} m  strict {row['strict_direct'] or row['qualified']}")
        return
    play(actor, checkpoint, args.scene, config["examples"])


if __name__ == "__main__":
    main()
