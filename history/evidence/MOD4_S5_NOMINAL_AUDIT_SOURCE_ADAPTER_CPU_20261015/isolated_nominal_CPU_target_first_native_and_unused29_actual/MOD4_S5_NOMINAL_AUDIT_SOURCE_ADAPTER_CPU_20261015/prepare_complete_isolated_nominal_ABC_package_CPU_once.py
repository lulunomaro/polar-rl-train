"""Build a new complete isolated source tree, without touching shared runtime.

Only new own audit modules, import provenance, nominal profile and namespace vary.
No transport, lease, GPU, PPO, Task or budget operation is performed here.
"""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.machinery
import json
import os
import shutil
import time
import traceback
import zipfile

os.environ['CUDA_VISIBLE_DEVICES']=''
import torch

D=Path(__file__).resolve().parent
W=D.parent
Q=D/'payload'
R=D/'reports'
M=W/'MOD4_S5_WHITEV2_DEVSEEDS_MATCHED_ABC_20261015'
S=W/'MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload'
ROOT='D:/MOD4_async_eval/'+D.name


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()


def put(name,value):
    with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)


def main():
    review=json.loads((R/'NOMINAL_ISOLATED_GUARDS_METADATA_D0_D7_NEGATIVES_CPU_ACTUAL.json').read_bytes())
    candidates=json.loads((R/'NOMINAL_ISOLATED_SOURCE_CANDIDATES_MATERIALIZED_ACTUAL.json').read_bytes())
    assert review['passed'] and not review['target_CPU_native_or_GPU_admission']
    assert not Q.exists() and not (R/'NOMINAL_COMPLETE_ISOLATED_ABC_CPU_PREPARED_ACTUAL.json').exists()
    original_manifest=json.loads((M/'payload/RETENTION_CPU_MANIFEST_V8.json').read_bytes())
    assert original_manifest['approved_GPU'] is False
    rng=torch.get_rng_state().clone()
    shutil.copytree(M/'payload',Q,ignore=shutil.ignore_patterns('__pycache__'))
    I=Q/'frozen_shared';I.mkdir()
    original=[]
    for row in original_manifest['shared_source_freeze']:
        p=S/row['relative'];out=I/row['relative']
        assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
        if out.exists():assert sha(out)==row['sha256']
        else:out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out)
        original.append(dict(relative=row['relative'],bytes=row['bytes'],sha256=row['sha256']))
    overlays=[]
    for row in candidates['candidates']:
        p=Path(row['candidate']);assert sha(p)==row['candidate_SHA'] and sha(row['original'])==row['original_SHA']
        relative=p.name if p.name.startswith('factor_runtime') else 'frozen_shared/runtime/isaac/mod4/'+p.name
        out=Q/relative
        previous=sha(out) if out.exists() else None
        assert previous in (None,row['original_SHA'])
        shutil.copyfile(p,out)
        overlays.append(dict(relative=relative,original_SHA=row['original_SHA'],candidate_SHA=sha(out),kind='explicit_independent_audit_source_overlay'))
    helper=Q/'frozen_shared/runtime/isaac/mod4/nominal_d0_source_audit_v1.py'
    assert not helper.exists();shutil.copyfile(D/'isolated/nominal_d0_source_audit_v1.py',helper)
    overlays.append(dict(relative=helper.relative_to(Q).as_posix(),candidate_SHA=sha(helper),kind='new_readonly_audit_helper'))
    worker_old=(M/'payload/retention_worker_v8.py').read_text(encoding='utf8');worker=worker_old
    swaps=[(M.name,D.name),
           ("L=S/'runtime'","L=D/'frozen_shared/runtime'"),
           ("sys.path[:0]=[str(C),str(L),str(S),str(D)]","sys.path[:0]=[str(C),str(L),str(D),str(D/'frozen_shared'),str(S)]"),
           ("os.environ['RM_MILD_DR_PROFILE']='white_v2'","os.environ['RM_MILD_DR_PROFILE']='nominal'\nassert os.environ['RM_DR_OFF']=='1'"),
           ("a.dr_profile='white_v2'","a.dr_profile='nominal'")]
    for old,new in swaps:assert old in worker;worker=worker.replace(old,new)
    inverse=worker
    for old,new in reversed(swaps):inverse=inverse.replace(new,old)
    assert ast.dump(ast.parse(inverse))==ast.dump(ast.parse(worker_old))
    (Q/'retention_worker_v8.py').write_text(worker,encoding='utf8')
    old=(M/'payload/retention_native_witness_v8.py').read_text(encoding='utf8')
    witness=old.replace("DR_profile='white_v2'","DR_profile='nominal'")
    assert ast.dump(ast.parse(witness.replace("DR_profile='nominal'","DR_profile='white_v2'")))==ast.dump(ast.parse(old))
    (Q/'retention_native_witness_v8.py').write_text(witness,encoding='utf8')
    def rewrite(x):
        if isinstance(x,str):return x.replace('D:/MOD4_async_eval/'+M.name,ROOT)
        if isinstance(x,dict):return {k:rewrite(v) for k,v in x.items()}
        if isinstance(x,list):return [rewrite(v) for v in x]
        return x
    for name in ('S4_PAIR_SOURCE_MANIFEST.json','S4_TRAINED_GATE_SOURCE_MANIFEST.json'):
        (Q/name).write_text(json.dumps(rewrite(json.loads((Q/name).read_bytes())),indent=2),encoding='utf8')
    exact=[]
    for kind in ('flat','spin','world'):
        name='retention_'+kind+'_native_v8.py';assert (Q/name).read_bytes()==(M/'payload'/name).read_bytes()
        exact.append(dict(kind=kind,sha256=sha(Q/name)))
    controls=('s5_single_frozen35_v1.py','s4_shared_feedback_hardtop1_v1.py','s5_ABC_evaluation_adapter_v1.py',
              's5_retention_single_adapter_v1.py','s4_retention_pair_adapter_v1.py')
    for name in controls:assert (Q/name).read_bytes()==(M/'payload'/name).read_bytes()
    whole=[]
    for name,count,expected in [('E0_frozen_source.pt',94,'b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8'),
        ('E1_WAVE35_frozen_source.pt',102,'b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'),
        ('S4_gate_first_final.pt',113,'02718c74024508c50ff559be2fa6351b7f63046afeb4ee3fd7c51ad6160ae1f3')]:
        p=Q/'source'/name;assert sha(p)==expected
        value=torch.load(p,map_location='cpu',weights_only=False);tensors=[]
        def walk(x):
            if torch.is_tensor(x):
                assert x.device.type=='cpu' and (not x.is_floating_point() or torch.isfinite(x).all());tensors.append(x)
            elif hasattr(x,'items'):
                for v in x.values():walk(v)
            elif isinstance(x,(tuple,list)):
                for v in x:walk(v)
        walk(value);assert sum(x.is_floating_point() for x in tensors)==count
        whole.append(dict(name=name,bytes=p.stat().st_size,sha256=expected,tensors=len(tensors),floating=count))
    search=[str(I/'runtime/isaac/mod4'),str(I/'runtime'),str(Q),str(I),str(S)]
    provenance={}
    for name in ('nominal_d0_source_audit_v1','spring_pressure_audit_runtime','gas_damping_sdk_adapter',
                 'chassis_com_pose_roundtrip_sdk_adapter','explicit_pd_sdk_adapter','chassis_pd_training_env',
                 'nominal_parameter_audit','factor_runtime_3060_reference17b_v1','mod4_task',
                 's5_ABC_evaluation_adapter_v1','retention_native_witness_v8'):
        spec=importlib.machinery.PathFinder.find_spec(name,search)
        assert spec and Path(spec.origin).resolve().is_relative_to(Q.resolve())
        provenance[name]=dict(path=str(Path(spec.origin).resolve()),sha256=sha(spec.origin),CPU_resolution_only_not_SDK_import=True)
    for p in Q.rglob('*.py'):ast.parse(p.read_text(encoding='utf8'),filename=str(p))
    isolated=[]
    overlay_by_relative={x['relative']:x for x in overlays}
    for p in sorted(I.rglob('*')):
        if p.is_file():
            rel=p.relative_to(Q).as_posix()
            isolated.append(dict(relative=rel,bytes=p.stat().st_size,sha256=sha(p),
                                 kind='declared_audit_overlay' if rel in overlay_by_relative else 'original_frozen_copy'))
    m=rewrite(copy.deepcopy(original_manifest))
    m.update(epoch=time.time(),namespace=D.name,DR_profile='nominal',approved_GPU=False,
             status='CPU_PREPARED_ONLY_NOT_ACTUAL_LEASE',declared_development_seeds=[20261002,20261003],
             isolated_runtime_root='frozen_shared/runtime',source_overlay=overlays,
             original_shared_source_files_frozen=len(original),isolated_source_freeze=isolated,
             historical_copied_bundle_manifests_not_current_overlay_attestations=True,
             worker_explicit_isolated_import_order=True,actual_import_origins_required_by_own_native=True,
             CPU_candidate_review_SHA=sha(R/'NOMINAL_ISOLATED_GUARDS_METADATA_D0_D7_NEGATIVES_CPU_ACTUAL.json'))
    m['package_files_v8']=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
        for p in sorted(Q.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='RETENTION_CPU_MANIFEST_V8.json']
    (Q/'RETENTION_CPU_MANIFEST_V8.json').write_text(json.dumps(m,indent=2),encoding='utf8')
    z=D/'S5_NOMINAL_COMPLETE_ISOLATED_ABC_V1.zip'
    with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as f:
        for p in sorted(Q.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:f.write(p,p.relative_to(Q).as_posix())
    assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
    for row in original_manifest['shared_source_freeze']:assert sha(S/row['relative'])==row['sha256']
    value=dict(epoch=time.time(),CPU_prepared_no_remote_or_GPU=True,
        package=dict(path=str(z),bytes=z.stat().st_size,sha256=sha(z)),manifest_SHA=sha(Q/'RETENTION_CPU_MANIFEST_V8.json'),
        worker_SHA=sha(Q/'retention_worker_v8.py'),profile='nominal',seeds=[20261002,20261003],
        full_isolated_source_copies=isolated,declared_overlay=overlays,original_shared_files_unchanged=len(original),
        whole_source_CPU=whole,original3_mainloops_byteexact=exact,original5_control_adapters_byteexact=True,
        worker_AST_inverse_except_profile_namespace_explicit_isolated_roots=True,
        witness_AST_inverse_except_profile_metadata=True,CPU_module_resolution=provenance,
        actual_target_CPU_import_GPU_native_readback_not_yet_passed=True,
        no_CUDA_optimizer_global_CPU_RNG_advance_PPO_budget=True)
    put('NOMINAL_COMPLETE_ISOLATED_ABC_CPU_PREPARED_ACTUAL.json',value)
    print(json.dumps(dict(prepared=True,package=value['package'],files=len(m['package_files_v8']),original_shared=len(original),
                          isolated_files=len(isolated),explicit_overlay=len(overlays),no_GPU=True,target_pending=True)))


if __name__=='__main__':
    try:main()
    except BaseException:
        put('NOMINAL_COMPLETE_PACKAGE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),
            no_GPU_network_PPO_budget=True,partial_local_files_preserved_do_not_replay_existing_preparation=True))
        raise
