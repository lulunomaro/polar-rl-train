"""Export measured curves and rendered frozen states, without driving the viewer."""
from pathlib import Path
import argparse
import json
import math
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mujoco
import numpy as np
from PIL import Image,ImageDraw,ImageFont

T=Path(__file__).resolve().parent;E=T/'evidence'
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args()
out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
def load(path):
    with np.load(path) as source:return {k:source[k] for k in source.files}
base=load(E/'pilot_teacher_r1/teacher_v0.4_s0/trajectory.npz')
pulse=load(E/'retraction_grid_t6_r1/teacher_v0.4_s0_retract0.173_0.3/trajectory.npz')
colors=['#147d92','#c04739'];fig,axes=plt.subplots(3,2,figsize=(12,9),constrained_layout=True)
for data,color,label in [(base,colors[0],'Frozen teacher'),(pulse,colors[1],'Retract after blocked')]:
    mask=(data['time']>=4.3)&(data['time']<=7.1);t=data['time'][mask]
    axes[0,0].plot(t,data['vx_body'][mask],color=color,label=label,linewidth=1.1)
    axes[0,1].plot(t,data['wheel'][mask,:,2].min(1)-.2625,color=color,linewidth=1.4)
    axes[1,0].plot(t,data['hip_to_wheel'][mask].mean(1),color=color,linewidth=1.4)
    axes[1,1].plot(t,data['root'][mask,2],color=color,linewidth=1.4)
    axes[2,0].plot(t,data['pose_deg'][mask,0],color=color,linewidth=1.2)
    b=int(data['base_body_id']);g=data['guide_body_ids'];w=data['wheel_body_ids'];f=data['body_contact_force'][mask]
    if label=='Retract after blocked':
        for ids,c,n in [(w,'#147d92','Drive wheels'),(g,'#6b8e26','Guide rollers'),([b],'#c04739','Chassis')]:
            vertical=f[:,ids,2].sum(1);smooth=np.convolve(vertical,np.ones(20)/20,mode='same')
            axes[2,1].plot(t,smooth,color=c,label=n,linewidth=1.2)
for ax,title,ylabel in zip(axes.flat,
    ['Actual forward speed','Both-wheel lower-rim clearance','Mean hip-to-wheel distance','Root height','Pitch','Vertical support force (50ms mean)'],
    ['m/s','m above first tread','m','m','degrees','N']):
    ax.set_title(title,fontsize=11);ax.set_ylabel(ylabel);ax.set_xlabel('Simulation time (s)');ax.grid(alpha=.2)
    ax.axvline(6.,color='#555555',linestyle='--',linewidth=.9)
axes[0,1].axhline(0.,color='black',linewidth=.8);axes[0,1].set_ylim(-.22,.06)
axes[0,0].legend(fontsize=9);axes[2,1].legend(fontsize=8)
fig.suptitle('Blocked first step, then retract | teacher 715c | command 0.4m/s',fontsize=14)
fig.savefig(out/'blocked_retraction_curves.png',dpi=160);plt.close(fig)

scene=next((E/'pilot_teacher_r1/scene_assets').glob('scene*.xml'))
m=mujoco.MjModel.from_xml_path(str(scene));d=mujoco.MjData(m)
m.vis.headlight.ambient[:]=[.7,.7,.7];m.vis.headlight.diffuse[:]=[.9,.9,.9]
for gi in range(m.ngeom):
    if m.geom_type[gi]==mujoco.mjtGeom.mjGEOM_MESH and m.geom_dataid[gi]==m.mesh('tile_visual').id:
        m.geom_rgba[gi]=[.68,.73,.72,1.]
cam=mujoco.MjvCamera();cam.type=mujoco.mjtCamera.mjCAMERA_FREE;cam.lookat[:]=[-2.9,0.,.28];cam.distance=1.65;cam.azimuth=125.;cam.elevation=-12.
opt=mujoco.MjvOption();opt.geomgroup[5]=0
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
frames=[(base,4.6025,'A. First riser contact'),(base,6.,'B. Blocked state, before pulse'),(pulse,6.16,'C. Legs retracting'),(pulse,float(pulse['time'][(pulse['wheel'][:,:,2].min(1)).argmax()]),'D. Highest paired wheel position')]
canvas=Image.new('RGB',(1600,1120),'white')
with mujoco.Renderer(m,height=460,width=800) as renderer:
    for k,(data,tt,label) in enumerate(frames):
        i=int(np.abs(data['time']-tt).argmin());d.qpos[:]=data['qpos_after'][i];d.qvel[:]=0.;mujoco.mj_forward(m,d)
        renderer.update_scene(d,camera=cam,scene_option=opt)
        edge_geom=renderer.scene.geoms[renderer.scene.ngeom]
        mujoco.mjv_initGeom(edge_geom,mujoco.mjtGeom.mjGEOM_CAPSULE,np.zeros(3),np.zeros(3),np.eye(3).ravel(),np.array([.95,.65,.04,1.],dtype=np.float32))
        mujoco.mjv_connector(edge_geom,mujoco.mjtGeom.mjGEOM_CAPSULE,.003,np.array([-2.9,-.65,.2]),np.array([-2.9,.65,.2]));renderer.scene.ngeom+=1
        for position,rgba in [(data['com'][i],[.9,.15,.15,1.]),(data['root'][i],[.05,.6,.9,1.])]:
            geom=renderer.scene.geoms[renderer.scene.ngeom]
            mujoco.mjv_initGeom(geom,mujoco.mjtGeom.mjGEOM_SPHERE,np.array([.014,.014,.014]),np.asarray(position),np.eye(3).ravel(),np.asarray(rgba,dtype=np.float32));renderer.scene.ngeom+=1
        image=Image.fromarray(renderer.render());x=(k%2)*800;y=(k//2)*560;canvas.paste(image,(x,y+40))
        draw=ImageDraw.Draw(canvas);draw.text((x+18,y+8),label,font=font,fill='#222222')
        draw.text((x+18,y+503),f't={data["time"][i]:.3f}s | root z={data["root"][i,2]:.3f}m | min wheel z={data["wheel"][i,:,2].min():.3f}m',font=small,fill='#333333')
        draw.text((x+18,y+529),f'COM x-edge={data["com"][i,0]+2.9:+.3f}m | root x-edge={data["root"][i,0]+2.9:+.3f}m | step=0.200m',font=small,fill='#333333')
canvas.save(out/'rendered_robot_states.png')
from scipy.spatial import ConvexHull
from matplotlib.patches import Circle,Polygon
from replay_probe import geom_points
fig,axs=plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
base_id=m.body('base_link').id
chassis=[(gi,geom_points(m,gi)) for gi in range(m.ngeom) if m.geom_bodyid[gi]==base_id and m.geom_contype[gi]!=0]
wheel_ids=[m.body(n).id for n in ('left_wheel_link','right_wheel_link')]
for ax,(data,tt,label) in zip(axs.flat,frames):
    i=int(np.abs(data['time']-tt).argmin());d.qpos[:]=data['qpos_after'][i];d.qvel[:]=0.;mujoco.mj_forward(m,d)
    ax.fill([-3.5,-2.9,-2.9,-2.3,-2.3,-3.5],[0,0,.2,.2,-.03,-.03],color='#d9dfdf')
    ax.plot([-3.5,-2.9,-2.9,-2.3],[0,0,.2,.2],color='#555555',linewidth=2.)
    points=np.concatenate([v@d.geom_xmat[g].reshape(3,3).T+d.geom_xpos[g] for g,v in chassis])[:,[0,2]]
    hull=ConvexHull(points);ax.add_patch(Polygon(points[hull.vertices],facecolor='#8ca4ad',edgecolor='#33464e',alpha=.6))
    for bid in range(1,m.nbody):
        parent=int(m.body_parentid[bid])
        if parent>0 and bid not in range(24,32):
            ax.plot(d.xpos[[parent,bid],0],d.xpos[[parent,bid],2],color='#65727a',alpha=.55,linewidth=1.)
    for wi,(bid,c) in enumerate(zip(wheel_ids,['#147d92','#d66d24'])):
        position=data['wheel'][i,wi];ax.add_patch(Circle(position[[0,2]],.0625,fill=False,color=c,linewidth=2.))
        ax.plot(position[0],position[2],'.',color=c)
    ax.plot(data['root'][i,0],data['root'][i,2],'D',color='#147d92',markersize=6,label='Root')
    ax.plot(data['com'][i,0],data['com'][i,2],'x',color='#c04739',markersize=9,markeredgewidth=2.,label='Whole-robot COM')
    ax.set_xlim(-3.4,-2.35);ax.set_ylim(-.03,.62);ax.set_aspect('equal');ax.grid(alpha=.15)
    ax.set_title(f'{label} | t={data["time"][i]:.3f}s',fontsize=11)
    ax.set_xlabel('World x (m); edge=-2.900m');ax.set_ylabel('Height (m)')
    ax.text(-3.38,.565,f'Wheel lower rim: {data["wheel"][i,:,2].min()-.0625:.3f}m\nCOM x-edge: {data["com"][i,0]+2.9:+.3f}m',fontsize=9)
axs[0,0].legend(loc='upper right',fontsize=8)
fig.suptitle('Recorded geometric side projections | first tread=0.200m | wheel radius=0.0625m',fontsize=13)
fig.savefig(out/'blocked_retraction_keyframes.png',dpi=160);plt.close(fig)
print(str(out/'blocked_retraction_curves.png'));print(str(out/'blocked_retraction_keyframes.png'))
