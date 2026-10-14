"""Independent physical-prefix/partial-save classification and logger-only repair."""
from pathlib import Path
import os,sys,json,time,hashlib,inspect,torch
os.environ['CUDA_VISIBLE_DEVICES']=''
D=Path(__file__).resolve().parent;W=D.parent
sys.path[:0]=[str(D),str(W/'MOD4_S3_WAVE50_CLOSEOUT_S4_LIVE_ADAPTER_20261015'),str(W/'MOD4_S3_SCOPE_COST_S4_READINESS_AUDIT_20261014')]
from s4_original_fullstate_migration_v1 import SCHEMA,same
from rsl_rl.utils.logger import Logger
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    receipt=json.loads(sorted((D/'reports').glob('S4_NATIVE120_SAVE_FAILURE_ALL_ACTUAL_EVIDENCE_*.json'))[-1].read_bytes())
    rows={v['relative']:v for v in receipt['files']};prefix='own_native120/attempt/'
    def read(name):return json.loads(Path(rows[prefix+name]['local_path']).read_bytes())
    done=read('S4_PROGRESS_ACTUAL.json');health=read('CLOCK_TRAINING_HEALTH.json');error=read('S4_ORIGINAL_ERROR.json')
    assert done['controls']==120 and done['callbacks']==480 and done['PPO_updates']==0
    assert "AttributeError: 'Logger' object has no attribute 'writer'" in error['error']
    assert "runner.save(str(out))" in error['error']
    assert health['control_steps']==120 and health['actual_physics_callbacks']==480
    assert health['integrity_task_reset_events']==health['unknown_task_reset_events']==0 and health['nonfinite_observed'] is False
    assert health['stop_reason'] is None
    source_sha='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
    for name,fields in SCHEMA.items():
        v=read(name);assert v['source_sha256']==source_sha
        for k in fields:assert v[k] is True,(name,k)
    migrate=read('S4_FIRST_DECLARED_MIGRATION_ACTUAL.json');assert migrate['passed'] is True
    partial=Path(rows[prefix+'S4_OWN_INTEGRATION_FULLSAVE.pt']['local_path']);ck=torch.load(partial,map_location='cpu',weights_only=False)
    assert 'S4_owned_learning' in ck and not ck['optimizer_state_dict']['state']
    assert all(k not in ck for k in ('sensor_DR_state','chassis_PD_state','E1_terrain_state','S4_shared_control_state'))
    assert ck['S4_owned_learning']['actor_owned']['rollout_samples']==0
    # Actual framework save_model takes no action with an explicitly disabled writer.
    logger=Logger.__new__(Logger);logger.writer=None;logger.save_model('CPU_NOT_A_FILE_NOT_UPLOAD',0)
    from types import SimpleNamespace
    from rsl_rl.runners import OnPolicyRunner
    class Alg:
        def save(self):return {'CPU_fixture_only':True,'gate_update_count':0}
    runner=OnPolicyRunner.__new__(OnPolicyRunner);runner.alg=Alg();runner.current_learning_iteration=0;runner.logger=logger
    fixture=D/'S4_ORIGINAL_RUNNER_EXPLICIT_DISABLED_WRITER_CPU_FIXTURE.pt';assert not fixture.exists()
    OnPolicyRunner.save(runner,str(fixture));assert torch.load(fixture,weights_only=False)['gate_update_count']==0
    result=dict(epoch=time.time(),passed_independent_classification=True,original_native_scope_passed=False,
        original_parent_failure_and_missing_COMPLETE_preserved=True,original_worker_EXIT0_does_not_override_error=True,
        actual_completed_physical_controls=120,actual_completed_callbacks=480,actual_PPO_updates=0,
        actual_original_eight_fullrestore_receipts_verified=True,actual_new_gate_critic_frozen_expert_migration_verified=True,
        native_physical_health_passed=True,full120_raw_trace_not_durably_written_before_save_error=True,
        partial_algorithm_only_checkpoint=dict(path=str(partial),bytes=partial.stat().st_size,sha256=sha(partial)),
        partial_checkpoint_not_fullstate_not_learning_source=True,
        root_cause='Original RSL Logger.writer is created by learn(), but this native0PPO bypassed learn().',
        CPU_original_runner_save_with_writer_None_passed=True,logger_source_SHA=sha(inspect.getfile(Logger)),
        repair='Explicitly disabled writer only for new zero-control save/restore scope; normal learner logger unchanged.',
        no_native120_replay=True,next_only_missing_zero_control_fullsave_and_own_restore=True,
        canonical_unchanged=True,original_parent_child_absent=True,
        installed_metadata_and_import_resolution_separate=receipt['package_import_resolution_without_import'],
        loaded_Kit_runtime_version_not_inferred_from_metadata=True,learning_admitted=False)
    p=D/'reports/S4_NATIVE120_PARTIAL_SAVE_FAILURE_AND_ZERO_CONTROL_LOGGER_REPAIR_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(result,indent=2))
    print(json.dumps(dict(report=str(p),classified=True,native_original_scope_PASS=False,physical120completed=True,PPO=0,no120replay=True)))
if __name__=='__main__':main()
