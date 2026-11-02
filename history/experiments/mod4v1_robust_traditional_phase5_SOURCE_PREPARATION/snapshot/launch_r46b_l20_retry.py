"""Retry only the zero-physics schema failure with a new named nominal case."""
from pathlib import Path
import json,hashlib
from fresh_train_batch_v1 import launch
R=Path(__file__).resolve().parent
qa=json.loads((R/'MINIHOP_LANDING_V3/loader_preflight004/RESULT.json').read_bytes());assert qa['failures']==0
old=json.loads((R/'results/r46_l20_nominal/ERROR.json').read_bytes());assert old['controls']==0 and old['physics_steps']==0
c=json.loads((R/'batches/r46_landing_nominal2/r46_l20_nominal.json').read_bytes());name='r46b_l20_nominal';c['case_id']=name
sources=[]
for p in('run_minihop_landing_v4.py','MINIHOP_LANDING_V3/controller.py',Path(__file__).name):
    b=(R/p).read_bytes();sources.append(dict(path=p,SHA=hashlib.sha256(b).hexdigest()))
keys=['complete','stop','controls','physics_steps','first_all_world_air_s','max_all_world_air_s','maximum_main_mesh_clearance_during_full_air_m',
      'end_stable_s','proposed_flat_clear80mm_recover2s_v2','after_trigger_hard_contact_physics_ticks','after_trigger_guide_contact_physics_ticks',
      'max_pitch_rad','max_roll_rad','peak_positive_mechanical_power_W','trace_artifact','physical_artifact']
launch(R,'r46b_l20_nominal1','run_minihop_landing_v4.py',[(name,c)],dict(kind='R46B_NEW_NOMINAL_AFTER_ZERO_STEP_GAIN_SCHEMA_ERROR',
    source_before_physics=sources,old_error_unchanged=True,old_l40_success_not_rerun=True,controller_unchanged=True,
    loader_only_uses_existing_load_gain_adapter=True,no_new_contact_permission=True,
    acceptance='unchanged_v2_flat80mm_no_guide_hard_endstable2s'),keys,max_workers=1)
