"""Manual terrain playback using the existing MOD4 keyboard/control framework."""
from pathlib import Path
import json,time,sys,subprocess,tkinter as tk
from tkinter import ttk
from showcase import Replay,B,CN,FAMILIES,EXPECTED
from play_ppo_flatv1_control import ControlApp

class ManualRoughControl(ControlApp):
    def _build(self):
        self.root.title('MOD4 Rough-v1 120m | 手动控制与站立高度')
        self.root.geometry('535x755+25+35');self.root.minsize(510,700)
        self.root.configure(bg=self.BG)
        self.status_var=tk.StringVar(value='已暂停，按 P 开始')
        self.family_var=tk.StringVar(value=CN[FAMILIES.index(self.sim.family)])
        self.level_var=tk.IntVar(value=self.sim.level)
        self.speed_var=tk.DoubleVar(value=self.sim.args.vx)
        self.turn_var=tk.DoubleVar(value=self.sim.args.wz)
        self._last_status_write=0.
        outer=tk.Frame(self.root,bg=self.BG,padx=14,pady=10);outer.pack(fill='both',expand=True)
        def label(text,**kw):
            return tk.Label(outer,text=text,bg=self.BG,fg=self.TEXT,font=('Microsoft YaHei UI',10),**kw)
        tk.Label(outer,text='Rough-v1 120m · 手动驾驶与高度控制',bg=self.BG,fg=self.CYAN,font=('Microsoft YaHei UI',15,'bold')).pack(anchor='w')
        label('先按 P 开始；点击本控制窗后使用键盘，松开运动键停车。').pack(anchor='w',pady=(4,7))
        row=tk.Frame(outer,bg=self.BG);row.pack(fill='x')
        tk.Label(row,text='地形',bg=self.BG,fg=self.TEXT).pack(side='left',padx=(0,5))
        ttk.Combobox(row,textvariable=self.family_var,values=CN,state='readonly',width=21,takefocus=False).pack(side='left')
        tk.Label(row,text='难度',bg=self.BG,fg=self.TEXT).pack(side='left',padx=(12,5))
        ttk.Combobox(row,textvariable=self.level_var,values=list(range(10)),state='readonly',width=4,takefocus=False).pack(side='left')
        row=tk.Frame(outer,bg=self.BG);row.pack(fill='x',pady=7)
        for text,direction in [('载入上台阶起点','up'),('载入下台阶起点','down'),('载入跑图起点','run')]:
            tk.Button(row,text=text,command=lambda d=direction:self.load_scene(d),takefocus=False).pack(side='left',expand=True,fill='x',padx=2)
        row=tk.Frame(outer,bg=self.BG);row.pack(fill='x')
        tk.Label(row,text='站立高度指令',bg=self.BG,fg=self.YELLOW,font=('Microsoft YaHei UI',11,'bold')).pack(side='left')
        self.height_value=tk.StringVar(value=f'{self.sim.height:.3f} m')
        tk.Label(row,textvariable=self.height_value,bg=self.BG,fg=self.YELLOW,font=('Consolas',12)).pack(side='right')
        self.height_scale=tk.Scale(outer,from_=.20,to=.42,resolution=.005,orient='horizontal',showvalue=False,command=self._height_changed,takefocus=False,bg=self.BG,fg=self.TEXT,troughcolor='#30363d',highlightthickness=0)
        self.height_scale.set(self.sim.height);self.height_scale.pack(fill='x')
        row=tk.Frame(outer,bg=self.BG);row.pack(fill='x',pady=(0,5))
        for text,height in [('1  0.20m',.20),('2  0.28m',.28),('3  0.40m',.40)]:
            tk.Button(row,text=text,command=lambda h=height:self.set_height(h),takefocus=False).pack(side='left',expand=True,fill='x',padx=2)
        row=tk.Frame(outer,bg=self.BG);row.pack(fill='x')
        for text,var,high in [('行驶速度 m/s',self.speed_var,2.2),('转向速度 rad/s',self.turn_var,14.1)]:
            frame=tk.Frame(row,bg=self.BG);frame.pack(side='left',fill='x',expand=True,padx=3)
            tk.Scale(frame,label=text,variable=var,from_=0,to=high,resolution=.1,orient='horizontal',length=225,takefocus=False,bg=self.BG,fg=self.TEXT,troughcolor='#30363d',highlightthickness=0).pack(fill='x')
        row=tk.Frame(outer,bg=self.BG);row.pack(pady=5)
        for text,key,r,c in [('W 前进','w',0,1),('A 左转','a',1,0),('S 后退','s',1,1),('D 右转','d',1,2)]:
            button=tk.Button(row,text=text,width=12,takefocus=False)
            button.grid(row=r,column=c,padx=3,pady=2)
            button.bind('<ButtonPress-1>',lambda event,k=key:self._handle_key_down(k))
            button.bind('<ButtonRelease-1>',lambda event,k=key:self._handle_key_up(k))
            button.bind('<Leave>',lambda event,k=key:self._handle_key_up(k))
        row=tk.Frame(outer,bg=self.BG);row.pack(fill='x',pady=4)
        for text,command in [('P 开始／暂停',self._toggle_pause),('空格 停车',self._stop),('R 重置起点',self.reset_scene)]:
            tk.Button(row,text=text,command=command,takefocus=False).pack(side='left',fill='x',expand=True,padx=2)
        self.status_label=tk.Label(outer,textvariable=self.status_var,justify='left',anchor='w',bg=self.PANEL,fg=self.CYAN,font=('Consolas',10),padx=10,pady=8)
        self.status_label.pack(fill='x',pady=7)
        label('Q / E 降低／升高；1 / 2 / 3 高度预设\nW / S 前后，A / D 转向；P 暂停，空格停车，R 复位',justify='left').pack(anchor='w')
        tk.Button(outer,text='打开完整地形地图',command=self.open_map,takefocus=False).pack(fill='x',pady=(7,0))
        self.root.bind('<FocusOut>',lambda event:self.keys.clear())

    def set_height(self,height):
        self.sim.set_height(height);self._sync_height_widgets();self._event(f'height {self.sim.height:.3f}m')

    def _handle_key_down(self,key):
        allowed={'w','s','a','d','q','e','1','2','3','4','5','6','p','r','space','escape'}
        if key not in allowed:return
        if key=='r':
            self.reset_scene();return
        super()._handle_key_down(key)
        if key in {'4','5','6'}:self.speed_var.set(self.sim.args.vx)

    def _global_release(self,key):
        # Release a held control even if focus moved to the camera window.
        ch=self._pynput_key(key)
        if ch is not None:self._key_queue.put((ch,False))
        return True

    def reset_scene(self):
        self.keys.clear();self.sim.reset_standing();self.sim.paused=True
        self._event('起点已重置，按 P 开始');self._focus_control()

    def load_scene(self,direction):
        family=FAMILIES[CN.index(self.family_var.get())];height=self.sim.height
        self.keys.clear();self.sim.close()
        self.sim=Replay(level=int(self.level_var.get()),family=family,direction=direction,show=True)
        self.sim.args.vx=float(self.speed_var.get());self.sim.args.wz=float(self.turn_var.get())
        self.sim.set_height(height);self.sim.paused=True
        self._event('场景已载入，按 P 开始');self._focus_control()
        print('MANUAL_SCENE_LOADED',json.dumps(dict(family=family,level=self.sim.level,direction=direction,paused=True)),flush=True)

    def open_map(self):
        subprocess.Popen([sys.executable,'-X','utf8','-u',str(B/'showcase.py'),'--mode','map'],cwd=B,stdout=(B/'map_manual.log').open('w'),stderr=subprocess.STDOUT,creationflags=0x08000000)

    def _update_ui(self):
        self.sim.args.vx=float(self.speed_var.get());self.sim.args.wz=float(self.turn_var.get())
        # The original input/controller handles the movement and Q/E height commands.
        if not self._is_control_foreground():
            self.keys.clear();self.sim.cmd_vx=0.;self.sim.cmd_vy=0.;self.sim.cmd_wz=0.
        self._sync_height_widgets()
        state='暂停：按 P 开始' if self.sim.paused else '运行：键盘／按钮手动控制'
        self.status_var.set(f'{state}\n前进指令 {self.sim.cmd_vx:+.2f} / 实速 {self.sim.env.vx:+.2f} m/s\n转向指令 {self.sim.cmd_wz:+.2f} rad/s\n站立高度指令 {self.sim.height:.3f} / 离地实测 {self.sim.z:.3f} m\n闭链 {self.sim.closure*1000:.3f} mm / 场景重置 {self.sim.reset_count-1}\n{self.last_event}')
        if self.sim.viewer is not None:
            x,y=self.sim.env.d.qpos[:2];self.sim.viewer.cam.lookat[:]=[x+.6,y,self.sim.ground(x,y)+.25]
        now=time.monotonic()
        if now-self._last_status_write>.5:
            value=dict(manual=True,autoplay=False,paused=self.sim.paused,family=self.sim.family,level=self.sim.level,keys=sorted(self.keys),height_command=self.sim.height,height_measured=self.sim.z,cmd_vx=self.sim.cmd_vx,cmd_wz=self.sim.cmd_wz,vx=float(self.sim.env.vx),physics_time=float(self.sim.env.d.time),closure=self.sim.closure,checkpoint_sha256=EXPECTED,epoch=time.time())
            (B/'MANUAL_STATUS.json').write_text(json.dumps(value),encoding='utf8');self._last_status_write=now


def run():
    root=tk.Tk();sim=Replay(show=True);sim.paused=True
    app=ManualRoughControl(root,sim)
    root.after(200,app._focus_control)
    print('MANUAL_PLAYER_READY',json.dumps(dict(paused=True,autoplay=False,height_range=[.2,.42],height=sim.height,checkpoint_sha256=EXPECTED)),flush=True)
    root.mainloop()

if __name__=='__main__':run()
