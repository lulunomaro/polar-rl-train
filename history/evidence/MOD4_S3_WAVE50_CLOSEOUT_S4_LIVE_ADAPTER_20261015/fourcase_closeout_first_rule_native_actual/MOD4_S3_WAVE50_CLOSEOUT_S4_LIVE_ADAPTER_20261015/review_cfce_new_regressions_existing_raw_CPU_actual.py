"""Existing paired full raw only. No physical replay or threshold change."""
from pathlib import Path
import json,hashlib,time,numpy as np
D=Path(__file__).resolve().parent;W=D.parent;H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
paths=[W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014/reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json',W/'MOD4_3060_BODYFRAME_PHASE_FINAL_FULL80_20261015/reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json']
reviews=[json.loads(p.read_bytes()) for p in paths];data=[]
for r in reviews:
 assert r['passed'];p=Path(r['raw']['local_path']);assert H(p)==r['raw']['sha256']
 with np.load(p,allow_pickle=False) as z:data.append({k:z[k].copy() for k in ('root','before_root','command','impulse','episode','terminated','truncated','action','processed_action','closure')})
def prefix(r,a,i):
 row=r['rows'][i];assert row['env']==i
 ep=row['all_valid_episodes'][0];first=ep['valid_first_control'];last=ep['valid_last_control'];idx=slice(first,last+1)
 assert (a['episode'][idx,i]==ep['episode']).all()
 roots=np.concatenate((a['before_root'][first,i][None],a['root'][idx,i]))
 q=roots[:,3:7].astype(np.float64);x,y,z,w=q.T
 yaw=np.unwrap(np.arctan2(2*(w*z+x*y),1-2*(y*y+z*z)))
 xy=roots[:,:2].astype(np.float64);delta=xy-xy[0]
 initial_yaw=yaw[0];along=delta[:,0]*np.cos(initial_yaw)+delta[:,1]*np.sin(initial_yaw)
 cross=-delta[:,0]*np.sin(initial_yaw)+delta[:,1]*np.cos(initial_yaw)
 support=(a['impulse'][idx,i]/.01>1).all(-1)
 return dict(env=i,complete=row['contact_complete'],episode=ep['episode'],valid_first_control=first,valid_last_control=last,valid_controls=last-first+1,original_ordinary_failure_control=ep['ordinary_failure_control'],root_final_along_initial_body_m=float(along[-1]),root_final_cross_initial_body_m=float(cross[-1]),root_cross_peak_to_peak_m=float(np.ptp(cross)),final_yaw_change_deg=float(np.degrees(yaw[-1]-yaw[0])),max_abs_yaw_change_deg=float(np.degrees(abs(yaw-yaw[0]).max())),both_wheel_mean_load_strict_over1N_percent=float(support.mean()*100),left_raw_clip6_percent=float((abs(a['action'][idx,i,0])>6).mean()*100),max_closure_m=float(a['closure'][idx,i].max()),original_signed_wheel_route_range=ep['signed_wheel_route_range'],original_after_double1N_controls_present=bool(ep['after_double1N_controls']),prefix_no_post_reset_samples=True,root_displacement_not_wheel_route_certificate=True)
rows=[dict(env=i,protected_f516=prefix(reviews[0],data[0],i),new_cfce=prefix(reviews[1],data[1],i)) for i in (36,48,57,72,15,67)]
out=dict(epoch=time.time(),reviewed=True,original_full_physical_pair_reviews=[dict(path=str(p),sha256=H(p)) for p in paths],new_forward_regressions=[36,48,57,72],remaining_forward15_and_reverse67=True,rows=rows,terrain_preferred_source='f5166509d297814e3c3fe4f457ae064d9b02a8bd62702914759dc430f20d2139',cfce_world64_of64_distinct_retention_evidence=True,learning_and_birth_exposure_not_isolated_single_cause=True,raw_clipping_or_support_alone_not_unique_causal_proof=True,no_GPU_SSH_PPO_or_new_acceptance_threshold=True,no_third_blind_BODY_or_left_learning=True,qualified50=False)
p=D/'reports/CFCE_NEW_FORWARD_REGRESSIONS_AND_RETAINED_FAILURE_PREFIX_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps(dict(report=str(p),paired_existing_raw_only=True,rows=[dict(env=x['env'],cf_yaw=x['new_cfce']['final_yaw_change_deg'],cf_cross=x['new_cfce']['root_final_cross_initial_body_m'],cf_support=x['new_cfce']['both_wheel_mean_load_strict_over1N_percent']) for x in rows])))
