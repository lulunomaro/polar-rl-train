"""Native external MuJoCo OpenGL playground with a separate dark Livox Mid-360 LiDAR HUD."""
from nav_common import HERE,put,sha256
import argparse
import base64
import ctypes
from ctypes import wintypes
import io
import json
import math
import os
from pathlib import Path
import queue
import subprocess
import time
import tkinter as tk
from tkinter import ttk
import numpy as np
from PIL import Image
import mujoco as mj
import mujoco.viewer
from nav4d_runtime import Nav4DPolicy,Nav4DSimulation
from nav_maps import stage_scene

PLAYER_SUITES=(
 ('1 · RMUL2027 官方 3v3 全赛场 (Mid360先验+点云)','suite_rmul2027'),
 ('2 · RMUC2027 官方 5v5 全赛场 (Mid360先验+点云)','suite_rmuc2027'),
 ('3 · 综合试炼场 · 五车道','suite_proving'),
 ('4 · 200 mm 单阶','step_20'),('5 · +25° 斜向 200 mm','oblique_20'),
 ('6 · -25° 斜向 200 mm','oblique_20_negative'),('7 · 110 mm 路沿','curb_11'),
 ('8 · 西入口 400 mm 双阶','rm27_west_400'),('9 · 东入口 400 mm 双阶','rm27_east_400'),
 ('10 · 平地 0~3 m/s','flat'),('11 · L9 崎岖路面','rough_L9'))
VK={**{c:ord(c.upper()) for c in 'wasdqectvjrp'},'space':32,'escape':27}

def close_stale():
    user=ctypes.windll.user32
    command="[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; Get-CimInstance Win32_Process -Filter \"name = 'python.exe' OR name = 'pythonw.exe'\" | Select-Object ProcessId,ParentProcessId,CommandLine | ConvertTo-Json -Compress"
    raw=subprocess.check_output(['powershell.exe','-NoProfile','-Command',command],creationflags=subprocess.CREATE_NO_WINDOW,encoding='utf-8',errors='replace')
    records=json.loads((raw or '').strip() or '[]');records=records if isinstance(records,list) else [records]
    parent_map={int(r['ProcessId']):int(r.get('ParentProcessId') or 0) for r in records if r.get('ProcessId')}
    protect={os.getpid(),os.getppid()}
    cur=os.getpid()
    for _ in range(8):
        p=parent_map.get(cur,0)
        if not p or p in protect:break
        protect.add(p);cur=p
    ids={int(row['ProcessId']) for row in records if int(row['ProcessId']) not in protect and int(row.get('ParentProcessId') or 0) not in protect and
         any(tag in (row.get('CommandLine') or '') for tag in ('play_manual_fsm_wasd.py','play_lidar_nav_wasd.py'))}
    callback=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
    @callback
    def visit(hwnd,_):
        pid=wintypes.DWORD();user.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
        if pid.value in ids:user.PostMessageW(hwnd,0x0010,0,0)
        return True
    user.EnumWindows(visit,0)
    if ids:
        time.sleep(.35)
        for pid_old in ids:
            subprocess.run(['taskkill','/PID',str(pid_old),'/F'],creationflags=subprocess.CREATE_NO_WINDOW,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return sorted(ids)

class Playground:
    def __init__(self,course='suite_rmul2027',ui_smoke=False,sensor_mode='mid360_fusion',use_pcd_prior=False):
        self.root=tk.Tk();self.root.title('MOD4v3 · Mid-360 LiDAR 导航控制台')
        self.root.geometry('560x880+18+25');self.root.configure(bg='#111922');self.root.resizable(False,False)
        self.policy=Nav4DPolicy();self.sim=Nav4DSimulation(self.policy,sensor_mode=sensor_mode,use_pcd_prior=use_pcd_prior)
        self.viewer=None;self.events=queue.SimpleQueue();self.course=course;self.closed=False;self.ui_smoke=ui_smoke
        self.mission=[];self.last_keyset=set();self.status='就绪 · Mid-360点云在线，WASD 接管，Space 跳跃'
        self.user=ctypes.windll.user32
        self.user.GetForegroundWindow.restype=wintypes.HWND
        self.user.GetWindowThreadProcessId.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)]
        self.user.GetAsyncKeyState.argtypes=[ctypes.c_int];self.user.GetAsyncKeyState.restype=ctypes.c_short
        self.start=time.monotonic();self.next_tick=self.start;self.last_hud=0.;self.frame_count=0
        self.prev_e1=0.;self.prev_e2=0.;self.tilt_latched=False
        self.session_log=HERE/'evidence/PLAYER_SESSION_LOG.jsonl'
        self.input_audit=dict(native_focus_ticks=0,hud_focus_ticks=0,keyboard_dispatch_ticks=0,space_callbacks=0)
        self.make_hud();self.load_scene(course)
        self.log_event('session_start',stair_sha256=self.policy.sha,sensor_mode=sensor_mode,
            jump_sha256=sha256(self.policy.jump_checkpoint or HERE/'weights/jump_r10_donor.pt'))
        self.root.protocol('WM_DELETE_WINDOW',self.close)
        self.root.after(1,self.tick)
        if ui_smoke:self.root.after(55000,self.finish_ui_smoke)

    def log_event(self,event,**extra):
        if self.ui_smoke:return
        try:
            self.session_log.parent.mkdir(parents=True,exist_ok=True)
            if self.session_log.exists() and self.session_log.stat().st_size>5_000_000:
                bak=self.session_log.with_suffix('.prev.jsonl')
                bak.unlink(missing_ok=True);self.session_log.replace(bak)
            x,y,yaw=self.sim.pose();m=self.sim.measure()
            pc_pts=int(self.sim.mid360_detector.last_stair_pts_count) if self.sim.mid360_detector else 0
            row=dict(ts=round(time.time(),3),frame=self.frame_count,pid=os.getpid(),event=event,course=self.course,
                pose=[round(x,4),round(y,4),round(yaw,4)],vx=round(float(m['vx']),4),
                cmd_vx=round(float(self.sim.cmd_vx),4),max_vx=round(float(self.speed.get()),3),
                target_h=round(float(self.sim.target_h),4),body_h=round(float(m['body_height']),4),
                guide_low=round(float(m['guide_low']),4),pitch_deg=round(math.degrees(m['pitch']),2),
                roll_deg=round(math.degrees(m['roll']),2),g_step=[round(float(v),3) for v in self.sim.last_g],
                g_jump=[round(float(v),3) for v in self.sim.last_g_jump],mid360_stair_pts=pc_pts,
                route={k:int(v>0) for k,v in self.sim.route.items()},keys=sorted(self.last_keyset),**extra)
            with self.session_log.open('a',encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
        except OSError:pass

    def make_hud(self):
        style=ttk.Style(self.root);style.theme_use('clam')
        style.configure('TCombobox',fieldbackground='#20303e',background='#263e4e',foreground='#e2eef5',padding=4)
        style.map('TCombobox',fieldbackground=[('readonly','#20303e')],foreground=[('readonly','#e2eef5')])
        self.widgets=[]
        def label(text,font=('Microsoft YaHei UI',10),color='#d8e5ee'):
            w=tk.Label(self.root,text=text,bg='#111922',fg=color,font=font,anchor='w');w.pack(fill='x',padx=16,pady=2);self.widgets.append(w);return w
        label('MOD4v3  /  Livox Mid-360 NAV',('Segoe UI',17,'bold'),'#7fe1db')
        self.scene_box=ttk.Combobox(self.root,state='readonly',values=[n for n,_ in PLAYER_SUITES],font=('Microsoft YaHei UI',10))
        self.scene_box.current(next(i for i,(_,c) in enumerate(PLAYER_SUITES) if c==self.course));self.scene_box.pack(fill='x',padx=16,pady=5)
        self.scene_box.bind('<<ComboboxSelected>>',lambda _:self.load_scene(PLAYER_SUITES[self.scene_box.current()][1]));self.widgets.append(self.scene_box)
        self.spawn_box=ttk.Combobox(self.root,state='readonly',font=('Microsoft YaHei UI',10));self.spawn_box.pack(fill='x',padx=16,pady=3)
        self.spawn_box.bind('<<ComboboxSelected>>',lambda _:self.reset());self.widgets.append(self.spawn_box)
        row=tk.Frame(self.root,bg='#111922');row.pack(fill='x',padx=16,pady=5);self.widgets.append(row)
        for text,fn in [('自动冲占中央高地',self.assault),('全图巡航跑图',self.patrol),('停车 / 复位',self.reset)]:
            tk.Button(row,text=text,command=fn,bg='#254454',fg='#e2f6f5',activebackground='#346578',relief='flat',font=('Microsoft YaHei UI',10),padx=8,pady=7).pack(side='left',expand=True,fill='x',padx=2)
        self.pose_label=label('x 0.00   y 0.00   yaw 0°',('Consolas',11))
        self.g_label=label('g_step  [2.30, 0.00, 1.60, 0.00] m',('Consolas',10),'#7fe1db')
        self.route_label=label('E0 · 纯巡航',('Microsoft YaHei UI',10),'#b3c3ce')
        self.canvas=tk.Canvas(self.root,width=524,height=326,bg='#19232e',highlightthickness=0)
        self.canvas.pack(padx=16,pady=7);self.canvas.bind('<Button-1>',self.map_click);self.widgets.append(self.canvas)
        self.speed=tk.DoubleVar(value=1.0);self.height=tk.DoubleVar(value=.28)
        for title,var,low,high,res in [('速度 / m·s⁻¹',self.speed,.0,3.,.05),('站高 / m',self.height,.20,.42,.001)]:
            frame=tk.Frame(self.root,bg='#111922');frame.pack(fill='x',padx=16,pady=1);self.widgets.append(frame)
            tk.Label(frame,text=title,bg='#111922',fg='#d8e5ee',width=13,anchor='w',font=('Microsoft YaHei UI',10)).pack(side='left')
            tk.Scale(frame,variable=var,from_=low,to=high,resolution=res,orient='horizontal',length=370,bg='#111922',fg='#e1f4f2',
                highlightthickness=0,troughcolor='#31424e',activebackground='#54b3b0',font=('Consolas',10)).pack(side='right')
        toggles=tk.Frame(self.root,bg='#111922');toggles.pack(fill='x',padx=16,pady=5);self.widgets.append(toggles)
        self.assist=tk.BooleanVar(value=True);self.follow=tk.BooleanVar(value=True);self.show_cloud=tk.BooleanVar(value=True)
        tk.Checkbutton(toggles,text='地形辅助 T',variable=self.assist,command=lambda:setattr(self.policy,'assist',self.assist.get()),
            bg='#111922',fg='#e5eef5',selectcolor='#253c4c',activebackground='#111922',activeforeground='#e5eef5').pack(side='left')
        tk.Checkbutton(toggles,text='跟随镜头',variable=self.follow,bg='#111922',fg='#e5eef5',selectcolor='#253c4c',
            activebackground='#111922',activeforeground='#e5eef5').pack(side='left',padx=10)
        tk.Checkbutton(toggles,text='Mid360点云 P',variable=self.show_cloud,bg='#111922',fg='#7fe1db',selectcolor='#253c4c',
            activebackground='#111922',activeforeground='#7fe1db').pack(side='left',padx=6)
        self.status_label=label(self.status,('Microsoft YaHei UI',9),'#9fb7c7');self.status_label.configure(wraplength=520)
        label('WASD 驾驶  ·  Space / J 跳跃  ·  Q/E 站高\nT 辅助  ·  P 点云显示  ·  R 复位  ·  点击地图导航',('Microsoft YaHei UI',10),'#7b96a8')

    def load_scene(self,course):
        if self.viewer is not None:self.viewer.close();self.viewer=None
        self.course=course;self.sim.load_scene(course,height=self.height.get());self.mission=[]
        self.spawn_box.configure(values=[s['name'] for s in self.sim.scene_meta['spawns']]);self.spawn_box.current(0)
        self.viewer=mj.viewer.launch_passive(self.sim.m,self.sim.d,show_left_ui=False,show_right_ui=False,key_callback=self.on_native_key)
        with self.viewer.lock():
            self.viewer.opt.geomgroup[3]=0 if course=='suite_rmul2027' else 1
            self.viewer.opt.geomgroup[4]=1
            if self.sim.scene_meta.get('hide_group5'):self.viewer.opt.geomgroup[5]=0
            self.viewer.cam.distance=3.5;self.viewer.cam.azimuth=135.;self.viewer.cam.elevation=-26.
        self.root.after(200,self.position_native);self.draw_heatmap();self.next_tick=time.monotonic()
        self.status='Mid-360 先验图+实时点云已加载；点击地图自动导航或 WASD 接管'

    def on_native_key(self,key):
        if key in (32,ord('J')):self.events.put('jump');self.input_audit['space_callbacks']+=1
        elif key==ord('R'):self.events.put('reset')
        elif key==ord('T'):self.events.put('toggle_assist')
        elif key==ord('P'):self.events.put('toggle_cloud')

    def position_native(self):
        self.root.deiconify();self.root.update_idletasks()
        self.user.GetAncestor.argtypes=[wintypes.HWND,wintypes.UINT];self.user.GetAncestor.restype=wintypes.HWND
        self.user.ShowWindow.argtypes=[wintypes.HWND,ctypes.c_int]
        self.user.SetWindowPos.argtypes=[wintypes.HWND,wintypes.HWND,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,wintypes.UINT]
        self.user.GetWindowTextW.argtypes=[wintypes.HWND,wintypes.LPWSTR,ctypes.c_int]
        self.user.GetWindowRect.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.RECT)]
        self.user.ShowWindow(self.user.GetAncestor(self.root.winfo_id(),2),1)
        windows=[]
        callback=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
        @callback
        def visit(hwnd,_):
            pid=wintypes.DWORD();self.user.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
            if pid.value==os.getpid():
                text=ctypes.create_unicode_buffer(256);self.user.GetWindowTextW(hwnd,text,256)
                if 'MuJoCo' in text.value:
                    self.user.ShowWindow(hwnd,1);self.user.SetWindowPos(hwnd,0,582,25,1310,960,0x0004)
                if text.value:
                    rect=wintypes.RECT();self.user.GetWindowRect(hwnd,ctypes.byref(rect))
                    windows.append(dict(title=text.value,visible=bool(self.user.IsWindowVisible(hwnd)),hwnd=int(hwnd),
                        rect=[rect.left,rect.top,rect.right-rect.left,rect.bottom-rect.top]))
            return True
        self.user.EnumWindows(visit,0)
        put(HERE/'evidence/PLAYER_WINDOWS.json',dict(pid=os.getpid(),windows=windows))

    def poll_keys(self):
        hwnd=self.user.GetForegroundWindow();pid=wintypes.DWORD();self.user.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
        if pid.value!=os.getpid():return set()
        text=ctypes.create_unicode_buffer(256);self.user.GetWindowTextW(hwnd,text,256)
        field='native_focus_ticks' if 'MuJoCo' in text.value else 'hud_focus_ticks'
        self.input_audit[field]+=1
        keys=set()
        for k,v in VK.items():
            st=self.user.GetAsyncKeyState(v)
            if (st&0x8000) or (k in ('space','j','t','r','c','p') and (st&0x0001)):keys.add(k)
        if keys:self.input_audit['keyboard_dispatch_ticks']+=1
        return keys

    def reset(self):
        self.sim.target_h=self.height.get();self.sim.reset_at_spawn(max(0,self.spawn_box.current()));self.mission=[]
        self.prev_e1=0.;self.prev_e2=0.;self.tilt_latched=False
        self.status='已复位 · 直接驾驶或点击地图';self.log_event('reset')

    def goals(self):
        if self.course=='suite_rmul2027':return [(-2.5,.8),(-2.5,2.1),(-4.7,2.1),(-4.9,-2.3)]
        if self.course=='suite_rmuc2027':return [(-14.0,-4.80),(-13.6,-4.45),(-16.8,-4.85)]
        return [(4.,0.),(-1.,0.)]
    def assault(self):self.mission=[];self.dispatch(*self.goals()[0])
    def patrol(self):
        self.mission=self.goals();goal=self.mission.pop(0);self.dispatch(*goal)
    def dispatch(self,x,y):
        try:
            self.sim.navigate_to(x,y,min(1.2,max(.45,self.speed.get())))
            self.status=f'自动导航 → ({x:.2f}, {y:.2f}) · WASD 接管'
        except ValueError as error:self.status=str(error)
    def map_click(self,event):
        x,y=self.from_canvas(event.x,event.y);self.mission=[];self.dispatch(x,y)

    def draw_heatmap(self):
        m=self.sim.elevation;h=m.h
        self.scale=min(512/(m.x[-1]-m.x[0]),310/(m.y[-1]-m.y[0]))
        self.map_w=int((m.x[-1]-m.x[0])*self.scale);self.map_h=int((m.y[-1]-m.y[0])*self.scale)
        self.map_left=(524-self.map_w)/2;self.map_top=(326-self.map_h)/2
        t=np.clip(np.nan_to_num(h,nan=0.)/.5,0,1)
        colors=np.stack((30+65*t,52+132*t,66+95*t),-1).astype(np.uint8)
        colors[m.blocked|~m.traversable]=[65,68,85];colors[m.semantic==2]=[68,145,140];colors[~m.valid]=[17,25,34]
        image=Image.fromarray(colors[::-1]).resize((self.map_w,self.map_h),Image.Resampling.NEAREST)
        buffer=io.BytesIO();image.save(buffer,format='PNG')
        self.map_image=tk.PhotoImage(data=base64.b64encode(buffer.getvalue()).decode('ascii'))
        self.canvas.delete('all');self.canvas.create_image(self.map_left,self.map_top,image=self.map_image,anchor='nw',tags='heatmap')
    def to_canvas(self,x,y):
        m=self.sim.elevation;return self.map_left+(x-m.x[0])*self.scale,self.map_top+(m.y[-1]-y)*self.scale
    def from_canvas(self,x,y):
        m=self.sim.elevation;return m.x[0]+(x-self.map_left)/self.scale,m.y[-1]-(y-self.map_top)/self.scale

    def draw_markers(self):
        self.canvas.delete('live');path=self.sim.planned_path
        det=self.sim.mid360_detector
        if det is not None and det.dyn_blocked is not None and det.last_dyn_cells_count>0:
            ys,xs=np.nonzero(det.dyn_blocked)
            for iy,ix in zip(ys[::8],xs[::8]):
                cx,cy=self.to_canvas(float(self.sim.elevation.x[ix]),float(self.sim.elevation.y[iy]))
                self.canvas.create_rectangle(cx-2,cy-2,cx+2,cy+2,fill='#ff5964',outline='',tags='live')
        if len(path)>1:
            points=[v for p in path for v in self.to_canvas(*p)];self.canvas.create_line(*points,fill='#61deb2',width=2,tags='live')
        x,y,yaw=self.sim.pose();px,py=self.to_canvas(x,y)
        self.canvas.create_oval(px-4,py-4,px+4,py+4,fill='#fbdf7c',outline='',tags='live')
        self.canvas.create_line(px,py,px+14*math.cos(yaw),py-14*math.sin(yaw),fill='#fbdf7c',width=3,tags='live')
        with self.viewer.lock():
            scn=self.viewer.user_scn;scn.ngeom=0
            for i,p in enumerate(path[:220]):
                z=float(self.sim.elevation.sample(*p))+.035
                if not np.isfinite(z):continue
                mj.mjv_initGeom(scn.geoms[scn.ngeom],mj.mjtGeom.mjGEOM_SPHERE,np.array([.028]*3),np.array([*p,z]),np.eye(3).ravel(),np.array([.2,.95,.65,.9],np.float32));scn.ngeom+=1
                if i and scn.ngeom<scn.maxgeom:
                    q=path[i-1];qz=float(self.sim.elevation.sample(*q))+.035
                    mj.mjv_initGeom(scn.geoms[scn.ngeom],mj.mjtGeom.mjGEOM_LINE,np.zeros(3),np.zeros(3),np.eye(3).ravel(),np.array([.2,.95,.65,.8],np.float32))
                    mj.mjv_connector(scn.geoms[scn.ngeom],mj.mjtGeom.mjGEOM_LINE,3.,np.array([*q,qz]),np.array([*p,z]));scn.ngeom+=1
            for d,h in np.asarray(self.sim.last_g).reshape(2,2):
                if h>.06 and scn.ngeom<scn.maxgeom:
                    xx=x+float(d)*math.cos(yaw);yy=y+float(d)*math.sin(yaw);zz=float(self.sim.elevation.sample(xx,yy))+.06
                    mj.mjv_initGeom(scn.geoms[scn.ngeom],mj.mjtGeom.mjGEOM_SPHERE,np.array([.055]*3),np.array([xx,yy,zz]),np.eye(3).ravel(),np.array([.15,.9,1.,.9],np.float32));scn.ngeom+=1
            gj=self.sim.last_g_jump
            if float(self.sim.last_g[1])<=.05 and float(gj[2])>.08 and float(gj[0])<=2.20 and scn.ngeom<scn.maxgeom:
                xx=x+float(gj[0])*math.cos(yaw);yy=y+float(gj[0])*math.sin(yaw)
                base_z=float(self.sim.elevation.sample(x,y))
                zz=(base_z if np.isfinite(base_z) else 0.)+float(gj[2])+.04
                mj.mjv_initGeom(scn.geoms[scn.ngeom],mj.mjtGeom.mjGEOM_SPHERE,np.array([.055]*3),np.array([xx,yy,zz]),np.eye(3).ravel(),np.array([1.,.58,.15,.92],np.float32));scn.ngeom+=1
            # Render live subsampled 3D Livox Mid-360 point cloud around robot (`P` toggle)
            if self.show_cloud.get() and det is not None and len(det.last_points_world)>0:
                pw=det.last_points_world
                d2=(pw[:,0]-x)**2+(pw[:,1]-y)**2
                near=pw[(d2<=9.5)&(pw[:,2]<=1.05)]
                if len(near)>0:
                    step_k=max(1,len(near)//110)
                    z0=float(self.sim.ground_z(x,y))
                    eye9=np.eye(3).ravel()
                    sz_pt=np.array([.014,.014,.014])
                    for pt in near[::step_k]:
                        if scn.ngeom>=scn.maxgeom-4:break
                        rz=float(pt[2])-z0
                        if .06<=rz<=.265:rgba=np.array([.18,.95,1.,.85],np.float32)
                        elif .265<rz<=.415:rgba=np.array([1.,.64,.18,.88],np.float32)
                        elif rz>.415:rgba=np.array([1.,.34,.38,.82],np.float32)
                        else:rgba=np.array([.35,.82,.68,.55],np.float32)
                        mj.mjv_initGeom(scn.geoms[scn.ngeom],mj.mjtGeom.mjGEOM_SPHERE,sz_pt,pt.astype(np.float64),eye9,rgba);scn.ngeom+=1
            if self.follow.get():self.viewer.cam.lookat[:]=[x,y,float(self.sim.d.qpos[2])+.05]

    def tick(self):
        if self.closed:return
        try:
            while not self.events.empty():
                event=self.events.get()
                if event=='jump':self.sim.request_jump()
                elif event=='reset':self.reset()
                elif event=='toggle_assist':self.policy.assist=not self.policy.assist;self.assist.set(self.policy.assist)
                elif event=='toggle_cloud':self.show_cloud.set(not self.show_cloud.get())
            now=time.monotonic()
            if now>=self.next_tick:
                keys=self.poll_keys()
                if 'escape' in keys:self.close();return
                if 'r' in keys and 'r' not in self.last_keyset:self.reset()
                if 'p' in keys and 'p' not in self.last_keyset:self.show_cloud.set(not self.show_cloud.get())
                self.last_keyset=keys
                self.sim.max_vx=self.speed.get();self.sim.target_h=self.height.get()
                self.sim.step(keys);self.height.set(round(self.sim.target_h,4))
                self.assist.set(self.policy.assist);self.frame_count+=1
                e1_now=float(self.sim.route['e1']);e2_now=float(self.sim.route['e2'])
                if e1_now>.5 and self.prev_e1<=.5:self.log_event('stair_enter')
                elif e1_now<=.5 and self.prev_e1>.5:self.log_event('stair_exit')
                if e2_now>.5 and self.prev_e2<=.5:self.log_event('jump_enter')
                self.prev_e1=e1_now;self.prev_e2=e2_now
                if self.frame_count%25==0:
                    m_chk=self.sim.measure()
                    high_tilt=abs(math.degrees(m_chk['pitch']))>35. or abs(math.degrees(m_chk['roll']))>30.
                    if high_tilt and not self.tilt_latched:self.tilt_latched=True;self.log_event('high_tilt_alert')
                    elif not high_tilt:self.tilt_latched=False
                    if keys or abs(m_chk['vx'])>.08:self.log_event('sample')
                if self.sim.follower is not None and self.sim.follower.done and self.mission:
                    self.dispatch(*self.mission.pop(0))
                if self.viewer is not None:
                    if self.follow.get():
                        with self.viewer.lock():
                            self.viewer.cam.lookat[:]=[float(self.sim.d.qpos[0]),float(self.sim.d.qpos[1]),float(self.sim.d.qpos[2])+.05]
                    self.viewer.sync()
                self.next_tick=max(self.next_tick+.02,now-.04)
                if now-self.last_hud>=.08:
                    x,y,yaw=self.sim.pose();m=self.sim.measure();g=self.sim.last_g;gj=self.sim.last_g_jump
                    pc_pts=int(self.sim.mid360_detector.last_stair_pts_count) if self.sim.mid360_detector else 0
                    self.pose_label.configure(text=f'x {x:+6.2f}   y {y:+6.2f}   yaw {math.degrees(yaw):+5.0f}°   ·   Mid360台阶点 {pc_pts}')
                    if self.sim.route['e2'] or (g[1]<=.05 and gj[2]>.08 and gj[0]<=2.20):
                        self.g_label.configure(text=f'g_jump [{gj[0]:+.2f}, {gj[1]:+.2f}, {gj[2]:.2f}, {gj[3]:.2f}] m · Space 跳跃',fg='#f7b267')
                    else:
                        self.g_label.configure(text=f'g_step [{g[0]:+.2f}, {g[1]:.2f}, {g[2]:+.2f}, {g[3]:.2f}] m',fg='#7fe1db')
                    route='E_jump_unified' if self.sim.route['e2'] else 'E_stair_nav4d' if self.sim.route['e1'] else 'SymmetricE0'
                    self.route_label.configure(text=f'{route}  ·  v {m["vx"]:+.2f} m/s  ·  h {m["body_height"]:.2f} m  ·  pitch {math.degrees(m["pitch"]):+.1f}°')
                    self.status_label.configure(text=self.status);self.draw_markers();self.last_hud=now
                    if self.frame_count%50<4:
                        put(HERE/'evidence/PLAYER_TELEMETRY.json',dict(course=self.course,pose=[x,y,yaw],
                            vx=float(m['vx']),max_vx=float(self.speed.get()),target_h=float(self.sim.target_h),
                            body_height=float(m['body_height']),pitch_deg=math.degrees(m['pitch']),
                            roll_deg=math.degrees(m['roll']),g_step=[float(v) for v in g],
                            mid360_stair_pts=pc_pts,sensor_mode=self.sim.sensor_mode,
                            stair_sha256=self.policy.sha,input_audit=self.input_audit,route=self.sim.route,
                            frame_count=self.frame_count,native_user_geoms=self.viewer.user_scn.ngeom))
            if self.viewer is not None and not self.viewer.is_running():self.close();return
        except Exception as error:
            import traceback
            put(HERE/'evidence/PLAYER_ERROR.json',dict(error=str(error),traceback=traceback.format_exc()))
            self.status_label.configure(text=str(error));self.close();raise
        self.root.after(1,self.tick)

    def finish_ui_smoke(self):
        self.root.update_idletasks();clipped=[]
        for w in self.widgets:
            if w.winfo_y()+w.winfo_height()>self.root.winfo_height() or w.winfo_x()+w.winfo_width()>self.root.winfo_width():clipped.append(w.winfo_class())
        windows=json.loads((HERE/'evidence/PLAYER_WINDOWS.json').read_text(encoding='utf-8'))['windows']
        actual=next((w['rect'] for w in windows if 'MuJoCo' in w['title']),None)
        put(HERE/'evidence/UI_SMOKE.json',dict(passed=not clipped and self.viewer.is_running() and actual==[582,25,1310,960],clipped_widgets=clipped,
            external_mujoco_viewer_running=self.viewer.is_running(),hud_size=[self.root.winfo_width(),self.root.winfo_height()],
            frame_count=self.frame_count,input_audit=self.input_audit,native_requested_rect=[582,25,1310,960],
            native_actual_rect=actual,stair_sha256=self.policy.sha,
            jump_sha256=sha256(self.policy.jump_checkpoint or HERE/'weights/jump_r10_donor.pt'),
            two_dimensional_canvas_only=True,native_user_geoms=self.viewer.user_scn.ngeom))
        self.close()
    def close(self):
        if self.closed:return
        self.closed=True
        if self.viewer is not None:self.viewer.close()
        self.root.destroy()

def smoke():
    policy=Nav4DPolicy();sim=Nav4DSimulation(policy);rows=[]
    for _,course in PLAYER_SUITES[:3]:
        start=time.perf_counter();sim.load_scene(course);load=time.perf_counter()-start
        for _ in range(50):sim.step(set(),command=(0.,0.))
        m=sim.measure();rows.append(dict(course=course,load_s=load,finite=bool(np.isfinite(sim.d.qpos).all()),
            pitch_deg=math.degrees(m['pitch']),route=sim.route,body_height=m['body_height'],
            mid360_pts=int(len(sim.mid360_detector.last_points_world)) if sim.mid360_detector else 0))
    result=dict(passed=all(r['finite'] for r in rows),scenes=rows)
    put(HERE/'evidence/SMOKE.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--course',default='suite_rmul2027');p.add_argument('--smoke',action='store_true')
    p.add_argument('--ui-smoke',action='store_true');p.add_argument('--close-stale',action='store_true')
    p.add_argument('--sensor-mode',choices=('mid360_fusion','mid360_online','prior_only'),default='mid360_fusion')
    p.add_argument('--pcd-prior',action='store_true',help='Load pre-built Mid-360 .pcd reconstructed 2.5D map')
    args=p.parse_args()
    if args.close_stale:close_stale()
    if args.smoke:smoke()
    else:app=Playground(args.course,args.ui_smoke,sensor_mode=args.sensor_mode,use_pcd_prior=args.pcd_prior);app.root.mainloop()
