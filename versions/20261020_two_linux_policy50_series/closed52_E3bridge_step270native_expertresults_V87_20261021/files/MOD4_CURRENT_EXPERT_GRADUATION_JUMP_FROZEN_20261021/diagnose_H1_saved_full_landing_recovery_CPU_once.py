from pathlib import Path
import json,time,numpy as np
B=Path(__file__).resolve().parent;R=B/'reports';O=B/'H1_full1500_actual/out'
review=json.loads((R/'H1_FULL1500_ALL_ROWS_INDEPENDENT_CPU_ACTUAL.json').read_bytes());assert review['passed_independent_execution_CPU'] and review['total_ordinary_resets']==0
landed=np.zeros(80,bool);recovered=np.zeros(80,bool);streak=np.zeros(80,np.int64);longest=streak.copy();total=streak.copy();yaw0=None;off={k:streak.copy() for k in ('both_wheel_support','nonwheel_clean','no_penetration','vertical_speed','planar_speed','roll','pitch','yaw')};first_land=np.full(80,-1);clock=0
for pp in sorted(O.glob('PHYSICS_*.npz')):
 p=np.load(pp,allow_pickle=False)
 yaw=p['yaw'];root=p['root13'];wheel=p['wheel_norm_N'];non=p['nonwheel_max'];clear=p['all34_clearance'];speed=p['root_planar_speed'];roll=p['roll'];pitch=p['pitch'];land=p['landing'];rec=p['recovery']
 if yaw0 is None:yaw0=yaw[0].copy()
 for i in range(len(root)):
  fresh=land[i]&~landed;first_land[fresh]=clock;landed|=land[i];recovered|=rec[i]
  dyaw=np.arctan2(np.sin(yaw[i]-yaw0),np.cos(yaw[i]-yaw0))
  gates=dict(both_wheel_support=(wheel[i]>1).all(-1),nonwheel_clean=non[i]<=1,no_penetration=clear[i].min(-1)>=-.001,vertical_speed=abs(root[i,:,9])<=.03,planar_speed=speed[i]<=.03,roll=abs(roll[i])<np.deg2rad(10),pitch=abs(pitch[i])<np.deg2rad(10),yaw=abs(dyaw)<.2)
  stable=landed.copy()
  for k,g in gates.items():off[k]+=landed&~g;stable&=g
  total+=landed;streak=np.where(stable,streak+1,0);longest=np.maximum(longest,streak);clock+=1
assert clock==6000 and landed.sum()==80 and np.array_equal(recovered,np.asarray(review['per_environment']['recovered'])) and np.array_equal(longest>=200,recovered)
bad=~recovered
rates={k:float(v[bad].sum()/total[bad].sum()) for k,v in off.items()}
v=dict(epoch=time.time(),passed_exact_original_stable_gate_reconstruction=True,source_SHA=review['source_SHA'],no_GPU_or_training=True,not_causal_reward_ablation=True,original_stable_requirement=dict(physical_dt_s=.0025,consecutive_callbacks=200,duration_s=.5,planar_v_m_s=.03,vertical_v_m_s=.03,roll_pitch_deg=10,yaw_rad=.2),landed=80,recovered=int(recovered.sum()),not_recovered=70,failed70_postlanding_gate_violation_fractions=sorted(rates.items(),key=lambda x:-x[1]),longest_stable_seconds_by_env=(longest*.0025).tolist(),failed70_longest_stable_seconds_quantiles={str(q):float(np.quantile(longest[bad]*.0025,q)) for q in (0,.5,.9,1)},first_landing_seconds_by_env=((first_land+1)*.0025).tolist(),limits='Observed gate violations explain missing original credit, but are not a controlled estimate of which reward change will learn faster. A true 270mm step was not present.')
(R/'H1_FULL1500_POSTLANDING_STABLE_GATE_DIAGNOSTIC_CPU_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(v,indent=2));print(json.dumps({k:x for k,x in v.items() if not k.endswith('by_env')}))
