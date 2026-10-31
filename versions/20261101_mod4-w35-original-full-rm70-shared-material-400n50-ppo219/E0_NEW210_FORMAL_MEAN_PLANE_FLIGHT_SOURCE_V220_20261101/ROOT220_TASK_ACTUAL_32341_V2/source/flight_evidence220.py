"""50Hz endpoint evidence; no reward/guard changes or success-rate threshold."""
import numpy as np


def runs(mask):
 result=[];begin=None
 for i,value in enumerate(list(mask)+[False]):
  if value and begin is None:begin=i
  elif not value and begin is not None:result.append((begin,i-1));begin=None
 return result


def summarize(contact_xyz,bottoms,flags,root13,actions,nonwheel_force_max=None):
 contact=np.asarray(contact_xyz,dtype=np.float32);bottom=np.asarray(bottoms,dtype=np.float32)
 norms=np.linalg.norm(contact,axis=-1);known=np.isfinite(bottom).all(1)
 low=(norms<=1.).all(1);clear=known&(bottom>.005).all(1);candidate=low&clear
 allruns=runs(candidate);confirmed=[(a,b) for a,b in allruns if b-a+1>=2]
 episodes=[]
 for a,b in confirmed:
  prev=a-1 if a else None;next_contact=next((k for k in range(b+1,len(bottom)) if (norms[k]>1.).any()),None)
  next_both=next((k for k in range(b+1,len(bottom)) if (norms[k]>1.).all()),None)
  after=None
  if next_contact is not None:
   k=next_contact;after=dict(control=k+1,both_wheel_force_norm_gt1N=bool((norms[k]>1.).all()),
    wheel_force_norm_N=norms[k].tolist(),authored_bottom_m=bottom[k].tolist() if known[k] else None,
    root_vz_m_s=float(root13[k,9]),terminal_flags=flags[k],stable_landing_claim=False)
  episodes.append(dict(start_control=a+1,end_control=b+1,consecutive_50Hz_endpoints=b-a+1,
   observed_endpoint_span_s=(b-a)*.02,
   observed_supported_endpoint_before=bool(prev is not None and known[prev] and (norms[prev]>1.).all() and (bottom[prev]<=.005).all()),
   left_censored_at_first_endpoint=a==0,right_censored_without_later_both_wheel_contact=next_both is None,
   first_contact_reappearance=after,both_wheel_contact_reappearance_control=None if next_both is None else next_both+1,
   minimum_common_authored_bottom_m=float(bottom[a:b+1].min()),
   maximum_wheel_force_norm_N=float(norms[a:b+1].max()),
   terminal_flags_in_air=[dict(control=k+1,flags=flags[k]) for k in range(a,b+1) if any(flags[k].values())],
   post_reset_pose_used=False,stable_landing_or_270_success=False))
 z=contact[:,:,2]
 status='OBSERVED' if confirmed else ('NOT_OBSERVED' if bool(known.all()) else 'UNKNOWN_GEOMETRY')
 da=np.diff(np.asarray(actions,dtype=np.float32),axis=0)
 return dict(status=status,
  definition='Both already-read wheel XYZ force norms<=1N AND both authored collision mesh bottoms>0.005m above original plane,>=2 consecutive50Hz endpoints',
  sampled_endpoint_evidence_only_not400Hz_continuous_or_cooked_depth=True,
  geometry_known_rows=int(known.sum()),geometry_unknown_rows=int((~known).sum()),
  row_index_basis='zero_based for *_rows;one_based for control fields',
  force_only_low_runs_not_flight_proof=[dict(start_control=a+1,end_control=b+1,endpoints=b-a+1) for a,b in runs(low)],
  candidate_rows=int(candidate.sum()),confirmed_runs=episodes,
  isolated_single_endpoint_candidates=[a+1 for a,b in allruns if a==b],
  both_force_norm_le1N_rows=int(low.sum()),both_force_z_le1N_rows=int((z<=1.).all(1).sum()),
  z_only_would_ignore_lateral_force_rows=np.flatnonzero((z<=1.).all(1)&~low).astype(int).tolist(),
  force_contact_with_authored_bottom_above5mm_rows=np.flatnonzero(known&(norms>1.).any(1)&(bottom>.005).all(1)).astype(int).tolist(),
  force_low_without_authored_5mm_clearance_rows=np.flatnonzero(low&known&~clear).astype(int).tolist(),
  all_terminal_events=[dict(control=k+1,flags=f) for k,f in enumerate(flags) if any(f.values())],
  wheel_evidence_with_nonwheel_force_gt1N_rows=[] if nonwheel_force_max is None else np.flatnonzero(candidate&(np.asarray(nonwheel_force_max)>1.)).astype(int).tolist(),
  wheel_only_evidence_not_whole_body_flight_certification=True,
  maximum_raw_action_abs=float(np.max(np.abs(actions))),
  maximum_consecutive_raw_action_change=0. if len(da)==0 else float(np.max(np.abs(da))),
  no_flight_does_not_mean_source_execution_failed=True,
  population_success_rate_or_stable_landing_or_270_skill_claim=False)
