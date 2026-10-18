"""Local MuJoCo WASD driving. Only this application's focused windows accept keys."""
from pathlib import Path
import ctypes,json,math,os,threading,time,traceback
import tkinter as tk
from tkinter import ttk,messagebox
import mujoco,mujoco.viewer,numpy as np
from current_sim import CurrentSim

D=Path(__file__).resolve().parent
SPAWNS=[('平地 → 前方 RMUC2026 起伏路',-1.,0.,0.),('RM 起伏路入口 · 7 cm / 24 cm 间距',.3,0.,0.),('蓝色缓坡入口 · 高度 0–8 cm',.6,2.7,0.),('紫色轻度练习路 · 高度 0–2.5 cm',.3,-3.,0.)]
KEYS={key:ord(key) for key in 'WASDXRPF1234'};KEYS['SPACE']=32
def write_json(path,value):
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8');temp.replace(path)

class Driver:
    def __init__(self):
        self.root=tk.Tk();self.root.title('MOD4 最新检查点 · MuJoCo WASD');self.root.geometry('575x565+35+70')
        self.root.configure(bg='#15232d');self.quit=threading.Event();self.guard=threading.Lock()
        self.virtual=set();self.speed=.6;self.turn=1.8;self.requests=[];self.snapshot={};self.error=None
        self.status=tk.StringVar(value='正在打开 MuJoCo 窗口…');self.details=tk.StringVar(value='等待仿真数据')
        self.location=tk.StringVar(value=SPAWNS[0][0]);self.speedtext=tk.StringVar(value='速度 0.60 m/s')
        style=ttk.Style();style.theme_use('clam');style.configure('TFrame',background='#15232d');style.configure('TLabel',background='#15232d',foreground='#e2edf1',font=('Microsoft YaHei UI',11));style.configure('TButton',font=('Microsoft YaHei UI',11),padding=8)
        frame=ttk.Frame(self.root,padding=18);frame.pack(fill='both',expand=True)
        receipt=json.loads((D/'BUILD_RECEIPT.json').read_text())
        ttk.Label(frame,text='MOD4 · '+receipt['checkpoint'],font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
        ttk.Label(frame,text='MuJoCo 物理 · 100 Hz 策略 · 无扶正/航向辅助',wraplength=520).pack(anchor='w',pady=(6,10))
        ttk.Label(frame,text='点击本窗口或仿真窗口后，按住 WASD 操控，松手停车。\nW / S 前后走    A / D 左右转    空格 / X 停车\nR 复位    F 换路段    P 暂停    1 / 2 / 3 / 4 选择起点',wraplength=520).pack(anchor='w')
        ttk.Label(frame,textvariable=self.speedtext).pack(anchor='w',pady=(12,0))
        scale=ttk.Scale(frame,from_=.1,to=1.5,command=self.change_speed);scale.set(.6);scale.pack(fill='x')
        buttons=ttk.Frame(frame);buttons.pack(fill='x',pady=8)
        for text,key in [('前进 W','W'),('左转 A','A'),('后退 S','S'),('右转 D','D')]:
            button=ttk.Button(buttons,text=text);button.pack(side='left',fill='x',expand=True,padx=2)
            button.bind('<ButtonPress-1>',lambda e,k=key:self.press(k));button.bind('<ButtonRelease-1>',lambda e,k=key:self.release(k));button.bind('<Leave>',lambda e,k=key:self.release(k))
        row=ttk.Frame(frame);row.pack(fill='x')
        for text,action in [('停车', 'stop'),('复位 R','reset'),('换路段 F','spawn'),('暂停 P','pause')]:
            ttk.Button(row,text=text,command=lambda a=action:self.request(a)).pack(side='left',fill='x',expand=True,padx=2)
        ttk.Label(frame,textvariable=self.location,wraplength=520).pack(anchor='w',pady=(15,4))
        ttk.Label(frame,textvariable=self.status,wraplength=520).pack(anchor='w')
        ttk.Label(frame,textvariable=self.details,wraplength=520).pack(anchor='w',pady=(6,10))
        ttk.Label(frame,text='绿色：RMUC2026 V2.0 CAD 凸起，高 7 cm、间距 24 cm。\n紫色：原 2.5 cm 练习路。鼠标拖动视角，滚轮缩放。\n这是独立路段跨仿真试玩，未复刻整场 1.5°地板坡度。',wraplength=520,font=('Microsoft YaHei UI',9)).pack(anchor='w')
        self.root.protocol('WM_DELETE_WINDOW',self.close)
        self.root.bind('<FocusOut>',lambda e:self.clear_virtual())
        self.thread=threading.Thread(target=self.simulate,name='MOD4-MuJoCo',daemon=True);self.thread.start()
        self.root.after(100,self.refresh)
    def change_speed(self,value):
        with self.guard:self.speed=float(value)
        self.speedtext.set(f'速度 {float(value):.2f} m/s')
    def press(self,key):
        with self.guard:self.virtual.add(key)
    def release(self,key):
        with self.guard:self.virtual.discard(key)
    def clear_virtual(self):
        with self.guard:self.virtual.clear()
    def request(self,action):
        with self.guard:self.requests.append(action)
    def focused_keys(self):
        user32=ctypes.windll.user32;foreground=user32.GetForegroundWindow();pid=ctypes.c_ulong()
        user32.GetWindowThreadProcessId(foreground,ctypes.byref(pid))
        if pid.value!=os.getpid():return set(),False
        return {key for key,code in KEYS.items() if user32.GetAsyncKeyState(code)&0x8000},True
    def simulate(self):
        try:
            sim=CurrentSim();params=sim.parameter_readback();spawn=0;paused=False;fault=None;previous=set();blocked=False;current_v=0.;current_w=0.
            with mujoco.viewer.launch_passive(sim.model,sim.data,show_left_ui=False,show_right_ui=False) as viewer:
                viewer.cam.type=mujoco.mjtCamera.mjCAMERA_TRACKING;viewer.cam.trackbodyid=sim.chassis_id
                viewer.cam.distance=2.4;viewer.cam.azimuth=140;viewer.cam.elevation=-25
                write_json(D/'INTERACTIVE_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),checkpoint=sim.policy.path.name,viewer_running=viewer.is_running(),parameter_readback=params))
                nexttick=time.perf_counter();last_packet=0.;steps=0;begin=nexttick
                while not self.quit.is_set() and viewer.is_running():
                    keys,focused=self.focused_keys()
                    with self.guard:
                        keys|=self.virtual if focused else set();speed=self.speed;turn=self.turn;requests=self.requests[:];self.requests.clear()
                    pressed=keys-previous;previous=keys
                    if 'R' in pressed:requests.append('reset')
                    if 'F' in pressed:requests.append('spawn')
                    if 'P' in pressed:requests.append('pause')
                    if 'SPACE' in keys or 'X' in keys:requests.append('stop')
                    for key in ('1','2','3','4'):
                        if key in pressed:requests.append('spawn'+key)
                    for req in requests:
                        if req=='pause':paused=not paused
                        if req=='stop':blocked=True;current_v=current_w=0.;self.clear_virtual()
                        if req=='reset' or req.startswith('spawn'):
                            if req=='spawn':spawn=(spawn+1)%len(SPAWNS)
                            elif req.startswith('spawn') and len(req)>5:spawn=int(req[-1])-1
                            _,x,y,yaw=SPAWNS[spawn];sim.reset(x,y,yaw);fault=None;current_v=current_w=0.;blocked=True
                    if not keys.intersection('WASD'):blocked=False
                    target_v=(('W' in keys)-('S' in keys))*speed if focused and not blocked else 0.
                    target_w=(('A' in keys)-('D' in keys))*turn if focused and not blocked else 0.
                    current_v+=float(np.clip(target_v-current_v,-.008,.008));current_w+=float(np.clip(target_w-current_w,-.04,.04))
                    if not paused and fault is None:
                        sim.command.vx=current_v;sim.command.wz=current_w;sim.step_control();steps+=1
                        h=sim.health()
                        if h['upright_cos']<.60 or sim.base_position[2]<.12:fault='已倾倒，按 R 复位'
                    now=time.perf_counter()
                    if now-last_packet>.10:
                        velocity=np.zeros(6);mujoco.mj_objectVelocity(sim.model,sim.data,mujoco.mjtObj.mjOBJ_BODY,sim.chassis_id,velocity,1)
                        h=sim.health();packet=dict(epoch=time.time(),pid=os.getpid(),checkpoint=sim.policy.path.name,terrain=SPAWNS[spawn][0],paused=paused,fault=fault,focused=focused,command_vx=current_v,command_yaw=current_w,actual_vx=float(velocity[3]),actual_yaw=float(velocity[2]),height=float(sim.base_position[2]),tilt_deg=float(np.degrees(np.arccos(np.clip(h['upright_cos'],-1,1)))),closure_mm=1000*h['closure_error_m'],mimic_rad=h['mimic_error_rad'],sim_time=float(sim.data.time),finite=h['finite'])
                        with self.guard:self.snapshot=packet
                        write_json(D/'INTERACTIVE_CURRENT.json',packet);last_packet=now
                    viewer.sync();nexttick+=.01;time.sleep(max(0.,nexttick-time.perf_counter()))
                    if time.perf_counter()-nexttick>.2:nexttick=time.perf_counter()
        except Exception:
            self.error=traceback.format_exc();(D/'INTERACTIVE_ERROR.txt').write_text(self.error,encoding='utf8')
        finally:self.quit.set()
    def refresh(self):
        with self.guard:s=dict(self.snapshot)
        if self.error:
            self.status.set('启动/运行失败，详见 INTERACTIVE_ERROR.txt');self.details.set(self.error[-450:])
        elif s:
            self.location.set(s['terrain'])
            self.status.set(s['fault'] or ('已暂停 · P 继续' if s['paused'] else '可以操控 · 点击任一窗口，按住 WASD'))
            self.details.set(f"指令 {s['command_vx']:+.2f} m/s  实际 {s['actual_vx']:+.2f} m/s\n转向 {s['command_yaw']:+.2f} rad/s  实际 {s['actual_yaw']:+.2f} rad/s\n高度 {s['height']*1000:.1f} mm  倾斜 {s['tilt_deg']:.1f}°\n闭链 {s['closure_mm']:.4f} mm  仿真 {s['sim_time']:.1f} s")
        if self.quit.is_set() and not self.error:self.close();return
        self.root.after(100,self.refresh)
    def close(self):
        self.quit.set();self.root.destroy()
    def run(self):self.root.mainloop()

if __name__=='__main__':
    import msvcrt
    lock=open(D/'driver.lock','a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
    try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    except OSError:raise SystemExit('The local MOD4 driver is already running.')
    try:Driver().run()
    finally:lock.close()
