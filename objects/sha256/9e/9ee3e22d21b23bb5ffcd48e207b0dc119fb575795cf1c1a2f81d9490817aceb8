"""Operator panel and local-only Isaac playback launcher."""
from pathlib import Path
import collections
import json
import os
import subprocess
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox

ROOT = Path(__file__).resolve().parent
ISAAC_PYTHON = Path(r'C:\Users\lulu\miniconda3\envs\env_isaaclab\python.exe')
PLAYER = ROOT/'isaac/mod4/play_local_isaac.py'


def atomic_json(path, data):
    temp = path.with_suffix('.partial')
    temp.write_text(json.dumps(data, indent=2), encoding='utf-8')
    for _ in range(20):
        try:os.replace(temp, path);return
        except PermissionError:time.sleep(.002)
    raise OSError('Unable to publish operator command; another reader locked the file')


class Control:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('MOD4 · model8725 · Isaac物理 / MuJoCo画面')
        self.window.geometry('590x690+50+70')
        self.window.configure(bg='#14202b')
        self.window.attributes('-topmost', True)
        self.command = dict(vx=0., paused=False, reset_id=0, quit=False)
        self.start = time.time()
        self.history = collections.deque(maxlen=180)
        self.held = None
        self.closing = False
        self.persist()
        self.status = tk.StringVar(value='正在启动 Isaac Lab，首次启动可能需要约一分钟…')
        self.detail = tk.StringVar(value='等待真实回放数据')
        self.motion = tk.StringVar(value='停车 · 指令 0.00 m/s')
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#14202b')
        style.configure('TLabel', background='#14202b', foreground='#dde7ec', font=('Microsoft YaHei UI', 11))
        style.configure('TButton', font=('Microsoft YaHei UI', 11), padding=8)
        frame = ttk.Frame(self.window, padding=18)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text='MOD4 最新检查点：8725', font=('Microsoft YaHei UI', 17, 'bold')).pack(anchor='w')
        ttk.Label(frame, text='Isaac物理 · USD原几何 · MuJoCo显示 · 无扶正辅助').pack(anchor='w', pady=(4,12))
        ttk.Label(frame, textvariable=self.status, wraplength=550).pack(anchor='w')
        ttk.Label(frame, textvariable=self.motion, font=('Microsoft YaHei UI',14)).pack(anchor='w', pady=12)
        self.speed = tk.DoubleVar(value=.6)
        ttk.Label(frame, text='驾驶速度：0.1–1.5 m/s（先从 0.6 开始）').pack(anchor='w')
        self.speed_label = ttk.Label(frame, text='0.60 m/s')
        self.speed_label.pack(anchor='w')
        ttk.Scale(frame, from_=.1, to=1.5, variable=self.speed,
                  command=lambda value:self.speed_label.configure(text=f'{float(value):.2f} m/s')).pack(fill='x')
        row = ttk.Frame(frame);row.pack(fill='x', pady=12)
        for text, callback in [('前进 W',lambda:self.drive(1)),('停车 X',self.stop),('后退 S',lambda:self.drive(-1))]:
            ttk.Button(row, text=text, command=callback).pack(side='left', expand=True, fill='x', padx=3)
        row = ttk.Frame(frame);row.pack(fill='x')
        ttk.Button(row, text='复位 R', command=self.reset).pack(side='left', expand=True, fill='x', padx=3)
        self.pause_button = ttk.Button(row, text='暂停 P', command=self.pause)
        self.pause_button.pack(side='left', expand=True, fill='x', padx=3)
        ttk.Label(frame, text='点击本控制窗后，按住 W/S 驾驶，松开停车。\n按钮驾驶持续生效；X 停车，R 复位，P 暂停。\n在仿真窗口拖动鼠标查看；驾驶键只作用于本控制窗。',
                  wraplength=550).pack(anchor='w', pady=12)
        ttk.Label(frame, textvariable=self.detail, font=('Consolas',12), justify='left').pack(anchor='w', pady=4)
        ttk.Label(frame, text='实时速度曲线：青色实际速度 / 黄色指令速度').pack(anchor='w', pady=(10,3))
        self.canvas = tk.Canvas(frame, width=545, height=108, bg='#0c141d', highlightthickness=0)
        self.canvas.pack(fill='x')
        ttk.Button(frame, text='打开日志目录', command=lambda:os.startfile(str(ROOT))).pack(anchor='w', pady=12)
        for key in ['w','s']:
            self.window.bind(f'<KeyPress-{key}>', self.key_down)
            self.window.bind(f'<KeyRelease-{key}>', self.key_up)
        for key, callback in [('x',self.stop),('r',self.reset),('p',self.pause)]:
            self.window.bind(f'<KeyPress-{key}>',lambda event, fn=callback:fn())
        self.window.bind('<space>',lambda event:self.stop())
        self.window.bind('<FocusOut>',lambda event:self.stop_if_held())
        self.window.protocol('WM_DELETE_WINDOW',self.close)
        env = os.environ.copy();env['PYTHONUTF8']='1'
        self.log = (ROOT/'isaac_interactive.log').open('w', encoding='utf-8')
        flags = subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
        # Single-robot CPU physics avoids GPU round trips. MuJoCo displays actual USD poses.
        self.process = subprocess.Popen([str(ISAAC_PYTHON),str(PLAYER),'--profile','interactive','--device','cpu',
                                         '--headless'],
                                        cwd=str(ROOT), env=env, stdout=self.log, stderr=subprocess.STDOUT,
                                        creationflags=flags)
        self.display_log=(ROOT/'mujoco_display.log').open('w',encoding='utf8')
        self.display_process=subprocess.Popen([sys.executable,str(ROOT/'view_live_isaac.py'),'--since',str(self.start)],
                                             cwd=str(ROOT),env=env,stdout=self.display_log,stderr=subprocess.STDOUT,
                                             creationflags=flags)
        atomic_json(ROOT/'local_playback_process.json', {'pid':self.process.pid,'started_epoch':self.start,
                    'display_pid':self.display_process.pid,'checkpoint':'model_8725.pt',
                    'engine':'Isaac Sim5.1 PhysX / MuJoCo live USD pose display'})
        self.window.after(200,self.update)

    def persist(self):
        self.command['updated_epoch']=time.time()
        atomic_json(ROOT/'operator_command.json',self.command)

    def drive(self, direction):
        self.command['vx']=direction*round(self.speed.get(),2)
        self.command['paused']=False
        self.pause_button.configure(text='暂停 P')
        self.persist()
        self.motion.set(f'{"前进" if direction>0 else "后退"} · 目标 {self.command["vx"]:+.2f} m/s')

    def stop(self):
        self.held=None;self.command['vx']=0.;self.persist();self.motion.set('停车 · 指令 0.00 m/s')

    def reset(self):
        self.stop();self.command['reset_id']+=1;self.command['paused']=False;self.persist()
        self.pause_button.configure(text='暂停 P')

    def pause(self):
        self.command['paused']=not self.command['paused'];self.persist()
        self.pause_button.configure(text='继续 P' if self.command['paused'] else '暂停 P')

    def key_down(self, event):
        self.held=event.keysym.lower();self.drive(1 if self.held=='w' else -1)

    def key_up(self, event):
        if self.held==event.keysym.lower():self.stop()

    def stop_if_held(self):
        if self.held:self.stop()

    def update(self):
        if self.closing:return
        try:
            data=json.loads((ROOT/'isaac_telemetry.json').read_text(encoding='utf-8'))
            if data.get('updated_epoch',0)>self.start:
                age=time.time()-data['updated_epoch']
                if data.get('fault'):
                    self.status.set('已保留故障姿态：'+data['fault']+'；按 R 复位')
                elif age>3:
                    self.status.set(f'数据 {age:.0f} 秒未更新；暂停时属于正常现象')
                else:self.status.set('本机实时回放 · '+('暂停' if self.command['paused'] else '运行中'))
                self.detail.set(f'实际速度  {data["actual_vx"]:+.3f} m/s    指令 {data["command_vx"]:+.3f}\n'
                                f'根部车高  {data["height_m"]*1000:.1f} mm     倾斜 {data["tilt_deg"]:.2f}°\n'
                                f'闭链残差  {data["closure_mm"]:.3f} mm    耦合 {data["mimic_rad"]:.5f} rad\n'
                                f'轮载荷    左 {data.get("left_wheel_load_n",0):.1f} / 右 {data.get("right_wheel_load_n",0):.1f} N\n'
                                f'仿真时间  {data["sim_time_s"]:.2f} s    实时倍率 {data.get("realtime_ratio",0):.2f}x')
                self.history.append((data['command_vx'],data['actual_vx']))
                self.draw()
        except (OSError,ValueError,KeyError):pass
        if self.process.poll() is not None:
            self.status.set('回放进程已退出；详细原因见 isaac_interactive.log')
        elif self.display_process.poll() is not None:
            self.status.set('画面窗口已关闭；关闭控制窗可停止本机回放')
        self.window.after(200,self.update)

    def draw(self):
        self.canvas.delete('all');width=max(100,self.canvas.winfo_width());height=108
        self.canvas.create_line(0,height/2,width,height/2,fill='#394656')
        for index,color in [(0,'#eed46a'),(1,'#49d8df')]:
            points=[]
            for n,row in enumerate(self.history):
                points.extend([n*width/179,height/2-max(-1.8,min(1.8,row[index]))*height/4])
            if len(points)>=4:self.canvas.create_line(*points,fill=color,width=2)

    def close(self):
        self.closing=True;self.command.update(vx=0.,quit=True);self.persist()
        self.window.destroy()
        try:self.process.wait(timeout=20)
        except subprocess.TimeoutExpired:self.process.terminate()
        try:self.display_process.wait(timeout=5)
        except subprocess.TimeoutExpired:self.display_process.terminate()
        self.log.close();self.display_log.close()


if __name__=='__main__':
    import ctypes
    existing=ctypes.windll.user32.FindWindowW(None,'MOD4 · model8725 · Isaac物理 / MuJoCo画面')
    if existing:
        ctypes.windll.user32.ShowWindow(existing,9)
        ctypes.windll.user32.SetForegroundWindow(existing)
        raise SystemExit
    import msvcrt
    panel_lock=(ROOT/'.panel.lock').open('a+b')
    if panel_lock.tell()==0:panel_lock.write(b'1');panel_lock.flush()
    panel_lock.seek(0)
    try:msvcrt.locking(panel_lock.fileno(),msvcrt.LK_NBLCK,1)
    except OSError:
        prompt=tk.Tk();prompt.withdraw()
        messagebox.showinfo('MOD4','驾驶窗口已经打开，请使用现有控制窗。')
        prompt.destroy();raise SystemExit
    if not ISAAC_PYTHON.is_file():raise SystemExit('Isaac Python 不存在：'+str(ISAAC_PYTHON))
    operator=Control();operator.window.mainloop()
