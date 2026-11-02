"""Fresh paired TRAIN: only extend wheel/ground-constraint observation quarantine."""
from pathlib import Path
import json,hashlib,copy,ast
from fresh_train_batch_v1 import launch
R=Path(__file__).resolve().parent
qa=json.loads((R/'MINIHOP_OBSERVER_V2/preflight002/RESULT.json').read_bytes());assert qa['failures']==0 and qa['only_14_expected_observer_ticks_changed']
configs=[];pairs=[]
for seed in range(4221,4225):
    old=f'r44_miniDR_{seed}';c=json.loads((R/'batches/r44_minihop_DR4'/(old+'.json')).read_bytes())
    name=f'r45_quarantineDR_{seed}';c['case_id']=name;c['cohort']='new_paired_TRAIN_observer_only_not_holdout'
    c['hop']['observer_quarantine_after_push_s']=.50
    configs.append((name,c));pairs.append(dict(new=name,old=old,same_DR_seed_and_physics=True,
             before2p0_control_and_physics_prefix_should_match=True,changed_ticks='200..213_observer_flags_only'))
src=[]
for f in('run_minihop_observer_v2.py','MINIHOP_OBSERVER_V2/controller.py',Path(__file__).name):
    raw=(R/f).read_bytes();ast.parse(raw);src.append(dict(path=f,SHA=hashlib.sha256(raw).hexdigest()))
keys=['complete','stop','controls','physics_steps','first_all_world_air_s','first_landing','max_all_world_air_s','maximum_main_mesh_clearance_during_full_air_m',
      'end_stable_s','proposed_flat_clear80mm_recover2s_v2','after_trigger_hard_contact_physics_ticks','after_trigger_guide_contact_physics_ticks',
      'max_pitch_rad','max_roll_rad','peak_positive_mechanical_power_W','trace_artifact','physical_artifact']
launch(R,'r45_quarantine4','run_minihop_observer_v2.py',configs,dict(kind='R45_NEW_PAIRED_TRAIN_OBSERVER_QUARANTINE',paired=pairs,
     source_before_physics=src,observer_change='wheel_and_ground_kinematic_flags_extend_from_2p00_to2p14_not_new_contact_cue',
     phase_timing_torque_math_gravity_schedule_unchanged=True,old_scores_unchanged=True,
     full_DR_original=True,acceptance='unchanged_v2_flat80mm_no_guide_hard_endstable2s',hardware_qualified=False),keys,max_workers=2)
