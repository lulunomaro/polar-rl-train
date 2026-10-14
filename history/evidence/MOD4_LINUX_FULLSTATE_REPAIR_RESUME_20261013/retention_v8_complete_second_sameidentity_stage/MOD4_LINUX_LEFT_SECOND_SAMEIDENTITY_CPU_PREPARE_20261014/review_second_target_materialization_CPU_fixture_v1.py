"""Actual local CPU fixtures only. Never invokes target/transport functions."""
from pathlib import Path
import sys,os,json,time,traceback,copy,hashlib,ast
os.environ['CUDA_VISIBLE_DEVICES']=''
D=Path(__file__).resolve().parent;P=D/'payload_v1';R=D/'reports';W=D.parent
sys.path.insert(0,str(P));import second_target_CPU_pure_guard as old
import second_target_CPU_pure_guard_v2 as g
decision_path=W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/reports/BEST2B_COMPLETE_FOURCASE_SECOND_SAMEIDENTITY_SCOPE_DECISION_ACTUAL.json'
source=W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_formal_final_actual/0_model_32635.pt'
def write_once(p,v):
    with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
def main():
    decision=json.loads(decision_path.read_bytes());files={k:Path(v['path']) for k,v in decision['evidence'].items()}
    try:old.validate_evidence_packet(decision,files)
    except AssertionError:
        write_once(R/'SECOND_ORIGINAL_V1_LEGACY_FLAGS_DICT_SCHEMA_REJECTION_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),old_source=g.record(P/'second_target_CPU_pure_guard.py'),actual_schema={k:type(json.loads(files['three_pairs'].read_bytes())['result']['full_pairs'][k]['legacy_false_preserved']).__name__ for k in ('flat','spin','world')},preSSH_preTarget_preGPU=True,original_false_preserved=True))
    else:raise AssertionError('Original v1 schema rejection expected; do not overwrite history')
    evidence=g.validate_evidence_packet(decision,files)
    import torch,numpy as np
    assert not torch.cuda.is_initialized();rng=torch.get_rng_state().clone();np_rng=g.tree_sha(np.random.get_state())
    assert g.sha(source)==g.SOURCE_SHA
    c=torch.load(source,map_location='cpu',weights_only=False);info=g.logical_fullsave(c);fingerprint=g.tree_sha(c)
    negative=g.negative_logical_checks(c)
    decisions=[]
    for key in g.DECISION_TRUE_FIELDS:
        for mode in ('false','missing','int'):
            wrong=copy.deepcopy(decision)
            if mode=='missing':wrong.pop(key)
            else:wrong[key]=False if mode=='false' else 1
            try:g.validate_decision(wrong)
            except AssertionError:decisions.append(dict(key=key,mode=mode,strict_rejected=True))
            else:raise AssertionError(('Baddecisionaccepted',key,mode))
    wrong=copy.deepcopy(decision);wrong['selected_source_SHA']='0'*64
    try:g.validate_decision(wrong)
    except AssertionError:decisions.append(dict(key='source_SHA',strict_rejected=True))
    else:raise AssertionError('Wrong source SHA accepted')
    disk=D/'SOURCE2B_LOCAL_CPU_DISK_ROUNDTRIP_PREPARED_EVIDENCE_ONLY.pt';assert not disk.exists();torch.save(c,disk)
    with disk.open('r+b') as f:os.fsync(f.fileno())
    restored=torch.load(disk,map_location='cpu',weights_only=False);assert g.same(c,restored)
    src=dict(g.walk(c));dst=dict(g.walk(restored))
    assert all(not x.numel() or x.untyped_storage().data_ptr()!=dst[k].untyped_storage().data_ptr() for k,x in src.items())
    assert g.tree_sha(c)==fingerprint and g.sha(source)==g.SOURCE_SHA
    assert torch.equal(torch.get_rng_state(),rng) and g.tree_sha(np.random.get_state())==np_rng and not torch.cuda.is_initialized()
    compiled=[]
    for path in list(P.glob('*.py'))+list(D.glob('*_v1.py')):
        compile(path.read_text(),str(path),'exec');compiled.append(g.record(path))
    target_files=['second_source_target_materialize_CPU_v1.py','second_formal_target_dispatch_from_actualmanifest_v1.py']
    for name in target_files:
        tree=ast.parse((P/name).read_text());assert not any(isinstance(n,ast.ImportFrom) and n.module and 'once' in n.module for n in ast.walk(tree))
    out=dict(epoch=time.time(),passed=True,actual_local_source=g.record(source),actual_decision=g.record(decision_path),actual_evidence_packet=evidence,whole_source_logical_CPU=info,local_CPU_fulltree_disk_roundtrip_exact=True,all195_tensor_restored_storage_independent=True,source_fingerprint_before_after=fingerprint,source_SHA_unchanged=True,no_CPU_numpy_RNG_draw=True,no_CUDA_initialized=True,source_identity_negatives=negative,scope_decision_negatives=decisions,compiled_sources=compiled,old_v1_legacy_flags_schema_rejection_preserved=True,independent_guard_v2_only_schema_fix=True,local_disk_evidence_not_formal_source=g.record(disk),target_CPU_not_executed=True,no_SSH_no_GPU_no_budget_transaction=True,proposed_remote_root_not_created=True,pending_Git_by_root=True)
    path=R/'SECOND_TARGET_MATERIALIZER_DISPATCHER_LOCAL_CPU_FIXTURE_ACTUAL.json';write_once(path,out)
    print(json.dumps(dict(report=str(path),logical_CPU=info,decision_negative_count=len(decisions),source_negative_count=len(negative),target_not_executed=True)))
if __name__=='__main__':
    try:main()
    except BaseException:
        path=R/('SECOND_LOCAL_CPU_FIXTURE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');write_once(path,dict(epoch=time.time(),error=traceback.format_exc(),no_SSH_no_GPU_no_budget=True));raise
