"""R22-matched geometry/gain/command, one new IMU fore/aft reference policy."""
from pathlib import Path
import ast,hashlib,json
from fresh_train_batch_v1 import launch
R=Path(__file__).resolve().parent
qa=json.loads((R/'ROUGH_WORLD_LEG_V1/preflight001/RESULT.json').read_bytes());assert qa['failures']==0 and qa['physics_steps']==0
configs=[];pairs=[]
for delta in(0,20):
    for height in(40,60):
        baseline=f'r22_height{delta}bar{height}'
        source=R/'batches/r22_height_rough9'/(baseline+'.json');raw=source.read_bytes();c=json.loads(raw)
        name=f'r40_world_d{delta}_bar{height}';c['case_id']=name;c['cohort']='new_nominal_TRAIN_worldleg_counterfactual_not_holdout'
        assert c['seed']==0 and c['nominal']is True and c['terrain_seed']==9001
        c['controller'].update(world_pitch_gain=.75,world_pitch_limit_rad=.30,world_pitch_rate_rad_s=2.)
        configs.append((name,c))
        pairs.append(dict(new=name,existing_baseline=baseline,config_path=str(source),config_SHA=hashlib.sha256(raw).hexdigest(),old_once_not_replayed=True,
                          same_height_gain_terrain_commands=True,changed='sensor_pitch_shared_hip_crank_foreaft_reference_only'))
for name in('run_world_leg_case_v1.py','ROUGH_WORLD_LEG_V1/controller.py','fresh_train_batch_v1.py',Path(__file__).name):ast.parse((R/name).read_bytes())
keys=['complete','stop_reason','controls','physics_callbacks','rough_case_pass','rough_progress_m','rough_max_y_m','max_pitch_abs','max_roll_abs','physics_nonwheel_contact_ticks',
      'tail_v_tracking_RMSE','tail_velocity_mean_m_s','max_closure','max_mimic','peak_positive_mechanical_power_W','trace_artifact','scene']
launch(R,'r40_world_leg4','run_world_leg_case_v1.py',configs,dict(kind='R40_NEW_NOMINAL_WORLDLEG_COUNTERFACTUAL',pairing=pairs,physics_dt_s=.0005,control_dt_s=.01,
      nominal_only=True,new_fullDR_holdout=False,old_H1_H2_H4_unchanged=True,reference_policy=dict(k=.75,shift_cap_rad=.30,rate_rad_s=2.,hip_ref_limit=.48),
      acceptance='unchanged_original_rough_screen_progress_ge6p5m_maxy_le0p3m_no_nonwheel_contact_tail_pose_speed_support',
      no_contact_collision_material_changes=True,no_truepose_or_DR_control_input=True),keys,max_workers=2)
