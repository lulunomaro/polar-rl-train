"""Same four TRAIN geometries with a new shaped-stop restoration policy."""
from pathlib import Path
import ast,hashlib,json
from fresh_train_batch_v1 import launch
R=Path(__file__).resolve().parent
qa=json.loads((R/'ROUGH_WORLD_LEG_V2/preflight001/RESULT.json').read_bytes());assert qa['failures']==0 and qa['physics_steps']==0
configs=[];pairs=[]
for delta in(0,20):
    for height in(40,60):
        baseline=f'r22_height{delta}bar{height}';previous=f'r40_world_d{delta}_bar{height}'
        source=R/'batches/r22_height_rough9'/(baseline+'.json');raw=source.read_bytes();c=json.loads(raw)
        name=f'r41_capture_d{delta}_bar{height}';c['case_id']=name;c['cohort']='new_nominal_TRAIN_scheduled_worldleg_not_holdout'
        c['controller'].update(world_pitch_gain=.75,world_pitch_limit_rad=.30,world_pitch_rate_rad_s=2.,world_full_activation_m_s=.4)
        configs.append((name,c));pairs.append(dict(new=name,original_baseline=baseline,previous_constant_gain=previous,
                   original_config_SHA=hashlib.sha256(raw).hexdigest(),old_once_not_replayed=True,
                   change='gain_scheduled_by_previous_shaped_speed_return_bodyfixed_at_stop',model_gain_terrain_command_unchanged=True))
for f in('run_world_leg_case_v2.py','ROUGH_WORLD_LEG_V2/controller.py',Path(__file__).name):ast.parse((R/f).read_bytes())
keys=['complete','stop_reason','controls','physics_callbacks','rough_case_pass','rough_progress_m','rough_max_y_m','max_pitch_abs','max_roll_abs','physics_nonwheel_contact_ticks',
      'tail_v_tracking_RMSE','tail_velocity_mean_m_s','tail_pitch_RMS','max_closure','max_mimic','trace_artifact']
launch(R,'r41_world_capture4','run_world_leg_case_v2.py',configs,dict(kind='R41_NEW_NOMINAL_SCHEDULED_WORLDLEG_COUNTERFACTUAL',pairing=pairs,physics_dt_s=.0005,control_dt_s=.01,
      nominal_only=True,new_fullDR_holdout=False,old_H1_H2_H4_unchanged=True,full_activation_speed_m_s=.4,
      acceptance='UNCHANGED_R22_R40_rough_gate_no_relaxation',causal_selection='R40d0h4_only_failed_tail_pitch_observer_RMSerror0p004_not_weakening_gate',
      no_model_contact_material_DR_changes=True,no_truepose_or_DR_control_input=True),keys,max_workers=2)
