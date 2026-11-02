"""Frozen nominal-admitted landing schedules, new paired TRAIN on four DR seeds."""
from pathlib import Path
import json,hashlib,copy
from fresh_train_batch_v1 import launch
R=Path(__file__).resolve().parent
assert json.loads((R/'MINIHOP_LANDING_V3/loader_preflight004/RESULT.json').read_bytes())['failures']==0
admitted=[('l40','r46_l40_nominal'),('l20','r46b_l20_nominal')];configs=[];admissions=[]
for label,case in admitted:
    r=json.loads((R/'results'/case/'result.json').read_bytes())
    assert r['complete'] and r['controls']==600 and r['physics_steps']==12000 and r['proposed_flat_clear80mm_recover2s_v2']
    admissions.append(dict(case=case,passed_unchanged_nominal_gate=True,result_SHA=hashlib.sha256((R/'results'/case/'result.json').read_bytes()).hexdigest()))
    for seed in range(4221,4225):
        c=copy.deepcopy(r['config']);name=f'r47_{label}_DR{seed}'
        c.update(case_id=name,cohort='paired_TRAIN_landing_schedule_not_holdout',nominal=False,seed=seed)
        configs.append((name,c))
sources=[]
for f in('run_minihop_landing_v4.py','MINIHOP_LANDING_V3/controller.py','MINIHOP_OBSERVER_V2/controller.py',Path(__file__).name,'JUMP270_V1/GAIN_BANK.json','nominal_gain_v1.json'):
    b=(R/f).read_bytes();sources.append(dict(path=f,SHA=hashlib.sha256(b).hexdigest()))
keys=['complete','stop','controls','physics_steps','first_all_world_air_s','max_all_world_air_s','maximum_main_mesh_clearance_during_full_air_m',
      'end_stable_s','proposed_flat_clear80mm_recover2s_v2','after_trigger_hard_contact_physics_ticks','after_trigger_guide_contact_physics_ticks',
      'max_pitch_rad','max_roll_rad','peak_positive_mechanical_power_W','trace_artifact','physical_artifact']
launch(R,'r47_landing_DR8','run_minihop_landing_v4.py',configs,dict(kind='R47_FROZEN_CAPTURE_LANDING_GAIN_REFERENCE_PAIRED_TRAIN',
       source_before_physics=sources,nominal_admissions=admissions,baseline='existing_R45_quarantineDR_same_4221..4224_seeds',
       original_DR_and_plant_path=True,no_heldout_tuning=True,no_contact_confidence_promotion=True,
       schedule_s=.20,observer_quarantine_after_push_s=.50,original_v2_grade_unchanged=True,
       hardware_qualified=False,old_cases_not_replayed=True),keys,max_workers=2)
