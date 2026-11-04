"""One new V4 front nominal, separate parent+independent-review SHA gate, no auto retry."""
from pathlib import Path
import hashlib,json
from fresh_train_batch_v2 import launch
R=Path(__file__).resolve().parent;D=R/'STARTUP_STAND_V4/front_admission002'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    a=json.loads((D/'PARENT_APPROVAL.json').read_bytes());assert a['approved'] is True and a['scope']=='ONE_NEW_V4_FRONT_NOMINAL_ONLY'
    for key,name in [('config_SHA','CONFIG.json'),('protocol_SHA','PROTOCOL.json'),('source_index_SHA','SOURCE_PREEXEC.json')]:assert sha(D/name)==a[key]
    assert sha(Path(__file__))==a['launcher_SHA']
    review_path=D/'FINAL_ENTRY_REVIEW_001.json';assert sha(review_path)==a['independent_review_SHA']
    review=json.loads(review_path.read_bytes());assert review['ready_one_front_nominal'] is True and review['issues']==[]
    for key in ('config_SHA','source_index_SHA','runner_SHA','candidate_SHA'):assert review[key]==a[key]
    roots=[R.resolve(),(R.parent/'traditional_control_20261101').resolve()]
    for x in json.loads((D/'SOURCE_PREEXEC.json').read_bytes())['files']:
        p=Path(x['path']).resolve();assert any(p.is_relative_to(root) for root in roots) and sha(p)==x['SHA'],x['path']
    protocol=json.loads((D/'PROTOCOL.json').read_bytes());cfg=json.loads((D/'CONFIG.json').read_bytes())
    assert cfg==protocol['config'] and cfg['case_id']=='startup_front065_world_support_v4_nominal1' and cfg['nominal'] is True and cfg['seed']==0
    assert cfg['controller']==dict(operator_enable=True,recovery_tracking_enable=True,alignment_wheel_enable=False,support_geometry_enable=True)
    assert protocol['runner']=='run_startup_stand_case_v6.py' and protocol['max_workers']==1 and protocol['profile_B_not_admitted'] is True
    assert a['runner_SHA']==sha(R/protocol['runner']) and a['candidate_SHA']==sha(R/'STARTUP_STAND_V4/controller.py')
    assert a['saved_proof_SHA']==sha(R/'STARTUP_STAND_V4/preflight001/RESULT.json')
    return launch(R,cfg['case_id'],protocol['runner'],[(cfg['case_id'],cfg)],
        dict(kind=protocol['kind'],admission_protocol=str(D/'PROTOCOL.json'),parent_approval=str(D/'PARENT_APPROVAL.json'),
            independent_review=str(review_path),new_sensor_geometry_strategy_after_V3_not_bookkeeping_replay=True,
            no_automatic_DR_back_side_second_variant_or_retry=True),
        ['complete','stop','controls','physics_steps','startup_stand_original_v1_gate','controller_phase','controller_fault_reason',
         'controller_transitions','first_BALANCE_command_s','end_stable_s','max_stable_s','body_height_gain_m','max_root_xy_displacement_m'],max_workers=1)
if __name__=='__main__':main()
