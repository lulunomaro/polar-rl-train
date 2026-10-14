"""Independent actual local CPU verifier. Requires a genuine completed collection."""
from pathlib import Path
import argparse,json,sys,os,time,traceback,copy
os.environ['CUDA_VISIBLE_DEVICES']=''
import second_root_owned_transport_common_v1 as t
from left_second_saved_positive_CPU_math_v1 import verify_positive_state,verify_latest_health
sys.path.insert(0,str(t.P))
from second_target_CPU_pure_guard_v2 import tree_sha,SOURCE_SHA
from left_sameidentity_typed13_receipts import validate_one,REQUIRED_BOOLEAN_SCHEMA
def main():
    a=argparse.ArgumentParser();a.add_argument('--collection',required=True);args=a.parse_args()
    report=Path(args.collection);v=json.loads(report.read_bytes());remote=v['remote_CPU'];assert remote['passed'] is True and remote['root']==t.ROOT and remote['formal_final_claimed'] is False
    rows=v['two_host_byteSHA_exact'];assert len(rows)==16
    for row in rows:assert Path(row['local_path']).stat().st_size==row['bytes'] and t.sha(row['local_path'])==row['sha256']
    local=json.loads((t.REPORTS/'SECOND_ROOT_UNIQUE_FORMAL_DISPATCH_ACTUAL.json').read_bytes());assert local['source']['sha256']==SOURCE_SHA
    assert remote['source']==local['source'] and remote['source_manifest']['sha256']==local['manifest_SHA']
    assert rows[0]['remote_path']==remote['own_checkpoint']['path'] and rows[0]['sha256']==remote['own_checkpoint']['sha256']
    manifests=[x for x in rows if x['remote_path']==t.ROOT+'/LEFT_SECOND_SAMEIDENTITY_ADMISSION_MANIFEST.json'];assert len(manifests)==1
    m=json.loads(Path(manifests[0]['local_path']).read_bytes());assert m['source']==local['source'] and len(m['sourcefreeze'])==local['actual_sourcefreeze_count']==541
    assert m['no_initializer_repeat'] is True and m['scope_learning_block_index']==m['max_blocks_same_axis']==2
    dispatches=[x for x in rows if x['remote_path']==t.ROOT+'/left_second_formal3600_v1/DISPATCH_RECEIPT.json'];assert len(dispatches)==1
    dispatch=json.loads(Path(dispatches[0]['local_path']).read_bytes());assert dispatch==remote['own_dispatch'] and dispatch['parent']['pid']==local['pid']
    markers={x['remote_path'].rsplit('/',1)[1]:x for x in rows if x['remote_path'].rsplit('/',1)[1] in REQUIRED_BOOLEAN_SCHEMA};assert len(markers)==13
    typed=[validate_one(name,json.loads(Path(row['local_path']).read_bytes()),dispatch['child']['pid'],SOURCE_SHA) for name,row in markers.items()]
    import torch,numpy as np
    assert not torch.cuda.is_initialized();rng=torch.get_rng_state().clone();np_rng=tree_sha(np.random.get_state())
    parent=t.W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_formal_final_actual/0_model_32635.pt';assert t.sha(parent)==SOURCE_SHA
    own=Path(rows[0]['local_path']);own_SHA=t.sha(own)
    c=torch.load(own,map_location='cpu',weights_only=False);source=torch.load(parent,map_location='cpu',weights_only=False);fingerprint=tree_sha(c)
    math=verify_positive_state(c,source);assert math==remote['saved_state'];verify_latest_health(remote['health_latest_separate_from_saved_controls'])
    assert tree_sha(c)==fingerprint and t.sha(own)==own_SHA and t.sha(parent)==SOURCE_SHA
    assert torch.equal(torch.get_rng_state(),rng) and tree_sha(np.random.get_state())==np_rng and not torch.cuda.is_initialized()
    out=dict(epoch=time.time(),passed=True,actual_collection=dict(path=str(report),sha256=t.sha(report)),source=local['source'],actual_local_source=dict(path=str(parent),bytes=parent.stat().st_size,sha256=SOURCE_SHA),own_local_checkpoint=rows[0],saved_state=math,thirteen_sameidentity_startup_actual_verified=typed,fullbranch_old_initializer_metadata_exact_not_repeated=True,CPU_source_and_own_trees_unchanged=True,no_CPU_numpy_RNG_draw=True,no_CUDA_initialized=True,health_live_snapshot_not_forced_equal_to_saved_update=True,formal_final_claimed=False,qualified50=False,all_original_false_error_and_future_final_review_required=True,pending_Git_by_root=True)
    path=t.REPORTS/('LEFT_SECOND_OWN_POSITIVE_WEIGHT_LOCAL_CPU_VERIFIED_'+str(time.time_ns())+'.json');t.write_once(path,out)
    print(json.dumps(dict(local_CPU_report=str(path),saved_state=math,formal_final=False,qualified50=False)))
if __name__=='__main__':
    try:main()
    except BaseException:t.original_error('LEFT_SECOND_OWN_POSITIVE_LOCAL_CPU_ORIGINAL_ERROR');raise
