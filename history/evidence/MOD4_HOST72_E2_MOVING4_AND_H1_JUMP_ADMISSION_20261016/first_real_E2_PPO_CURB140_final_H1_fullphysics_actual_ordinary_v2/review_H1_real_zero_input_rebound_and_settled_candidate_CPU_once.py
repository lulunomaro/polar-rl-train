"""Consume already collected dynamics; no new GPU rollout or change to old results."""
from pathlib import Path
import json,time,hashlib,numpy as np
from h1_settled_support_evidence_candidate_v2 import SettledH1Evidence
D=Path(__file__).resolve().parent;R=D/'reports'
def base(n=2):
 return dict(wheel_force_N=np.full((n,2),5.),wheel_clearance_m=np.zeros((n,2)),all_collider_min_clearance_m=np.zeros(n),nonwheel_force_N=np.zeros((n,29)),root_vz_m_s=np.zeros(n),roll_rad=np.zeros(n),pitch_rad=np.zeros(n),yaw_error_rad=np.zeros(n),speed_error_m_s=np.zeros(n),done=np.zeros(n,bool),operator_jump=np.ones(n,bool))
def main():
 f=SettledH1Evidence(2);v=base()
 for i in range(199):assert not f.update(**v)['settled_ground_armed'].any()
 assert f.update(**v)['settled_ground_armed'].all()
 for i in range(12):
  v['root_vz_m_s'][:]=.1;f.update(**v)
 v['wheel_force_N'][:]=0;v['wheel_clearance_m'][:]=.03;v['all_collider_min_clearance_m'][:]=.03
 for i in range(16):o=f.update(**v)
 assert o['takeoff'].all()
 v['wheel_force_N'][:]=5;v['wheel_clearance_m'][:]=0;v['all_collider_min_clearance_m'][:]=0;v['root_vz_m_s'][:]=0
 for i in range(12):o=f.update(**v)
 assert o['landing'].all()
 for i in range(200):o=f.update(**v)
 assert f.base.recovered.all()
 v['done'][:]=True;f.update(**v);assert not f.armed.any() and not f.base.launched.any()
 # Actual original calibration's immediate reset rebound must not arm from brief support.
 c=json.loads((R/'H1_FULLPHYSICS_CALIBRATION_V2_ACTUAL_BOUND_COLLECTION.json').read_bytes());ref=next(x['value'] for x in c['files'] if x['path'].endswith('/ACTUAL_AUTHORED_ALL_COLLIDER_REFERENCE.json'));non=[i for i,n in enumerate(ref['actual_contact_view_body_names']) if n not in ('left_wheel','right_wheel')];f=SettledH1Evidence(80);last=None;events=np.zeros((3,80),int);reward=np.zeros(80);armed=np.zeros(80,bool);rows=0;episodes=np.zeros(80,int);zero_group_reset_vz=[]
 for r in c['complete_local_raw']:
  if not Path(r['path']).name.startswith('physics_'):continue
  p=Path(r['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA']
  with np.load(p,allow_pickle=False) as z:
   for i in range(len(z['tick'])):
    ep=z['episode'][i];done=np.zeros(80,bool) if last is None else ep!=last;episodes+=done
    if rows==0 or done[0]:zero_group_reset_vz.append(float(z['root13'][i,0,9]))
    last=ep.copy();root=z['root13'][i];o=f.update(wheel_force_N=np.linalg.norm(z['wheel_5ms_mean_force'][i],axis=-1),wheel_clearance_m=z['wheel_clearance'][i],all_collider_min_clearance_m=z['all_shape_clearance'][i].min(1),nonwheel_force_N=np.linalg.norm(z['all_body_contact_force'][i][:,non],axis=-1),root_vz_m_s=root[:,9],roll_rad=z['roll'][i],pitch_rad=z['pitch'][i],yaw_error_rad=z['yaw'][i],speed_error_m_s=np.linalg.norm(root[:,7:9],axis=1),done=done,operator_jump=np.ones(80,bool));armed|=o['settled_ground_armed'];reward+=o['control_event_reward']
    for k,n in enumerate(('takeoff','landing','recovery')):events[k]+=o[n]
    rows+=1
 assert rows==1696 and not events.any() and not reward.any() and not armed.any()
 old=json.loads((R/'H1_ACTUAL_FULLCOLLIDER_TAKEOFF_LANDING_CALIBRATION_V2_CPU_REVIEW.json').read_bytes())
 report=dict(epoch=time.time(),actual_fullprefix_rows=rows,actual_zero_action_group0_V1_takeoff_envs=old['groups'][0]['takeoff_envs'],actual_zero_action_group0_V1_landing_envs=old['groups'][0]['landing_envs'],allgroups_V1_stable_recovery_envs=sum(x['recovery_envs'] for x in old['groups']),V1_reward_not_approved_for_PPO=True,V1_original_report_and_source_unchanged=True,interpretation='Zero action means original position-controller default target, not zero torque. Observed air is actual reference/contact motion but is not proof of actor-learned commanded jumping; reset/control-settling rebound is a candidate explanation, not a uniquely identified physical fault.',new_candidate='Require 500ms stable two-wheel ground support at low vertical and planar speed before arming; reset clears arming. Require authored full-collider ground consistency at landing. New thresholds are a declared candidate, not reduced original physics guards.',synthetic_same_episode_support_takeoff_landing_recovery_passed=True,synthetic_selected_reset_disarms_passed=True,actual80env1696callbacks_all_zero_false_jump_credit_after_settle_guard=True,actual_armed_envs=int(armed.sum()),actual_event_counts=events.tolist(),actual_reward_sum=float(reward.sum()),actual_episode_increments=int(episodes.sum()),group0_initial_after_reset_vz=zero_group_reset_vz,whole_collider_clearance_vs_actual_contact_during_landing_requires_geometry_frame_enabled_shape_audit=True,cookedShapeLocal_not_directly_read=True,new_candidate_not_installed_in_any_runtime=True,full20k_H1_source_phase_save_resume_and_reward_termination_release_not_passed=True,H1_PPO_dispatched=False,no_new_GPU_or_optimizer_or_budget=True)
 with (R/'H1_ZERO_INPUT_REBOUND_REJECTED_AND_SETTLED_GROUND_CANDIDATE_CPU_ACTUAL.json').open('x',encoding='utf8') as out:json.dump(report,out,indent=2)
 print(json.dumps(dict(actual_all_rows=rows,old_zero_action_takeoff_envs=report['actual_zero_action_group0_V1_takeoff_envs'],stable_recovery_envs=report['allgroups_V1_stable_recovery_envs'],new_candidate_actual_false_credit=0,no_jump_PPO=True)),flush=True)
if __name__=='__main__':main()
