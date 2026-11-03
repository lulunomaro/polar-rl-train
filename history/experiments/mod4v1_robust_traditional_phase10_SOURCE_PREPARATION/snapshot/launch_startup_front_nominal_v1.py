"""Exactly one reviewed/frozen front-lying nominal case; no automatic DR/retry."""
from pathlib import Path
import hashlib,json
from fresh_train_batch_v2 import launch
R=Path(__file__).resolve().parent;D=R/'STARTUP_STAND_V1/front_admission001'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    approval=json.loads((D/'PARENT_LAUNCH_APPROVAL.json').read_bytes())
    assert approval['scope']=='ONE_FRONT065_NOMINAL_ONLY'and approval['approved']is True
    names={'config_SHA':'CONFIG.json','protocol_SHA':'PROTOCOL.json','source_index_SHA':'SOURCE_PREEXEC.json','review_SHA':'FINAL_ENTRY_REVIEW_002.json'}
    for key,name in names.items():assert sha(D/name)==approval[key],name
    assert sha(Path(__file__))==approval['launcher_SHA']
    review=json.loads((D/'FINAL_ENTRY_REVIEW_002.json').read_bytes());assert review['ready_for_one_nominal_physics']is True
    for rec in json.loads((D/'SOURCE_PREEXEC.json').read_bytes())['files']:
        p=(R/rec['path']).resolve();assert p.is_relative_to(R)and sha(p)==rec['SHA'],rec['path']
    cfg=json.loads((D/'CONFIG.json').read_bytes());protocol=json.loads((D/'PROTOCOL.json').read_bytes())
    assert cfg==protocol['config']and cfg['case_id']=='startup_front065_nominal_v1'and cfg['nominal']is True and cfg['duration_s']==10.
    assert protocol['runner']=='run_startup_stand_case_v2.py'and protocol['max_workers']==1
    assert approval['runner_SHA']==sha(R/protocol['runner'])
    return launch(R,'startup_front065_nominal1',protocol['runner'],[(cfg['case_id'],cfg)],
        dict(kind=protocol['kind'],admission_protocol=str(D/'PROTOCOL.json'),independent_review=str(D/'FINAL_ENTRY_REVIEW_002.json'),
             parent_approval=str(D/'PARENT_LAUNCH_APPROVAL.json'),no_automatic_DR_back_side_or_retry=True),
        ['complete','stop','controls','physics_steps','startup_stand_original_v1_gate','controller_phase','controller_fault_reason',
         'controller_transitions','first_BALANCE_command_s','end_stable_s','max_stable_s','body_height_gain_m','max_root_xy_displacement_m'],max_workers=1)
if __name__=='__main__':main()
