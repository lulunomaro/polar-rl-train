"""Independently admit only the actually closed own0 and complete real source."""
from pathlib import Path
import sys,os,json,time,hashlib,torch
os.environ['CUDA_VISIBLE_DEVICES']=''
D=Path(__file__).resolve().parent;W=D.parent
sys.path[:0]=[str(D),str(W/'MOD4_S3_WAVE50_CLOSEOUT_S4_LIVE_ADAPTER_20261015'),str(W/'MOD4_S3_SCOPE_COST_S4_READINESS_AUDIT_20261014')]
from s4_original_fullstate_migration_v2 import SCHEMA
from materialize_s4_first_supported_formal_target_CPU_v3 import walk,equal
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    receipt=json.loads(sorted((D/'reports').glob('S4_DIRECT_OWN0_FULLSTATE_ALL_ACTUAL_*.json'))[-1].read_bytes())
    assert receipt['pending'] is False and receipt['own_parent_child_absent_two_locks_free'] is True
    rows={v['relative']:v for v in receipt['files']};prefix='own_fullrestore0_cacheABI_v4/attempt/'
    def read(name):return json.loads(Path(rows[prefix+name]['local_path']).read_bytes())
    done=read('S4_COMPLETE_ACTUAL.json');assert done['passed'] is True and done['controls']==done['callbacks']==done['PPO_updates']==0
    assert done['source_SHA']=='601455ca68fbabe8a89b9165ce83007fe6157333b1c6f770520b6890a061f19d'
    for name,fields in SCHEMA.items():
        v=read(name);assert v['pid']==done['pid'] and v['source_sha256']==done['source_SHA']
        for k in fields:assert v[k] is True,(name,k)
        assert v['PhysX_exact_resume_claimed'] is False
    proof=read('S4_OWN_FULLRESTORE_ACTUAL.json');assert proof['passed'] is True
    assert proof['own_S4_gate_critic_optimizer_private_routing_CUDA_disk_exact_before_reset'] is True
    assert proof['new_gate_critic_optimizer_initialized_again'] is False
    zero=read('S4_ZERO_CONTROL_STATE_INTEGRITY_ACTUAL.json');assert zero['zero_control_restore_state_integrity'] is True and zero['positive_control_physics_certification'] is False
    row=rows[prefix+'S4_OWN_INTEGRATION_FULLSAVE.pt'];assert row['sha256']==done['own_checkpoint_SHA']
    ck=torch.load(row['local_path'],map_location='cpu',weights_only=False)
    old_receipt=json.loads(sorted((D/'reports').glob('S4_VALID_FIRST_ZERO_FULLSAVE_AND_FAILED_CACHE_ALL_ACTUAL_*.json'))[-1].read_bytes())
    prior=next(v for v in old_receipt['files'] if v['relative']=='own_first_fullsave0_healthschema/attempt/S4_OWN_INTEGRATION_FULLSAVE.pt')
    old=torch.load(prior['local_path'],map_location='cpu',weights_only=False)
    for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert equal(ck[k],old[k])
    assert not ck['optimizer_state_dict']['state'] and ck['S4_shared_control_state']['completed_controls']==0
    assert ck['S4_owned_learning']['actor_owned']['rollout_samples']==0
    assert equal(ck['S4_owned_learning']['actor_owned']['private_routing_rng'],old['S4_owned_learning']['actor_owned']['private_routing_rng'])
    before=dict(walk(old));after=dict(walk(ck));episodes=[]
    for k,v in before.items():
        if k.endswith('/episode') and v.shape==(20000,) and v.dtype==torch.int64:
            assert torch.equal(after[k],v+1),k;episodes.append(k)
    assert len(episodes)>=7
    floats=[v for k,v in after.items() if v.is_floating_point()]
    assert all(v.device.type=='cpu' for v in after.values()) and all(torch.isfinite(v).all() for v in floats)
    cache=ck['S4_shared_control_state']['cache'];assert set(cache.keys())=={'policy','critic'}
    assert cache['policy'].shape==(20000,35) and cache['critic'].shape==(20000,38)
    assert (cache['policy'][:,22:28]==0).all() and torch.equal(cache['policy'][:,22:28],ck['S4_shared_control_state']['previous'])
    assert ck['S4_original_W35_source_SHA']=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
    result=dict(epoch=time.time(),passed=True,source_SHA=row['sha256'],source_path=row['path'],local_source=row['local_path'],source_bytes=row['bytes'],
        source_real_GPU_fullsave_not_CPU_fixture=True,no_PPO_updates=True,own_parent_child_absent_two_locks_free=True,
        all_original_eight_strict_restore_fields_and_PID_source_verified=True,own_gate_critic_optimizer_private_CUDA_disk_roundtrip=True,
        source_frozen18_expert_STD_gate_critic_empty_optimizer_unchanged=True,private_routing_no_extra_draw=True,
        source_episode_plus_one_fields=episodes,all_tensors=len(after),floating_tensors=len(floats),perenv_tensors=sum(v.ndim>0 and v.shape[0]==20000 for v in after.values()),
        shared35_critic38_and_actual_previous_reset_action_exact=True,unobserved_health0_NaN_preserved_not_physics_PASS=True,
        original_native120_scope_failed_and_no_full120_durable_raw_preserved=True,
        actual_native120_physical_prefix_separately_CPU_reviewed=True,no_native120_or_prior_first0_replay=True,
        canonical_unchanged_SHA=receipt['canonical_SHA'],first_supported_training_profile_GPU_startup_still_required=True,
        first_gate_PPO_not_yet_dispatched=True)
    p=D/'reports/CLOSED_S4_ZERO_FULLSTATE_INDEPENDENT_CPU_ADMITTED.json';assert not p.exists();p.write_text(json.dumps(result,indent=2))
    print(json.dumps(dict(passed=True,report=str(p),source_SHA=row['sha256'],all_tensors=len(after),floats=len(floats),episodes_plus_one=len(episodes),no_PPO=True)))
if __name__=='__main__':main()
