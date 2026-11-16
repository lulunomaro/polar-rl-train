"""Rebuild Serial ten-state model using only MOD4 compiled mass/COM/inertia/FK."""
from pathlib import Path
import sys,json,time,importlib.util
import numpy as np,mujoco as mj
from scipy.linalg import solve_discrete_are
ROOT=Path(__file__).resolve().parent;sys.path[:0]=[str(ROOT),str(ROOT/'sim'),str(ROOT.parent)]
from native_geometry import G,PLANT,Mod4ClosedChainLeg
from mod4_retarget import Mod4Retarget
spec=importlib.util.spec_from_file_location('mod4_serial_linearize',ROOT/'tools/linearize.py');lin=importlib.util.module_from_spec(spec);spec.loader.exec_module(lin)
import yaml
cfg=yaml.safe_load((ROOT/'config/robot_params.yaml').read_text());cfg['simulation'].update(timestep_s=.0025,control_period_s=.02,control_frequency_hz=50)
cfg['mujoco']['base_body']='base_link';cfg['geometry']['wheel']['radius_m']=.0625;cfg['mujoco']['xml_path']=str(PLANT/'mjcf/scene.xml')
cfg['mujoco']['active_joints']={s+'_'+role:s+'_'+joint for s in ['left','right']for role,joint in [('front','front1_joint'),('back','rear1_joint')]}
cfg['mujoco']['wheel_joints']={s:s+'_wheel_joint'for s in ['left','right']}
m=G.m;d=G.d;ik=Mod4Retarget()
class Solver(lin.LegPoseSolver):
 def __init__(self):
  self.model=m;self._leg_body_ids={s:[b for b in G.bodies[i]if b!=G.wheel_ids[i]]for i,s in enumerate(['left','right'])};self._active_joints=cfg['mujoco']['active_joints'];self._wheel_joints=cfg['mujoco']['wheel_joints']
 def solve(self,data,h,seed=None):
  target=np.sqrt(h*h+ik.lateral_offset**2);r=ik.fit(target,0.);q=r['qpos'];q[:3]=[0,0,h+.0625];q[3:7]=[1,0,0,0];data.qpos[:]=q;data.qvel[:]=0.;mj.mj_forward(m,data);return q.copy()
solver=Solver();solver.solve(d,.25)
lin.chassis_body_ids=lambda model,base:G.chassis
body_com=lin.load_model_parameters(m,d,cfg,solver)
params=dict(total_mass_kg=float(sum(m.body_mass)),body_mass_kg=lin.M_BODY,leg_mass_per_side_kg=lin.M_LEG,wheel_mass_kg=lin.M_WHEEL,body_COM_from_hip_m=body_com.tolist(),body_inertia_kg_m2=[lin.I_BODY_XX,lin.I_BODY_YY,lin.I_BODY_ZZ],wheel_Iyy_kg_m2=lin.I_WHEEL_YY,wheel_radius_m=lin.WHEEL_RADIUS,half_track_m=lin.HALF_TRACK,control_period_s=lin.DT,leg_length_bounds_2d_m=[.11537519977075085,.34671288759430147],table_range_m=[.125,.346],source_Q=lin.Q_DIAG.tolist(),source_R=lin.R_MAT.tolist())
(ROOT/'PHYSICAL_PARAMETERS.json').write_text(json.dumps(params,indent=2)+'\n');print('PARAMETERS',json.dumps(params),flush=True)
cfg['geometry']['chassis'].update(half_track_m=lin.HALF_TRACK,track_width_m=2*lin.HALF_TRACK)
cfg['mass_properties']['total_robot_mass_kg']=float(sum(m.body_mass));cfg['mass_properties']['body'].update(mass_kg=lin.M_BODY,inertia_kg_m2=params['body_inertia_kg_m2'],com_local_m=body_com.tolist())
cfg['mass_properties']['links']={m.body(b).name:float(m.body_mass[b])for b in G.bodies[0]if b!=G.wheel_ids[0]};cfg['mass_properties']['wheel'].update(mass_kg=lin.M_WHEEL)
cfg['geometry']['five_link'].update(min_length_m=.125,max_length_m=.34671288759430147)
cfg['control_initial']['leg_length_trajectory'].update(min_length_m=.125,max_length_m=.34671288759430147,default_length_m=.25)
cfg['control_initial']['jump'].update(force_per_leg_n=500*float(sum(m.body_mass))/19.98001704448441,thrust_end_length_m=.34,retract_length_m=.125,wheel_speed_limit_radps=55.35573187814664)
cfg['control_initial']['self_righting']['enabled']=False
(ROOT/'config/robot_params.yaml').write_text(yaml.safe_dump(json.loads(json.dumps(cfg,default=lambda v: v.item())),allow_unicode=True,sort_keys=False),encoding='utf8')
start=time.perf_counter();dynamics=lin.build_serial_model();print('BUILT_SYMBOLIC',time.perf_counter()-start,flush=True)
grid=np.linspace(.125,.346,7);physical={}
for L in grid:
 solver.solve(d,float(L));physical[float(L)]={s:dict(com=solver.leg_com(d,s),inertia=solver.leg_inertia(d,s),axes=solver.leg_inertia_diagonal(d,s)[[0,2]],y=solver.leg_lateral_offset(d,s))for s in ['left','right']}
arrays={k:[]for k in ['L_l','L_r','A','B','Ad','Bd','K','u_eq','equilibrium','poles']};stats=dict(count=0,nonconverged=0,exceptions=0,max_residual=0.,worst=None)
for ll in grid:
 for lr in grid:
  l,r=physical[float(ll)]['left'],physical[float(lr)]['right'];A,B,u,pitch,el,er=lin.linearize_at_length(ll,lr,*l['com'],*r['com'],*dynamics[:3],stats,l['inertia'],r['inertia'],l['axes'],r['axes'],l['y'],r['y'])
  Ad,Bd=lin.discretize_zoh(A,B,.02);K=lin.design_supported_gain(Ad,Bd,np.diag(lin.Q_DIAG),lin.R_MAT);poles=np.abs(np.linalg.eigvals(Ad-Bd@K))
  for key,value in dict(L_l=ll,L_r=lr,A=A,B=B,Ad=Ad,Bd=Bd,K=K,u_eq=u,equilibrium=[0,0,pitch,el,er,0,0,0,0,0],poles=poles).items():arrays[key].append(value)
  print('GAIN',len(arrays['K']),float(ll),float(lr),'rho',float(max(poles)),flush=True)
np.savez_compressed(ROOT/'native_gains.npz',grid=grid,**{k:np.asarray(v)for k,v in arrays.items()})
(ROOT/'GAIN_BUILD.json').write_text(json.dumps(dict(points=len(arrays['K']),actual_seconds=time.perf_counter()-start,statistics=stats,max_pole=float(np.max(arrays['poles'])),source_gain_reused=False,physical_parameters=params,controller_period_s=.02,native_hold_model='Initially exact ZOH torque model; native PD inverse/hold consistency tested separately'),indent=2)+'\n')
