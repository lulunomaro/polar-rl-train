"""One new coupled-recovery strategy nominal case. Never old-case replay."""
from pathlib import Path
import hashlib,json
from fresh_train_batch_v2 import launch
R=Path(__file__).resolve().parent;D=R/'STARTUP_STAND_V2/front_admission001'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    a=json.loads((D/'PARENT_APPROVAL.json').read_bytes());assert a['approved']is True and a['scope']=='ONE_NEW_V2_FRONT_NOMINAL_ONLY'
    for key,name in [('config_SHA','CONFIG.json'),('protocol_SHA','PROTOCOL.json'),('source_index_SHA','SOURCE_PREEXEC.json')]:assert sha(D/name)==a[key]
    assert sha(Path(__file__))==a['launcher_SHA']
    paths=[R.resolve(),(R.parent/'traditional_control_20261101').resolve()]
    for x in json.loads((D/'SOURCE_PREEXEC.json').read_bytes())['files']:
        p=Path(x['path']).resolve();assert any(p.is_relative_to(base)for base in paths)and sha(p)==x['SHA'],x['path']
    protocol=json.loads((D/'PROTOCOL.json').read_bytes());cfg=json.loads((D/'CONFIG.json').read_bytes())
    assert cfg==protocol['config']and cfg['case_id']=='startup_front065_coupled_v2_nominal1'and cfg['nominal']is True and cfg['seed']==0
    assert cfg['controller']==dict(operator_enable=True,recovery_actuation_enable=True)
    assert protocol['runner']=='run_startup_stand_case_v4.py'and protocol['max_workers']==1
    assert a['runner_SHA']==sha(R/protocol['runner'])and a['candidate_SHA']==sha(R/'STARTUP_STAND_V2/controller.py')
    assert a['saved_proof_SHA']==sha(R/'STARTUP_STAND_V2/PREFLIGHT_RESULT.json')
    return launch(R,'startup_front065_coupled_v2_nominal1',protocol['runner'],[(cfg['case_id'],cfg)],
       dict(kind=protocol['kind'],admission_protocol=str(D/'PROTOCOL.json'),parent_approval=str(D/'PARENT_APPROVAL.json'),
            new_strategy_after_failed_V1_not_a_bookkeeping_replay=True,no_automatic_DR_back_side_or_retry=True),
       ['complete','stop','controls','physics_steps','startup_stand_original_v1_gate','controller_phase','controller_fault_reason',
        'controller_transitions','first_BALANCE_command_s','end_stable_s','max_stable_s','body_height_gain_m','max_root_xy_displacement_m'],max_workers=1)
if __name__=='__main__':main()
