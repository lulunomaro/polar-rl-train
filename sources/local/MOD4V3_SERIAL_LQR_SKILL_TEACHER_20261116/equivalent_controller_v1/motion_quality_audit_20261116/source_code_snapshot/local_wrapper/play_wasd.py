"""WASD console for the upstream Serial_Leg_Simulation plant and controller."""
from pathlib import Path
import sys,time,json,queue,ctypes,os,math,traceback,argparse
from ctypes import wintypes
import numpy as np
import mujoco as mj
import mujoco.viewer
import tkinter as tk
from tkinter import ttk
from pynput import keyboard

LOCAL=Path(__file__).resolve().parent
REPO=LOCAL.parent/'Serial_Leg_Simulation'
sys.path.insert(0,str(REPO/'sim'))
from main import parse_args
from utils import load_config,require_actuator_order
from controller import StandController

SCENES={f'{h} cm 单台阶':REPO/'mjcf'/f'bigeye_step_{h:02d}cm_local.xml' for h in [7,5,10,15,20]}
SCENES.update({'平地 / 跳跃':REPO/'mjcf/bigeye_flat.xml','RMUC2027 原版场地':REPO/'mjcf/bigeye_rmuc2027.xml'})
PHASE={'idle':'就绪','thrust':'蹬地起跳','retract':'腾空收腿','extend':'腾空伸腿','landing':'落地缓冲'}

class SerialSimulation:
    def __init__(self,scene='7 cm 单台阶'):
        self.scene=scene
        cfg=load_config()
        saved=sys.argv
        try:
            sys.argv=[str(__file__),'--headless','--scene',str(SCENES[scene]),'--log-every','1','--balance-controller','lqr']
            args=parse_args()
        finally:sys.argv=saved
        args.fall_angle=cfg['control_initial']['fall_angle_rad']
        self.m=mj.MjModel.from_xml_path(str(SCENES[scene]));self.d=mj.MjData(self.m)
        mj.mj_forward(self.m,self.d)
        require_actuator_order(self.m,cfg['mujoco']['actuator_order'])
        self.c=StandController(self.m,self.d,cfg,args)
        self.paused=False;self.pending_jump=False;self.jump_requests=0;self.jump_cycles=0
        self.previous_phase='idle';self.speed=.6;self.yaw_speed=1.5;self.viewer=None
        self.height=float(self.c.target_leg_length_command);self.height_pending=False
        self.cmd_vx=0.;self.cmd_wz=0.
        self.base_id=mj.mj_name2id(self.m,mj.mjtObj.mjOBJ_BODY,'base')

    def set_height(self,value):
        # Player intent is independent of temporary jump/climb leg references.
        self.height=float(np.clip(value,self.c.leg_length_min,self.c.leg_length_max))
        self.height_pending=True
        self.apply_height_command()

    def apply_height_command(self):
        if self.height_pending and self.c.jump_state=='idle' and self.c.step_climb.phase=='idle' and not self.c.recovery.active:
            self.c.target_leg_length_command=self.height
            self.c.target_leg_length=self.height
            self.c._jump_returning=False
            self.height_pending=False

    def reset(self):
        mj.mj_resetData(self.m,self.d);mj.mj_forward(self.m,self.d)
        self.c.reset_internal_state();self.pending_jump=False;self.paused=False;self.previous_phase='idle'
        self.cmd_vx=self.cmd_wz=0.;self.height_pending=True;self.apply_height_command()

    def jump(self):
        self.pending_jump=True;self.jump_requests+=1

    def step(self,keys):
        if self.paused:return
        speed=float('w' in keys)-float('s' in keys)
        yaw=float('a' in keys)-float('d' in keys)
        if 'space' in keys:speed=yaw=0.
        self.cmd_vx=speed*self.speed;self.cmd_wz=yaw*self.yaw_speed
        height_axis=float('e' in keys)-float('q' in keys)
        if height_axis:self.set_height(self.height+height_axis*.14*float(self.m.opt.timestep))
        self.apply_height_command()
        if self.c.reference_governor is not None:
            self.c.reference_governor.max_speed=self.speed
            self.c.reference_governor.max_yaw_rate=self.yaw_speed
        # Height keys never enter the upstream keyboard-axis path.
        self.c.step((speed,yaw,0.,self.pending_jump))
        self.pending_jump=False
        phase=self.c.jump_state
        if phase!='idle' and self.previous_phase=='idle':self.jump_cycles+=1
        self.previous_phase=phase

    def state(self):
        c=self.c;R=self.d.xmat[self.base_id].reshape(3,3)
        pitch=math.degrees(math.asin(float(np.clip(-R[2,0],-1,1))))
        forward=R[:2,0];forward=forward/max(np.linalg.norm(forward),1e-8)
        return dict(scene=self.scene,time_s=float(self.d.time),root_xyz=self.d.qpos[:3].tolist(),pitch_deg=pitch,
                    vx=float(self.d.qvel[:2]@forward),height_command=self.height,controller_height_command=float(c.target_leg_length_command),cmd_vx=self.cmd_vx,cmd_wz=self.cmd_wz,
                    leg_lengths=[float(c.left_leg.length),float(c.right_leg.length)],jump_phase=c.jump_state,
                    climb_phase=c.step_climb.phase,paused=self.paused,jump_requests=self.jump_requests,
                    jump_cycles=self.jump_cycles,speed_limit=self.speed,controller='upstream LQR + VMC')

    def close(self):
        if self.viewer:self.viewer.close()
        self.c.recovery_log.finish('wasd_player_closed')

class App:
    BG='#0d1117';PANEL='#161b22';TEXT='#e6edf3';MUTED='#8b949e';CYAN='#39d5ff';GREEN='#4be38a';YELLOW='#ffd166'
    def __init__(self,root):
        self.root=root;self.sim=None;self.keys=set();self.events=queue.Queue();self.closed=False;self.syncing=False
        self.last_status=0.;self.last_draw=0.;self.event='准备就绪';self.scene_var=tk.StringVar(value='7 cm 单台阶')
        self.user32=ctypes.WinDLL('user32',use_last_error=True)
        self.user32.GetForegroundWindow.restype=wintypes.HWND
        self.user32.GetWindowThreadProcessId.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)]
        self.user32.GetAncestor.argtypes=[wintypes.HWND,wintypes.UINT];self.user32.GetAncestor.restype=wintypes.HWND
        self.build()
        root.update_idletasks();self.control_hwnd=int(root.winfo_id())
        self.load_scene()
        self.listener=keyboard.Listener(on_press=lambda k:self.key_event(k,True),on_release=lambda k:self.key_event(k,False))
        self.listener.daemon=True;self.listener.start()
        root.protocol('WM_DELETE_WINDOW',self.close)
        root.after(1,self.tick)
        root.lift();root.attributes('-topmost',True);root.after(800,lambda:root.attributes('-topmost',False))

    def build(self):
        root=self.root;root.title('串联轮腿 · WASD 控制台 · 跳跃 / 上台阶');root.geometry('500x830+25+55');root.minsize(470,790);root.configure(bg=self.BG)
        o=tk.Frame(root,bg=self.BG,padx=16,pady=14);o.pack(fill='both',expand=True)
        tk.Label(o,text='SERIAL LEG  /  WASD PLAYER',bg=self.BG,fg=self.CYAN,font=('Microsoft YaHei UI',17,'bold'),anchor='w').pack(fill='x')
        tk.Label(o,text='原版串联轮腿 · LQR + VMC · 跳跃 / 台阶体验',bg=self.BG,fg=self.MUTED,font=('Microsoft YaHei UI',9),anchor='w').pack(fill='x',pady=(4,12))
        box=tk.Frame(o,bg=self.PANEL,padx=12,pady=8);box.pack(fill='x');self.vars={}
        for i,(name,key) in enumerate([('实际车身高度','z'),('前进速度','vx'),('俯仰角','pitch'),('站高 / 腿长指令','height'),('左右实际腿长','legs'),('跳跃状态','jump'),('上阶辅助状态','climb'),('仿真时间','time')]):
            tk.Label(box,text=name,bg=self.PANEL,fg=self.MUTED,font=('Microsoft YaHei UI',10),anchor='w').grid(row=i,column=0,sticky='w',pady=2)
            v=tk.StringVar(value='—');self.vars[key]=v
            tk.Label(box,textvariable=v,bg=self.PANEL,fg=self.CYAN if key=='jump' else self.TEXT,font=('Microsoft YaHei UI',10,'bold'),anchor='e').grid(row=i,column=1,sticky='e',pady=2)
        box.columnconfigure(1,weight=1)
        tk.Label(o,text='场景',bg=self.BG,fg=self.TEXT,font=('Microsoft YaHei UI',10,'bold'),anchor='w').pack(fill='x',pady=(12,4))
        row=tk.Frame(o,bg=self.BG);row.pack(fill='x')
        ttk.Combobox(row,textvariable=self.scene_var,values=list(SCENES),state='readonly',font=('Microsoft YaHei UI',10)).pack(side='left',fill='x',expand=True)
        self.button(row,'载入 / 复位',self.load_scene,self.CYAN).pack(side='right',padx=(8,0))
        self.height_var=tk.DoubleVar(value=.25)
        self.height_scale=self.slider(o,'站高 / 腿长指令  Q↓ / E↑',self.height_var,.13,.34,.005,None)
        # Bind user gestures; display synchronization cannot invoke this setter.
        for sequence in ('<ButtonPress-1>','<B1-Motion>','<ButtonRelease-1>'):
            self.height_scale.bind(sequence,lambda event:self.root.after_idle(self.height_changed))
        self.speed_var=tk.DoubleVar(value=.6)
        self.slider(o,'W / S 速度上限 (m/s)',self.speed_var,.2,2.,.1,self.speed_changed)
        buttons=tk.Frame(o,bg=self.BG);buttons.pack(fill='x',pady=(7,3))
        for i,(label,cmd,color) in enumerate([('J  起跳',self.jump,self.GREEN),('R  复位',self.reset,self.CYAN),('P  暂停 / 继续',self.pause,self.YELLOW),('Space  停车',self.stop,'#ff6b81')]):
            self.button(buttons,label,cmd,color).grid(row=i//2,column=i%2,sticky='ew',padx=4,pady=4)
        buttons.columnconfigure((0,1),weight=1)
        presets=tk.Frame(o,bg=self.BG);presets.pack(fill='x',pady=(2,8))
        for text,value in [('1  低站姿',.16),('2  默认',.2496265),('3  上阶站姿',.34)]:
            self.button(presets,text,lambda v=value:self.set_height(v),self.MUTED).pack(side='left',fill='x',expand=True,padx=3)
        tk.Label(o,text='W / S 前后　A / D 转向　Q / E 站高\nSpace 停车　J 起跳　R 复位　P 暂停\n上阶先按 3，再用 W 接近；7 cm 台阶就在正前方。\n在本控制台使用键盘，松开 WASD 即发停车指令。',bg=self.PANEL,fg=self.TEXT,font=('Microsoft YaHei UI',10),justify='left',anchor='w',padx=10,pady=9).pack(fill='x')
        self.follow_var=tk.BooleanVar(value=True)
        tk.Checkbutton(o,text='镜头跟随机器人',variable=self.follow_var,bg=self.BG,fg=self.MUTED,selectcolor=self.PANEL,activebackground=self.BG,activeforeground=self.TEXT,takefocus=False).pack(anchor='w',pady=(5,2))
        self.status_var=tk.StringVar(value='载入中…')
        tk.Label(o,textvariable=self.status_var,bg=self.BG,fg=self.CYAN,font=('Microsoft YaHei UI',9),anchor='w',wraplength=455).pack(fill='x',pady=(3,0))

    def button(self,parent,text,command,color):
        return tk.Button(parent,text=text,command=command,bg=self.PANEL,fg=color,activebackground='#30363d',activeforeground=color,relief='flat',font=('Microsoft YaHei UI',10,'bold'),padx=8,pady=7,takefocus=False)

    def slider(self,parent,label,var,lo,hi,res,command):
        tk.Label(parent,text=label,bg=self.BG,fg=self.TEXT,font=('Microsoft YaHei UI',10,'bold'),anchor='w').pack(fill='x',pady=(10,0))
        options=dict(from_=lo,to=hi,resolution=res,variable=var,orient='horizontal',bg=self.BG,fg=self.YELLOW,troughcolor='#30363d',highlightthickness=0,bd=0,takefocus=False)
        if command is not None:options['command']=command
        scale=tk.Scale(parent,**options);scale.pack(fill='x');return scale

    def focused(self):
        foreground=self.user32.GetForegroundWindow()
        control=self.user32.GetAncestor(self.control_hwnd,2) or self.control_hwnd
        return bool(foreground) and int(foreground)==int(control)

    def key_event(self,key,down):
        if down and not self.focused():return
        if key==keyboard.Key.space:name='space'
        elif key==keyboard.Key.esc:name='escape'
        else:name=(getattr(key,'char',None) or '').lower()
        if name in {'w','s','a','d','q','e','1','2','3','4','5','6','space','j','p','r','x','escape'}:
            self.events.put((name,down))

    def on_key(self,key,down):
        if not down:self.keys.discard(key);return
        if key in self.keys:return
        self.keys.add(key)
        if key=='j':self.jump()
        elif key in ('space','x'):self.stop()
        elif key=='r':self.reset()
        elif key=='p':self.pause()
        elif key in ('1','2','3'):self.set_height({'1':.16,'2':.2496265,'3':.34}[key])
        elif key in ('4','5','6'):
            self.sim.speed={'4':.9,'5':1.5,'6':2.}[key];self.speed_var.set(self.sim.speed)

    def set_height(self,value):
        self.sim.set_height(value);self.event=f'腿长指令 {value:.3f} m'

    def height_changed(self):
        if self.sim:self.set_height(self.height_var.get())

    def speed_changed(self,value):
        if self.sim:self.sim.speed=float(value)

    def jump(self):
        self.sim.jump();self.event='已请求起跳'

    def reset(self):
        self.keys.clear();self.sim.reset();self.deadline=time.perf_counter();self.event='已复位'

    def pause(self):
        self.keys.clear();self.sim.paused=not self.sim.paused;self.deadline=time.perf_counter();self.event='暂停' if self.sim.paused else '继续'

    def stop(self):
        self.keys.difference_update({'w','s','a','d'});self.event='停车'

    def load_scene(self):
        self.keys.clear();self.status_var.set('正在载入场景…');self.root.update_idletasks()
        if self.sim:self.sim.close()
        self.sim=SerialSimulation(self.scene_var.get());self.sim.speed=self.speed_var.get()
        self.height_var.set(self.sim.height)
        self.sim.viewer=mujoco.viewer.launch_passive(self.sim.m,self.sim.d,show_left_ui=False,show_right_ui=False)
        with self.sim.viewer.lock():
            cam=self.sim.viewer.cam;cam.lookat[:]=[.7,0,.25];cam.distance=4.0;cam.azimuth=135.;cam.elevation=-22.
        self.deadline=time.perf_counter();self.event='载入 '+self.scene_var.get()

    def tick(self):
        if self.closed:return
        if not self.sim.viewer.is_running():self.close();return
        try:
            while True:
                try:k,down=self.events.get_nowait()
                except queue.Empty:break
                self.on_key(k,down)
            if not self.focused():self.keys.clear()
            now=time.perf_counter();count=0
            with self.sim.viewer.lock():
                if self.sim.paused:self.deadline=now
                else:
                    while self.deadline<=time.perf_counter() and count<24:
                        self.sim.step(self.keys);self.deadline+=float(self.sim.m.opt.timestep);count+=1
                    if self.deadline<now-.12:self.deadline=now
                if self.follow_var.get():self.sim.viewer.cam.lookat[:]=self.sim.d.xpos[self.sim.base_id]+[.55,0,-.02]
            if now-self.last_draw>=.025:
                self.sim.viewer.sync();self.last_draw=now;self.update_ui()
            self.root.after(1,self.tick)
        except Exception:
            traceback.print_exc();self.close()

    def update_ui(self):
        s=self.sim.state()
        for key,value in {'z':f"{s['root_xyz'][2]:.3f} m",'vx':f"{s['vx']:+.2f} m/s",'pitch':f"{s['pitch_deg']:+.1f}°",'height':f"{s['height_command']:.3f} m",'legs':f"{s['leg_lengths'][0]:.3f} / {s['leg_lengths'][1]:.3f} m",'jump':PHASE.get(s['jump_phase'],s['jump_phase']),'climb':s['climb_phase'],'time':f"{s['time_s']:.1f} s"}.items():self.vars[key].set(value)
        self.height_var.set(s['height_command'])
        self.status_var.set(('暂停' if self.sim.paused else '运行中')+f"  |  指令 {s['cmd_vx']:+.2f} m/s / {s['cmd_wz']:+.2f} rad/s  |  "+self.event)
        now=time.perf_counter()
        if now-self.last_status>=.5:
            s.update(pid=os.getpid(),pressed=sorted(self.keys),event=self.event,updated_epoch=time.time())
            (LOCAL/'WASD_STATUS.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');self.last_status=now

    def close(self):
        if self.closed:return
        self.closed=True
        if hasattr(self,'listener'):self.listener.stop()
        if self.sim:self.sim.close()
        self.root.destroy()

def smoke():
    sim=SerialSimulation('7 cm 单台阶');phases=set();peak=float(sim.d.qpos[2]);initial=peak
    while sim.d.time<6.:
        if 2.<=sim.d.time<2.+float(sim.m.opt.timestep):sim.jump()
        sim.step(set());phases.add(sim.c.jump_state);peak=max(peak,float(sim.d.qpos[2]))
    result=dict(sim.state(),observed_jump_phases=sorted(phases),initial_height=initial,peak_height=peak,jump_triggered=sim.jump_cycles>0)
    sim.close();(LOCAL/'WASD_SMOKE.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))
    if not result['jump_triggered']:raise RuntimeError('Jump request did not reach the upstream controller')

if __name__=='__main__':
    try:
        if '--smoke' in sys.argv:smoke()
        else:root=tk.Tk();App(root);root.mainloop()
    except Exception:
        (LOCAL/'WASD_ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
