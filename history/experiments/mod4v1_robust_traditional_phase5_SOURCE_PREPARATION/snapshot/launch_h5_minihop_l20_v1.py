"""Execute exactly the pre-frozen H5 only after independent review+parent receipt."""
from pathlib import Path
import json,hashlib,copy
from fresh_train_batch_v1 import launch
R=Path(__file__).resolve().parent;D=R/'MINIHOP_L20_H5_V1'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((D/'PROTOCOL.json').read_bytes());a=json.loads((D/'PARENT_LAUNCH_APPROVAL.json').read_bytes())
assert a['approved_for_frozen_simulation_holdout']is True and a['protocol_SHA']==digest(D/'PROTOCOL.json')
assert a['review_SHA']==digest(D/a['review_file'])
assert digest(D/'FROZEN_BASE_CONFIG.json')==p['base_config_SHA']and digest(D/'CONTROLLER_SOURCE_INDEX.json')==p['source_index_SHA']
src=json.loads((D/'CONTROLLER_SOURCE_INDEX.json').read_bytes())
for row in src['files']:assert digest(Path(row['path']))==row['SHA'],row['path']
base=json.loads((D/'FROZEN_BASE_CONFIG.json').read_bytes())
assert base['nominal']is False and base['scene']=='flat'and float(base.get('forward_m_s',0.))==0.
assert p['seeds']==list(range(62100,62164))and p['max_workers']==4 and p['duration_s']==6.
configs=[]
for seed in p['seeds']:
    name=f'h5_l20_minihop_{seed}';c=copy.deepcopy(base);c.update(case_id=name,seed=seed)
    configs.append((name,c))
keys=['complete','stop','controls','physics_steps','maximum_main_mesh_clearance_during_full_air_m','end_stable_s',
      'proposed_flat_clear80mm_recover2s_v2','after_trigger_guide_contact_physics_ticks','after_trigger_hard_contact_physics_ticks',
      'max_pitch_rad','max_roll_rad']
launch(R,'h5_l20_minihop64','run_minihop_landing_v4.py',configs,dict(kind=p['kind'],frozen_protocol_path=str(D/'PROTOCOL.json'),
       frozen_protocol_SHA=digest(D/'PROTOCOL.json'),parent_approval_SHA=digest(D/'PARENT_LAUNCH_APPROVAL.json'),
       launcher_SHA=digest(Path(__file__)),nominal=False,independent_seed_range=[62100,62163],
       unchanged_controller_sources_verified=len(src['files']),no_holdout_retuning=True,all_robot_failures_retained=True,
       software_failure_stops_remaining_waves=True,no_C_jump_or_hardware_qualification=True),keys,max_workers=4)
