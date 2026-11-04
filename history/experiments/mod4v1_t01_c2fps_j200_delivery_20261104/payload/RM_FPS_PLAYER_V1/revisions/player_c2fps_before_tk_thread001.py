"""Native GLFW FPS controls + Tk panel, keeping the body-first MOD4v1 LQR.
UI/layout lineage: Desktop/claude/mjcf/mod4-onnx-mujoco-launcher/drive_wasd.py.
No old policy, yaw-assist or external/root force is imported.
"""
import os
for _name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_name] = '1'
from pathlib import Path
import sys
import argparse
import math
import time
import traceback
import collections
import tkinter as tk
from tkinter import ttk
import numpy as np
import glfw
import mujoco

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from RM_FPS_PLAYER_V1.runtime import Engine
from sensor_core_v4 import rpy

SCENES = {'最新 WASD · RMUC 全场': 'latest_rm', 'RM 全地形 · 11 类配方': 'rm_all', '旧 WASD 综合场': 'classic_rm', '平地稳态练习': 'flat'}
CONTROLLERS = {'C2 腿调平 + FPS航向（试验）': 'c2_fps', '原 coord_soft（对照）': 'coord_soft'}


def wrap(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


class Player:
    def __init__(self, scene='latest_rm', difficulty=.5, seed=9001, controller='c2_fps'):
        self.controller_mode = controller
        if not glfw.init():
            raise RuntimeError('GLFW initialization failed')
        self.actions = collections.deque()
        self.running = True
        self.captured = False
        self.first_person = False
        self.overview = False
        self.virtual = set()
        self.blocked = False
        self.mouse_last = None
        self.heading = 0.
        self.view_pitch = math.radians(-17.)
        self.distance = 2.25
        self.forward = self.yaw_rate = 0.
        self.frames = 0
        self.fps = 0.
        self.error = ''
        self.context = None
        mode = glfw.get_video_mode(glfw.get_primary_monitor())
        sw, sh = mode.size if mode is not None else (1600, 900)
        width, height = max(720, min(1280, sw-405)), max(560, min(900, sh-120))
        glfw.window_hint(glfw.SAMPLES, 4)
        self.window = glfw.create_window(width, height, 'MOD4v1 | RM FPS | BODY-FIRST LQR', None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError('GLFW window creation failed')
        glfw.set_window_pos(self.window, 10, 45)
        glfw.make_context_current(self.window)
        glfw.swap_interval(0)
        glfw.set_key_callback(self.window, self.on_key)
        glfw.set_cursor_pos_callback(self.window, self.on_mouse)
        glfw.set_mouse_button_callback(self.window, self.on_mouse_button)
        glfw.set_scroll_callback(self.window, self.on_scroll)
        glfw.set_window_focus_callback(self.window, self.on_focus)
        self.build_panel(width+25, 45, height, scene, difficulty, seed)
        self.load_scene(scene, difficulty, seed)
        self.camera = mujoco.MjvCamera()
        mujoco.mjv_defaultCamera(self.camera)
        self.camera.type = mujoco.mjtCamera.mjCAMERA_FREE
        self.option = mujoco.MjvOption()
        mujoco.mjv_defaultOption(self.option)
        self.option.flags[mujoco.mjtVisFlag.mjVIS_JOINT] = False
        self.option.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] = False
        self.panel.update()
        glfw.focus_window(self.window)
        print(f'RM_FPS_READY pid={os.getpid()} scene={scene} zones={len(self.engine.meta["zones"])} '
              f'controller={self.controller_mode} physics=.0005 control=.01 model=full_contacts', flush=True)

    def build_panel(self, x, y, height, scene, difficulty, seed):
        self.panel = tk.Tk()
        self.panel.title('MOD4v1 · RM / FPS 操作面板')
        self.panel.geometry(f'365x{height}+{x}+{y}')
        self.panel.configure(bg='#121b29')
        self.panel.protocol('WM_DELETE_WINDOW', self.close)
        style = ttk.Style(self.panel)
        style.theme_use('clam')
        style.configure('.', font=('Microsoft YaHei UI', 10), background='#182438', foreground='#e5edf7')
        style.configure('TFrame', background='#121b29')
        style.configure('TLabel', background='#121b29')
        style.configure('TButton', padding=6)
        style.map('TButton', background=[('active', '#35557b')])
        self.scene_var = tk.StringVar(value=next((k for k,v in SCENES.items() if v == scene), list(SCENES)[0]))
        self.level_var = tk.DoubleVar(value=difficulty)
        self.seed_var = tk.StringVar(value=str(seed))
        self.zone_var = tk.StringVar()
        self.speed_var = tk.DoubleVar(value=1.)
        self.sensitivity_var = tk.DoubleVar(value=.15)
        self.status_var = tk.StringVar(value='正在建立物理场景…')
        self.message_var = tk.StringVar(value='点击三维画面锁定鼠标；Esc 释放鼠标')
        outer = tk.Canvas(self.panel, bg='#121b29', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.panel, orient='vertical', command=outer.yview)
        outer.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        outer.pack(side='left', fill='both', expand=True)
        pad = ttk.Frame(outer, padding=12)
        interior = outer.create_window((0,0), window=pad, anchor='nw')
        pad.bind('<Configure>', lambda event:outer.configure(scrollregion=outer.bbox('all')))
        outer.bind('<Configure>', lambda event:outer.itemconfigure(interior, width=event.width))
        self.panel.bind_all('<MouseWheel>', lambda event:outer.yview_scroll(-int(event.delta/120),'units'))
        ttk.Label(pad, text='MOD4v1  /  RM FPS', font=('Microsoft YaHei UI', 17, 'bold')).pack(anchor='w')
        ttk.Label(pad, text='底盘平稳优先 · 真实接触 / 电机力矩').pack(anchor='w', pady=(0,9))
        self.controller_var = tk.StringVar(value=next(k for k,v in CONTROLLERS.items() if v==self.controller_mode))
        ttk.Combobox(pad, textvariable=self.controller_var, values=list(CONTROLLERS), state='readonly').pack(fill='x')
        ttk.Button(pad, text='应用控制器（用户复位）', command=lambda:self.actions.append(('controller',None))).pack(fill='x',pady=3)
        ttk.Label(pad, text='C2：0.3m/s名义低速有证据；高速/跳跃未验', wraplength=330, foreground='#e8c887').pack(anchor='w')
        ttk.Label(pad, text='场景').pack(anchor='w')
        ttk.Combobox(pad, textvariable=self.scene_var, values=list(SCENES), state='readonly').pack(fill='x')
        row = ttk.Frame(pad)
        row.pack(fill='x', pady=4)
        ttk.Label(row, text='地形种子').pack(side='left')
        ttk.Entry(row, textvariable=self.seed_var, width=12).pack(side='right')
        ttk.Label(pad, text='地形难度（沿用配方原始高度范围）').pack(anchor='w')
        ttk.Scale(pad, from_=0., to=1., variable=self.level_var).pack(fill='x')
        ttk.Button(pad, text='载入所选场景', command=lambda:self.actions.append(('scene', None))).pack(fill='x', pady=4)
        ttk.Label(pad, text='地形 / 复位点').pack(anchor='w', pady=(4,0))
        self.zone_box = ttk.Combobox(pad, textvariable=self.zone_var, state='readonly')
        self.zone_box.pack(fill='x')
        ttk.Button(pad, text='前往此地形入口 / 复位  [ R ]', command=lambda:self.actions.append(('reset', self.zone_box.current()))).pack(fill='x', pady=4)
        drive = ttk.Frame(pad)
        drive.pack(fill='x', pady=3)
        for label, key in [('前 W','W'), ('左 A','A'), ('后 S','S'), ('右 D','D')]:
            button = ttk.Button(drive, text=label, width=6)
            button.pack(side='left', fill='x', expand=True)
            button.bind('<ButtonPress-1>', lambda event,k=key:self.virtual_press(k))
            button.bind('<ButtonRelease-1>', lambda event,k=key:self.virtual.discard(k))
            button.bind('<Leave>', lambda event,k=key:self.virtual.discard(k))
        ttk.Button(pad, text='全场俯视 / 跟随  [ M ]', command=lambda:self.actions.append(('overview',None))).pack(fill='x', pady=3)
        row = ttk.Frame(pad)
        row.pack(fill='x')
        self.jump_button = ttk.Button(row, text='试验跳跃 [ Space / J ]', command=lambda:self.actions.append(('jump', None)))
        self.jump_button.pack(side='left', fill='x', expand=True)
        ttk.Button(row, text='刹停 [ X ]', command=lambda:self.actions.append(('brake', None))).pack(side='left', padx=(4,0))
        row = ttk.Frame(pad)
        row.pack(fill='x', pady=4)
        ttk.Button(row, text='暂停 / 继续 [ P ]', command=lambda:self.actions.append(('pause', None))).pack(side='left', fill='x', expand=True)
        ttk.Button(row, text='第一 / 三人称 [ F ]', command=lambda:self.actions.append(('camera', None))).pack(side='left', fill='x', expand=True, padx=(4,0))
        ttk.Button(pad, text='返回画面并锁定鼠标', command=lambda:self.actions.append(('capture', None))).pack(fill='x')
        ttk.Label(pad, text='普通行驶速度（Shift = 2 m/s）').pack(anchor='w', pady=(6,0))
        ttk.Scale(pad, from_=.2, to=2., variable=self.speed_var).pack(fill='x')
        ttk.Label(pad, text='鼠标灵敏度').pack(anchor='w')
        ttk.Scale(pad, from_=.04, to=.35, variable=self.sensitivity_var).pack(fill='x')
        self.map_canvas = tk.Canvas(pad, height=100, bg='#0b1320', highlightthickness=0)
        self.map_canvas.pack(fill='x', pady=5)
        ttk.Label(pad, textvariable=self.status_var, justify='left', font=('Consolas', 10)).pack(anchor='w')
        ttk.Label(pad, textvariable=self.message_var, wraplength=330, foreground='#86cfec').pack(anchor='w', pady=(5,0))
        ttk.Label(pad, text='W/S 前后 · A/D 转向 · 鼠标指向\nShift 加速 · Space/J 跳跃 · X 刹停\nF 视角 · 滚轮缩放 · R 复位 · P 暂停\nTab 面板 · Esc 释放鼠标\n跳跃为试验动作；摔倒后可按 R。', wraplength=330, foreground='#adbbcf').pack(anchor='w', pady=(6,0))

    def load_scene(self, scene, difficulty, seed):
        self.release_mouse()
        new_engine = Engine(scene, difficulty, seed, controller_mode=self.controller_mode)
        glfw.make_context_current(self.window)
        if self.context is not None:
            self.context.free()
        self.engine = new_engine
        self.engine.plant.m.vis.map.znear = .0002  # relative to large arena extent; render only
        self.context = mujoco.MjrContext(self.engine.plant.m, mujoco.mjtFontScale.mjFONTSCALE_150)
        self.render_scene = mujoco.MjvScene(self.engine.plant.m, maxgeom=12000)
        zones = self.engine.meta['zones']
        self.zone_box['values'] = [z['label'] for z in zones]
        self.zone_box.current(0)
        self.heading = self.engine.estimated_yaw()
        self.message_var.set(('已载入最新碰撞修正版 RMUC 全场。' if scene=='latest_rm' else '场景已载入。')+'站姿复位是交互起点，不计作自主起立。')
        self.error = ''
        print(f'SCENE_LOADED {scene} difficulty={difficulty:.3f} seed={seed} '
              f'ngeom={self.engine.plant.m.ngeom} nq={self.engine.plant.m.nq}', flush=True)

    def close(self):
        self.running = False

    def release_mouse(self):
        self.captured = False
        self.mouse_last = None
        if getattr(self, 'window', None):
            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_NORMAL)

    def capture_mouse(self):
        glfw.focus_window(self.window)
        self.captured = True
        self.overview = False
        self.mouse_last = None
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        if glfw.raw_mouse_motion_supported():
            glfw.set_input_mode(self.window, glfw.RAW_MOUSE_MOTION, True)
        self.message_var.set('鼠标已锁定：左右控制朝向，上下控制视角。Esc 释放。')

    def virtual_press(self, key):
        self.blocked = False
        self.virtual.add(key)

    def on_focus(self, window, focused):
        if not focused:
            self.release_mouse()
            self.forward = self.yaw_rate = 0.
            self.blocked = True

    def on_mouse(self, window, x, y):
        if not self.captured:
            self.mouse_last = None
            return
        if self.mouse_last is not None:
            dx, dy = x-self.mouse_last[0], y-self.mouse_last[1]
            sensitivity = math.radians(float(self.sensitivity_var.get()))
            self.heading -= dx*sensitivity
            self.view_pitch = float(np.clip(self.view_pitch-dy*sensitivity, -1.15, .85))
        self.mouse_last = (x,y)

    def on_mouse_button(self, window, button, action, mods):
        if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS and not self.captured:
            self.capture_mouse()

    def on_scroll(self, window, dx, dy):
        self.distance = float(np.clip(self.distance*math.exp(-.12*dy), .65, 8.))

    def on_key(self, window, key, scancode, action, mods):
        if action != glfw.PRESS:
            return
        mapping = {glfw.KEY_SPACE:'jump', glfw.KEY_J:'jump', glfw.KEY_R:'reset',
                   glfw.KEY_P:'pause', glfw.KEY_G:'pause', glfw.KEY_F:'camera', glfw.KEY_M:'overview', glfw.KEY_X:'brake'}
        if key in mapping:
            self.actions.append((mapping[key], None))
        elif key == glfw.KEY_ESCAPE:
            self.release_mouse()
        elif key == glfw.KEY_TAB:
            self.release_mouse()
            self.panel.deiconify()
            self.panel.lift()
            self.panel.focus_force()

    def handle_actions(self):
        while self.actions:
            action, value = self.actions.popleft()
            print(f'UI_ACTION {action} value={value} sim_t={self.engine.plant.d.time:.2f}',flush=True)
            if action == 'scene':
                try:
                    seed = int(self.seed_var.get())
                    self.load_scene(SCENES[self.scene_var.get()], float(self.level_var.get()), seed)
                except Exception as exc:
                    self.error = str(exc)
                    self.message_var.set('场景载入出错：'+str(exc))
                    traceback.print_exc()
            elif action == 'controller':
                self.controller_mode = CONTROLLERS[self.controller_var.get()]
                self.engine.controller_mode = self.controller_mode
                self.engine.reset(self.engine.zone)
                self.heading = 0.
                self.forward = self.yaw_rate = 0.
                self.message_var.set('已应用 '+self.controller_mode+' 并按用户操作复位；不代表新技能验收。')
                self.error = ''
                print('CONTROLLER_APPLIED '+self.controller_mode,flush=True)
            elif action == 'reset':
                zone = self.zone_box.current() if value is None else int(value)
                self.engine.reset(max(0,zone))
                self.heading = 0.
                self.forward = self.yaw_rate = 0.
                self.message_var.set('已按用户操作复位至地形入口。')
                self.error = ''
            elif action == 'jump':
                self.engine.request_jump()
                self.message_var.set(self.engine.jump_message)
            elif action == 'pause':
                if not self.engine.fault:
                    self.engine.paused = not self.engine.paused
            elif action == 'camera':
                self.first_person = not self.first_person
                self.overview = False
            elif action == 'overview':
                self.overview = not self.overview
                if self.overview:
                    self.release_mouse()
            elif action == 'brake':
                self.blocked = True
                self.virtual.clear()
                self.heading = self.engine.estimated_yaw()
                self.forward = self.yaw_rate = 0.
            elif action == 'capture':
                self.capture_mouse()

    def controls(self):
        focused = bool(glfw.get_window_attrib(self.window, glfw.FOCUSED))
        if not focused and not self.virtual:
            return 0., 0.
        key = lambda k:(focused and glfw.get_key(self.window,k) in (glfw.PRESS,glfw.REPEAT)) or (k<128 and chr(k) in self.virtual)
        held_drive = any(key(k) for k in (glfw.KEY_W,glfw.KEY_A,glfw.KEY_S,glfw.KEY_D))
        if not held_drive:
            self.blocked = False
        if self.blocked:
            return 0.,0.
        turning = int(key(glfw.KEY_A))-int(key(glfw.KEY_D))
        self.heading += turning*1.5*.01
        boost = key(glfw.KEY_LEFT_SHIFT) or key(glfw.KEY_RIGHT_SHIFT)
        speed = 2. if boost else float(self.speed_var.get())
        v = speed*(int(key(glfw.KEY_W))-int(key(glfw.KEY_S)))
        w = float(np.clip(3.*wrap(self.heading-self.engine.estimated_yaw()), -1.5, 1.5))
        # Physical wheeled turning, not fictitious sideways/root translation.
        # Bound lateral acceleration at speed while keeping in-place steering.
        yaw_cap = min(1.5, 1.6/max(abs(v), .25))
        w = float(np.clip(w, -yaw_cap, yaw_cap))
        if key(glfw.KEY_X):
            v = w = 0.
            self.heading = self.engine.estimated_yaw()
        return v,w

    def draw(self):
        p = self.engine.plant
        pos = p.d.qpos[:3].copy()  # render only, never a controller input
        camera_yaw = self.heading + self.engine.spawn_yaw
        forward = np.array([math.cos(self.view_pitch)*math.cos(camera_yaw),
                            math.cos(self.view_pitch)*math.sin(camera_yaw), math.sin(self.view_pitch)])
        self.camera.azimuth = math.degrees(camera_yaw)+180.
        self.camera.elevation = math.degrees(self.view_pitch)
        if self.overview:
            self.camera.lookat[:] = self.engine.meta.get('camera_lookat',[0.,0.,.3])
            self.camera.distance = self.engine.meta.get('camera_distance',24.)
            self.camera.azimuth = 110.
            self.camera.elevation = -65.
        elif self.first_person:
            eye = pos + np.array([.06*math.cos(camera_yaw), .06*math.sin(camera_yaw), .065])
            self.camera.lookat[:] = eye + .6*forward
            self.camera.distance = .6
        else:
            self.camera.lookat[:] = pos + np.array([0.,0.,.04])
            self.camera.distance = self.distance
        width,height = glfw.get_framebuffer_size(self.window)
        if width <= 0 or height <= 0:
            return
        viewport = mujoco.MjrRect(0,0,width,height)
        mujoco.mjv_updateScene(p.m,p.d,self.option,None,self.camera,mujoco.mjtCatBit.mjCAT_ALL,self.render_scene)
        mujoco.mjr_render(viewport,self.render_scene,self.context)
        shown = np.rad2deg(rpy(p.d.qpos[3:7]))
        velocity = float(self.engine.estimate.state14[7]) if self.engine.estimate is not None else 0.
        phase = 'FALL - R RESET' if self.engine.fault else ('PAUSED' if self.engine.paused else self.engine.phase)
        left = f'MOD4v1  |  {self.controller_mode}\nWASD  Shift  Space/J jump\nMouse aim  Esc unlock  Tab panel\nF camera  P pause  R reset'
        right = f'{phase}\nv {velocity:+.2f} m/s\npitch {shown[1]:+.2f}  roll {shown[0]:+.2f} deg\n{self.fps:.0f} FPS | sim {p.d.time:.2f}s'
        mujoco.mjr_overlay(mujoco.mjtFont.mjFONT_NORMAL,mujoco.mjtGridPos.mjGRID_TOPLEFT,viewport,left,'',self.context)
        mujoco.mjr_overlay(mujoco.mjtFont.mjFONT_NORMAL,mujoco.mjtGridPos.mjGRID_TOPRIGHT,viewport,right,'',self.context)
        mujoco.mjr_overlay(mujoco.mjtFont.mjFONT_NORMAL,mujoco.mjtGridPos.mjGRID_BOTTOMLEFT,viewport,
                           'Jump = joint/motor action | no root assist | R = explicit respawn','',self.context)
        glfw.swap_buffers(self.window)
        self.frames += 1

    def update_panel(self):
        p = self.engine.plant
        shown = np.rad2deg(rpy(p.d.qpos[3:7]))
        e = self.engine.estimate
        velocity = float(e.state14[7]) if e is not None else 0.
        phase = self.engine.fault or ('PAUSED' if self.engine.paused else self.engine.phase)
        self.status_var.set(f'{phase}\nPitch {shown[1]:+7.2f}°  Roll {shown[0]:+7.2f}°\n'
                            f'v {velocity:+.2f} m/s   {self.fps:4.0f} FPS\n'
                            f't {p.d.time:7.2f}s  u {np.max(np.abs(self.engine.last_tau)):.1f} Nm')
        self.jump_button.state(['disabled'] if self.engine.jump.active or self.engine.paused else ['!disabled'])
        self.update_map()
        self.panel.update_idletasks()
        self.panel.update()

    def update_map(self):
        canvas = self.map_canvas
        width,height = max(300,canvas.winfo_width()),100
        zones = self.engine.meta['zones']
        valid = [z for z in zones if 'bounds' in z]
        if not valid:
            return
        bounds = np.asarray([z['bounds'] for z in valid],float)
        xmin,xmax = bounds[:,0].min()-1., bounds[:,1].max()+1.
        ymin,ymax = bounds[:,2].min()-1., bounds[:,3].max()+1.
        sx,sy = (width-8)/max(xmax-xmin,1.), (height-8)/max(ymax-ymin,1.)
        xy = lambda x,y:(4+(x-xmin)*sx,height-4-(y-ymin)*sy)
        canvas.delete('all')
        for i,z in enumerate(valid):
            a,b,c,d = z['bounds']
            x1,y1 = xy(a,c);x2,y2 = xy(b,d)
            canvas.create_rectangle(x1,y1,x2,y2,fill='#31506d' if i != self.engine.zone else '#397e87',outline='#6d859f')
            canvas.create_text((x1+x2)/2,(y1+y2)/2,text=str(i),fill='white',font=('Consolas',8))
        x,y = xy(*self.engine.plant.d.qpos[:2])
        canvas.create_oval(x-3,y-3,x+3,y+3,fill='#ffd25c',outline='')

    def run(self):
        previous = time.perf_counter()
        accumulator = 0.
        next_render = previous
        next_panel = previous
        fps_epoch = previous
        status_epoch = previous
        try:
            while self.running and not glfw.window_should_close(self.window):
                now = time.perf_counter()
                elapsed = min(.05,max(0.,now-previous))
                previous = now
                glfw.poll_events()
                self.handle_actions()
                accumulator += elapsed
                loops = 0
                while accumulator >= .01 and loops < 5:
                    self.forward,self.yaw_rate = self.controls()
                    self.engine.tick(self.forward,self.yaw_rate)
                    accumulator -= .01
                    loops += 1
                if now >= next_render:
                    self.draw()
                    next_render = now+1/60
                if now >= next_panel:
                    self.update_panel()
                    next_panel = now+.10
                if now-fps_epoch >= 1.:
                    self.fps = self.frames/(now-fps_epoch)
                    self.frames = 0
                    fps_epoch = now
                if now-status_epoch >= 5.:
                    ang = np.rad2deg(rpy(self.engine.plant.d.qpos[3:7]))
                    print(f'LIVE sim_t={self.engine.plant.d.time:.2f} phase={self.engine.phase} '
                          f'target=({self.forward:+.2f},{self.yaw_rate:+.2f}) '
                          f'pitch={ang[1]:+.3f} roll={ang[0]:+.3f} '
                          f'jump={self.engine.jump.active} fps={self.fps:.1f} fault={self.engine.fault}',flush=True)
                    status_epoch = now
                time.sleep(.001)
        finally:
            self.release_mouse()
            if self.context is not None:
                self.context.free()
            glfw.destroy_window(self.window)
            glfw.terminate()
            try:
                self.panel.destroy()
            except tk.TclError:
                pass
        print('RM_FPS_CLOSED',flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene',choices=list(SCENES.values()),default='latest_rm')
    parser.add_argument('--difficulty',type=float,default=.5)
    parser.add_argument('--seed',type=int,default=9001)
    parser.add_argument('--controller',choices=list(CONTROLLERS.values()),default='c2_fps')
    args = parser.parse_args()
    Player(args.scene,args.difficulty,args.seed,args.controller).run()


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        traceback.print_exc()
        raise
