"""One new V3B eligible pose-alignment nominal case, source-locked and artifact-aware."""
from pathlib import Path
import hashlib,json
from fresh_train_batch_v2 import launch
R=Path(__file__).resolve().parent;D=R/'STARTUP_STAND_V3/front_B_admission001'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    a=json.loads((D/'PARENT_APPROVAL.json').read_bytes());assert a['approved']is True and a['scope']=='ONE_NEW_V3B_FRONT_NOMINAL_ONLY'
    for key,name in [('config_SHA','CONFIG.json'),('protocol_SHA','PROTOCOL.json'),('source_index_SHA','SOURCE_PREEXEC.json')]:assert sha(D/name)==a[key]
    assert sha(Path(__file__))==a['launcher_SHA']
    paths=[R.resolve(),(R.parent/'traditional_control_20261101').resolve()]
    for x in json.loads((D/'SOURCE_PREEXEC.json').read_bytes())['files']:
        p=Path(x['path']).resolve();assert any(p.is_relative_to(base)for base in paths)and sha(p)==x['SHA'],x['path']
    protocol=json.loads((D/'PROTOCOL.json').read_bytes());cfg=json.loads((D/'CONFIG.json').read_bytes())
    assert cfg==protocol['config']and cfg['case_id']=='startup_front065_tracking_v3b_nominal1'and cfg['nominal']is True and cfg['seed']==0
    assert cfg['controller']==dict(operator_enable=True,recovery_tracking_enable=True,alignment_wheel_enable=True)
    assert protocol['runner']=='run_startup_stand_case_v5.py'and protocol['max_workers']==1 and protocol['profile_B_not_admitted']is False and protocol['A_saved_evidence_required']is True
    assert a['runner_SHA']==sha(R/protocol['runner'])and a['candidate_SHA']==sha(R/'STARTUP_STAND_V3/controller.py')
    assert a['saved_proof_SHA']==sha(R/'STARTUP_STAND_V3/PREFLIGHT_RESULT.json')
    az=json.loads((R/'STARTUP_STAND_V3/front_A_saved_analysis001/RESULT.json').read_bytes())
    ar=json.loads((R/'results/startup_front065_tracking_v3a_nominal1/result.json').read_bytes())
    assert az['future_B_condition_available_but_NOT_launch_permission']is True and az['actual_A_sensor_alignment_eligible_count']>0 and ar['startup_stand_original_v1_gate']is False
    assert ar['trace_artifact']==az['source_trace_producer']
    return launch(R,cfg['case_id'],protocol['runner'],[(cfg['case_id'],cfg)],
        dict(kind=protocol['kind'],admission_protocol=str(D/'PROTOCOL.json'),parent_approval=str(D/'PARENT_APPROVAL.json'),
             new_strategy_after_failed_V1_V2_not_bookkeeping_replay=True,no_automatic_DR_back_side_or_retry=True),
        ['complete','stop','controls','physics_steps','startup_stand_original_v1_gate','controller_phase','controller_fault_reason',
         'controller_transitions','first_BALANCE_command_s','end_stable_s','max_stable_s','body_height_gain_m','max_root_xy_displacement_m'],max_workers=1)
if __name__=='__main__':main()
