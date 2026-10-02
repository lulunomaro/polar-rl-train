from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.font_manager import FontProperties
from PIL import Image
import mujoco
from extract_mod4 import model,data,set_pose,envelope,leg_configuration

HERE=Path(__file__).resolve().parent
OUT=HERE/'results/figures'
OUT.mkdir(parents=True,exist_ok=True)
S=json.loads((HERE/'results/summary.json').read_text(encoding='utf8'))
P=json.loads((HERE/'mod4_extracted_parameters.json').read_text(encoding='utf8'))
font=FontProperties(fname='C:/Windows/Fonts/msyh.ttc')
plt.rcParams.update({'font.family':font.get_name(),'axes.unicode_minus':False,'font.size':10})
nom=S['nominal_pose']
poses=[('LQR 平衡姿态',nom['hip_rad']+S['nominal_system']['trim'],nom['difference_rad']),
       ('长腿姿态',P['poses'][-1]['hip_rad'],P['poses'][-1]['difference_rad']),
       ('狗洞微调姿态',.47016973374134735,-1.0660137925490711)]
opt=mujoco.MjvOption();opt.geomgroup[:]=[1,1,1,0,0,0]
camera=mujoco.MjvCamera();camera.azimuth=90;camera.elevation=-8;camera.distance=1.1
renderer=mujoco.Renderer(model,height=720,width=1280)
records=[]
for i,(name,hip,diff) in enumerate(poses):
    set_pose(hip,diff)
    camera.lookat[:]=[0,0,.20]
    renderer.update_scene(data,camera=camera,scene_option=opt)
    img=renderer.render().copy()
    path=OUT/f'cad_pose_{i}.png';Image.fromarray(img).save(path)
    lo,top=envelope()
    records.append({'name':name,'hip_rad':hip,'crank_rad':hip+diff,'difference_rad':diff,
                    'root_height_m':float(data.qpos[2]),'full_visual_height_m':top,'lowest_visual_m':lo})
renderer.close()
(HERE/'results/posture_geometry.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')

fig,axes=plt.subplots(1,3,figsize=(14,5.5))
fig.subplots_adjust(left=.055,right=.995,top=.90,bottom=.20,wspace=.25)
links=[(['O','P','K'],'#204d78','大腿'),(['O','A'],'#e48c37','曲柄'),(['A','B'],'#a562aa','第一耦杆'),
       (['B','P','C'],'#298ca8','摇杆'),(['C','D'],'#5599a9','第二耦杆'),(['D','K','T','W'],'#31805e','小腿')]
for ax,(name,hip,diff),record in zip(axes,poses,records):
    _,pins=leg_configuration(hip,diff,'left');rootZ=record['root_height_m']
    pins={k:np.array(v)+[0,rootZ] for k,v in pins.items()}
    for keys,color,label in links:
        pts=np.array([pins[k] for k in keys]);ax.plot(pts[:,0]*1000,pts[:,1]*1000,'-o',lw=2,color=color,label=label,markersize=3)
    st=np.array([pins[k] for k in ['S','T']]);ax.plot(st[:,0]*1000,st[:,1]*1000,'--',lw=2,color='#7950ad',label='氮气弹簧')
    ax.add_patch(Circle(pins['W']*1000,62.5,fill=False,lw=2,color='#222a30'))
    for k,v in pins.items():ax.text(v[0]*1000+3,v[1]*1000+3,k,fontsize=9)
    ax.axhline(0,color='#555',lw=1);ax.axhline(247.2,color='#c45137',lw=1,ls=':')
    ax.set_aspect('equal');ax.set_xlim(-280,160);ax.set_ylim(-10,470);ax.grid(alpha=.15)
    ax.set_title(name);ax.set_xlabel('前后位置 (mm)');ax.set_ylabel('距主轮切平面的高度 (mm)')
handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=7,bbox_to_anchor=(.5,.02))
fig.savefig(OUT/'cad_kinematics.png',dpi=190,bbox_inches='tight');plt.close(fig)
print(json.dumps(records,ensure_ascii=False))
