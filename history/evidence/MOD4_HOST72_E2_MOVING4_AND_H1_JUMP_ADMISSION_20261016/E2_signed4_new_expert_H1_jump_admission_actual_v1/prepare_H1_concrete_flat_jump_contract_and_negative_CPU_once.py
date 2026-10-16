"""Freeze narrow H1 proposal and actual CPU evidence machine; SDK release remains gated."""
from pathlib import Path
import json,hashlib,time,copy
import numpy as np
from h1_flat_jump_evidence_reward_cpu_v1 import H1Evidence
D=Path(__file__).resolve().parent;R=D/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def row(n=2,**kw):
 x=dict(wheel_force_N=np.full((n,2),10.),wheel_clearance_m=np.zeros((n,2)),all_collider_min_clearance_m=np.zeros(n),nonwheel_force_N=np.zeros((n,29)),root_vz_m_s=np.zeros(n),roll_rad=np.zeros(n),pitch_rad=np.zeros(n),yaw_error_rad=np.zeros(n),speed_error_m_s=np.zeros(n),done=np.zeros(n,bool),operator_jump=np.ones(n,bool));x.update(kw);return x
def play(states):
 f=H1Evidence(2);total=np.zeros(2)
 for repeat,x in states:
  for i in range(repeat):total+=f.update(**x)['control_event_reward']
 return f,total
def put(p,v):
 with p.open('x',encoding='utf8') as out:json.dump(v,out,indent=2)
def main():
 ground=row();air=row(wheel_force_N=np.zeros((2,2)),wheel_clearance_m=np.full((2,2),.03),all_collider_min_clearance_m=np.full(2,.03),root_vz_m_s=np.full(2,.5));land=row()
 f,total=play([(12,ground),(20,air),(212,land)]);assert f.recovered.all() and np.array_equal(total,np.full(2,7.))
 checks=[]
 for name,states in [('standing_no_takeoff',[(500,ground)]),('root_rise_without_wheel_clearance',[(12,ground),(100,row(root_vz_m_s=np.ones(2)))]),('body_contact_cannot_be_air',[(12,ground),(100,{**air,'nonwheel_force_N':np.ones((2,29))*2})]),('short_air_not40ms',[(12,ground),(15,air),(230,land)]),('falling_no_positive_takeoff',[(12,ground),(100,{**air,'root_vz_m_s':np.full(2,-.5)})])]:
  z,reward=play(states);assert not z.launched.any() and (reward==0).all();checks.append(name)
 z,reward=play([(12,ground),(20,air),(1000,air)]);assert (reward==2).all() and not z.landed.any();checks.append('no_per_second_air_reward')
 z,reward=play([(12,ground),(20,air),(1,row(done=np.ones(2,bool))),(230,land)]);assert not z.landed.any() and not z.recovered.any();checks.append('reset_cannot_inherit_air_credit')
 z=H1Evidence(2)
 for i in range(12):z.update(**ground)
 snapshot=copy.deepcopy(vars(z));z.reset([0])
 for k,v in snapshot.items():
  if isinstance(v,np.ndarray):assert z.__dict__[k][1]==v[1]
 checks.append('selected_reset_only_own_row')
 try:H1Evidence(2).update(**row(all_collider_min_clearance_m=np.full(2,np.nan)))
 except ValueError:checks.append('missing_collider_unknown_rejected')
 else:raise AssertionError('Missing collider evidence accepted')
 proposal=dict(id='MOD4-E5-H1-FLAT-COMMANDED-JUMP-ADMISSION-20261016',epoch=time.time(),status='CONCRETE_CPU_CANDIDATE_NATIVE_ADMISSION_ONLY',human_requested_jump_and_selected_jump_before_selfrescue=True,approved_for_PPO=False,source_SHA='b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8',source_all_D0_D7_floating=94,source_actor9_critic8_STD17Adam_preserved=True,geometry='Existing flat native Plane; no step and no airborne reset',target_minimum_wheel_bottom_apex_clearance_m=.03,operator_mode_jump=[0,0,0,0,1,0,0],normal_commands=[0,0,0],script_probability=0,teacher_or_upward_force_or_extra_torque=False,physics=dict(dt=.0025,decimation=4,TGS=[32,4],policy_Hz=100,contact_bin=.005,actor35_critic38_action6=True),event_proposal=dict(ground_support_eachwheel_N_strictly_over=1,pre_support_seconds=.03,both_wheel_clearance_strictly_over_m=.005,all_body_contact_and_collision_clearance_required=True,air_seconds=.04,landing_support_seconds=.03,recovery_seconds=.5),candidate_reward=dict(one_attempt_peak_increment_total_cap=1,takeoff_once=1,two_wheel_landing_once=2,recovery_once=3,maximum_positive_per_attempt=7,no_airtime_accumulation=True,RewardManager_event_conversion='Candidate control_event_reward / control_dt to offset stock RewardManager dt multiplication; not installed in native',source_conflicts_to_mask_only_jump_request_rows=['height tracking','vertical velocity penalty','both-wheel-ground height shaping'],original_hardware_energy_action_rate_costs_and_integrity_guards_retained=True),first_proposed_learning_parent_cap_seconds_including_optimizer_prechecks=1800,exit_headroom_seconds=300,new_authorized_budget_seconds=0,source_original_solecanonical_only=True,release_blockers=['Actual native operator mode/input/source action consistency and query/contact/COM/hardware evidence','Actual full collision geometry and legal ground reset readback; no sourceUSD==cookedShapeLocal claim','Actual full source20k typed restoration and new H1 phase/RNG/reset save-resume','Actual real takeoff/airborne/landing data to audit candidate reward and original height/termination conflicts','Freeze executable reward/termination/phase config SHA and review this exact narrow H1 training release'],H2_step_and_H3_airborne_reset_not_in_this_release=True,selfrescue_retained_as_later_pending=True,CPU_evidence_source_SHA=H(D/'h1_flat_jump_evidence_reward_cpu_v1.py'),old_V2_step_hop_draft_preserved=True)
 p=D/'H1_FLAT_COMMANDED_JUMP_CONCRETE_ADMISSION_AND_TRAINING_RELEASE_PROPOSAL_V1.json';put(p,proposal)
 put(R/'H1_FLAT_JUMP_EVIDENCE_REWARD_NEGATIVE_CPU_ACTUAL.json',dict(epoch=time.time(),passed_CPU_only=True,negative_checks=checks,successful_synthetic_attempt_reward=[float(x) for x in total],actual_dynamics_or_airborne_or_PPO_not_claimed=True,executable_proposal_path=str(p.resolve()),proposal_SHA=H(p),native80_fresh_DR_does_not_replace_full20k_restore=True))
 print(json.dumps(dict(CPU_evidence_passed=True,negative_checks=len(checks),proposal_SHA=H(p),jump_PPO_not_yet_admitted=True)),flush=True)
if __name__=='__main__':main()
