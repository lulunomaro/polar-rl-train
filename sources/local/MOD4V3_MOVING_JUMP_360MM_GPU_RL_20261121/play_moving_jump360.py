"""WASD operating panel for the 360 mm moving-jump arena."""
from __future__ import annotations

from argparse import ArgumentParser
import json
from pathlib import Path
import time

import torch

from eval_moving_jump_360mm import MeasuredPlant, NeuralControl, Trial, replay_example, run_trial
from jump360_scene import COMMAND_DT, HERE, json_save, model_from, mujoco, sha


def selected_checkpoint(path):
    if path:
        return HERE / path
    data = json.loads((HERE/"CANDIDATE.json").read_text(encoding="utf-8"))
    chosen = HERE/data["file"]
    if sha(chosen) != data["sha256"]:
        raise ValueError("Candidate checkpoint SHA-256 mismatch")
    return chosen


def play(policy, starting_scene, checkpoint, example):
    import tkinter as tk
    from tkinter import ttk
    from PIL import Image, ImageTk

    plant = MeasuredPlant(visual=True)
    renderer = mujoco.Renderer(plant.m, width=896, height=504)
    camera = mujoco.MjvCamera()
    camera.distance, camera.elevation, camera.azimuth = 2.8, -13., 113.
    view = mujoco.MjvOption()
    view.geomgroup[3] = 0
    keys = set()
    root = tk.Tk()
    root.title(f"MOD4v3 跑动跳 • {sha(checkpoint)[:8]}")
    panel = ttk.Frame(root, padding=12)
    panel.grid(sticky="nsew")
    display = ttk.Label(panel)
    display.grid(row=0, columnspan=3)
    speed = tk.DoubleVar(value=example.get("speed", 1.4))
    stance = tk.DoubleVar(value=example.get("height", .32))
    scene = tk.StringVar(value=starting_scene)
    status = tk.StringVar()
    vx, yaw = 0., 0.

    def reset():
        nonlocal vx, yaw
        keys.clear()
        vx, yaw = 0., 0.
        plant.setup(stance.get())
        tested_edge = example.get("wall_at") if scene.get() == starting_scene else None
        plant.wall(scene.get(), tested_edge if tested_edge is not None else 3.3)
        policy.reset_history()
        root.focus_set()

    selector = ttk.Frame(panel)
    selector.grid(row=1, column=0, sticky="w", pady=(10, 3))
    for label, kind in (("平地", "flat"), ("360 mm 台面", "platform"), ("360 mm 高栏", "hurdle")):
        ttk.Radiobutton(selector, text=label, value=kind, variable=scene, command=reset).pack(side="left")
    ttk.Button(panel, text="复位 R", command=reset, takefocus=False).grid(row=1, column=2, sticky="e")
    sliders = ttk.Frame(panel)
    sliders.grid(row=2,columnspan=3,sticky="ew",pady=4)
    speed_label, height_label = tk.StringVar(), tk.StringVar()
    ttk.Label(sliders, textvariable=speed_label, width=20).grid(row=0, column=0)
    ttk.Scale(sliders, from_=.6,to=2.,variable=speed,length=270,takefocus=False).grid(row=0,column=1)
    ttk.Label(sliders, textvariable=height_label, width=22).grid(row=0,column=2)
    ttk.Scale(sliders, from_=.22,to=.42,variable=stance,length=220,takefocus=False).grid(row=0,column=3)
    ttk.Label(panel, text="W/S 前进与后退   A/D 转向   按住 Space 或 J 约 0.9 秒跳跃").grid(
        row=3, columnspan=3, sticky="w", pady=4)
    ttk.Label(panel, textvariable=status).grid(row=4,columnspan=3,sticky="w")

    def on_press(event):
        key = event.keysym.lower()
        if key == "r" and key not in keys:
            reset()
        keys.add(key)

    def on_release(event):
        keys.discard(event.keysym.lower())

    root.bind("<KeyPress>", on_press)
    root.bind("<KeyRelease>", on_release)
    root.bind("<FocusOut>", lambda _: keys.clear())
    reset()
    previous = time.perf_counter()
    accumulator = 0.
    last_draw = 0.

    def tick():
        nonlocal previous, accumulator, last_draw, vx, yaw
        now = time.perf_counter()
        accumulator += min(.10, now-previous)
        previous = now
        for _ in range(int(accumulator/COMMAND_DT)):
            accumulator -= COMMAND_DT
            target = float(("w" in keys)-("s" in keys))*speed.get()
            turn = float(("a" in keys)-("d" in keys))*1.35
            vx += (target-vx)/12.
            yaw += (turn-yaw)/12.
            jumping = bool({"space","j"}&keys)
            observation = plant.command(vx, stance.get(), jumping, yaw)
            plant.advance(policy(plant,observation))
            if plant.tilt_fault:
                break
        if now-last_draw >= .038:
            last_draw = now
            camera.lookat[:] = [plant.d.qpos[0]+.27, 0., .32]
            renderer.update_scene(plant.d, camera, scene_option=view)
            frame = plant.frame()
            if plant.tilt_fault:
                status.set("已失稳 · 按 R 复位")
            else:
                distance = f"   距墙 {plant.wall_edge-frame.max_x:+.2f} m" if scene.get()!="flat" else ""
                status.set(f"实际速度 {frame.vx:+.2f} m/s{distance}")
            speed_label.set(f"速度 {speed.get():.2f} m/s")
            height_label.set(f"站高 {stance.get():.3f} m")
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
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--scene", choices=("flat", "platform", "hurdle"), default="platform")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    torch.set_num_threads(1)
    checkpoint = selected_checkpoint(args.checkpoint)
    actor = NeuralControl(model_from(checkpoint))
    trial = Trial(101, 1.4, .32, 0., args.scene, .85)
    example = {}
    result_file = HERE/"JUMP360_RESULT.json"
    if result_file.is_file():
        result = json.loads(result_file.read_text(encoding="utf-8"))
        if result["sha256"] == sha(checkpoint):
            example = replay_example(result["trials"], args.scene)
        if example:
            trial = Trial(**{key:example[key] for key in vars(trial)})
    if args.smoke:
        plant = MeasuredPlant()
        record, _, obs, _ = run_trial(plant,actor,trial,collect_actions=True)
        on = int((obs[:,30]>.5).sum())
        json_save(HERE/f"evidence/PLAYER_SMOKE_{args.scene.upper()}.json",
                  dict(record=record, checkpoint_sha256=sha(checkpoint),
                  input_shape=list(obs.shape), key_high_ticks=on, key_released=bool(obs[-1,30]==0.)))
        if not on or not record["triggered"]:
            raise RuntimeError("Jump key did not reach observation 30")
        print(f"Player smoke | {sha(checkpoint)[:8]} | key-high ticks {on} | peak {record['flight_peak_all_m']:.4f} m")
        return
    play(actor, args.scene, checkpoint, example)


if __name__ == "__main__":
    main()
