"""Preserve original per-environment first failure and source gates; no threshold change."""
from pathlib import Path
import json,time,os
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
B=Path(__file__).resolve().parent;R=B/'reports'

def main():
 cpu=json.loads((R/'H1_PUBLIC4FINAL_LINUX72_1500_ALL_PHYSICAL_PUBLIC04_SOURCE_FP64_REFERENCE_CPU_V3_ACTUAL.json').read_bytes());assert cpu['passed_complete_data_and_source_CPU']
 j=json.loads((R/'LINUX_GPU1_PUBLIC4FINAL_FULL1500_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json').read_bytes())
 def row(name):return next(x for x in j['files'] if x['relative'].endswith('/'+name))
 probe=json.loads(Path(row('probe.json')['local_path']).read_bytes());names=probe['native_readonly_witness']['reason_names'];raw=row('retention_full_control_substep_actual.npz')
 with np.load(raw['local_path'],allow_pickle=False) as z:
  done=z['terminated']|z['truncated'];S,N=done.shape;first=np.where(done.any(0),done.argmax(0),S);valid=np.arange(S)[:,None]<first[None,:];rows=[];counts={n:0 for n in names};modecounts={};failed=int((first<S).sum())
  for env,t in enumerate(first):
   reasons=[n for i,n in enumerate(names) if t<S and z['reasons'][t,env,i]]
   for n in reasons:counts[n]+=1
   mode=int(z['H1_public_request'][t,env]) if t<S else None
   if t<S:modecounts[str(mode)]=modecounts.get(str(mode),0)+1
   rows.append(dict(env=env,first_failure_control=int(t) if t<S else None,valid_first_duration_s=float(t*.01),original_reason_names=reasons,public4_request_at_failed_control=bool(mode) if t<S else None,closure_at_failed_control=float(z['closure'][t,env]) if t<S else None,mimic_at_failed_control=float(z['mimic'][t,env]) if t<S else None,ready_before_first_public4=bool(z['H1_phase_ready'][99,env]) if t>99 else None,original_air_ticks_max_before_failure=int(z['H1_phase_air_ticks'][:t,env].max()) if t>0 else 0))
  bounds={}
  for label,mask in [('normal_valid_prefix',valid&~z['H1_public_request']),('public4_valid_prefix',valid&z['H1_public_request'])]:
   v=z['raw_actor_action'][...,0][mask];bounds[label]=dict(rows=int(mask.sum()),raw_left_crank_below_minus6_fraction=float((v < -6).mean()) if len(v) else None,raw_left_crank_within_clip_fraction=float((abs(v)<=6).mean()) if len(v) else None)
 out=dict(epoch=time.time(),source_SHA=cpu['source_SHA'],actual_full_raw_index=raw,ordinary_total=cpu['ordinary'],truncations_total=cpu['truncations'],environments_with_first_failure=failed,whole15s_without_reset=N-failed,first_failure_counts_by_reason=counts,first_failure_counts_by_public4_request=modecounts,per_environment=rows,valid_prefix_action_bounds=bounds,failed_control_and_post_reset_events_not_counted_as_success=True,no_original_thresholds_gate_source_or_reward_changed=True,not_unique_optimizer_cause_proof=True,no_new_paid_window_permission=True)
 with (R/'PUBLIC4_V2_FINAL_FULL1500_ORIGINAL_FIRST_FAILURE_REASONS_AND_VALID_PREFIX_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps({k:out[k] for k in ['ordinary_total','truncations_total','environments_with_first_failure','whole15s_without_reset','first_failure_counts_by_reason','first_failure_counts_by_public4_request','valid_prefix_action_bounds']}))

if __name__=='__main__':main()
