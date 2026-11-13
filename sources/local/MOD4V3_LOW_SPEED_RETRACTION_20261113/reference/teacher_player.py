"""Interactive frozen stair teacher; original controls and validated 100/400 Hz drive."""
from pathlib import Path
import hashlib, importlib.util, json, math, sys, time, traceback, types
import numpy as np
import torch
import mujoco

HERE = Path(__file__).resolve().parent
T = HERE.parent
R = T.parents[2]
D = R / "deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112"
OUT = HERE / "runtime/teacher_715c"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "tiles").mkdir(exist_ok=True)
MODEL = T / "weights/selected_stair_teacher.pt"
SHA = "715c40b6bd18c51d050d0bae38c0d04008f3841cc4a40ddca980a9cd52623ff5"
assert hashlib.sha256(MODEL.read_bytes()).hexdigest() == SHA
sys.path.insert(0, str(HERE))
from replay_training_guards import replay_step

torch.set_num_threads(1)
spec = importlib.util.spec_from_file_location("showcase", D / "viewer/showcase.py")
show = importlib.util.module_from_spec(spec)
sys.modules["showcase"] = show
spec.loader.exec_module(show)
show.CKPT, show.EXPECTED, show.B = MODEL, SHA, OUT

def tiledata(level, family):
    name = f"r{level:02d}_c{show.COLS[family]:02d}"
    with np.load(D / "viewer/tiles" / (name + ".npz")) as source:
        vertices, faces = source["vertices"].copy(), source["faces"].copy()
    if family in (show.FAMILIES[0], show.FAMILIES[4]) and level == 3:
        vertices[:, 2] *= .2 / float(np.unique(vertices[:, 2])[1])
        name += "_200mm"
    dest = OUT / "tiles" / (name + ".npz")
    if not dest.exists():
        np.savez_compressed(dest, vertices=vertices, faces=faces)
    return name, vertices, faces
show.tiledata = tiledata
original_scene = show.make_scene

def scene(level, family):
    path, vertices, heightfield = original_scene(level, family)
    import xml.etree.ElementTree as ET
    tree = ET.parse(path)
    tree.getroot().set("model", "MOD4 stair teacher 715c - two 200mm steps")
    tree.write(path, encoding="utf8", xml_declaration=True)
    return path, vertices, heightfield
show.make_scene = scene
OriginalReplay = show.Replay

class TeacherReplay(OriginalReplay):
    def __init__(self, level=3, family=None, direction="up", show=True):
        self.start_angle = 0.
        self.demo = False
        self.demo_result = ""
        self.demo_hold = 0.
        super().__init__(level=level, family=family or globals()["show"].FAMILIES[0], direction=direction, show=show)
        owner = self
        def physics(env, act):
            act = act.clamp(-env.action_clip, env.action_clip)
            for j in range(env.decim):
                tau = env._torque(act).detach().cpu().numpy().reshape(-1)
                if j % 4 == 0:
                    env.d.ctrl[env.act_ids[:4]] = tau[:4]
                env.d.ctrl[env.act_ids[4:]] = tau[4:]
                mujoco.mj_step(env.m, env.d)
                if not np.isfinite(env.d.qpos).all() or not np.isfinite(env.d.qvel).all():
                    raise globals()["show"].SafetyStop("nonfinite")
                owner.closure = max(float(np.linalg.norm(env.d.site_xpos[u] - env.d.site_xpos[v])) for u, v in owner.pairs)
                if owner.closure > .002:
                    raise globals()["show"].SafetyStop("closure>2mm")
            env.a_prev = act.detach().to(env.device)
            return env.state()
        self.env.step = types.MethodType(physics, self.env)
        self.args.vx, self.args.wz = 2.2, math.pi
        self.set_height(.42)
        self.paused = True
        self.wheel_ids = [self.env.m.body(n).id for n in ("left_wheel_link", "right_wheel_link")]

    def reset_standing(self):
        super().reset_standing()
        yaw = math.radians(self.start_angle)
        if self.direction == "up":
            x = -3.9
            y = (x + 1.1) * math.tan(yaw)
            self.env.d.qpos[:3] = [x, y, self.ground(x, y) + self.env.bank_z]
            self.env.d.qpos[3:7] = [math.cos(yaw/2), 0., 0., math.sin(yaw/2)]
            self.env.d.qvel[:] = 0.
            mujoco.mj_forward(self.env.m, self.env.d)
        self._repair_contact_steps = self._replay_tilt_steps = self._repair_stair_stage = 0
        self.demo_hold = 0.

    advance = replay_step(show.Simulation, show.SafetyStop, duration_steps=10, event_dir=OUT / "reset_events")

    def step(self, pressed):
        if self.paused:
            return self.telemetry()
        demo = self.demo
        if demo:
            self.set_height(.28 + .14 * min(float(self.env.d.time)/2., 1.))
            pressed = {"w"} if self.env.d.time >= 3. else set()
        resets = self.reset_count
        result = self.advance(pressed)
        if demo:
            wheels = self.env.d.xpos[self.wheel_ids]
            on_top = bool((np.abs(wheels[:, 0]) < 1.4).all() and (np.abs(wheels[:, 1]) < 1.4).all() and (wheels[:, 2] > .3925).all())
            self.demo_hold = self.demo_hold + .02 if on_top else 0.
            if self.reset_count != resets:
                self.demo_result = "保护重置：" + self.reason
            elif self.demo_hold >= .3:
                self.demo_result = "已登上第二阶，暂停观察；R 复位 / P 手动继续"
            elif self.env.d.time >= 20.:
                self.demo_result = "演示时间结束，可复位重试"
            if self.demo_result:
                self.demo = False
                self.paused = True
                self.cmd_vx = self.cmd_vy = self.cmd_wz = 0.
                print("TEACHER_DEMO_END " + json.dumps(dict(result=self.demo_result, time=float(self.env.d.time), xyz=self.env.d.qpos[:3].tolist(), angle=self.start_angle, closure=self.closure), ensure_ascii=False), flush=True)
        return result
show.Replay = TeacherReplay
sys.path.insert(0, str(D / "viewer"))
import manual_control
import tkinter as tk
BaseControl = manual_control.ManualRoughControl

class TeacherControl(BaseControl):
    def _build(self):
        super()._build()
        self.root.title("MOD4 上台阶教师 715c | 200mm 连续两阶 · 可操控")
        self.root.geometry("535x825+20+30")
        outer = next(iter(self.root.winfo_children()))
        widgets = list(outer.winfo_children())
        widgets[0].configure(text="上台阶教师 · 连续两级 200 mm")
        map_button = widgets[-1]
        map_button.configure(text="演示连续两级台阶（键盘可接管）", command=self.start_demo)
        row = tk.Frame(outer, bg=self.BG)
        row.pack(fill="x", pady=4, before=map_button)
        for label, angle in [("正向起点", 0), ("斜向 −15°", -15), ("斜向 +15°", 15)]:
            tk.Button(row, text=label, command=lambda a=angle:self.set_angle(a), takefocus=False).pack(side="left", expand=True, fill="x", padx=2)

    def set_angle(self, angle):
        if self.sim.direction != "up" or self.sim.level != 3 or self.sim.family != show.FAMILIES[0]:
            self.family_var.set(manual_control.CN[0])
            self.level_var.set(3)
            self.load_scene("up")
        self.sim.start_angle = angle
        self.reset_scene()
        self._event(f"起点 {angle:+d}°，高度0.42m；按演示或 P 后手动驾驶")

    def reset_scene(self):
        self.sim.demo = False
        self.sim.demo_result = ""
        super().reset_scene()

    def start_demo(self):
        if self.sim.direction != "up" or self.sim.level != 3 or self.sim.family != show.FAMILIES[0]:
            self.set_angle(0)
        self.reset_scene()
        self.speed_var.set(2.2)
        self.sim.args.vx = 2.2
        self.sim.set_height(.28)
        self.sim.demo = True
        self.sim.paused = False
        self._event("演示：2秒升高、3秒后前进；WASD/空格可手动接管")

    def _handle_key_down(self, key):
        if self.sim.demo and key in {"w", "s", "a", "d", "j", "l", "q", "e", "space"}:
            self.sim.demo = False
            self.keys.clear()
            self._event("已切换手动控制")
        super()._handle_key_down(key)

    def _stop(self):
        self.sim.demo = False
        super()._stop()

    def _is_control_foreground(self):
        return bool(self.sim.demo or super()._is_control_foreground())

    def _update_ui(self):
        super()._update_ui()
        if self.sim.demo_result:
            self.status_var.set(self.status_var.get() + "\n" + self.sim.demo_result)
        elif self.sim.demo:
            self.status_var.set(self.status_var.get() + "\n正在演示连续上两阶，键盘可接管")
manual_control.ManualRoughControl = TeacherControl

if __name__ == "__main__":
    try:
        print("TEACHER_PLAYER_START " + json.dumps(dict(model=str(MODEL), sha256=SHA, iteration=25432, stair_height_m=.2, stair_count=2, physics_s=.0025, legs_hz=100, wheels_hz=400, policy_hz=50, manual=True, initial_paused=True)), flush=True)
        root = tk.Tk()
        sim = TeacherReplay(show=True)
        app = TeacherControl(root, sim)
        root.after(200, app._focus_control)
        if "--demo" in sys.argv:
            root.after(1500, app.start_demo)
        print("TEACHER_PLAYER_READY", flush=True)
        root.mainloop()
    except Exception:
        (OUT / "ERROR.log").write_text(traceback.format_exc(), encoding="utf8")
        raise
