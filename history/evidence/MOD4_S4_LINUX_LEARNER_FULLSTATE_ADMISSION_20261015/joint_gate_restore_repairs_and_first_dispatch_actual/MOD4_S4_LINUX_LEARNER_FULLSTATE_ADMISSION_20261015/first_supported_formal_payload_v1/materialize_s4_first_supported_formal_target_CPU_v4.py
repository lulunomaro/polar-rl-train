"""Source-bound first gate target, CPU only; actual closed GPU evidence required."""
from pathlib import Path
import os,sys,json,hashlib,time,fcntl,shutil,traceback
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
    with Path(p).open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
def walk(x,key=''):
    import torch
    if torch.is_tensor(x):yield key,x
    elif hasattr(x,'items'):
        for k,v in x.items():yield from walk(v,key+'/'+str(k))
    elif isinstance(x,(tuple,list)):
        for i,v in enumerate(x):yield from walk(v,key+'/'+str(i))
def equal(a,b):
    import torch
    if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a.cpu(),b.cpu())
    if hasattr(a,'items'):return set(a.keys())==set(b.keys()) and all(equal(a[k],b[k]) for k in a.keys())
    if isinstance(a,(tuple,list)):return type(a)is type(b) and len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    return type(a)is type(b) and a==b
def main(ctx):
    assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
    root=Path(ctx['target_root']);stage=Path(ctx['upload_stage']);old=Path(ctx['closed_zero_root'])
    assert not root.exists()
    for name,h in ctx['files'].items():
        p=stage/name;assert sha(p)==h
        if p.suffix=='.py':compile(p.read_bytes(),str(p),'exec')
    sys.path.insert(0,str(stage))
    from s4_first_supported_gate_formal_parent_v2 import LOCKS,B,budget_guard
    import psutil,subprocess,torch
    locks=[];created=False
    try:
        for p in LOCKS:
            f=p.open('r+b');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
        budget_guard();budget_before=sha(B)
        assert psutil.virtual_memory().available>=55000000000 and shutil.disk_usage(old).free>=30000000000
        assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
        parent=json.loads((old/'PARENT_IDENTITY_ACTUAL.json').read_bytes());assert not psutil.pid_exists(parent['pid'])
        done=json.loads((old/'PIPELINE_COMPLETE_ACTUAL.json').read_bytes());assert done['passed'] is True and done['PPO_updates']==0
        assert done['own_fullrestore0_from_valid601_complete'] is True
        assert len(done['stages'])==1
        source=Path(done['stages'][-1]['checkpoint']);assert sha(source)==ctx['source_SHA']==done['stages'][-1]['checkpoint_SHA']
        source_cpu=json.loads((stage/'CLOSED_S4_ZERO_FULLSTATE_INDEPENDENT_CPU_ADMITTED.json').read_bytes())
        assert source_cpu['passed'] is True and source_cpu['source_SHA']==ctx['source_SHA'] and source_cpu['own_parent_child_absent_two_locks_free'] is True
        assert source_cpu['no_PPO_updates'] is True
        prior=json.loads((stage/'NATIVE120_SAVE_FAILURE_INDEPENDENT_CPU_CLASSIFICATION.json').read_bytes())
        assert prior['passed_independent_classification'] is True and prior['original_native_scope_passed'] is False
        assert prior['actual_completed_physical_controls']==120 and prior['actual_completed_callbacks']==480 and prior['native_physical_health_passed'] is True
        assert prior['full120_raw_trace_not_durably_written_before_save_error'] is True
        # The physical-prefix limit is disclosed, never upgraded to old scope PASS.
        original=json.loads((old/'S4_NATIVE_FULLSTATE_TARGET_CPU_ACTUAL.json').read_bytes())
        refs=original['refs'];assert [v['sha256'] for v in refs]==['b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8','b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd']
        for v in refs:assert sha(v['local_path'])==v['sha256']
        initial=torch.get_rng_state().clone();ck=torch.load(source,map_location='cpu',weights_only=False)
        assert ck['S4_native_integration_checkpoint_not_production_learning_source'] is True and ck['S4_GPU_learning_admitted'] is False
        assert ck['S4_original_W35_source_SHA']==refs[1]['sha256'] and not ck['optimizer_state_dict']['state']
        assert ck['S4_shared_control_state']['completed_controls']==0
        assert ck['S4_owned_learning']['actor_owned']['rollout_samples']==0
        assert ck['sensor_DR_state']['n']==20000 and ck['E1_terrain_state']['profile']=='mod4_G3_CAD_derived_35mm_v1'
        tensors=list(walk(ck));assert all(v.device.type=='cpu' for k,v in tensors)
        assert all(torch.isfinite(v).all() for k,v in tensors if v.is_floating_point())
        root.mkdir();created=True
        for row in original['runtime_files']:
            p=Path(row['path']);assert sha(p)==row['sha256'];out=root/row['relative'];out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
        for name,h in ctx['files'].items():shutil.copy2(stage/name,root/name);assert sha(root/name)==h
        sys.path.insert(0,str(root))
        from s4_rsl5_frozen_pair_learner_v1 import S4FrozenPairActor,S4NewSourceCritic
        from tensordict import TensorDict
        td=TensorDict(dict(policy=torch.zeros(1,35),critic=torch.zeros(1,38)),batch_size=[1]);td['policy'][:,28]=1
        groups=dict(actor=['policy'],critic=['critic'])
        actor=S4FrozenPairActor(td,groups,'actor',6,expert_refs=refs,routing_seed=20261015)
        critic=S4NewSourceCritic(td,groups,'critic',1,expert_refs=refs)
        assert equal(actor.state_dict(),ck['actor_state_dict']) and equal(critic.state_dict(),ck['critic_state_dict'])
        assert actor.verify_frozen()
        disk=root/'S4_SOURCE_WHOLE_CPU_EVIDENCE_NOT_TRAINING_SOURCE.pt';torch.save(ck,disk)
        loaded=torch.load(disk,map_location='cpu',weights_only=False);assert equal(ck,loaded)
        loaded_rows=dict(walk(loaded))
        for k,v in tensors:
            if v.numel():assert v.untyped_storage().data_ptr()!=loaded_rows[k].untyped_storage().data_ptr()
        from s4_portable_supported_shadow_CPU_v1 import check
        import inspect
        from rsl_rl.algorithms import PPO
        from rsl_rl.runners import OnPolicyRunner
        from rsl_rl.utils.logger import Logger
        assert sha(inspect.getfile(PPO))=='a2d35e7ad7b884c80b7434e7d2ce785a6da1e18d93c96f1179fbd3a208669f8c'
        assert sha(inspect.getfile(OnPolicyRunner))=='39358a0a60219fdb360df7acddf80f6a382837aa58e2ec0ccf875df4afee4825'
        assert sha(inspect.getfile(Logger))=='d9822d8317724507a7c817e85399db0db9e56a4eae959435138e75cf92e44b8d'
        shadow=check(root,refs);assert shadow['passed'] and shadow['optimizer_updates']==0
        assert torch.equal(initial,torch.get_rng_state()) and not torch.cuda.is_initialized()
        assert sha(source)==ctx['source_SHA'] and sha(B)==budget_before
        # The real 32MB reset NPZ is a runtime asset and MUST be frozen. Only
        # CPU evidence artifacts outside the runtime are omitted from this map.
        names={row['relative'] for row in original['runtime_files']}|set(ctx['files'])
        freeze={name:sha(root/name) for name in sorted(names)}
        put(root/'S4_FIRST_FORMAL_SOURCE_FREEZE.json',dict(sha256=freeze))
        result=dict(epoch=time.time(),passed=True,source_CPU_complete=True,closed_native_and_zero_fullrestore_CPU_admitted=True,
            native_original_failed_SCOPE_not_relabelled=True,physical_native120_prefix_limited_proof_disclosed=True,
            root=str(root),source_path=str(source),source_SHA=ctx['source_SHA'],expert_refs=refs,
            original_environment=original['original_environment'],sourcefreeze=freeze,duration_seconds=2700,
            source_all_tensors=len(tensors),source_floating_tensors=sum(v.is_floating_point() for k,v in tensors),
            source_perenv_tensors=sum(v.ndim>0 and v.shape[0]==20000 for k,v in tensors),
            actual_supported_shadow_CPU=shadow,original522_runtime_assets_byteexact=True,
            original_geometry_commands_DR_reward_clock_unchanged=True,only_supported24_bootstrap_gradient_sequences=True,
            source_weights_STD_gate_critic_optimizer_unchanged=True,canonical_bytes_unchanged=budget_before,
            actual_sourcebound_first_formal_GPU_startup_still_required=True,GPU_dispatched=False)
        put(root/'S4_FIRST_FORMAL_TARGET_CPU_ACTUAL.json',result)
        print(json.dumps(dict(passed=True,root=str(root),receipt_SHA=sha(root/'S4_FIRST_FORMAL_TARGET_CPU_ACTUAL.json'),source_SHA=ctx['source_SHA'],shadow_CPU=shadow,GPU=False)))
    except BaseException:
        put((root if created else stage)/('S4_FIRST_FORMAL_TARGET_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
    finally:
        for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
if __name__=='__main__':main(CONTEXT)
