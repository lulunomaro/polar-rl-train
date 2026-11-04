"""One requested CPU MuJoCo parked/rear-folded startup test, same current E3.
No training or new original-skill acceptance threshold. Reuses existing local adapter.
"""
from pathlib import Path
import json,time,types,math,sys
D=Path(__file__).resolve().parent;SRC=D/'mujoco_core.py';ns={'__file__':str(SRC),'__name__':'e3_startup_core'};text=SRC.read_text(encoding='utf8').split("state={'paused'")[0];exec(compile(text,str(SRC),'exec'),ns)
np=ns['np'];mujoco=ns['mujoco'];sim=ns['E3Sim']();pose_file=Path('C:/Users/lulu/Desktop/claude/mjcf/chassis_mod4_work/folded_pose_sim/folded_pose_report.json');pose=json.loads(pose_file.read_bytes())['solutions']['clearance_0mm'];assert not(D/'RESULT.json').exists();records={}
def reset():
 mujoco.mj_resetData(sim.model,sim.data);sim.data.qpos[:3]=(-4.,0.,pose['root_height_m']);sim.data.qpos[3:7]=(1.,0.,0.,0.)
 for side,vals in pose['joint_values_rad'].items():
  for name,val in vals.items():j=sim.model.joint(side+'_'+name);sim.data.qpos[j.qposadr[0]]=val
 sim.data.qvel[:]=0;sim.data.ctrl[:]=0;sim.data.xfrc_applied[:]=0;sim.last_action[:]=0;sim.control_steps=0;sim._push_remaining=0;sim._observation_history=[];sim.command=ns['rt'].UserCommand(height=.25,mode=3,auto_mode=False);mujoco.mj_forward(sim.model,sim.data)
 # Position the lowest floor collision at rest rather than initialise penetration.
 distances=[float(c.dist)for c in sim.data.contact if sim.model.geom_type[c.geom1]==mujoco.mjtGeom.mjGEOM_PLANE or sim.model.geom_type[c.geom2]==mujoco.mjtGeom.mjGEOM_PLANE]
 lift=max(0.,-min(distances)+.0005)if distances else 0.;sim.data.qpos[2]+=lift;mujoco.mj_forward(sim.model,sim.data);sim._seed_observation_history(sim.observation_frame());return lift

def sample(t):
 R=sim.data.xmat[sim.chassis_id].reshape(3,3);v=np.zeros(6);mujoco.mj_objectVelocity(sim.model,sim.data,mujoco.mjtObj.mjOBJ_BODY,sim.chassis_id,v,1);g=R.T@np.array([0.,0.,-1.]);return dict(t=t,root_xyz=sim.data.qpos[:3].tolist(),upright_degrees=math.degrees(math.acos(float(np.clip(-g[2],-1,1)))),linear_speed=float(np.linalg.norm(v[3:])),angular_speed=float(np.linalg.norm(v[:3])),vx_body=float(v[3]),cmd_vx=sim.command.vx,mode=sim.command.mode,closure_m=sim.closure_error())

def image(name):
 try:
  with mujoco.Renderer(sim.model,height=500,width=800)as r:
   cam=mujoco.MjvCamera();cam.lookat[:]=sim.data.qpos[:3];cam.distance=1.35;cam.azimuth=90;cam.elevation=-12;r.update_scene(sim.data,camera=cam);from PIL import Image;Image.fromarray(r.render()).save(D/(name+'.png'))
 except Exception as e:(D/(name+'_render_error.txt')).write_text(repr(e),encoding='utf8')

for kind in('E3_recover_then_drive_same_weights',):
 lift=reset();initial=sample(0.);rows=[initial];q=[sim.data.qpos.copy()];actions=[np.zeros(6)];
 if kind.startswith('E3'):image('01_REAR_FOLDED_INITIAL')
 for i in range(650):
  sim.command.vx=0. if i<400 else .2;sim.command.mode=3 if i<400 else 0
  if kind.startswith('E3'):a=sim.step_control()
  else:
   sim.data.ctrl[:]=0
   for k in range(8):mujoco.mj_step(sim.model,sim.data)
   a=np.zeros(6)
  assert np.isfinite(sim.data.qpos).all()and np.isfinite(sim.data.qvel).all();rows.append(sample((i+1)*.02));q.append(sim.data.qpos.copy());actions.append(np.asarray(a).copy())
  if kind.startswith('E3')and i==399:image('02_AFTER_E3_RECOVERY_8S')
 if kind.startswith('E3'):image('03_AFTER_DRIVE_COMMAND_13S')
 heights=[r['root_xyz'][2]for r in rows];first=next((r['t']for r in rows if r['root_xyz'][2]>=.23 and r['upright_degrees']<10),None);rec=rows[400];end=rows[-1];drive=rows[401:];records[kind]=dict(initial=initial,floor_collision_initialisation_lift_m=lift,recovery_at_8s=rec,end_at_13s=end,first_230mm_and_upright10deg_s=first,max_root_height_m=max(heights),min_root_height_m=min(heights),drive_displacement_world_xy_m=[end['root_xyz'][j]-rec['root_xyz'][j]for j in(0,1)],drive_average_body_vx_m_s=float(np.mean([r['vx_body']for r in drive])),last2s_mean_body_vx_m_s=float(np.mean([r['vx_body']for r in rows[-100:]])),max_closure_m=max(r['closure_m']for r in rows),trajectory_rows=rows)
 np.savez_compressed(D/(kind+'.npz'),qpos=np.asarray(q),action=np.asarray(actions),time=np.arange(651)*.02)
result=dict(kind='NEW_TRAINED_E3_SAME_REAR_FOLDED_STARTUP_LOCAL_MUJOCO',epoch=time.time(),model_SHA=sim.policy.SHA,iteration=sim.policy.iteration,backend='existing local MuJoCo adapter, clean nominal; not native/fullDR/hardware qualification',initial_pose_source=str(pose_file),initial_pose_kind='level chassis, symmetric closed-linkage rear fold, zero joint/root velocity',target_height_m=.25,commands='0-8s recovery mode3/vx0;8-13s normal mode0/vx0.2; same E3 weights throughout',no_scripted_joint_targets_or_assisted_lifting=True,reference_230mm_descriptive_only_not_original_graduation=True,training_registry_or_budget_operations=0,cases=records)
(D/'RESULT.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf8');print(json.dumps({k:{a:b for a,b in r.items()if a!='trajectory_rows'}for k,r in records.items()},indent=2))

compact=dict(model_SHA=sim.policy.SHA,iteration=sim.policy.iteration,cases={k:{a:b for a,b in r.items()if a!='trajectory_rows'}for k,r in records.items()},backend='local nominal MuJoCo, not native fullDR/hardware');(D/'SUMMARY.json').write_text(json.dumps(compact,indent=2,allow_nan=False),encoding='utf8')
