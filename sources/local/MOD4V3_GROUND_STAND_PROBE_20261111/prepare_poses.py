"""Generate eight collision-feasible belly-on-floor leg poses; never changes the plant."""
from pathlib import Path
import sys,json,hashlib,math
import numpy as np,mujoco
ROOT=Path('D:/claude2/fangzhen');OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'runs3060/mod4v3_play_20261107'))
from eval_flatv2_final import args_for
from play_ppo_flatv1_control import Simulation
weight=ROOT/'_mod4v2_src_20261106/sources/local/MOD4V3_ROUGH_R1_ROUND2_20261111/weights/model_005m.pt'
s=Simulation(args_for(str(weight)));m,d=s.env.m,s.env.d
bank_path=ROOT/'_mod4v2_src_20261106/sources/local/MOD4V3_ROUGH_R1_ROUND2_20261111/support/mod4v3_ppo_v1/remaining_reset_bank.json'
bank=json.loads(bank_path.read_text());names=bank['joint_names'];qbank=np.asarray(bank['positions']);rng=np.random.default_rng(11112026)
qadr=np.asarray([m.jnt_qposadr[m.joint(n).id] for n in names]);ground=m.geom('ground').id
colliders=[i for i in range(m.ngeom) if m.geom_bodyid[i]>0 and (m.geom_contype[i] or m.geom_conaffinity[i])]
belly=[i for i in colliders if m.geom_bodyid[i]==s.env.base_id]
support=belly+[i for i in colliders if (m.geom(i).name or '').startswith('guide_wheel_')]
def distances(ids):return np.asarray([mujoco.mj_geomDistance(m,d,ground,i,3.,None) for i in ids])
def closure():
 errors=[]
 for i in range(m.neq):
  if m.eq_type[i]!=mujoco.mjtEq.mjEQ_CONNECT:continue
  b1,b2=m.eq_obj1id[i],m.eq_obj2id[i]
  if m.eq_objtype[i]==mujoco.mjtObj.mjOBJ_SITE:errors.append(float(np.linalg.norm(d.site_xpos[b1]-d.site_xpos[b2])))
  else:
   a=m.eq_data[i,:3];b=m.eq_data[i,3:6]
   errors.append(float(np.linalg.norm(d.xpos[b1]+d.xmat[b1].reshape(3,3)@a-d.xpos[b2]-d.xmat[b2].reshape(3,3)@b)))
 return max(errors,default=0.)
patterns=[('front_front','ground_positive','ground_positive'),('rear_rear','ground_negative','ground_negative'),('front_rear','ground_positive','ground_negative'),('rear_front','ground_negative','ground_positive'),('random_04',None,None),('random_05',None,None),('random_06',None,None),('random_07',None,None)]
rows=[]
for label,lmode,rmode in patterns:
 for attempt in range(10000):
  d.qpos[:]=m.qpos0;d.qvel[:]=0.;d.qpos[:3]=[0.,0.,1.];d.qpos[3:7]=[1.,0.,0.,0.]
  picks=[];modes=[];q=np.zeros(len(names))
  for side,requested in [('left',lmode),('right',rmode)]:
   mode=requested or rng.choice(['ground_positive','ground_negative']);pick=int(rng.choice(bank['mode_indices'][mode]));picks.append(pick);modes.append(mode)
   cols=[i for i,n in enumerate(names) if n.startswith(side+'_')];q[cols]=qbank[pick,cols]
  d.qpos[qadr]=q;mujoco.mj_forward(m,d);d.qpos[2]-=float(distances(support).min());mujoco.mj_forward(m,d)
  ds=distances(colliders);cl=closure()
  if ds.min()>=-0.0002 and cl<0.0001:break
 else:
  print('GEOMETRY_DEBUG',label,'closure',cl,'base',float(distances(belly).min()),'lowest',[(mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_GEOM,colliders[i]),float(ds[i])) for i in np.argsort(ds)[:8]],flush=True)
  raise RuntimeError('No belly-supported nonpenetrating pose: '+label)
 rows.append(dict(id=label,kind='belly_ground_random_legs',root_position=d.qpos[:3].tolist(),root_quaternion_xyzw=d.qpos[[4,5,6,3]].tolist(),joint_positions=dict(zip(names,q.tolist())),selected_bank_ids=picks,leg_modes=modes,leg_length_m=[bank['lengths'][i] for i in picks],leg_angle_rad=[bank['angles'][i] for i in picks],minimum_floor_clearance_m=float(ds.min()),chassis_floor_clearance_m=float(distances(belly).min()),chassis_support_clearance_m=float(distances(support).min()),closure_m=cl,rejection_draws=attempt))
s.env.reset();rows.append(dict(id='standing_control',kind='standing_control',root_position=d.qpos[:3].tolist(),root_quaternion_xyzw=d.qpos[[4,5,6,3]].tolist(),joint_positions={n:float(d.qpos[i]) for n,i in zip(names,qadr)}))
result=dict(checkpoint=str(weight),checkpoint_sha256=hashlib.sha256(weight.read_bytes()).hexdigest(),xml=str(s.args.xml),xml_sha256=hashlib.sha256(Path(s.args.xml).read_bytes()).hexdigest(),reset_bank_sha256=hashlib.sha256(bank_path.read_bytes()).hexdigest(),seed=11112026,pose_generation='Unmodified MOD4 feasible linkage bank, independent legs; reject only floor penetration or invalid closure at chassis underside/guide-roller support; actual rollers project 11mm below chassis belly. These are eight finite samples, not all reachable states.',cases=rows)
(OUT/'INITIAL_POSES.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');s.close()
for r in rows:print(r['id'],r['root_position'][2],r.get('leg_modes'),r.get('closure_m'),flush=True)
