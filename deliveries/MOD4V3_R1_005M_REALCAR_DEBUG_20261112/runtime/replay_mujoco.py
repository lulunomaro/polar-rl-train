"""Self-contained ONNX MuJoCo replay using the delivered plant, no Torch/Isaac."""
from pathlib import Path
import argparse,json,math,time,csv
import numpy as np,mujoco
from control import Controller,limit_torque
B=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--suite',action='store_true');p.add_argument('--viewer',action='store_true');p.add_argument('--vx',type=float,default=0.);p.add_argument('--wz',type=float,default=0.);p.add_argument('--height',type=float,default=.28);p.add_argument('--seconds',type=float,default=8.);p.add_argument('--out');a=p.parse_args()
m=mujoco.MjModel.from_xml_path(str(B/'plant/mjcf/scene.xml'));d=mujoco.MjData(m);ctrl=Controller();C=ctrl.session;cfg=json.loads((B/'config/deployment_contract.json').read_text(encoding='utf-8'));order=cfg['output']['order'];qidx=[m.jnt_qposadr[m.joint(n).id] for n in order];vidx=[m.jnt_dofadr[m.joint(n).id] for n in order];act=[m.actuator(n+'_motor').id for n in order];base=m.body('base_link').id
rows=json.loads((B/'plant/semantics.json').read_text(encoding='utf-8'))['coordinates']['native_from_v2'];bank=json.loads((B/'plant/reset_bank.json').read_text(encoding='utf-8'));pose=next(x for x in bank['poses'] if .24<=x['root_height_m']<=.272)
assert abs(m.opt.timestep-.0025)<1e-12
viewer=None
if a.viewer:
 import mujoco.viewer
 viewer=mujoco.viewer.launch_passive(m,d);viewer.cam.distance=2.;viewer.cam.elevation=-17.
def reset():
 mujoco.mj_resetData(m,d);d.qpos[:3]=[0,0,pose['root_height_m']];d.qpos[3:7]=[1,0,0,0]
 for name,row in rows.items():d.qpos[m.jnt_qposadr[m.joint(name).id]]=pose['joint_pos'].get(row['source'],0.)+row['offset_si']
 mujoco.mj_forward(m,d);ctrl.reset()
def closure():
 errors=[]
 for i in range(m.neq):
  if m.eq_type[i]!=mujoco.mjtEq.mjEQ_CONNECT:continue
  x,y=m.eq_obj1id[i],m.eq_obj2id[i]
  if m.eq_objtype[i]==mujoco.mjtObj.mjOBJ_SITE:errors.append(np.linalg.norm(d.site_xpos[x]-d.site_xpos[y]))
  else:errors.append(np.linalg.norm(d.xpos[x]+d.xmat[x].reshape(3,3)@m.eq_data[i,:3]-d.xpos[y]-d.xmat[y].reshape(3,3)@m.eq_data[i,3:6]))
 return max(errors,default=0.)
def state(command):
 R=d.xmat[base].reshape(3,3);velocity=np.zeros(6);mujoco.mj_objectVelocity(m,d,mujoco.mjtObj.mjOBJ_BODY,base,velocity,1)
 return dict(command=command,joint_position_rad=d.qpos[qidx].tolist(),joint_velocity_rad_s=d.qvel[vidx].tolist(),gyro_b_rad_s=velocity[:3].tolist(),gravity_b=(R.T@np.array([0.,0.,-1.])).tolist())
tasks=[('stand',0,0,.28),('forward_0p3',.3,0,.28),('forward_2p0',2.,0,.28),('forward_2p2',2.2,0,.28),('backward_1p5',-1.5,0,.28),('yaw',0,14.137167,.28),('low',0,0,.2),('high',0,0,.4)] if a.suite else [('manual',a.vx,a.wz,a.height)]
results=[];trace=[]
try:
 for name,vx,wz,h in tasks:
  reset();points=[];failure=None;worst=0.;held=np.zeros(6,np.float32)
  for step in range(int(a.seconds/.02)):
   begun=time.monotonic();reply=ctrl.policy_tick(state([vx,0.,wz,h]));target=np.asarray(reply['target'],np.float32)
   for sub in range(8):
    if sub%4==0:held=ctrl.PD_tick(d.qpos[qidx],d.qvel[vidx])
    d.ctrl[act]=limit_torque(held,d.qvel[vidx]);mujoco.mj_step(m,d);cl=closure();worst=max(worst,float(cl))
    if not np.isfinite(d.qpos).all() or not np.isfinite(d.qvel).all() or cl>.002:failure=dict(time_s=float(d.time),reason='closure2mm' if cl>.002 else 'nonfinite',closure_m=float(cl));break
   R=d.xmat[base].reshape(3,3);row=[name,float(d.time),float(d.qpos[0]),float(d.qpos[1]),float(d.qpos[2]),float(d.qvel[0]*R[0,0]+d.qvel[1]*R[1,0]),float(d.qvel[5]),float(R[2,2]),float(cl)];trace.append(row);points.append(row)
   if viewer:
    viewer.cam.lookat[:]=[d.qpos[0],d.qpos[1],.25];viewer.sync();time.sleep(max(0,.02-(time.monotonic()-begun)))
    if not viewer.is_running():break
   if failure:break
  tail=np.asarray([x[1:] for x in points[-100:]],float);results.append(dict(case=name,command=[vx,0,wz,h],steps=len(points),safety_failure=failure,closure_max_m=worst,vx_tail_mean=float(tail[:,4].mean()),wz_tail_mean=float(tail[:,5].mean()),height_tail_mean=float(tail[:,3].mean()),tilt_cos_tail_min=float(tail[:,6].min())))
finally:
 if viewer:viewer.close()
result=dict(checkpoint_sha256=cfg['checkpoint_sha256'],engine='MuJoCo, delivered ONNX+codec, nominal parameters, no artificial delay; no actual hardware',no_automatic_reset=True,results=results)
if a.out:
 out=Path(a.out);out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 with out.with_suffix('.csv').open('w',newline='',encoding='utf-8') as f:w=csv.writer(f);w.writerow(['case','time_s','x','y','root_z','vx_body','wz_body','tilt_cos','closure_m']);w.writerows(trace)
print(json.dumps(result,ensure_ascii=False,indent=2))
