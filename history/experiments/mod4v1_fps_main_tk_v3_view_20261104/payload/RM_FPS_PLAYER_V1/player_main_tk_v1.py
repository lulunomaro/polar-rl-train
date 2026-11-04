"""Main-thread Tk / worker-owned GLFW+MuJoCo. Reuses frozen FPS layout/render/control.
No Tk widget/Variable crosses the renderer boundary; messages carry plain values.
"""
import os
for _name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[_name]='1'
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
import collections
import gc
import math
import queue
import threading
import time
import traceback
import tkinter as tk
import numpy as np
import glfw
import mujoco
from RM_FPS_PLAYER_V1.player import Player as FrozenPlayer, SCENES, CONTROLLERS, wrap
from RM_FPS_PLAYER_V1.runtime import Engine
from sensor_core_v4 import rpy


class Player(FrozenPlayer):
    def __init__(self,scene='latest_rm',difficulty=.5,seed=9001,controller='c2_fps',hidden_smoke_seconds=0.):
        if threading.current_thread() is not threading.main_thread():
            raise RuntimeError('Create Tk on the process main thread')
        self.tk_owner=threading.get_ident()
        self.hidden_smoke_seconds=float(hidden_smoke_seconds)
        self.actions=collections.deque();self.ui_messages=queue.SimpleQueue()
        self.worker_done=threading.Event();self.worker_error=''
        self.running=True;self.captured=False;self.first_person=False;self.overview=False
        self.virtual=set();self.blocked=False;self.mouse_last=None;self.heading=0.
        self.view_pitch=math.radians(-17.);self.distance=2.25
        self.forward=self.yaw_rate=0.;self.frames=0;self.fps=0.;self.error=''
        self.context=None;self.window=None;self.engine=None;self.controller_mode=controller
        self.worker=None;self.map_snapshot=None
        self.ui_input=dict(speed=1.,sensitivity=.15,scene=scene,difficulty=float(difficulty),
                           seed=str(seed),controller=controller,zone=0)
        # Existing layout only; never call the old constructor/worker-Tk lifecycle.
        self._build_panel(100,45,760,scene,difficulty,seed)
        if self.hidden_smoke_seconds:self.panel.withdraw()
        self.panel.report_callback_exception=self._tk_exception
        for variable in (self.speed_var,self.sensitivity_var,self.scene_var,self.level_var,
                         self.seed_var,self.controller_var,self.zone_var):
            variable.trace_add('write',self._publish_inputs)
        self._publish_inputs()
        self.start_args=(scene,float(difficulty),int(seed))
        print(f'TK_OWNER_READY main_thread={self.tk_owner} hidden={bool(self.hidden_smoke_seconds)}',flush=True)

    def _assert_tk_owner(self):
        if threading.get_ident()!=self.tk_owner:raise RuntimeError('Cross-thread Tk operation')

    def _publish_inputs(self,*unused):
        self._assert_tk_owner()
        # Publish a new dictionary, never mutate the worker's captured snapshot.
        self.ui_input=dict(speed=float(self.speed_var.get()),sensitivity=float(self.sensitivity_var.get()),
            scene=SCENES[self.scene_var.get()],difficulty=float(self.level_var.get()),seed=self.seed_var.get(),
            controller=CONTROLLERS[self.controller_var.get()],zone=max(0,self.zone_box.current()))

    def _post_ui(self,kind,value):
        self.ui_messages.put((kind,value))

    def _tk_exception(self,kind,value,tb):
        self._assert_tk_owner();traceback.print_exception(kind,value,tb)
        self.worker_error='Tk callback: '+str(value);self.close()

    def close(self):
        # Neither thread destroys the other's native resources. Main pump waits
        # for worker cleanup before destroying Tcl, including the WM-close path.
        self.running=False

    def _initialize_view(self,scene,difficulty,seed):
        if not glfw.init():raise RuntimeError('GLFW initialization failed')
        mode=glfw.get_video_mode(glfw.get_primary_monitor())
        sw,sh=mode.size if mode is not None else (1600,900)
        width,height=max(720,min(1280,sw-405)),max(560,min(900,sh-120))
        glfw.window_hint(glfw.SAMPLES,4)
        if self.hidden_smoke_seconds:
            glfw.window_hint(glfw.VISIBLE,glfw.FALSE)
            glfw.window_hint(glfw.FOCUSED,glfw.FALSE)
            glfw.window_hint(glfw.FOCUS_ON_SHOW,glfw.FALSE)
        self.window=glfw.create_window(width,height,'MOD4v1 | RM FPS | BODY-FIRST LQR',None,None)
        if not self.window:raise RuntimeError('GLFW window creation failed')
        glfw.set_window_pos(self.window,10,45);glfw.make_context_current(self.window);glfw.swap_interval(0)
        glfw.set_key_callback(self.window,self.on_key);glfw.set_cursor_pos_callback(self.window,self.on_mouse)
        glfw.set_mouse_button_callback(self.window,self.on_mouse_button);glfw.set_scroll_callback(self.window,self.on_scroll)
        glfw.set_window_focus_callback(self.window,self.on_focus)
        self._post_ui('geometry',f'365x{height}+{width+25}+45')
        self.load_scene(scene,difficulty,seed)
        self.camera=mujoco.MjvCamera();mujoco.mjv_defaultCamera(self.camera)
        self.camera.type=mujoco.mjtCamera.mjCAMERA_FREE
        self.option=mujoco.MjvOption();mujoco.mjv_defaultOption(self.option)
        self.option.flags[mujoco.mjtVisFlag.mjVIS_JOINT]=False
        self.option.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT]=False
        if not self.hidden_smoke_seconds:glfw.focus_window(self.window)
        self._post_ui('ready',True)
        print(f'RM_FPS_READY pid={os.getpid()} scene={scene} controller={self.controller_mode} '
              f'worker_thread={threading.get_ident()} hidden={bool(self.hidden_smoke_seconds)}',flush=True)

    def load_scene(self,scene,difficulty,seed):
        self.release_mouse()
        new_engine=Engine(scene,difficulty,seed,controller_mode=self.controller_mode)
        if self.hidden_smoke_seconds:new_engine.paused=True
        glfw.make_context_current(self.window)
        if self.context is not None:self.context.free()
        self.engine=new_engine;self.engine.plant.m.vis.map.znear=.0002
        self.context=mujoco.MjrContext(self.engine.plant.m,mujoco.mjtFontScale.mjFONTSCALE_150)
        self.render_scene=mujoco.MjvScene(self.engine.plant.m,maxgeom=12000)
        self.heading=self.engine.estimated_yaw();self.error=''
        self._post_ui('zones',[z['label'] for z in self.engine.meta['zones']])
        self._post_ui('message',('已载入最新碰撞修正版 RMUC 全场。' if scene=='latest_rm' else '场景已载入。')+'站姿复位是交互起点，不计作自主起立。')
        print(f'SCENE_LOADED {scene} difficulty={difficulty:.3f} seed={seed} '
              f'ngeom={self.engine.plant.m.ngeom} nq={self.engine.plant.m.nq}',flush=True)

    def capture_mouse(self):
        glfw.focus_window(self.window);self.captured=True;self.overview=False;self.mouse_last=None
        glfw.set_input_mode(self.window,glfw.CURSOR,glfw.CURSOR_DISABLED)
        if glfw.raw_mouse_motion_supported():glfw.set_input_mode(self.window,glfw.RAW_MOUSE_MOTION,True)
        self._post_ui('message','鼠标已锁定：左右控制朝向，上下控制视角。Esc 释放。')

    def on_mouse(self,window,x,y):
        if not self.captured:self.mouse_last=None;return
        if self.mouse_last is not None:
            dx,dy=x-self.mouse_last[0],y-self.mouse_last[1]
            sensitivity=math.radians(self.ui_input['sensitivity'])
            self.heading-=dx*sensitivity
            self.view_pitch=float(np.clip(self.view_pitch-dy*sensitivity,-1.15,.85))
        self.mouse_last=(x,y)

    def on_key(self,window,key,scancode,action,mods):
        if key==glfw.KEY_TAB and action==glfw.PRESS:
            self.release_mouse();self._post_ui('show_panel',None)
        else:super().on_key(window,key,scancode,action,mods)

    def handle_actions(self):
        while self.actions:
            action,value=self.actions.popleft();ui=self.ui_input
            print(f'UI_ACTION {action} value={value} sim_t={self.engine.plant.d.time:.2f}',flush=True)
            if action=='scene':
                try:self.load_scene(ui['scene'],ui['difficulty'],int(ui['seed']))
                except Exception as exc:
                    self.error=str(exc);self._post_ui('message','场景载入出错：'+str(exc));traceback.print_exc()
            elif action=='controller':
                self.controller_mode=ui['controller'];self.engine.controller_mode=self.controller_mode
                self.engine.reset(self.engine.zone);self.heading=0.;self.forward=self.yaw_rate=0.
                if self.hidden_smoke_seconds:self.engine.paused=True
                self.error='';self._post_ui('message','已应用 '+self.controller_mode+' 并按用户操作复位；不代表新技能验收。')
            elif action=='reset':
                self.engine.reset(max(0,ui['zone'] if value is None else int(value)))
                if self.hidden_smoke_seconds:self.engine.paused=True
                self.heading=0.;self.forward=self.yaw_rate=0.;self.error=''
                self._post_ui('message','已按用户操作复位至地形入口。')
            elif action=='jump':
                self.engine.request_jump();self._post_ui('message',self.engine.jump_message)
            elif action=='pause':
                if not self.engine.fault and not self.hidden_smoke_seconds:self.engine.paused=not self.engine.paused
            elif action=='camera':self.first_person=not self.first_person;self.overview=False
            elif action=='overview':
                self.overview=not self.overview
                if self.overview:self.release_mouse()
            elif action=='brake':
                self.blocked=True;self.virtual.clear();self.heading=self.engine.estimated_yaw();self.forward=self.yaw_rate=0.
            elif action=='capture':self.capture_mouse()

    def controls(self):
        focused=bool(glfw.get_window_attrib(self.window,glfw.FOCUSED))
        if not focused and not self.virtual:return 0.,0.
        key=lambda k:(focused and glfw.get_key(self.window,k) in (glfw.PRESS,glfw.REPEAT)) or (k<128 and chr(k) in self.virtual)
        if not any(key(k) for k in (glfw.KEY_W,glfw.KEY_A,glfw.KEY_S,glfw.KEY_D)):self.blocked=False
        if self.blocked:return 0.,0.
        self.heading+=(int(key(glfw.KEY_A))-int(key(glfw.KEY_D)))*1.5*.01
        boost=key(glfw.KEY_LEFT_SHIFT) or key(glfw.KEY_RIGHT_SHIFT)
        speed=2. if boost else self.ui_input['speed']
        v=speed*(int(key(glfw.KEY_W))-int(key(glfw.KEY_S)))
        w=float(np.clip(3.*wrap(self.heading-self.engine.estimated_yaw()),-1.5,1.5))
        w=float(np.clip(w,-min(1.5,1.6/max(abs(v),.25)),min(1.5,1.6/max(abs(v),.25))))
        if key(glfw.KEY_X):v=w=0.;self.heading=self.engine.estimated_yaw()
        return v,w

    def update_panel(self):
        p=self.engine.plant;shown=np.rad2deg(rpy(p.d.qpos[3:7]));e=self.engine.estimate
        velocity=float(e.state14[7]) if e is not None else 0.
        phase=self.engine.fault or ('PAUSED' if self.engine.paused else self.engine.phase)
        text=(f'{phase}\nPitch {shown[1]:+7.2f}°  Roll {shown[0]:+7.2f}°\n'
              f'v {velocity:+.2f} m/s   {self.fps:4.0f} FPS\n'
              f't {p.d.time:7.2f}s  u {np.max(np.abs(self.engine.last_tau)):.1f} Nm')
        zones=[dict(bounds=list(z['bounds'])) for z in self.engine.meta['zones'] if 'bounds' in z]
        self._post_ui('status',dict(text=text,jump_disabled=bool(self.engine.jump.active or self.engine.paused),
                                   zones=zones,zone=int(self.engine.zone),xy=p.d.qpos[:2].tolist()))

    def _draw_map_snapshot(self,snapshot):
        self._assert_tk_owner();canvas=self.map_canvas;valid=snapshot['zones']
        if not valid:return
        width,height=max(300,canvas.winfo_width()),100
        bounds=np.asarray([z['bounds'] for z in valid],float)
        xmin,xmax=bounds[:,0].min()-1.,bounds[:,1].max()+1.
        ymin,ymax=bounds[:,2].min()-1.,bounds[:,3].max()+1.
        sx,sy=(width-8)/max(xmax-xmin,1.),(height-8)/max(ymax-ymin,1.)
        xy=lambda x,y:(4+(x-xmin)*sx,height-4-(y-ymin)*sy)
        canvas.delete('all')
        for i,z in enumerate(valid):
            a,b,c,d=z['bounds'];x1,y1=xy(a,c);x2,y2=xy(b,d)
            canvas.create_rectangle(x1,y1,x2,y2,fill='#31506d' if i!=snapshot['zone'] else '#397e87',outline='#6d859f')
            canvas.create_text((x1+x2)/2,(y1+y2)/2,text=str(i),fill='white',font=('Consolas',8))
        x,y=xy(*snapshot['xy']);canvas.create_oval(x-3,y-3,x+3,y+3,fill='#ffd25c',outline='')

    def _pump_panel(self):
        self._assert_tk_owner()
        try:
            while True:
                kind,value=self.ui_messages.get_nowait()
                if kind=='message':self.message_var.set(value)
                elif kind=='zones':self.zone_box['values']=value;self.zone_box.current(0)
                elif kind=='geometry':self.panel.geometry(value)
                elif kind=='show_panel' and not self.hidden_smoke_seconds:
                    self.panel.deiconify();self.panel.lift();self.panel.focus_force()
                elif kind=='status':
                    self.status_var.set(value['text'])
                    self.jump_button.state(['disabled'] if value['jump_disabled'] else ['!disabled'])
                    self._draw_map_snapshot(value)
                elif kind=='ready' and self.hidden_smoke_seconds:
                    self.panel.after(round(self.hidden_smoke_seconds*1000),self.close)
        except queue.Empty:pass
        if self.worker_done.is_set():
            self.panel.destroy();return
        self.panel.after(25,self._pump_panel)

    def _viewer_worker(self):
        try:
            self._initialize_view(*self.start_args)
            previous=time.perf_counter();accumulator=0.;next_render=next_panel=previous
            fps_epoch=status_epoch=previous
            while self.running and not glfw.window_should_close(self.window):
                now=time.perf_counter();elapsed=min(.05,max(0.,now-previous));previous=now
                glfw.poll_events();self.handle_actions();accumulator+=elapsed;loops=0
                while accumulator>=.01 and loops<5:
                    self.forward,self.yaw_rate=self.controls()
                    if not self.hidden_smoke_seconds:self.engine.tick(self.forward,self.yaw_rate)
                    accumulator-=.01;loops+=1
                if now>=next_render:self.draw();next_render=now+1/60
                if now>=next_panel:self.update_panel();next_panel=now+.10
                if now-fps_epoch>=1.:
                    self.fps=self.frames/(now-fps_epoch);self.frames=0;fps_epoch=now
                if now-status_epoch>=5.:
                    ang=np.rad2deg(rpy(self.engine.plant.d.qpos[3:7]))
                    print(f'LIVE sim_t={self.engine.plant.d.time:.2f} phase={self.engine.phase} '
                          f'target=({self.forward:+.2f},{self.yaw_rate:+.2f}) pitch={ang[1]:+.3f} '
                          f'roll={ang[0]:+.3f} fps={self.fps:.1f} fault={self.engine.fault}',flush=True)
                    status_epoch=now
                time.sleep(.001)
            if self.hidden_smoke_seconds:
                p=self.engine.plant
                if self.engine.controls!=0 or p.tick_phys!=0 or float(p.d.time)!=0.:
                    raise RuntimeError('Paused lifecycle check advanced physics')
                print(f'HIDDEN_LIFECYCLE physics_steps={p.tick_phys} controls={self.engine.controls} sim_time={p.d.time}',flush=True)
        except BaseException:
            self.worker_error=traceback.format_exc();traceback.print_exc()
        finally:
            self.running=False
            try:
                if self.window:self.release_mouse()
                if self.context is not None:self.context.free();self.context=None
                if self.window:glfw.destroy_window(self.window);self.window=None
                glfw.terminate()
            except BaseException:
                self.worker_error+=traceback.format_exc();traceback.print_exc()
            self.worker_done.set()
            print('VIEWER_WORKER_CLOSED',flush=True)

    def run(self):
        self._assert_tk_owner()
        self.worker=threading.Thread(target=self._viewer_worker,name='MOD4-GLFW-physics-owner',daemon=False)
        self.worker.start();self.panel.after(25,self._pump_panel)
        try:self.panel.mainloop()
        finally:
            self.running=False;self.worker.join()
            try:self.panel.destroy()
            except tk.TclError:pass
            for name,obj in list(vars(self).items()):
                if isinstance(obj,(tk.Misc,tk.Variable)):setattr(self,name,None)
            gc.collect()
        if self.worker_error:raise RuntimeError(self.worker_error)
        print('RM_FPS_CLOSED main_Tk_clean_exit=True',flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene',choices=list(SCENES.values()),default='latest_rm')
    parser.add_argument('--difficulty',type=float,default=.5)
    parser.add_argument('--seed',type=int,default=9001)
    parser.add_argument('--controller',choices=list(CONTROLLERS.values()),default='c2_fps')
    parser.add_argument('--hidden-smoke-seconds',type=float,default=0.)
    args=parser.parse_args()
    if not math.isfinite(args.hidden_smoke_seconds) or not 0.<=args.hidden_smoke_seconds<=30.:
        raise ValueError('Hidden smoke seconds must be0..30')
    Player(args.scene,args.difficulty,args.seed,args.controller,args.hidden_smoke_seconds).run()

if __name__=='__main__':
    try:main()
    except BaseException:traceback.print_exc();raise
