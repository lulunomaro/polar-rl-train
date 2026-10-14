"""Bind existing full training exposure and isolate comparable first episode windows."""
from pathlib import Path
import json,numpy as np,hashlib,time
D=Path(__file__).resolve().parent;W=D.parent
def read(p):return json.loads(p.read_bytes())
def idx(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
r=read(D/'reports/E3_POSITIVE_4PI_ALL_PREFIX_MOTOR_CONTACT_ACTUAL_CPU_REVIEW.json')
ep=W/'MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014/reports/LEFT_SECOND_COMPLETE_SAVED_COMMAND_EXPOSURE_CPU_ACTUAL.json';exp=read(ep)
assert exp['passed_CPU_saved_command_counts'] and exp['own_final_SHA']==r['candidate']['checkpoint_sha256'] and exp['actual_controls']==4584 and exp['total_envsteps']==91680000
assert sum(v['total'] for v in exp['histogram'].values())==91680000
assert all(v['pure_yaw_positive']==v['pure_yaw_negative']==0 for v in exp['histogram'].values())
assert max(v['yaw_abs_max'] for v in exp['histogram'].values())<2
arrays={}
for kind in ('baseline','candidate'):
 with np.load(r[kind]['raw']['path'],allow_pickle=False) as z:arrays[kind]={k:z[k].copy() for k in ('root','impulse','raw_actor_action','terminated','truncated','before_root','before_q','policy_obs')}
assert np.array_equal(arrays['baseline']['before_root'][0],arrays['candidate']['before_root'][0]);assert np.array_equal(arrays['baseline']['before_q'][0],arrays['candidate']['before_q'][0])
common=[]
for br,cr in zip(r['baseline']['positive'],r['candidate']['positive']):
 i=br['env_id'];end=min(br['first_failure_control'],cr['first_failure_control']);assert end>=50
 row=dict(env_id=i,common_original_scored_controls=end-50,common_prefix_end_control=end,no_postfailure_samples=True)
 for k in ('baseline','candidate'):
  y=arrays[k]['root'][50:end,i,12];row[k]=dict(mean_yaw=float(y.mean()),mean_absolute_error=float(abs(y-4*np.pi).mean()),both_wheel1N_pct=float(np.mean((arrays[k]['impulse'][50:end,i]/.01>=1).all(-1))*100),rightwheel_raw_clip_pct=float(np.mean(arrays[k]['raw_actor_action'][50:end,i,5]>=6)*100))
 common.append(row)
out=D/'reports/E3_POSITIVE_SPIN_COMMON_VALID_PREFIX_AND_FULL_TRAINING_EXPOSURE_BOUND_CPU_ACTUAL.json';assert not out.exists()
out.write_text(json.dumps(dict(epoch=time.time(),no_SSH_GPU_PPO_budget_candidate=True,full_second_training_exposure_evidence=idx(ep),own_final_SHA=exp['own_final_SHA'],all4584x20000_saved_commands_reviewed_by_root=True,total_envsteps=91680000,actual_highest_absolute_yaw_rad_s=max(v['yaw_abs_max'] for v in exp['histogram'].values()),actual_pure_positive_or_negative_yaw_commands=0,observed_scope_mismatch_pure4pi_vs_projected_world_abs1to2=True,not_unique_causal_proof=True,common_positive_prefixes=common,ordinary_failure_control_endpoint_distinction='failure97th endpoint=.97s for zero-based control96; scored prefix excludes control96 and birth50 controls, 46 scored controls .50..96s phase labels. No post-reset mean credit.',next_minimal_frozen_single_axis_CPU_preparation={'axis':'saved actor35 command yaw input only','source':'retain exact own2b and e3 weights; no new weights or optimizer changes','test':'same saved actor35 vector, replace only yaw command at +-1/2/4pi, verify other34 exact and same35 baseline output exact first; compare executed6 clip domain under original guard. No physical rollout, no state/RNG mutation, no candidate','causal_limit':'same saved input counterfactual evaluates frozen actor response, not physical balance/traction/closed-loop causality','new_training_command_scope':'only if separately admitted to fixed approved contract; current production commands unchanged','deployment':False},current_fixed_parameters_not_changed=True,thresholds_not_changed=True,complete_parent_request=True),indent=2),encoding='utf8')
print(json.dumps(dict(output=str(out),common=common),indent=2))
