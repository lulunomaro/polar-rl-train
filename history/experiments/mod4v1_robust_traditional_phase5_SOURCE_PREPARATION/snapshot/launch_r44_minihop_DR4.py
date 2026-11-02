"""Four NEW fullDR stationary mini-hops, same R39 control, stricter v2 grade."""
from pathlib import Path
import json,hashlib,ast,copy
from fresh_train_batch_v1 import launch
R=Path(__file__).resolve().parent
v=json.loads((R/'MINIHOP_AUDIT_V2/VALIDATION.json').read_bytes())
assert v['valid']and v['unit_failures']==0 and v['boot_failures']==0 and v['all_integration_calls']==0
base=json.loads((R/'batches/r39_minihop4/r39_flat_d20_p14.json').read_bytes());configs=[]
for seed in range(4221,4225):
    c=copy.deepcopy(base);name=f'r44_miniDR_{seed}';c.update(seed=seed,nominal=False,case_id=name,cohort='new_fullDR_TRAIN_manual_minihop_not_RM_270_holdout')
    configs.append((name,c))
freeze=[]
for f in('MINIHOP_V1/controller.py','MINIHOP_AUDIT_V2/contact_grade_v2.py','MINIHOP_AUDIT_V2/run_minihop_case_v2.py',Path(__file__).name):
    raw=(R/f).read_bytes();ast.parse(raw);freeze.append(dict(path=f,SHA=hashlib.sha256(raw).hexdigest()))
keys=['complete','stop','controls','physics_steps','first_all_world_air_s','first_all_world_air_confirmed_s','max_all_world_air_s','maximum_main_mesh_clearance_during_full_air_m',
      'end_stable_s','proposed_flat_clear80mm_recover2s_v2','after_trigger_hard_contact_physics_ticks','after_trigger_guide_contact_physics_ticks','max_pitch_rad','max_roll_rad',
      'peak_positive_mechanical_power_W','trace_artifact','physical_artifact']
launch(R,'r44_minihop_DR4','MINIHOP_AUDIT_V2/run_minihop_case_v2.py',configs,dict(kind='R44_FIXED_R39_MINIHOP_CONTROL_NEW_FULLDR_V2_GRADE',
      source_before_new_seeds=freeze,seeds=list(range(4221,4225)),baseline_control='r39_flat_d20_p14_same_math_and_timing',
      grade='ALL_positive_world_contact_normals_total_le1N_for20ms_not_v1_percontact_filter',
      acceptance='v2_flat_air_mesh80mm_no_posttrigger_guide_hard_endstable2s',
      old_R39_scores_not_rewritten=True,all_D0_D7_original_physical_path=True,public_contact_cue_still_unknown=True,
      hardware_qualified=False,not_RM_or270_skill=True),keys,max_workers=2)
