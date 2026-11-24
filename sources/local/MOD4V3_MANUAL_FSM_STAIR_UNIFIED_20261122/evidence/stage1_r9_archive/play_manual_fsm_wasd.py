"""One-window MOD4v3 manual-FSM playground with all twelve core maps."""
from argparse import ArgumentParser
import math
import time
import numpy as np
import torch
import mujoco as mj
from fsm_paths import HERE
from fsm_io import put
from fsm_maps import MAPS,metadata
from manual_fsm_runtime import ManualPolicy,ManualSimulation
from manual_fsm_core import Phase,LABELS

def smoke(checkpoint=None):
    p=ManualPolicy(checkpoint)
    sim=ManualSimulation(p)
    rows=[]
    for label,course in MAPS:
        sim.load_map(metadata(course))
        sim.target_h=.39
        for _ in range(35):sim.step(set())
        for keys in ({'w'},{'s'},{'a'},{'d'}):
            for _ in range(6):
                sim.step(keys)
                assert sim.route['e1']==0. and np.isfinite(sim.prev_a).all()
        rows.append(dict(course=course,finite=True,cruise_stair_weight=sim.route['e1'],
                         physics_hz=1./sim.m.opt.timestep,tire_radius_m=sim.m.geom_size[sim.tire_gids,0].tolist()))
        print(label,'OK',flush=True)
    sim.load_map(metadata('flat'))
    sim.step({'c','w'})
    assert sim.mode_latched and sim.route['e1']==0.
    sim.step({'w','v'})
    assert sim.route['e1']==1.
    sim.step({'s'})
    assert sim.route['e1']==0. and p.fsm.phase[0]==Phase.CRUISE_E0
    sim.step({'c'})
    assert not sim.mode_latched and sim.route['e1']==0.
    sim.load_map(metadata('flat'))
    sim.cmd_vx=0.
    sim.step({'w','v'})
    assert sim.route['e1']==1.,'V must force climb on the first W tick'
    sim.step(set())
    assert sim.route['e1']==0. and p.fsm.phase[0]==Phase.CRUISE_E0
    sim.mode_latched=False
    sim.step({'w','f','v'})
    assert sim.route['e1']==1. and not sim.mode_latched
    sim.step({'w'})
    assert sim.route['e1']==0. and p.fsm.phase[0]==Phase.CRUISE_E0
    from fsm_paths import JUMP_PATH
    from fsm_io import sha256
    put(HERE/'evidence/PLAYER_SMOKE.json',dict(passed=True,maps=rows,stair_sha256=p.sha,
        same_tick_reverse_and_mode_off=True,same_tick_forward_release=True,same_tick_temporary_release=True,
        force_on_first_forward_tick=True,force_key=True,jump_sha256=sha256(JUMP_PATH)))

def play(checkpoint=None,initial_course='flat',ui_smoke=False):
    import tkinter as tk
    from tkinter import ttk
    from PIL import Image,ImageTk
    policy=ManualPolicy(checkpoint)
    sim=ManualSimulation(policy)
    root=tk.Tk()
    root.title('MOD4v3 · 手工状态机 · 全地图驾驶 · 实验候选')
    root.configure(bg='#101820')
    root.geometry('1330x800')
    root.minsize(1150,710)
    style=ttk.Style(root)
    style.theme_use('clam')
    style.configure('TFrame',background='#16222c')
    style.configure('TLabel',background='#16222c',foreground='#e7eef4',font=('Microsoft YaHei UI',10))
    style.configure('TButton',font=('Microsoft YaHei UI',10),padding=6)
    image_label=tk.Label(root,bg='#101820')
    image_label.grid(row=0,column=0,sticky='nsew',padx=10,pady=10)
    root.columnconfigure(0,weight=1);root.rowconfigure(0,weight=1)
    controls=ttk.Frame(root,padding=14,width=330)
    controls.grid(row=0,column=1,sticky='ns')
    ttk.Label(controls,text='MOD4v3 手工状态机',font=('Microsoft YaHei UI',17,'bold')).pack(anchor='w',pady=(0,12))
    scene=tk.StringVar(value=dict((c,l) for l,c in MAPS)[initial_course])
    spawn=tk.StringVar()
    speed=tk.DoubleVar(value=1.2);height=tk.DoubleVar(value=.35)
    state=tk.StringVar();telemetry=tk.StringVar();hint=tk.StringVar()
    keys=set()
    renderer=None
    ui_judge=None
    camera=mj.MjvCamera()
    camera.distance=2.8;camera.elevation=-16.;camera.azimuth=135.
    option=mj.MjvOption()
    option.geomgroup[3]=0
    ui_status=tk.StringVar(value='W/S 前后 · C 上阶档 · 空格大跳')
    accumulator=0.
    previous=time.perf_counter();last_draw=0.
    closed=False
    drawn=0;ui_failure=None
    ttk.Label(controls,text='地图').pack(anchor='w')
    selector=ttk.Combobox(controls,state='readonly',values=[l for l,_ in MAPS],textvariable=scene,width=31)
    selector.pack(fill='x',pady=(3,8))
    ttk.Label(controls,text='出生点').pack(anchor='w')
    spawn_selector=ttk.Combobox(controls,state='readonly',textvariable=spawn,width=31)
    spawn_selector.pack(fill='x',pady=(3,10))
    def focus():root.focus_set()
    def reset():
        nonlocal accumulator,previous,ui_judge
        keys.clear();sim.reset_at_spawn(max(0,spawn_selector.current()))
        sim.target_h=height.get();sim.max_vx=speed.get()
        from fsm_evaluation import ContactJudge
        course=sim.scene_meta['course']
        direction=-1 if course=='rm27_east' else 1
        ui_judge=ContactJudge(sim,dict(course=course,edge_sign=1),0.,direction,0.)
        accumulator=0.;previous=time.perf_counter()
        ui_status.set('已复位 · 按 W 出发');focus()
    def change_scene(_event=None):
        nonlocal renderer
        if renderer is not None:renderer.close()
        course=dict(MAPS)[scene.get()]
        sim.load_map(metadata(course))
        renderer=mj.Renderer(sim.m,height=540,width=960)
        spawn_selector.configure(values=[s['name'] for s in sim.scene_meta['spawns']])
        spawn_selector.current(0)
        option.geomgroup[5]=0 if sim.scene_meta.get('hide_group5') else 1
        reset()
    selector.bind('<<ComboboxSelected>>',change_scene)
    spawn_selector.bind('<<ComboboxSelected>>',lambda _:reset())
    tk.Label(controls,textvariable=state,bg='#223846',fg='#69e2c4',font=('Microsoft YaHei UI',14,'bold'),
             anchor='w',justify='left',padx=10,pady=12,wraplength=310).pack(fill='x',pady=(0,8))
    ttk.Label(controls,textvariable=telemetry,justify='left').pack(anchor='w',pady=(0,10))
    speed_label=tk.StringVar();height_label=tk.StringVar()
    ttk.Label(controls,textvariable=speed_label).pack(anchor='w')
    ttk.Scale(controls,from_=0.,to=3.,variable=speed,takefocus=False).pack(fill='x')
    presets=ttk.Frame(controls);presets.pack(fill='x',pady=(2,10))
    ttk.Button(presets,text='1 · 1.2 m/s',command=lambda:speed.set(1.2),takefocus=False).pack(side='left',expand=True,fill='x')
    ttk.Button(presets,text='2 · 2.8 m/s',command=lambda:speed.set(2.8),takefocus=False).pack(side='left',expand=True,fill='x')
    ttk.Label(controls,textvariable=height_label).pack(anchor='w')
    ttk.Scale(controls,from_=.24,to=.42,variable=height,takefocus=False).pack(fill='x',pady=(0,10))
    ttk.Button(controls,text='C · 切换上阶模式',command=lambda:sim.toggle_stair_mode(),takefocus=False).pack(fill='x',pady=3)
    ttk.Button(controls,text='空格 / J · 大跳',command=sim.request_jump,takefocus=False).pack(fill='x',pady=3)
    ttk.Button(controls,text='R · 复位',command=reset,takefocus=False).pack(fill='x',pady=3)
    ttk.Label(controls,text='W/S 前后  A/D 转向  Q/E 站高\nC 上阶开关  F 按住临时上阶\nW+V 贴阶强起  Space/J 大跳\n1 常用档  2 高速档  R 复位',justify='left').pack(anchor='w',pady=12)
    ttk.Label(controls,textvariable=hint,wraplength=310,justify='left').pack(anchor='w')
    ttk.Label(controls,textvariable=ui_status,wraplength=310,justify='left').pack(anchor='w',pady=10)
    def press(event):
        name=event.keysym.lower()
        if name=='r' and name not in keys:reset()
        if name=='1':speed.set(1.2)
        if name=='2':speed.set(2.8)
        keys.add(name)
    root.bind('<KeyPress>',press)
    root.bind('<KeyRelease>',lambda e:keys.discard(e.keysym.lower()))
    root.bind('<FocusOut>',lambda _:keys.clear())
    def close():
        nonlocal closed
        closed=True
        if renderer is not None:renderer.close()
        root.destroy()
    root.protocol('WM_DELETE_WINDOW',close)
    def tick():
        nonlocal previous,accumulator,last_draw,drawn,ui_failure
        if closed:return
        now=time.perf_counter();accumulator+=min(.10,now-previous);previous=now
        try:
            for _ in range(int(accumulator/.02)):
                accumulator-=.02
                sim.max_vx=speed.get();sim.target_h=height.get()
                sim.step(keys)
                if keys&{'q','e'}:height.set(sim.target_h)
            if now-last_draw>=.038:
                last_draw=now
                phase=int(policy.fsm.phase[0]);R=sim.d.xmat[sim.env.base_id].reshape(3,3)
                yaw=math.degrees(math.atan2(R[1,0],R[0,0]));pitch=math.degrees(math.asin(np.clip(-R[2,0],-1,1)))
                camera.lookat[:]=sim.d.qpos[:3]+np.array([.25*R[0,0],.25*R[1,0],.02])
                camera.azimuth=yaw+125.
                renderer.update_scene(sim.d,camera,scene_option=option)
                photo=ImageTk.PhotoImage(Image.fromarray(renderer.render()))
                image_label.configure(image=photo);image_label.image=photo
                drawn+=1
                mode='开启' if sim.mode_latched or 'f' in keys else '关闭'
                label='上阶预备(停车直立)' if mode=='开启' and phase==Phase.CRUISE_E0 else LABELS[phase]
                state.set(f'[C] 上阶模式：{mode}\n{label}')
                vx=float(sim.d.qvel[:2]@R[:2,0])
                # UI-only terrain query. It is not passed into policy/FSM.
                rel=float(sim.d.qpos[2]-sim.ground_z(*sim.d.qpos[:2]))
                telemetry.set(f'车速 {vx:+.2f} / {sim.cmd_vx:+.2f} m/s\n站高 {rel:.3f} m · 有效目标 {getattr(policy,"last_effective_height",height.get()):.3f} m\n俯仰 {pitch:+.1f}° · 上阶权重 {sim.route["e1"]:.0%}')
                speed_label.set(f'W/S 速度：{speed.get():.2f} m/s')
                height_label.set(f'站高 Q/E：{height.get():.3f} m')
                gap=ui_judge.front_gap() if sim.scene_meta['course'] not in ('flat','rough_L9') else None
                distance=f'距首台沿 {gap:+.2f} m（仅提示）\n' if gap is not None else ''
                jump_hint='大跳建议站高0.28m：1.6档约0.35m前、2.8档约0.85m前按空格。'
                hint.set(distance+'提前开上阶档保持直立，触阶后攀爬。松 W、倒车、关档立即退出。\n'+jump_hint)
        except Exception as exc:
            import traceback
            (HERE/'evidence/PLAYER_ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8')
            ui_status.set(f'已停止：{exc}');return
        root.after(5,tick)
    change_scene()
    root.after(5,tick)
    if ui_smoke:
        def layout_check():
            widgets=[]
            def visit(w):
                for child in w.winfo_children():
                    if child.winfo_ismapped():
                        box=[child.winfo_rootx()-root.winfo_rootx(),child.winfo_rooty()-root.winfo_rooty(),child.winfo_width(),child.winfo_height()]
                        try:text=child.cget('text')
                        except tk.TclError:text=''
                        widgets.append(dict(kind=child.winfo_class(),text=text,box=box,
                            clipped=box[0]<0 or box[1]<0 or box[0]+box[2]>root.winfo_width() or box[1]+box[3]>root.winfo_height()))
                    visit(child)
            visit(root)
            put(HERE/'evidence/UI_LAYOUT_SMOKE.json',dict(window=[root.winfo_width(),root.winfo_height()],
                rendered_frames=drawn,widgets=widgets,clipped=sum(w['clipped'] for w in widgets),
                passed=drawn>0 and not any(w['clipped'] for w in widgets),
                external_desktop_interaction_verified=False))
            close()
        root.after(1800,layout_check)
    root.mainloop()

def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint')
    p.add_argument('--scene',choices=[c for _,c in MAPS],default='flat')
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--ui-smoke',action='store_true')
    args=p.parse_args()
    torch.set_num_threads(1)
    try:
        if args.smoke:smoke(args.checkpoint)
        else:play(args.checkpoint,args.scene,args.ui_smoke)
    except Exception:
        import traceback
        (HERE/'evidence/PLAYER_START_ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8')
        raise

if __name__=='__main__':main()
