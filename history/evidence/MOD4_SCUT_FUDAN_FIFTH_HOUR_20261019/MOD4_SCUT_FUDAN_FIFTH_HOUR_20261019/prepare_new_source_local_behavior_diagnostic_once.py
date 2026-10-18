"""Copy the existing diagnostic protocol for only the newly closed H1 source.

Add read-only measured reward-rate telemetry; no control or threshold changes.
"""
from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_FOURTH_HOUR_20261019'
f=json.loads((P/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())
assert f['passed_all_three_whole_final_models_CPU']
s=(P/'review_third_reward_hour_new_source_local_behavior_once.py').read_text('utf8')
s=s.replace("P=W/'MOD4_SCUT_FUDAN_THIRD_HOUR_20261019'","P=W/'MOD4_SCUT_FUDAN_FOURTH_HOUR_20261019'")
s=s.replace('THIRD_SCUT_FUDAN_HOUR','FOURTH_SCUT_FUDAN_HOUR').replace('after_reward_hour3','after_reward_hour4').replace('local_third_reward_hour','local_fourth_reward_hour').replace('scut-fudan-third-hour','scut-fudan-fourth-hour')
s=s.replace('from h1_public_request_phase_v1 import H1PublicRequestPhase,PROFILE','from h1_public_request_phase_v1 import H1PublicRequestPhase,PROFILE\nfrom h1_scut_fudan_jump_reward_v1 import terms,PROFILE as REWARD_PROFILE,FUDAN_TERMS')
s=s.replace('phase=H1PublicRequestPhase(1,\'cpu\');rows=[];', 'phase=H1PublicRequestPhase(1,\'cpu\');rows=[];reward_rows=[];')
marker='      if fail:first_failure='
assert s.count(marker)==1
telemetry='''      # Diagnostic-only callback rates, not a PhysX RewardManager/PPO readback.
      # MuJoCo actuator order is hip,crank,wheel on each side; wheel torque is2,5.
      body_ids=[mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,n) for n in ('left_wheel','right_wheel')]
      delta=d.xpos[body_ids]-d.xpos[sim.chassis_id]
      body_omega=rot.T@vel[:3];gravity=rot.T@np.array([0.,0.,-1.])
      tensor=lambda x:torch.as_tensor(x,dtype=torch.float32)
      active=phase.attempt & phase.request_for_action;airborne=phase.air_ticks>0
      raw_rates=terms(active=active,airborne=airborne,supported=torch.tensor([(wheel_n>1.).any()]),vz=tensor([vel[5]]),leg_lengths=tensor(np.linalg.norm(delta,axis=1)[None]),wheel_bottom_relative_z=tensor((wc-d.xpos[sim.chassis_id,2])[None]),wheel_torque=tensor(np.asarray(tau)[[2,5]][None]),projected_gravity=tensor(gravity[None]),angular_velocity_body=tensor(body_omega[None]))
      weighted={n:(raw_rates[n]*w).clamp(-2.5,2.5) if n in FUDAN_TERMS else raw_rates[n]*w for n,w in REWARD_PROFILE['weights'].items()}
      reward_rows.append([d.time,control,int(active.item()),int(airborne.item()),int(phase.launched.item()),int(phase.landed.item()),int(phase.recovered.item()),int(phase.recover_ticks.item()),*body_omega,*gravity,*[float(weighted[n].item()) for n in REWARD_PROFILE['weights']]])
'''
s=s.replace(marker,telemetry+marker)
needle="np.savez_compressed(raw,callback=np.asarray(rows,dtype=np.float64))"
assert s.count(needle)==1
s=s.replace(needle,"np.savez_compressed(raw,callback=np.asarray(rows,dtype=np.float64),reward_callback=np.asarray(reward_rows,dtype=np.float64))")
needle="episodes=results,not_skill_graduation=True"
assert s.count(needle)==1
s=s.replace(needle,"reward_telemetry=dict(columns=['time','control','active','airborne','launched','landed','recovered','recover_ticks','body_angular_velocity3','projected_gravity3',*REWARD_PROFILE['weights']],profile=REWARD_PROFILE,callback_rates_only_not_PhysX_PPO_reward=True,weighted_Fudan_rate_clip=2.5,no_reward_used_for_control=True),episodes=results,not_skill_graduation=True")
ast.parse(s)
out=B/'review_fourth_reward_hour_new_source_local_behavior_once.py'
with out.open('x',encoding='utf8') as p:p.write(s)
with (B/'reports/NEW_SOURCE_LOCAL_DIAGNOSTIC_PROTOCOL_PREPARED_CPU_ACTUAL.json').open('x',encoding='utf8') as p:json.dump(dict(epoch=time.time(),source=f['experts']['h1']['final'],only_new_source_four_trajectories=True,unchanged_original_physics_control_thresholds=True,additional_readonly_callback_rate_telemetry=True,not_GPU_or_live_player_or_account_change=True),p,indent=2)
print(json.dumps(dict(prepared=str(out),source_SHA=f['experts']['h1']['final']['SHA'])))
