"""Human-requested local WASD control; process-focused keys, independent models."""
from pathlib import Path
import ctypes,json,math,os,threading,time,traceback
import tkinter as tk
from tkinter import ttk
import mujoco,mujoco.viewer,numpy as np
from series_sim import SeriesSim,SERIES,MODELS
from io_runtime import write_json

D=Path(__file__).resolve().parent
KEYS={k:ord(k) for k in 'WASDXRPFM1234567'};KEYS['SPACE']=32
COMMAND_MODES=['自由 WASD','原地小陀螺（W/S 禁用）','定向小陀螺 V=0.5（W/S 定向）']

def focused_keys():
    user=ctypes.windll.user32
    user.GetForegroundWindow.restype=ctypes.c_void_p
    user.GetWindowThreadProcessId.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_ulong)]
    foreground=user.GetForegroundWindow();pid=ctypes.c_ulong()
    user.GetWindowThreadProcessId(foreground,ctypes.byref(pid))
    if pid.value!=os.getpid():return set(),False
    return {k for k,c in KEYS.items() if user.GetAsyncKeyState(c)&0x8000},True

class Driver:
    def __init__(self,start_sim=True):
        self.root=tk.Tk();self.root.title('MOD4 · WASD / 小陀螺 / 地形系列');self.root.geometry('730x840+30+30')
        self.quit=threading.Event();self.guard=threading.Lock();self.virtual=set();self.requests=[];self.snapshot={};self.error=None
        self.speed=.3;self.spin=2.;self.command_mode=0;self.reverse=False;self.overview=False;self.spin_latch=0
        self.model_value=tk.StringVar(value=MODELS[0]['label']);self.scene_value=tk.StringVar(value=SERIES['scenes'][0]['label'])
        self.spin_value=tk.StringVar(value='2');self.mode_value=tk.StringVar(value=COMMAND_MODES[0]);self.reverse_value=tk.BooleanVar(value=False)
        self.status=tk.StringVar(value='正在打开本地仿真…');self.details=tk.StringVar(value='');self.scope=tk.StringVar(value=MODELS[0]['status']);self.speedtext=tk.StringVar(value='直行速度 0.30 m/s')
        st=ttk.Style();st.theme_use('clam');st.configure('TLabel',font=('Microsoft YaHei UI',10));st.configure('TButton',font=('Microsoft YaHei UI',10),padding=6)
        f=ttk.Frame(self.root,padding=16);f.pack(fill='both',expand=True)
        ttk.Label(f,text='MOD4 本地操控',font=('Microsoft YaHei UI',20,'bold')).pack(anchor='w')
        ttk.Label(f,text='W / S 前后   A / D 左右转   空格 / X 停车   R 复位   P 暂停\n1–7 选择小陀螺档位   F 换地形   M 换模型\n小陀螺：点下方按钮开始，再点停车；失去焦点立即停止。').pack(anchor='w',pady=8)
        for label,var,values,handler in [
            ('模型',self.model_value,[m['label'] for m in MODELS],self.pick_model),
            ('地形系列',self.scene_value,[s['label'] for s in SERIES['scenes']],self.pick_scene),
            ('操控方式',self.mode_value,COMMAND_MODES,self.pick_mode),
            ('小陀螺档位 rad/s',self.spin_value,SERIES['spin_labels'],self.pick_spin)]:
            row=ttk.Frame(f);row.pack(fill='x',pady=3);ttk.Label(row,text=label,width=18).pack(side='left')
            box=ttk.Combobox(row,textvariable=var,values=values,state='readonly');box.pack(side='left',fill='x',expand=True);box.bind('<<ComboboxSelected>>',handler)
        spin_row=ttk.LabelFrame(f,text='原地小陀螺 · 点击开始 / 停车停止',padding=5);spin_row.pack(fill='x',pady=7)
        for text,action,value in [('左小陀螺 ⟲','spin',1),('右小陀螺 ⟳','spin',-1),('停车 / 空格','stop',None)]:
            ttk.Button(spin_row,text=text,command=lambda a=action,v=value:self.request(a,v)).pack(side='left',fill='x',expand=True,padx=3)
        ttk.Label(f,textvariable=self.scope,wraplength=660,foreground='#9c5612').pack(anchor='w',pady=5)
        ttk.Label(f,textvariable=self.speedtext).pack(anchor='w')
        scale=ttk.Scale(f,from_=.1,to=1.5,command=self.change_speed);scale.set(.3);scale.pack(fill='x')
        row=ttk.Frame(f);row.pack(fill='x',pady=5)
        ttk.Checkbutton(row,text='反向起点 / 下行（切换会复位）',variable=self.reverse_value,command=self.pick_reverse).pack(side='left')
        ttk.Button(row,text='近景 / 全路视角',command=lambda:self.request('camera')).pack(side='right')
        row=ttk.Frame(f);row.pack(fill='x',pady=4)
        for text,key in [('前进 W','W'),('左转 A','A'),('后退 S','S'),('右转 D','D')]:
            b=ttk.Button(row,text=text);b.pack(side='left',fill='x',expand=True,padx=2)
            b.bind('<ButtonPress-1>',lambda e,k=key:self.press(k));b.bind('<ButtonRelease-1>',lambda e,k=key:self.release(k));b.bind('<Leave>',lambda e,k=key:self.release(k))
        row=ttk.Frame(f);row.pack(fill='x',pady=4)
        for text,action in [('停车','stop'),('复位 R','reset'),('暂停 P','pause')]:ttk.Button(row,text=text,command=lambda a=action:self.request(a)).pack(side='left',fill='x',expand=True,padx=2)
        ttk.Label(f,textvariable=self.status,wraplength=660,font=('Microsoft YaHei UI',11,'bold')).pack(anchor='w',pady=8)
        ttk.Label(f,textvariable=self.details,wraplength=660).pack(anchor='w')
        ttk.Label(f,text='起伏：10 / 20 / 35 mm 全十波，另有真实 CAD 约70 mm 采样路段。\n跨坎：20 / 35 / 50 mm；坡面：5 / 8 / 10°；派生台阶：20 mm ×3。\n起伏候选未合格；跨坎/坡面/台阶未提供已训练独立专家。\n这是名义 MuJoCo 试玩，手动选择模型；自动 MoE gate 尚未训练。\n鼠标拖动视角、滚轮缩放；地形外出界或倾倒会暂停，按 R 复位。',wraplength=660,font=('Microsoft YaHei UI',9)).pack(anchor='w',pady=10)
        self.root.protocol('WM_DELETE_WINDOW',self.close)
        self.thread=None
        if start_sim:
            self.thread=threading.Thread(target=self.simulate,daemon=True,name='MOD4-local-series');self.thread.start();self.root.after(100,self.refresh)
    def request(self,action,value=None):
        with self.guard:self.requests.append((action,value))
    def press(self,key):
        with self.guard:self.virtual.add(key)
    def release(self,key):
        with self.guard:self.virtual.discard(key)
    def clear_virtual(self):
        with self.guard:self.virtual.clear()
    def change_speed(self,value):
        with self.guard:self.speed=float(value)
        self.speedtext.set(f'直行速度 {float(value):.2f} m/s')
    def pick_model(self,e=None):self.request('model',next(m['id'] for m in MODELS if m['label']==self.model_value.get()))
    def pick_scene(self,e=None):self.request('scene',next(s['id'] for s in SERIES['scenes'] if s['label']==self.scene_value.get()))
    def pick_spin(self,e=None):
        with self.guard:self.spin=SERIES['spin_rad_s'][SERIES['spin_labels'].index(self.spin_value.get())]
    def pick_mode(self,e=None):
        with self.guard:self.command_mode=COMMAND_MODES.index(self.mode_value.get());self.spin_latch=0
        self.request('stop')
    def pick_reverse(self):self.request('reverse',self.reverse_value.get())
    def camera(self,viewer,sim):
        if self.overview:
            viewer.cam.type=mujoco.mjtCamera.mjCAMERA_FREE;viewer.cam.lookat[:]=(0,0,.15);viewer.cam.distance=10.;viewer.cam.azimuth=110;viewer.cam.elevation=-50
        else:
            viewer.cam.type=mujoco.mjtCamera.mjCAMERA_TRACKING;viewer.cam.trackbodyid=sim.chassis_id;viewer.cam.distance=2.4;viewer.cam.azimuth=140;viewer.cam.elevation=-25
    def simulate(self):
        scene='flat';model='e0';reverse=False;paused=False;previous=set();telemetry_errors=[]
        try:
            while not self.quit.is_set():
                sim=SeriesSim(scene,model,reverse);params=sim.parameter_readback();fault=None;blocked=False;v=w=0.;world_alpha=0.;world_sign=0
                rebuild=False
                with mujoco.viewer.launch_passive(sim.model,sim.data,show_left_ui=False,show_right_ui=False) as viewer:
                    self.camera(viewer,sim)
                    write_json(D/'INTERACTIVE_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),model=model,checkpoint_sha256=sim.policy.sha256,scene=scene,viewer_running=viewer.is_running(),parameter_readback=params),required=True)
                    nexttick=time.perf_counter();last_packet=0.;previous=set()
                    while not self.quit.is_set() and viewer.is_running():
                        keys,focused=focused_keys()
                        with self.guard:
                            if not focused:self.virtual.clear();self.spin_latch=0
                            else:keys|=self.virtual
                            speed=self.speed;spin=self.spin;cm=self.command_mode;requests=self.requests[:];self.requests.clear()
                        pressed=keys-previous;previous=keys
                        for key,action in [('R','reset'),('F','nextscene'),('M','nextmodel'),('P','pause')]:
                            if key in pressed:requests.append((action,None))
                        if 'SPACE' in keys or 'X' in keys:requests.append(('stop',None))
                        for i in range(1,8):
                            if str(i) in pressed:
                                spin=SERIES['spin_rad_s'][i-1]
                                with self.guard:self.spin=spin
                        for action,value in requests:
                            if action=='spin':
                                self.command_mode=cm=1;self.spin_latch=int(value);v=w=0.;blocked=False;self.clear_virtual()
                            elif action=='pause':paused=not paused;v=w=0.;self.spin_latch=0
                            elif action=='camera':self.overview=not self.overview;self.camera(viewer,sim)
                            elif action=='stop':blocked=True;v=w=0.;self.spin_latch=0;self.clear_virtual()
                            elif action=='reset':sim.reset_entry(reverse);fault=None;v=w=0.;blocked=True;world_sign=0;self.spin_latch=0
                            elif action=='reverse':reverse=bool(value);sim.reset_entry(reverse);fault=None;v=w=0.;blocked=True;world_sign=0;self.spin_latch=0
                            elif action in ('model','nextmodel'):
                                if action=='nextmodel':value=MODELS[([m['id'] for m in MODELS].index(model)+1)%len(MODELS)]['id']
                                model=value;sim.switch_model(model);fault=None;v=w=0.;blocked=True;world_sign=0;self.spin_latch=0
                            elif action in ('scene','nextscene'):
                                if action=='nextscene':value=SERIES['scenes'][([s['id'] for s in SERIES['scenes']].index(scene)+1)%len(SERIES['scenes'])]['id']
                                scene=value;self.spin_latch=0;rebuild=True;break
                        if rebuild:break
                        if not keys.intersection('WASD'):blocked=False
                        enabled=focused and not blocked and not paused and fault is None
                        tv=(('W' in keys)-('S' in keys))*speed if enabled and cm==0 else 0.
                        tw=(('A' in keys)-('D' in keys))*spin if enabled else 0.
                        if enabled and cm==1 and self.spin_latch:tw=self.spin_latch*spin
                        if enabled and cm==2:
                            sign=int('W' in keys)-int('S' in keys)
                            R=sim.data.xmat[sim.chassis_id].reshape(3,3);theta=math.atan2(R[1,0],R[0,0])
                            if sign and sign!=world_sign:world_alpha=theta+(math.pi if sign<0 else 0.)
                            world_sign=sign
                            tv=2*.5*math.cos(theta-world_alpha) if sign else 0.
                        # Focus loss, stop, or pause sets commands exactly zero immediately.
                        if not enabled:v=w=0.
                        else:v+=float(np.clip(tv-v,-.008,.008));w+=float(np.clip(tw-w,-.04,.04))
                        if not paused and fault is None:
                            sim.command.vx=v;sim.command.wz=w;sim.step_control();h=sim.health()
                            if h['upright_cos']<.60 or sim.base_position[2]<.12:fault='倾倒，按 R 复位'
                            elif sim.scene['kind']!='flat' and (abs(sim.base_position[0])>4.4 or abs(sim.base_position[1])>.95):fault='地形有效路段外，按 R 复位'
                        now=time.perf_counter()
                        if now-last_packet>.2:
                            vel=sim.body_velocity();h=sim.health()
                            packet=dict(epoch=time.time(),pid=os.getpid(),model_id=model,model_label=sim.model_item['label'],checkpoint_sha256=sim.policy.sha256,scope=sim.model_item['status'],scene_id=scene,terrain=sim.scene['label'],reverse=reverse,spin_rad_s=spin,spin_button_direction=self.spin_latch,command_mode=cm,paused=paused,fault=fault,focused=focused,command_vx=v,command_yaw=w,actual_vx=float(vel[3]),actual_yaw=float(vel[2]),height=float(sim.base_position[2]),tilt_deg=float(np.degrees(np.arccos(np.clip(h['upright_cos'],-1,1)))),closure_mm=1000*h['closure_error_m'],mimic_rad=h['mimic_error_rad'],sim_time=float(sim.data.time),finite=h['finite'],telemetry_errors=telemetry_errors[-3:],learned_gate=False)
                            with self.guard:self.snapshot=packet
                            err=write_json(D/'INTERACTIVE_CURRENT.json',packet)
                            if err and (not telemetry_errors or telemetry_errors[-1]['message']!=err['message']):telemetry_errors.append(dict(epoch=time.time(),**err))
                            last_packet=now
                        viewer.sync();nexttick+=.01;time.sleep(max(0.,nexttick-time.perf_counter()))
                        if time.perf_counter()-nexttick>.2:nexttick=time.perf_counter()
                if not rebuild:break
            write_json(D/'INTERACTIVE_EXIT.json',dict(epoch=time.time(),pid=os.getpid(),telemetry_errors=telemetry_errors),required=False)
        except Exception:
            self.error=traceback.format_exc();(D/'INTERACTIVE_ERROR.txt').write_text(self.error,encoding='utf8')
        finally:self.quit.set()
    def refresh(self):
        with self.guard:s=dict(self.snapshot)
        if self.error:self.status.set('运行失败，详见 INTERACTIVE_ERROR.txt');self.details.set(self.error[-450:])
        elif s:
            self.model_value.set(s['model_label']);self.scene_value.set(s['terrain']);self.reverse_value.set(s['reverse']);self.scope.set(s['scope']);self.mode_value.set(COMMAND_MODES[s['command_mode']])
            idx=min(range(7),key=lambda i:abs(SERIES['spin_rad_s'][i]-s['spin_rad_s']));self.spin_value.set(SERIES['spin_labels'][idx])
            self.status.set(s['fault'] or ('已暂停 · P 继续' if s['paused'] else '可操控' if s['focused'] else '等待焦点 · 指令已归零'))
            self.details.set(f"指令 {s['command_vx']:+.2f} m/s · 实际 {s['actual_vx']:+.2f} m/s\n转向 {s['command_yaw']:+.2f} rad/s · 实际 {s['actual_yaw']:+.2f} rad/s\n高度 {s['height']*1000:.1f} mm · 倾角 {s['tilt_deg']:.1f}°\n闭链 {s['closure_mm']:.4f} mm · 仿真 {s['sim_time']:.1f} s")
        if self.quit.is_set() and not self.error:self.close();return
        self.root.after(100,self.refresh)
    def close(self):self.quit.set();self.root.destroy()
    def run(self):
        self.root.mainloop()
        self.quit.set()
        if self.thread:self.thread.join(timeout=5)

if __name__=='__main__':
    import msvcrt
    lock=open(D/'driver.lock','a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
    try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    except OSError:raise SystemExit('The local series player is already running.')
    try:Driver().run()
    finally:lock.close()
