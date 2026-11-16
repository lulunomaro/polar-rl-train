"""Render only the measured candidate trajectory; no new teacher or policy actions."""
from pathlib import Path
import numpy as np,mujoco as mj,imageio.v2 as imageio,json,sys
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
T=Path(__file__).resolve().parent;dest=T/'local_probes/gated_v3/eval_00500/start_+000mm';a=np.load(dest/'rollout.npz');m=mj.MjModel.from_xml_path(str(dest/'scene.xml'));d=mj.MjData(m);renderer=mj.Renderer(m,height=480,width=720);camera=mj.MjvCamera();camera.azimuth=90;camera.elevation=-15;camera.distance=2.;camera.lookat[:]=[1.1,0,.3]
with imageio.get_writer(str(T/'preflight/SELECTED_STUDENT_CENTER_1X.mp4'),fps=25,codec='libx264',quality=7)as writer:
 for i in range(0,len(a['qpos']),2):
  d.qpos[:]=a['qpos'][i];mj.mj_forward(m,d);camera.lookat[0]=min(2.3,max(.8,float(d.qpos[0])));renderer.update_scene(d,camera=camera);writer.append_data(renderer.render())
renderer.close();fig,axes=plt.subplots(4,1,figsize=(11,9),sharex=True)
for dest in(T/'local_probes/gated_v3/eval_00500').glob('start_*'):
 tr=np.load(dest/'rollout.npz')['trace']
 for ax,y in zip(axes,[tr[:,1],tr[:,5],np.rad2deg(tr[:,6]),tr[:,3]]):ax.plot(tr[:,0],y,label=dest.name)
for ax,title in zip(axes,['Base X [m]','Horizontal speed [m/s]','Pitch [deg]','Base Z [m]']):ax.set_ylabel(title);ax.grid(True,alpha=.3)
axes[1].axhline(.6,color='k',ls='--');axes[0].legend(ncol=3);axes[-1].set_xlabel('Time [s]');fig.tight_layout();fig.savefig(T/'preflight/SELECTED_FIVE_STARTS.png',dpi=150);plt.close(fig);print('CANDIDATE_RENDER_COMPLETE',flush=True)
