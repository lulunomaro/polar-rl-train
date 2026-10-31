"""New source namespaces for explicit source cache; retains every DR guard."""
from pathlib import Path
import hashlib,json,time

HERE=Path(__file__).resolve().parent; PACKAGE=HERE.parent
OV=PACKAGE.parent/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
MOD=OV/'W35_PPO50_gas400_source_preparation_20261027/runtime_candidate_v1/isaac/mod4'
CASE=OV/'W35_ADAPTED92_NEW86_COMMAND_UID_CYCLE_COMPLETE_CASE_SOURCE_20261030_V2'


def main():
    with (HERE/'DERIVE_FULLSTATE_V3_ONCE.json').open('x') as f:
        json.dump(dict(ID='NEW208_FULLSTATE_CACHE_PARENT_ABI_SOURCE_V3',epoch=time.time(),
                       source_only=True,no_model_raw_SDK_GPU_or_test=True),f)
    names=['sensor_resume_contract','feedback_delay_checkpoint','action_delay_checkpoint',
           'spring_pressure_checkpoint','gas_damping_checkpoint','chassis_pd_checkpoint']
    mapping={name:name+'208_v3' for name in names}
    rows=[]
    for name in names:
        path=CASE/('REFERENCE_EXACT_'+name+'.py.txt')
        if not path.is_file():path=MOD/(name+'.py')
        raw=path.read_bytes(); value=raw.decode('utf8')
        for old,new in mapping.items():
            value=value.replace('from '+old+' import ', 'from '+new+' import ')
        value=value.replace('torch.load(', 'cached_load(')
        value=value.replace('hashlib.sha256(p.read_bytes()).hexdigest()', 'cached_H(p)')
        value='from source_cache208_v3 import cached_load,cached_H\n'+value
        dest=HERE/(mapping[name]+'.py')
        with dest.open('x',encoding='utf8',newline='\n') as f:f.write(value)
        rows.append(dict(source=str(path),source_SHA=hashlib.sha256(raw).hexdigest(),
            output=str(dest),bytes=dest.stat().st_size,SHA=hashlib.sha256(dest.read_bytes()).hexdigest(),
            original_DR_state_validation_and_RNG_guard_code_retained=True))
    path=PACKAGE/'source/checkpoint208.py';raw=path.read_bytes();value=raw.decode('utf8')
    value=value.replace('from chassis_pd_checkpoint import ', 'from chassis_pd_checkpoint208_v3 import ')
    value=value.replace('from spring_pressure_checkpoint import ', 'from spring_pressure_checkpoint208_v3 import ')
    value=value.replace('torch.load(', 'cached_load(')
    value=value.replace("with Path(path).open('rb') as source_file:\n            source_digest = hashlib.file_digest(source_file, 'sha256').hexdigest()",
                        'source_digest = cached_H(path)')
    value='from source_cache208_v3 import cached_load,cached_H\n'+value
    # Explicitly retain the NEW arena identity. No old G3 assignment is written
    # into the field or accepted as an exact geometry resume.
    value=value.replace("proof = dict(epoch=time.time(), source_sha256=result['source_sha256'],",
        "assert env.scene.terrain.retention_assignment_sha == COLLISION_USDC_SHA\n    assert cmd.state_dict_retention()['assignment_sha256'] == COLLISION_USDC_SHA\n    proof = dict(epoch=time.time(), source_sha256=result['source_sha256'],")
    with (HERE/'checkpoint_cache208_v3.py').open('x',encoding='utf8',newline='\n') as f:f.write(value)
    rows.append(dict(source=str(path),source_SHA=hashlib.sha256(raw).hexdigest(),
        output=str(HERE/'checkpoint_cache208_v3.py'),SHA=hashlib.sha256((HERE/'checkpoint_cache208_v3.py').read_bytes()).hexdigest()))
    raw=(HERE/'train208_v3.py').read_bytes();value=raw.decode('utf8')
    value=value.replace('from checkpoint208 import ', 'from checkpoint_cache208_v3 import ')
    value=value.replace('        runner.load(warm)',
        '        from source_cache208_v3 import runner_source_load_scope\n        with runner_source_load_scope():\n            runner.load(warm)')
    value=value.replace('    def _sha256(path):\n        import hashlib',
        '    def _sha256(path):\n        from source_cache208_v3 import cached_source_owns,cached_H\n        if cached_source_owns(path):return cached_H(path)\n        import hashlib')
    with (HERE/'train_full208_v3.py').open('x',encoding='utf8',newline='\n') as f:f.write(value)
    rows.append(dict(source=str(HERE/'train208_v3.py'),source_SHA=hashlib.sha256(raw).hexdigest(),
        output=str(HERE/'train_full208_v3.py'),SHA=hashlib.sha256((HERE/'train_full208_v3.py').read_bytes()).hexdigest()))
    with (HERE/'FULLSTATE_CACHE_V3_DERIVATION.json').open('x',encoding='utf8') as f:json.dump(dict(
        ID='NEW208_FULLSTATE_CACHE_PARENT_ABI_SOURCE_V3',rows=rows,
        actual_source_reads=0,actual_decodes=0,local_tests=0,actual_SDK_or_remote_calls=0,
        purpose_when_root_runs='one physical selectedPT read/hash/decode;explicit CPU cloned state cache;own produced artifact reads separately counted',
        all_original_actor_optimizer_D0_D7_guard_and_named_RNG_checks_retained=True,
        Path_open_or_builtin_open_monkeypatch=False,root_Git_pending=True),f,indent=2)


if __name__=='__main__':main()
