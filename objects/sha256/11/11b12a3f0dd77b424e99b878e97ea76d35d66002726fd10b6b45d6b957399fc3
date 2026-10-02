"""Independent driver panel for ONNX/MuJoCo and an authorized Isaac playback bundle."""
from __future__ import annotations

import argparse
import collections
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import time
import tkinter as tk
from tkinter import messagebox, ttk
import uuid

from playback_ipc import SessionLock, atomic_json, initial_command, read_json

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / '.playback'


def require_file(path):
    if path is None or not path.is_file():
        raise ValueError(f'文件不存在：{path}')
    return path.resolve()


def resolve_bundle(bundle, checkpoint=None):
    """Require the local compatibility port and receipt; never guess a remote task."""
    bundle = bundle.resolve()
    for name in ('run_manifest.remote.json', 'DOWNLOAD_RECEIPT.json', 'src_snapshot/robot.usd',
                 'isaac/mod4/mod4_task.py', 'isaac/mod4/mod4_env.py'):
        require_file(bundle / name)
    receipt = read_json(bundle / 'DOWNLOAD_RECEIPT.json')
    files = receipt.get('files', {})
    for relative in ('run_manifest.remote.json', 'src_snapshot/robot.usd'):
        if not files.get(relative) or hashlib.sha256((bundle / relative).read_bytes()).hexdigest() != files[relative]:
            raise ValueError('训练 manifest / USD 与交付包 SHA256 清单不一致：' + relative)
    candidates = [bundle / name for name in files if name.endswith('.pt') and (bundle / name).is_file()]
    if checkpoint is None:
        if len(candidates) != 1:
            raise ValueError('交付包中需要明确选择检查点（--checkpoint）；不能猜测最新策略。')
        checkpoint = candidates[0]
    checkpoint = require_file(checkpoint)
    relative = checkpoint.relative_to(bundle).as_posix()
    expected = files.get(relative)
    if not expected or hashlib.sha256(checkpoint.read_bytes()).hexdigest() != expected:
        raise ValueError('检查点与交付包 SHA256 清单不一致。')
    return bundle, checkpoint


class Control:
    def __init__(self, args):
        self.args = args
        self.session = uuid.uuid4().hex
        self.directory = CACHE / self.session
        self.directory.mkdir(parents=True)
        self.command_path, self.telemetry_path = self.directory / 'command.json', self.directory / 'telemetry.json'
        self.command = initial_command(self.session)
        self.command['height'] = args.height
        self.processes, self.logs = [], []
        self.history = collections.deque(maxlen=180)
        self.held, self.releases = set(), {}
        self.closing, self.last_sample = False, None
        self.persist()
        if not atomic_json(CACHE / 'active_session.json', dict(session_id=self.session,
                          command_file=str(self.command_path), panel_pid=os.getpid())):
            raise OSError('无法登记本机回放会话')
        self.window = tk.Tk()
        self.window.title('MOD4 驾驶 · ' + args.engine)
        self.window.geometry('650x860' if args.engine=='isaac-live' and args.yaw_limit else '650x745')
        self.window.configure(bg='#14202b')
        self.status = tk.StringVar(value='正在启动本机回放…')
        self.detail = tk.StringVar(value='等待真实回放数据')
        self.motion = tk.StringVar(value='停车 · 指令 0.00 m/s')
        self.speed = tk.DoubleVar(value=.6)
        self.spin_speed = tk.DoubleVar(value=min(2.,args.yaw_limit))
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#14202b')
        style.configure('TLabel', background='#14202b', foreground='#dde7ec', font=('Microsoft YaHei UI', 11))
        style.configure('TButton', padding=8)
        frame = ttk.Frame(self.window, padding=18)
        frame.pack(fill='both', expand=True)
        policy_name = args.policy.name if args.engine == 'mujoco' else args.checkpoint.name
        ttk.Label(frame, text='MOD4 · ' + policy_name, font=('Microsoft YaHei UI', 17, 'bold')).pack(anchor='w')
        explanation = ('MuJoCo 物理 + ONNX · 航向辅助 ' + ('开' if args.yaw_assist else '关')
                       if args.engine == 'mujoco' else 'Isaac PhysX 物理 · USD 原几何 · MuJoCo 仅显示 · 无扶正辅助')
        ttk.Label(frame, text=explanation, wraplength=605).pack(anchor='w', pady=(4, 12))
        ttk.Label(frame, textvariable=self.status, wraplength=605).pack(anchor='w')
        ttk.Label(frame, textvariable=self.motion).pack(anchor='w', pady=10)
        self.speed_label = ttk.Label(frame, text='速度 0.60 m/s · 范围 0.1–1.5 m/s')
        self.speed_label.pack(anchor='w')
        ttk.Scale(frame, from_=.1, to=1.5, variable=self.speed, command=self.speed_changed).pack(fill='x')
        row = ttk.Frame(frame)
        row.pack(fill='x', pady=10)
        for label, callback in [('前进 W', lambda: self.drive(1)), ('停车 X', self.stop), ('后退 S', lambda: self.drive(-1))]:
            ttk.Button(row, text=label, command=callback).pack(side='left', fill='x', expand=True, padx=3)
        if args.engine=='isaac-live' and args.yaw_limit:
            self.spin_label=ttk.Label(frame,text='自转 2.00 rad/s · 19.1转/分钟')
            self.spin_label.pack(anchor='w')
            ttk.Scale(frame,from_=1.,to=args.yaw_limit,variable=self.spin_speed,command=self.spin_changed).pack(fill='x')
            spin_row=ttk.Frame(frame);spin_row.pack(fill='x',pady=(4,8))
            for label,sign in [('左自转 A',1),('右自转 D',-1)]:
                ttk.Button(spin_row,text=label,command=lambda s=sign:self.spin(s)).pack(side='left',fill='x',expand=True,padx=3)
        row = ttk.Frame(frame)
        row.pack(fill='x')
        ttk.Button(row, text='复位 R', command=self.reset).pack(side='left', fill='x', expand=True, padx=3)
        self.pause_button = ttk.Button(row, text='暂停 P', command=self.pause)
        self.pause_button.pack(side='left', fill='x', expand=True, padx=3)
        keys = 'W/S 按住驾驶，松开停车；按钮驾驶持续生效。\nX/空格停车，R 复位，P 暂停；鼠标在画面中拖动查看。'
        keys += ('\nA/D 按住转向；驾驶键只作用于本控制窗。' if args.engine == 'mujoco'
                 else '\nA/D 按住原地自转；按钮持续自转，X停车。走跑与自转分别操控。' if args.yaw_limit
                 else '\n当前策略仅接受前进/后退。')
        ttk.Label(frame, text=keys, wraplength=605).pack(anchor='w', pady=12)
        ttk.Label(frame, textvariable=self.detail, font=('Consolas', 11), justify='left').pack(anchor='w')
        ttk.Label(frame, text='速度曲线：青色实际 / 黄色指令（按新数据采样）').pack(anchor='w', pady=(12, 3))
        self.canvas = tk.Canvas(frame, height=110, bg='#0c141d', highlightthickness=0)
        self.canvas.pack(fill='x')
        ttk.Button(frame, text='打开本次回放日志', command=self.open_logs).pack(anchor='w', pady=10)
        self.window.bind('<KeyPress>', self.key_down)
        self.window.bind('<KeyRelease>', self.key_up)
        self.window.bind('<FocusOut>', lambda event: self.stop() if self.held else None)
        self.window.protocol('WM_DELETE_WINDOW', self.close)
        try:
            self.launch()
        except Exception:
            self.close()
            raise
        self.window.after(200, self.update)

    def persist(self):
        self.command['updated_epoch'] = time.time()
        if not atomic_json(self.command_path, self.command):
            raise OSError('操控文件被锁定，未能发布指令')

    def spawn(self, command, name, cwd=None):
        log = (self.directory / (name + '.log')).open('w', encoding='utf-8')
        self.logs.append(log)
        env = os.environ.copy()
        env['PYTHONUTF8'] = '1'
        process = subprocess.Popen(command, cwd=str(cwd or ROOT), env=env, stdout=log,
                                   stderr=subprocess.STDOUT,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        self.processes.append(process)
        return process

    def launch(self):
        common = ['--command-file', str(self.command_path), '--output', str(self.telemetry_path), '--session-id', self.session]
        if self.args.engine == 'mujoco':
            command = [sys.executable, str(ROOT / 'play_onnx_panel.py'), '--policy', str(self.args.policy),
                       '--model', str(self.args.model), '--spawn', self.args.spawn, '--yaw-assist', str(self.args.yaw_assist)] + common
            if self.args.runtime_config:
                command += ['--runtime-config', str(self.args.runtime_config)]
            self.worker = self.spawn(command, 'mujoco')
        else:
            self.spawn([sys.executable, str(ROOT / 'isaac_display_pipeline.py'), '--bundle', str(self.args.bundle),
                        '--command-file', str(self.command_path), '--telemetry', str(self.telemetry_path),
                        '--session-id', self.session], 'display')
            self.worker = self.spawn([str(self.args.isaac_python), str(ROOT / 'play_isaac_bridge.py'),
                                     '--bundle', str(self.args.bundle), '--checkpoint', str(self.args.checkpoint),
                                     '--headless', '--device', self.args.device] + common, 'isaac', self.args.bundle)

    def drive(self, direction):
        self.command.update(vx=direction * round(self.speed.get(), 2), paused=False)
        if self.args.engine=='isaac-live':
            self.command['wz']=0.
            self.held.difference_update({'a','d'})
        self.pause_button.configure(text='暂停 P')
        self.persist()
        self.motion.set(f'目标速度 {self.command["vx"]:+.2f} m/s · 0.6 m/s² 缓升/刹停')

    def speed_changed(self, value):
        self.speed_label.configure(text=f'速度 {float(value):.2f} m/s · 范围 0.1–1.5 m/s')
        if self.command['vx']:
            self.drive(1 if self.command['vx'] > 0 else -1)

    def spin(self,direction):
        self.command.update(vx=0.,wz=direction*round(self.spin_speed.get(),2),paused=False)
        self.held.difference_update({'w','s'})
        self.pause_button.configure(text='暂停 P')
        self.persist()
        self.motion.set(f'原地自转 {self.command["wz"]:+.2f} rad/s · 刹停后切换')

    def spin_changed(self,value):
        rate=float(value)
        self.spin_label.configure(text=f'自转 {rate:.2f} rad/s · {rate*60/(2*3.141592653589793):.1f}转/分钟')
        if self.command['wz']:self.spin(1 if self.command['wz']>0 else -1)

    def stop(self):
        self.held.clear()
        self.command['vx'] = self.command['wz'] = 0.
        self.persist()
        self.motion.set('停车 · 速度指令缓降至 0')

    def reset(self):
        self.stop()
        self.command.update(reset_id=self.command['reset_id'] + 1, paused=False)
        self.pause_button.configure(text='暂停 P')
        self.persist()

    def pause(self):
        self.stop()
        self.command['paused'] = not self.command['paused']
        self.pause_button.configure(text='继续 P' if self.command['paused'] else '暂停 P')
        self.persist()

    def key_down(self, event):
        key = event.keysym.lower()
        if key in self.releases:
            self.window.after_cancel(self.releases.pop(key))
        if key in self.held:
            return  # OS key repeat must not toggle pause/reset repeatedly
        if key in ('w', 's', 'a', 'd'):
            if key in ('a', 'd') and self.args.engine != 'mujoco' and not self.args.yaw_limit:
                return
            self.held.add(key)
            if key in ('w', 's'):
                self.drive(1 if key == 'w' else -1)
            else:
                if self.args.engine=='isaac-live':self.spin(1 if key=='a' else -1)
                else:
                    self.command['wz'] = 1. if key == 'a' else -1.
                    self.persist()
        elif key in ('x', 'space', 'r', 'p'):
            {'x': self.stop, 'space': self.stop, 'r': self.reset, 'p': self.pause}[key]()
            self.held.add(key)

    def key_up(self, event):
        key = event.keysym.lower()
        if key in self.releases:
            self.window.after_cancel(self.releases[key])
        # X11 auto-repeat emits release/press pairs; debounce a genuine release.
        self.releases[key] = self.window.after(25, lambda: self.release(key))

    def release(self, key):
        self.releases.pop(key, None)
        if key not in self.held:
            return
        self.held.discard(key)
        if key in ('w', 's'):
            self.command['vx'] = (.0 if not self.held.intersection({'w', 's'}) else
                                  round(self.speed.get(), 2) * (1 if 'w' in self.held else -1))
        elif key in ('a', 'd'):
            rate=self.spin_speed.get() if self.args.engine=='isaac-live' else 1.
            self.command['wz'] = 0. if not self.held.intersection({'a', 'd'}) else (rate if 'a' in self.held else -rate)
        self.persist()
        self.motion.set(f'目标速度 {self.command["vx"]:+.2f} m/s · 转向 {self.command["wz"]:+.1f} rad/s')

    def update(self):
        if self.closing:
            return
        if (self.directory / 'stop.request').exists():
            self.close()
            return
        try:
            self.persist()  # heartbeat; worker ramps to stop if the panel disappears
            data = read_json(self.telemetry_path)
            if data.get('session_id') == self.session:
                age = time.time() - data['updated_epoch']
                self.status.set(('故障冻结：' + data['fault'] + '；R 复位') if data.get('fault') else
                                f'数据 {age:.1f}s 未更新' if age > 3 else '暂停' if self.command['paused'] else '本机回放运行中')
                def number(key, scale=1, precision=3):
                    v = data.get(key)
                    return '—' if v is None else f'{v * scale:.{precision}f}'
                self.detail.set(f'实际 / 指令 {number("actual_vx")} / {number("command_vx")} m/s\n'
                                f'自转 实际 / 指令 {number("actual_wz")} / {number("command_wz")} rad/s  {number("actual_rpm", precision=1)} rpm\n'
                                f'根部高度 {number("height_m", 1000, 1)} mm  倾斜 {number("tilt_deg", precision=2)}°\n'
                                f'闭链 {number("closure_mm")} mm  耦合 {number("mimic_rad", precision=5)} rad\n'
                                f'瞬时轮载 左 {number("left_wheel_load_n", precision=1)} / 右 {number("right_wheel_load_n", precision=1)} N\n'
                                f'动作 delta / d2 {number("delta")} / {number("d2")}\n'
                                f'仿真 {number("sim_time_s", precision=2)} s  实时倍率 {number("realtime_ratio", precision=2)}x')
                if data['updated_epoch'] != self.last_sample and data.get('actual_vx') is not None:
                    self.last_sample = data['updated_epoch']
                    self.history.append((data['command_vx'], data['actual_vx']))
                    self.draw()
            if self.worker.poll() is not None:
                self.status.set(f'物理回放进程已退出（{self.worker.returncode}），请查看本次日志')
            elif any(p.poll() is not None for p in self.processes if p is not self.worker):
                self.status.set('显示窗口已关闭或启动失败；关闭控制窗停止本次物理回放')
        except (OSError, ValueError, KeyError, TypeError) as error:
            self.status.set(str(error))
        self.window.after(200, self.update)

    def draw(self):
        self.canvas.delete('all')
        width, height = max(100, self.canvas.winfo_width()), 110
        self.canvas.create_line(0, height / 2, width, height / 2, fill='#394656')
        for index, color in ((0, '#eed46a'), (1, '#49d8df')):
            points = [v for n, row in enumerate(self.history) for v in
                      (n * width / 179, height / 2 - max(-1.8, min(1.8, row[index])) * height / 4)]
            if len(points) >= 4:
                self.canvas.create_line(*points, fill=color, width=2)

    def open_logs(self):
        if os.name == 'nt':
            os.startfile(str(self.directory))
        else:
            subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', str(self.directory)])

    def close(self):
        if self.closing:
            return
        self.closing = True
        self.command.update(vx=0., wz=0., quit=True)
        try:
            self.persist()
        finally:
            self.window.destroy()
            for process in reversed(self.processes):
                try:
                    process.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    process.terminate()  # only this panel's own local subprocess
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
            for log in self.logs:
                log.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=('mujoco', 'isaac-live'), default='mujoco')
    parser.add_argument('--policy', type=Path)
    parser.add_argument('--model', type=Path, default=ROOT / 'model/rm_training_arena.xml')
    parser.add_argument('--runtime-config', type=Path)
    parser.add_argument('--spawn', choices=[f'f{i}' for i in range(1, 9)], default='f1')
    parser.add_argument('--height', type=float, default=.34)
    parser.add_argument('--yaw-assist', type=float, default=0.)
    parser.add_argument('--bundle', type=Path)
    parser.add_argument('--checkpoint', type=Path)
    parser.add_argument('--isaac-python', type=Path)
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--stop-session', action='store_true')
    args = parser.parse_args()
    args.yaw_limit=0.
    CACHE.mkdir(exist_ok=True)
    if args.stop_session:
        active = read_json(CACHE / 'active_session.json')
        if active:
            path = Path(active['command_file']).resolve()
            if not path.is_relative_to(CACHE.resolve()):
                raise ValueError('会话指令文件必须位于当前播放器缓存目录')
            command = read_json(path)
            if command.get('session_id') == active.get('session_id'):
                # A separate file prevents a heartbeat from overwriting a quit packet.
                (path.parent / 'stop.request').touch()
        return
    if not .178 <= args.height <= .34:
        raise ValueError('高度指令必须在 0.178–0.34 m 范围内')
    if args.engine == 'mujoco':
        args.policy, args.model = require_file(args.policy), require_file(args.model)
        if args.runtime_config:
            require_file(args.runtime_config)
    else:
        if args.bundle is None:
            raise ValueError('Isaac 回放需要 --bundle 本机兼容交付包')
        args.bundle, args.checkpoint = resolve_bundle(args.bundle, args.checkpoint)
        args.isaac_python = require_file(args.isaac_python)
        capabilities=read_json(args.bundle/'PLAYBACK_CAPABILITIES.json')
        if capabilities:
            expected=read_json(args.bundle/'DOWNLOAD_RECEIPT.json')['files'].get('PLAYBACK_CAPABILITIES.json')
            if hashlib.sha256((args.bundle/'PLAYBACK_CAPABILITIES.json').read_bytes()).hexdigest()!=expected:
                raise ValueError('自转能力文件与下载清单不一致')
            args.yaw_limit=float(capabilities.get('yaw_max_rad_s',0.))
            if not 1. <= args.yaw_limit <= 4*3.141592653589793:
                raise ValueError('自转指令范围无效')
    lock = SessionLock(CACHE / 'panel.lock')
    try:
        panel = Control(args)
        try:
            panel.window.mainloop()
        finally:
            panel.close()
    finally:
        lock.close()


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        prompt = tk.Tk()
        prompt.withdraw()
        messagebox.showerror('MOD4 回放启动失败', str(error))
        prompt.destroy()
        raise
