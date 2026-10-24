"""Local MuJoCo WASD driving. Only this application's focused windows accept keys."""
from pathlib import Path
import ctypes,json,math,os,threading,time,traceback
import tkinter as tk
from tkinter import ttk,messagebox
import mujoco,mujoco.viewer,numpy as np
from rm7v7_contact_stable_candidate_v1 import ContactStableRM7V7MoESim as RM7V7MoESim, ROUTES
from player_status_io import write_json
from player_wallclock_speed_v1 import WallClockSpeed
from player_camera import set_player_camera

D=Path(__file__).resolve().parent
RUN=D/'rm7v7_moe_runs'/str(time.time_ns());RUN.mkdir(parents=True)
ROUTE_KEYS=['flat_run','flat_jump','rough_forward','island_ramp_up','rough_reverse','fly_jump','fly_jump_mirror','central_upper','central_upper_down','central_lip','trapezoid','tunnel','tunnel_mirror','island_ramp_down','slope_spin']
SPAWNS=[(ROUTES[k]['name_zh'],*ROUTES[k]['spawn_ground_m'][:2],ROUTES[k]['spawn_yaw_rad']) for k in ROUTE_KEYS]
KEYS={key:ord(key) for key in 'WASDXRPF1234JKNZBM'};KEYS['SPACE']=32
class Driver:
    def __init__(self):
        self.root=tk.Tk();self.root.title('MOD4 小坎修正版 · 速度与实时时钟');self.root.geometry('650x880+35+40')
        self.root.configure(bg='#15232d');self.quit=threading.Event();self.guard=threading.Lock()
        self.virtual=set();self.speed=.6;self.turn=1.8;self.requests=[];self.snapshot={};self.error=None
        self.status=tk.StringVar(value='正在打开 MuJoCo 窗口…');self.details=tk.StringVar(value='等待仿真数据')
        self.location=tk.StringVar(value=SPAWNS[0][0]);self.speedtext=tk.StringVar(value='目标指令速度 0.60 m/s（仿真秒）')
        style=ttk.Style();style.theme_use('clam');style.configure('TFrame',background='#15232d');style.configure('TLabel',background='#15232d',foreground='#e2edf1',font=('Microsoft YaHei UI',11));style.configure('TButton',font=('Microsoft YaHei UI',11),padding=8)
        frame=ttk.Frame(self.root,padding=18);frame.pack(fill='both',expand=True)
        ttk.Label(frame,text='MOD4 · 小坎碰撞修正版 / 同一 MoE',font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
        ttk.Label(frame,text='最新完整源 H1第47轮 / E2第52轮 / E3第47轮 + 原 E0/W35门控',wraplength=600).pack(anchor='w')
        ttk.Label(frame,text='MuJoCo · 小坎碰撞修正版 · 原专家与控制频率不变',wraplength=520).pack(anchor='w',pady=(6,10))
        ttk.Label(frame,text='点击本窗口或仿真窗口后，按住 WASD 操控，松手停车。\nW / S 前后走    A / D 左右转    空格 / X 停车\nR 复位    F 换起点    P 暂停    1平地 / 2跳跃 / 3起伏 / 4中心岛',wraplength=600).pack(anchor='w')
        ttk.Label(frame,textvariable=self.speedtext).pack(anchor='w',pady=(12,0))
        scale=ttk.Scale(frame,from_=.1,to=1.5,command=self.change_speed);scale.set(.6);scale.pack(fill='x')
        buttons=ttk.Frame(frame);buttons.pack(fill='x',pady=8)
        for text,key in [('前进 W','W'),('左转 A','A'),('后退 S','S'),('右转 D','D')]:
            button=ttk.Button(buttons,text=text);button.pack(side='left',fill='x',expand=True,padx=2)
            button.bind('<ButtonPress-1>',lambda e,k=key:self.press(k));button.bind('<ButtonRelease-1>',lambda e,k=key:self.release(k));button.bind('<Leave>',lambda e,k=key:self.release(k))
        row=ttk.Frame(frame);row.pack(fill='x')
        for text,action in [('停车', 'stop'),('复位 R','reset'),('换路段 F','spawn'),('暂停 P','pause')]:
            ttk.Button(row,text=text,command=lambda a=action:self.request(a)).pack(side='left',fill='x',expand=True,padx=2)
        skills=ttk.Frame(frame);skills.pack(fill='x',pady=(10,3))
        for text,action in [('跳跃 J','jump'),('恢复 K','recover'),('普通 N','normal')]:
            ttk.Button(skills,text=text,command=lambda a=action:self.request(a)).pack(side='left',fill='x',expand=True,padx=2)
        spins=ttk.Frame(frame);spins.pack(fill='x',pady=3)
        for text,action in [('左自旋 +4 · Z','spin_left'),('右自旋 −4 · B','spin_right')]:
            ttk.Button(spins,text=text,command=lambda a=action:self.request(a)).pack(side='left',fill='x',expand=True,padx=2)
        ttk.Button(frame,text='全场俯视 / 跟随机器人 · M',command=lambda:self.request('camera')).pack(fill='x',pady=3)
        selector=ttk.Combobox(frame,values=[s[0] for s in SPAWNS],state='readonly')
        selector.current(0);selector.pack(fill='x',pady=(8,3))
        selector.bind('<<ComboboxSelected>>',lambda e:self.request('route:'+str(selector.current())))
        ttk.Label(frame,text='J 向前跳跃0.8秒（指令0.8 m/s）；K 恢复；Z/B 自旋；N/X 回普通驾驶。\n初始暂停，P 开始；直接 J 会先站稳1秒再跳。',wraplength=570).pack(anchor='w',pady=(6,0))
        ttk.Label(frame,textvariable=self.location,wraplength=520).pack(anchor='w',pady=(15,4))
        ttk.Label(frame,textvariable=self.status,wraplength=520).pack(anchor='w')
        ttk.Label(frame,textvariable=self.details,wraplength=520).pack(anchor='w',pady=(6,10))
        ttk.Label(frame,text='使用你提供的 RMUC2026_V2.0.0.stp 全场地形，约29×16m。\n双方地板1.5°坡度、起伏路、飞坡、中心岛、狗洞均保留。\n本版已测平地小坎；跳跃、恢复和全场稳定性尚未据此合格。\n现有CAD转换不含基地/前哨等机关；鼠标拖动视角，滚轮缩放。',wraplength=600,font=('Microsoft YaHei UI',9)).pack(anchor='w')
        self.root.protocol('WM_DELETE_WINDOW',self.close)
        self.root.bind('<FocusOut>',lambda e:self.clear_virtual())
        self.thread=threading.Thread(target=self.simulate,name='MOD4-MuJoCo',daemon=True);self.thread.start()
        self.root.after(100,self.refresh)
    def change_speed(self,value):
        with self.guard:self.speed=float(value)
        self.speedtext.set(f'目标指令速度 {float(value):.2f} m/s（仿真秒）')
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
            sim=RM7V7MoESim();params=sim.parameter_readback();spawn=0;paused=True;fault=None;previous=set();blocked=False;current_v=0.;current_w=0.;spin_w=0.
            with mujoco.viewer.launch_passive(sim.model,sim.data,show_left_ui=False,show_right_ui=False) as viewer:
                overview=True
                set_player_camera(viewer,sim.chassis_id,overview)
                write_json(RUN/'INTERACTIVE_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),checkpoint=sim.policy.path.name,viewer_running=viewer.is_running(),parameter_readback=params,source_bundle=sim.delivery,driver_path=str(Path(__file__).resolve()),speed_telemetry_version=1,speed_telemetry_scope='active-window wall versus simulation clock; bounded1200 one-Hz status packets; no physics or policy change'))
                nexttick=time.perf_counter();last_packet=0.;steps=0;begin=nexttick
                speed_clock=WallClockSpeed();last_sync_ms=0.;last_timing_log=nexttick;timing_log_count=0
                while not self.quit.is_set() and viewer.is_running():
                    keys,focused=self.focused_keys()
                    with self.guard:
                        keys|=self.virtual if focused else set();speed=self.speed;turn=self.turn;requests=self.requests[:];self.requests.clear()
                    pressed=keys-previous;previous=keys
                    if 'R' in pressed:requests.append('reset')
                    if 'F' in pressed:requests.append('spawn')
                    if 'P' in pressed:requests.append('pause')
                    if 'M' in pressed:requests.append('camera')
                    for key,action in [('J','jump'),('K','recover'),('N','normal'),('Z','spin_left'),('B','spin_right')]:
                        if key in pressed:requests.append(action)
                    if 'SPACE' in keys or 'X' in keys:requests.append('stop')
                    for key in ('1','2','3','4'):
                        if key in pressed:requests.append('spawn'+key)
                    for req in requests:
                        if req=='camera':
                            overview=not overview
                            set_player_camera(viewer,sim.chassis_id,overview)
                        if req=='pause':paused=not paused
                        if req=='stop':blocked=True;current_v=current_w=0.;self.clear_virtual();sim.select_skill(0)
                        if req in ('jump','recover','normal','spin_left','spin_right'):
                            current_v=current_w=0.;fault=None
                            if req=='jump':sim.request_jump();paused=False
                            elif req=='recover':sim.select_skill(3);paused=False
                            elif req=='normal':sim.select_skill(0)
                            else:sim.select_skill(6);spin_w=4. if req=='spin_left' else -4.;paused=False
                        if req=='reset' or req.startswith('spawn') or req.startswith('route:'):
                            if req=='spawn':spawn=(spawn+1)%len(SPAWNS)
                            elif req.startswith('spawn') and len(req)>5:spawn=int(req[-1])-1
                            elif req.startswith('route:'):spawn=int(req.split(':')[1])
                            sim.reset_route(ROUTE_KEYS[spawn]);speed_clock.reset();fault=None;current_v=current_w=0.;blocked=True
                    if not keys.intersection('WASD'):blocked=False
                    target_v=(('W' in keys)-('S' in keys))*speed if focused and not blocked else 0.
                    target_w=(('A' in keys)-('D' in keys))*turn if focused and not blocked else 0.
                    if sim.jump_pending or sim.command.mode==3:target_v=target_w=0.
                    elif sim.command.mode==4:target_v=.8;target_w=0.
                    elif sim.command.mode==6:target_w=spin_w if focused and not blocked else 0.
                    current_v+=float(np.clip(target_v-current_v,-.008,.008));current_w+=float(np.clip(target_w-current_w,-.04,.04))
                    if sim.command.mode==4:current_v=.8;current_w=0.
                    advanced=not paused and fault is None
                    step_begin=time.perf_counter()
                    if not paused and fault is None:
                        sim.command.vx=current_v;sim.command.wz=current_w;sim.step_control();steps+=1
                        h=sim.health()
                        if (h['upright_cos']<.60 or sim.base_position[2]<.12) and sim.command.mode!=3:fault='已倾倒，按 K 尝试恢复或 R 复位'
                    step_ms=(time.perf_counter()-step_begin)*1000 if advanced else 0.
                    now=time.perf_counter()
                    speed_clock.observe(now,float(sim.data.time),sim.base_position,advanced,step_ms,last_sync_ms)
                    if now-last_packet>.10:
                        velocity=np.zeros(6);mujoco.mj_objectVelocity(sim.model,sim.data,mujoco.mjtObj.mjOBJ_XBODY,sim.chassis_id,velocity,1)
                        h=sim.health();packet=dict(epoch=time.time(),pid=os.getpid(),checkpoint=sim.policy.path.name,terrain=SPAWNS[spawn][0],paused=paused,fault=fault,focused=focused,command_vx=current_v,command_yaw=current_w,actual_vx=float(velocity[3]),actual_yaw=float(velocity[2]),height=float(sim.base_position[2]),tilt_deg=float(np.degrees(np.arccos(np.clip(h['upright_cos'],-1,1)))),closure_mm=1000*h['closure_error_m'],mimic_rad=h['mimic_error_rad'],sim_time=float(sim.data.time),finite=h['finite'])
                        packet['skill']=sim.skill
                        packet.update(speed_clock.metrics(),target_slider_vx=float(speed),speed_timebase='actual_vx is per simulation second; ground_speed_wall_mps is horizontal path per active wall second',driver_path=str(Path(__file__).resolve()))
                        if advanced and now-last_timing_log>=1. and timing_log_count<1200:
                            with (RUN/'INTERACTIVE_TIMING.jsonl').open('a',encoding='utf8') as timing_file:timing_file.write(json.dumps(packet,ensure_ascii=False)+'\n')
                            timing_log_count+=1;last_timing_log=now
                        packet['timing_log_samples']=timing_log_count
                        packet['timing_log_sample_limit']=1200
                        with self.guard:self.snapshot=packet
                        write_json(RUN/'INTERACTIVE_CURRENT.json',packet);last_packet=now
                    sync_begin=time.perf_counter();viewer.sync();last_sync_ms=1000*(time.perf_counter()-sync_begin)
                    nexttick+=.01;time.sleep(max(0.,nexttick-time.perf_counter()))
                    if time.perf_counter()-nexttick>.2:nexttick=time.perf_counter()
        except Exception:
            self.error=traceback.format_exc();(RUN/'INTERACTIVE_ERROR.txt').write_text(self.error,encoding='utf8')
        finally:self.quit.set()
    def refresh(self):
        with self.guard:s=dict(self.snapshot)
        if self.error:
            self.status.set('启动/运行失败，详见 INTERACTIVE_ERROR.txt');self.details.set(self.error[-450:])
        elif s:
            self.location.set(s['terrain'])
            self.status.set(s['fault'] or ('已暂停 · P 开始；J 跳跃' if s['paused'] else s['skill']+' · 点击任一窗口，按住 WASD'))
            rate=s.get('realtime_factor');ground=s.get('ground_speed_wall_mps')
            clockline='实时时钟：采样中 / 已暂停' if rate is None else f"现实秒地面速度 {ground:.2f} m/s · 实时倍率 {rate:.2f}×"
            costline='' if rate is None else f"\n控制/物理 {s['step_control_wall_ms']:.1f} ms · 同步 {s['viewer_sync_wall_ms']:.1f} ms"
            self.details.set(f"指令 {s['command_vx']:+.2f} / 实际 {s['actual_vx']:+.2f} m/s（仿真秒）\n{clockline}\n转向 {s['command_yaw']:+.2f} / 实际 {s['actual_yaw']:+.2f} rad/s\n高度 {s['height']*1000:.1f} mm · 倾斜 {s['tilt_deg']:.1f}°\n闭链 {s['closure_mm']:.4f} mm · 仿真 {s['sim_time']:.1f} s{costline}")
        if self.quit.is_set() and not self.error:self.close();return
        self.root.after(100,self.refresh)
    def close(self):
        self.quit.set();self.root.destroy()
    def run(self):self.root.mainloop()

if __name__=='__main__':
    import msvcrt
    lock=open(D/'rm7v7_moe_driver.lock','a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
    try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    except OSError:raise SystemExit('The local MOD4 driver is already running.')
    try:Driver().run()
    finally:lock.close()
