"""ROOT-only actual SDK readback through existing component audits;lazy Torch."""
from dr0_contract import KIND,validate_snapshot

def collect(env,new_streams_not_restored_from_source):
 import torch
 from sensor_a0_runtime import state
 from feedback_delay_runtime import delay_state
 s=state(env);d=delay_state(env);q=env._physics_action_delay.queue
 mild=env._mild_dr;spring=env._spring_pressure;gas=env._gas_damping;com=env._chassis_com;pd=env._explicit_pd
 assert mild.profile=='all_off_nominal_v1' and mild.dr0
 # Existing wrapped D0 audit also verifies actual COM and explicit PD against
 # authored constructor snapshots. Reuse it,do not invent extra physical gates.
 d0=mild.audit();d5=spring.audit();d6=gas.audit()
 assert d5['actual_stiffness_range_N_m']==[2000.,2000.] and d6['actual_damping_range_Ns_m']==[3.,3.]
 assert d0['actual_parameters_pass'] and not spring.component.enabled and not gas.component.enabled and not com.component.enabled and not pd.component.enabled
 assert bool((mild.factor==1).all()) and bool(mild.nominal.all()) and all(bool((x.episode_scale==1).all() and (x.step_scale==1).all()) for name,x in env.scene['robot'].actuators.items() if name in ('legs','wheels'))
 assert bool((mild.mu==.9).all()) and s.profile=='off' and bool((s.bias==0).all()) and all(x==0 for x in s.draw_counts.values())
 assert not d.enabled and bool((d.delay==0).all()) and not q.enabled and all(bool((x['lag_steps']==0).all()) for x in q.groups.values())
 assert bool((spring.component.factor==1).all()) and bool((gas.component.factor==1).all()) and bool((com.component.delta_m==0).all()) and all(bool((x==1).all()) for x in pd.component.factor.values())
 assert env.cfg.terminations.closure.params['threshold']==.002 and env.cfg.terminations.mimic.params['threshold']==.01
 snap=dict(kind=KIND,actual_SDK_readback=True,mass_inertia_authored_baseline=True,motor_gains_one=True,wheel_mu_original_nominal09=True,
  nonwheel_material_authored_baseline=True,ground_cfg_unchanged_from_source=True,sensor_noise_and_bias_off=True,feedback_added_delay_zero=True,physical_target_added_delay_zero=True,
  gas_stiffness_nominal2000=True,gas_damping_nominal3=True,COM_delta_zero_AUTHORED_absolute_preserved=True,PD_nominal=True,
  new_DR0_streams_not_old_DR_restore=bool(new_streams_not_restored_from_source),closure_m=.002,mimic_rad=.01,
  D0_actual_wrapped_audit=d0,D5_actual_audit=d5,D6_actual_audit=d6,
  source_scope='New constructor baseline and all-off branch;no old DR state load',
  ground_material_scope='Original authored/source cfg unchanged;no added PhysX ground-material getter;actual ground-handle value UNKNOWN',
  COM_absolute_baseline_source='ChassisCOMSDK.original_pose plus zero delta;actual current principal-axis orientation preserved',
  sensor_recipe=s.receipt(),D3_enabled=d.enabled,D4_enabled=q.enabled,D5_enabled=spring.component.enabled,D6_enabled=gas.component.enabled,D7_COM_enabled=com.component.enabled,D7_PD_enabled=pd.component.enabled)
 validate_snapshot(snap);return snap
