"""Six sliders + native MuJoCo rendering; passive loop joints close analytically."""
from pathlib import Path
import argparse
import numpy as np
import mujoco
from kinematics import set_configuration,PARAMS
ROOT=Path(__file__).parent

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--save',help='Render one pose to PNG without opening a window');args=ap.parse_args()
    m=mujoco.MjModel.from_xml_path(str(ROOT/'scene.xml'));d=mujoco.MjData(m)
    renderer=mujoco.Renderer(m,720,1100);opt=mujoco.MjvOption();opt.geomgroup[3]=0;opt.sitegroup[:]=0
    cam=mujoco.MjvCamera();cam.lookat[:]=[0,0,.28];cam.distance=1.3;cam.azimuth=135;cam.elevation=-20
    values=[0.]*6
    def pixels():
        mujoco.mj_resetData(m,d)
        set_configuration(m,d,left=(values[0],values[1]),right=(values[3],values[4]))
        for side,i in [('left',2),('right',5)]:d.qpos[m.joint(side+'_wheel_spin').qposadr[0]]=values[i]
        mujoco.mj_forward(m,d)
        d.qpos[2]+=.0645-min(d.site_xpos[m.site(side+'_wheel_center').id,2] for side in ['left','right'])
        mujoco.mj_forward(m,d);renderer.update_scene(d,cam,scene_option=opt);return renderer.render()
    from PIL import Image
    if args.save:
        Image.fromarray(pixels()).save(args.save);renderer.close();return
    import tkinter as tk
    from tkinter import ttk
    from PIL import ImageTk
    window=tk.Tk();window.title('MOD4 关节拓扑检查 — MuJoCo 渲染')
    canvas=tk.Label(window);canvas.grid(row=0,column=0,sticky='nsew')
    panel=ttk.Frame(window,padding=12);panel.grid(row=0,column=1,sticky='ns')
    ttk.Label(panel,text='拖动滑块，闭环从动关节自动跟随\n这是运动学预览，不执行动力学。').pack()
    labels=['左髋 hip','左输入差 crank − hip','左轮','右髋 hip','右输入差 crank − hip','右轮']
    sliders=[]
    def set_value(i,v):values[i]=float(v)
    for i,name in enumerate(labels):
        side='left' if i<3 else 'right'
        lo,hi=PARAMS['hip_range_rad'] if i%3==0 else PARAMS['limits'][side]['input_difference_rad'] if i%3==1 else [-np.pi,np.pi]
        s=tk.Scale(panel,from_=lo,to=hi,resolution=.002,orient='horizontal',length=300,label=name,
                   command=lambda v,i=i:set_value(i,v));s.set(0.);s.pack();sliders.append(s)
    def reset():
        for slider in sliders:slider.set(0.)
    ttk.Button(panel,text='恢复零位',command=reset).pack(pady=6)
    markers=tk.BooleanVar();collisions=tk.BooleanVar()
    ttk.Checkbutton(panel,text='显示闭环锚点',variable=markers).pack(anchor='w')
    ttk.Checkbutton(panel,text='显示碰撞体',variable=collisions).pack(anchor='w')
    ttk.Label(panel,text='机身 → 大腿 → 小腿 → 轮\n机身 → 输入杆 → 连杆2 ↔ 摇杆\n大腿 → 摇杆 → 连杆4 ↔ 小腿\n大腿 → 弹簧内杆 → 外筒 ↔ 小腿\n\n画面上拖动鼠标旋转视角；滚轮缩放。').pack(pady=10)
    status=ttk.Label(panel,text='');status.pack()
    drag=[None]
    canvas.bind('<ButtonPress-1>',lambda e:drag.__setitem__(0,(e.x,e.y)))
    def move(e):
        if drag[0] is not None:
            x,y=drag[0];cam.azimuth+=(e.x-x)*.4;cam.elevation=np.clip(cam.elevation+(e.y-y)*.3,-89.,-2.);drag[0]=(e.x,e.y)
    canvas.bind('<B1-Motion>',move)
    canvas.bind('<MouseWheel>',lambda e:setattr(cam,'distance',float(np.clip(cam.distance*(.90 if e.delta>0 else 1.1),.5,3.))))
    running=[True]
    def close():running[0]=False;window.destroy()
    window.protocol('WM_DELETE_WINDOW',close)
    def refresh():
        if not running[0]:return
        opt.sitegroup[4]=int(markers.get());opt.geomgroup[3]=int(collisions.get())
        try:
            frame=ImageTk.PhotoImage(Image.fromarray(pixels()));canvas.configure(image=frame);canvas.image=frame
            error=max(np.linalg.norm(d.site_xpos[m.site(s+'_'+a).id]-d.site_xpos[m.site(s+'_'+b).id]) for s in ['left','right'] for a,b in [('proximal_a','proximal_b'),('distal_a','distal_b'),('gas_end','gas_mount')])
            status.configure(text=f'闭环偏差 {error*1000:.6f} mm')
        except ValueError as e:status.configure(text=str(e))
        window.after(33,refresh)
    try:refresh();window.mainloop()
    finally:renderer.close()
if __name__=='__main__':main()
