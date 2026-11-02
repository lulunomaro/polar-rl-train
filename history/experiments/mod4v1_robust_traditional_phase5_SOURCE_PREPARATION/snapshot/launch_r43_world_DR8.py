"""Freeze the R42 nominal candidate before fresh fullDR TRAIN8; no tuning."""
from pathlib import Path
import ast,json,hashlib,copy
from fresh_train_batch_v1 import launch
R=Path(__file__).resolve().parent
proof=json.loads((R/'ROUGH_WORLD_LEG_V3/prefix_validation001/RESULT.json').read_bytes());assert proof['bit_or_discrete_mismatches']==0 and proof['new_case_passed_original_rough_gate']
base=json.loads((R/'batches/r42_latched_capture1/r42_latched_d0_bar40.json').read_bytes());configs=[]
for seed in range(4401,4409):
    c=copy.deepcopy(base);name=f'r43_worldDR4cm_{seed}';c.update(case_id=name,seed=seed,nominal=False,cohort='new_fullDR_TRAIN_fixed_candidate_not_holdout')
    configs.append((name,c))
freeze=[]
for f in('run_world_leg_case_v3.py','ROUGH_WORLD_LEG_V3/controller.py','ROUGH_WORLD_LEG_V1/controller.py',Path(__file__).name):
    raw=(R/f).read_bytes();ast.parse(raw);freeze.append(dict(path=f,SHA=hashlib.sha256(raw).hexdigest()))
keys=['complete','stop_reason','controls','physics_callbacks','full_D0_D7_on_control_path','rough_case_pass','rough_progress_m','rough_max_y_m','max_pitch_abs','max_roll_abs','physics_nonwheel_contact_ticks',
      'tail_v_tracking_RMSE','tail_pitch_RMS','max_closure','max_mimic','trace_artifact']
launch(R,'r43_world_DR8','run_world_leg_case_v3.py',configs,dict(kind='R43_FROZEN_4CM_WORLDLEG_FULLDR_TRAIN8',
      freeze_before_new_seeds=freeze,training_seeds=list(range(4401,4409)),old_holdouts_untouched=True,
      terrain_family='SCUT_exact_tiny_step_fixed_seed9001_height4cm_NOT_allRM_or6cm',
      acceptance='UNCHANGED_R22_rough_gate',no_model_material_contact_delay_limit_changes=True,callback_dt_s=.0005,control_dt_s=.01),keys,max_workers=2)
