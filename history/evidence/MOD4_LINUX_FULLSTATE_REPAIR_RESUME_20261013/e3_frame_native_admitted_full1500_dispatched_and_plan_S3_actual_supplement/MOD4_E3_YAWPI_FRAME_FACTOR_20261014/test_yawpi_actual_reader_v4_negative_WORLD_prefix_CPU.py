"""Actual native proof + synthetic failures, no future full1500 pass."""
from pathlib import Path
import json,time,copy,numpy as np
import yawpi_actual_reader_components_v4 as m
D=Path(__file__).resolve().parent;R=D/'reports';native=R/'YAWPI_OWN_NATIVE120_ACTUAL_CPU_ADMITTED_V3.json';ad=m.read(native);assert ad['passed_actual_data_and_factor_admission'] and ad['controls']==120 and ad['callbacks']==480
first=m.read(ad['factor_firstphysics_snapshot']['local_path']);birth=first['actual_last_birth'];m.birth_receipt(birth)
bad=[]
for key,value in [('profile','wrongprofile'),('full_collision_points',25199),('full_q30_exact',False),('XY_exact',False),('original_clearance_m',.001),('minimum_sampled_clearance_m',0.),('extra_physics_steps_forward_render_reset',1),('no_rng_draw',False)]:
 b=copy.deepcopy(birth);b[key]=value;bad.append(b)
for field,offset in ((3,None),(0,.1),(2,.1)):
 b=copy.deepcopy(birth)
 if offset is None:b['factor_root_xyzw'][0][3:7]=b['original_root_xyzw'][0][3:7]
 else:b['factor_root_xyzw'][0][field]+=offset
 bad.append(b)
rejected=0
for b in bad:
 try:m.birth_receipt(b)
 except AssertionError:rejected+=1
 else:raise AssertionError('Malformed own-birth fixture admitted')
ids,_,after=m.birth_receipt(birth)
with np.load(ad['query']['local_path']) as z:tri=z['world_triangles'].copy()
with np.load(m.W/'MOD4_3060_LEFT_SECOND_FULL80_20261014/payload/runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz') as z:pick=int(np.argmin(abs(z['root_height']-.25)));points=z['points_root'][pick].astype(np.float32)
m.independent_safe_z(ids[:1],after[:1],tri,points)
wrong=after[:1].copy();wrong[:,2]+=.01
try:m.independent_safe_z(ids[:1],wrong,tri,points)
except AssertionError:rejected+=1
else:raise AssertionError('Illegal safeZ admitted')
half=1.2032113635;steps=3;g=np.arange(80)%3;sign=np.where(g==1,-1,1)
data=dict(root=np.zeros((steps,80,13)),group_ids=g,physical_wheel_force_N=np.zeros((steps*4,80,2,3),np.float32),COM_link_pos=np.zeros((steps,80,2,3),np.float32),episode=np.zeros((steps,80),np.int64),terminated=np.zeros((steps,80),bool))
data['physical_wheel_force_N'][...,2]=1.01
for s,x in enumerate((-half-.201,0.,half+.201)):data['COM_link_pos'][s,:,:,0]=(x*sign)[:,None]
report=dict(route_scope=dict(tile_centers=np.zeros((80,2)).tolist(),wave_x_halfspan_m=half),body_names=['left_wheel','right_wheel'])
per=m.route_rows(data,report);assert sum(x['contact_complete'] for x in per if x['group']==0)==27 and sum(x['contact_complete'] for x in per if x['group']==1)==27 and not any(x['contact_complete'] for x in per if x['group']==2)
data['terminated'][1,0]=True;per=m.route_rows(data,report);assert not per[0]['contact_complete'] and per[0]['all_valid_episodes'][0]['valid_controls']==1
data['terminated'][:]=False;data['episode'][1:,0]=1;per=m.route_rows(data,report);assert not per[0]['contact_complete']
data['episode'][:]=0;data['physical_wheel_force_N'][:,0,:,2]=.99;per=m.route_rows(data,report);assert not per[0]['contact_complete'] and per[0]['position_complete'] and per[0]['all_valid_episodes'][0]['position_contact_agree'] is False
data['physical_wheel_force_N'][:,0,:,2]=1.;per=m.route_rows(data,report);assert not per[0]['contact_complete'],'Original strict >1N became >=1N'
try:m.review(D/'reports/FUTURE_FULL1500_NOT_GENERATED.json',m.W/'MOD4_3060_LEFT_SECOND_FULL80_20261014/reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json',1500,native)
except FileNotFoundError:rejected+=1
else:raise AssertionError('Missing future full1500 admitted')
o=R/'YAWPI_V4_READER_ACTUAL_NATIVE_AND_NEGATIVE_PREFIX_CPU_TESTED.json';assert not o.exists()
o.write_text(json.dumps(dict(epoch=time.time(),passed_CPU_reader_test_only=True,own_actual_native120_proof=dict(path=str(native),sha256=m.sha(native)),strict_negative_cases_rejected=rejected,synthetic_WORLD_cohort_sign_preserved=True,synthetic_original_strict1N_support_behavior_failure_separate_from_position=True,synthetic_ordinary_prefix_and_cross_episode_teleport_not_credited=True,actual_25200point_safeZ_good_and_bad_CPU_tested=True,missing_future_full1500_failclosed=True,full1500_actual_NOT_generated_or_claimed=True,no_SSH_GPU_PPO_budget=True,reader_components_SHA=m.sha(Path(m.__file__)),Git_pending_root=True),indent=2),encoding='utf8')
print(json.dumps(dict(report=str(o),rejected=rejected,actual_native120=True,future_full1500=False)))
