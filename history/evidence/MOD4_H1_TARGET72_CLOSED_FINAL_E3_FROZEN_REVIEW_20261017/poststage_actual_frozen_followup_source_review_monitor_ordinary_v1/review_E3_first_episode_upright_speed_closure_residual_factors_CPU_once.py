"""Separate existing source upright/speed/window factors, keeping original0/96 unchanged."""
from pathlib import Path
import json,time,hashlib,os
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
B=Path(__file__).resolve().parent;R=B/'reports';proof=json.loads((R/'E3_CLOSED85_FULL1500_ORIGINAL_FIRST_EPISODE_RECOVERY_AND_NORMAL_RETENTION_RESIDUAL_CPU_V2_ACTUAL.json').read_bytes());raw=Path(proof['actual_raw']['path']);assert hashlib.sha256(raw.read_bytes()).hexdigest()==proof['actual_raw']['SHA']
with np.load(raw,allow_pickle=False) as z:a={k:z[k] for k in ('E3_gravity_z','E3_root13','E3_phase_request','E3_phase_stable','E3_phase_credited','terminated','truncated')}
def streak(v):
 n=best=0
 for good in v:n=n+1 if good else 0;best=max(best,n)
 return best
rows=[];summary={}
for old in proof['all_environment_valid_first_episode_rows']:
 i=old['env_id'];last=old['valid_controls_before_first_failure'];g=a['E3_gravity_z'][:last,i];root=a['E3_root13'][:last,i];request=a['E3_phase_request'][:last,i];up=g<-.984807753;speed=np.linalg.norm(root[:,7:10],axis=-1);angular=np.linalg.norm(root[:,10:13],axis=-1);slow=speed<.03;still=angular<.2;original_good=up&slow&still&request
 assert streak(original_good)==int(a['E3_phase_stable'][:last,i].max(initial=0))
 row=dict(env_id=i,recipe_id=old['recipe_id'],valid_prefix_controls=last,first_failure_reasons=old['first_failure_reasons'],ever_source_upright10deg=bool(up.any()),longest_upright_controls_any_request_state=streak(up),longest_upright_controls_original_request_window=streak(up&request),longest_original_upright_slow_still_requested_controls=streak(original_good),source_upright_and_slow_count=int((up&slow&request).sum()),source_upright_and_still_count=int((up&still&request).sum()),source_upright_requested_controls=int((up&request).sum()),source_good_without_request_mask_max_streak_diagnostic_only=streak(up&slow&still),upright_root_speed_median_m_s=float(np.median(speed[up])) if up.any() else None,upright_angular_speed_median_rad_s=float(np.median(angular[up])) if up.any() else None,minimum_tilt_deg=float(np.rad2deg(np.arccos(np.clip(-g,-1,1)))).min() if len(g) else None)
 rows.append(row)
for rid in range(13):
 rr=[r for r in rows if r['recipe_id']==rid];summary[str(rid)]=dict(environments=8,ever_upright10deg=sum(r['ever_source_upright10deg'] for r in rr),upright_at_least50_controls_any_request_state=sum(r['longest_upright_controls_any_request_state']>=50 for r in rr),upright50_in_original_request_window=sum(r['longest_upright_controls_original_request_window']>=50 for r in rr),original_stable50_credit=sum(r['longest_original_upright_slow_still_requested_controls']>=50 for r in rr),first_closure_failures=sum('closure' in r['first_failure_reasons'] for r in rr))
out=dict(epoch=time.time(),source_SHA=proof['source_SHA'],original_first_episode_recovery0of96_unchanged=True,normal8of8_whole15s_no_reset_unchanged=True,original_closure2mm_selectedreset_guard_not_relaxed=True,all_environment_factors=rows,per_recipe_factors=summary,source_original_condition_upright10deg_speed003_ang02_50controls_request3=True,upright_alone_or_after_window_diagnostics_not_reclassified_as_original_success=True,no_unique_physical_or_reward_cause_proven=True,no_GPU_reward_scope_or_learning_change=True)
with (R/'E3_FULL1500_SOURCE_UPRIGHT_SPEED_WINDOW_CLOSURE_FACTOR_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps(dict(original_success0of96=True,per_recipe=summary)),flush=True)
