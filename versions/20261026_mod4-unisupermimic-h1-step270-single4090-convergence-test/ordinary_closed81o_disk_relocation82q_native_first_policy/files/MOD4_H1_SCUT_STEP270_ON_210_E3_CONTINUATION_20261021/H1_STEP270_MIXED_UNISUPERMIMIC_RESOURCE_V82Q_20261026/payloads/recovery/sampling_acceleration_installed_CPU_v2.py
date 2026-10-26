"""New-payload CPU source/data admission. API: check(B, key).

B is the actual h1 or recovery payload root, key is 'h1' or 'recovery'.
No Isaac import, GPU API, policy inference, scene, reset, rollout or budget write.
Recovery checks read this NEW payload bank once, then reuse those same bytes in
memory for normal/inference constructor comparison. This is not a live SDK test.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
import hashlib,importlib.util,io,json,sys
from pathlib import Path
from unittest import mock

EXPECTED={
 'h1':{
  'h1_production_control_prefix_trace_v1.py':'a24011df3a43e580fa15037791c30e9f8dacdaf4d0f6b9dd62b00276798414bd',
  'sampling_trace_npz_lossless_v1.py':'ce2335df8ac300fb52659d69fd41df82dd8a58964adc990448709cd332d8057f'},
 'recovery':{
  'job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py':'7e1d28e8ef1622f7923c00358f2683ea8682cf4553f0e1aacf40e68446b2ae2d',
  'job0/runtime/isaac/mod4/e3_reset_bank_cache_v1.py':'ba4f5cd584f911a9313de2f60f6465b1114f645a47c1ffcda5fcc9930dd8109a'}}
BASE={
 'h1':{'h1_production_control_prefix_trace_v1.py':'d14f69cd14a1297f558ea7f7df83f17f735cec2f99da037f3b2d623a2f590dd6'},
 'recovery':{'job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py':'0f8fd2c24b25a4a80f18bb4c3aae016acfa6873b418d6e2e32a3f72ff6199fbd'}}
BANK_SHA='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83'
BANK_BYTES=32022178
PERMUTATION_SHA='e1b5a6ddc0d0bbd9115387fb366e5ccabd05c035395f9d91b7aba0f2a07bb119'


def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m


def _original_geometry(torch,points,recipe):
    # Original source0f8fd2... place_declared_fall per-selected arithmetic.
    device=points.device;degrees=torch.tensor([-90.,-60.,-30.,30.,60.,90.],device=device)
    angle=torch.where(recipe<12,degrees[recipe.clamp(max=11)%6],0.)*torch.pi/180
    quat=torch.zeros((len(recipe),4),device=device)
    quat[torch.arange(len(recipe),device=device),torch.where(recipe<6,0,1)]=torch.sin(angle/2);quat[:,3]=torch.cos(angle/2)
    minimum=torch.empty(len(recipe),device=device)
    for first in range(0,len(recipe),128):
        last=min(first+128,len(recipe));v=quat[first:last,None,:3];p=points[None].expand(last-first,-1,-1)
        rot=p+2*torch.cross(v.expand_as(p),torch.cross(v.expand_as(p),p,dim=-1)+quat[first:last,None,3:4]*p,dim=-1)
        minimum[first:last]=rot[:,:,2].amin(-1)
    return quat,minimum,(1+torch.cos(angle))/2


def check(B,key):
    """Return JSON-serializable receipt or raise on any source/data mismatch."""
    import numpy as np
    B=Path(B).resolve();key='recovery' if key=='e3' else key
    if key not in EXPECTED:raise ValueError('Expected h1 or recovery payload root')
    actual={rel:H(B/rel) for rel in EXPECTED[key]}
    if actual!=EXPECTED[key]:raise RuntimeError('Installed acceleration file SHA mismatch')
    result=dict(passed=False,status='checking_CPU_only',key=key,base=str(B),
                expected_base_SHA=BASE[key],candidate_SHA=actual,
                exact_source_allowlist=list(EXPECTED[key]),no_GPU_API_SDK_scene_policy_physics_or_canonical=True,
                actual_live_SDK_joint_order_or_CUDA_outputs_not_claimed=True)
    if key=='h1':
        helper=_module('owned_acceleration_npz_CPU_check',B/'sampling_trace_npz_lossless_v1.py')
        rng=np.random.Generator(np.random.PCG64(20261025))
        arrays=dict(policy35=rng.standard_normal((24,3,35),dtype=np.float32),
                    q30=rng.standard_normal((24,3,30),dtype=np.float32),
                    history5ms=rng.standard_normal((24,3,3,2,3),dtype=np.float32),
                    counts=np.arange(72,dtype=np.int64).reshape(24,3),
                    flags=np.zeros((24,3),dtype=np.bool_),
                    special=np.array([0,0x80000000,0x7fc00001,0xffc00002,0x7f800000,0xff800000],dtype=np.uint32).view(np.float32))
        buf=io.BytesIO();helper.write_arrays_npz(buf,arrays,compresslevel=1);buf.seek(0)
        with np.load(buf,allow_pickle=False) as loaded:
            assert loaded.files==list(arrays)
            assert all(loaded[k].dtype==v.dtype and loaded[k].shape==v.shape and loaded[k].tobytes()==v.tobytes() for k,v in arrays.items())
        rows=[{k:v[i] for k,v in arrays.items() if k!='special'} for i in range(24)]
        buf=io.BytesIO();helper.write_trace_rows_npz(buf,rows,compresslevel=1);buf.seek(0)
        with np.load(buf,allow_pickle=False) as loaded:
            assert all(loaded[k].dtype==v.dtype and loaded[k].shape==v.shape and loaded[k].tobytes()==v.tobytes() for k,v in arrays.items() if k!='special')
        assert helper.sha256_file(B/'sampling_trace_npz_lossless_v1.py')==actual['sampling_trace_npz_lossless_v1.py']
        result.update(passed=True,status='CPU_exact_installed_sources_and_lossless_fixture_passed',
                      NPZ_array_bytes_dtype_shape_exact=True,full_SHA_preserved=True,
                      actual_persist_retention_evidence='V1 actual persist/retention/fault CPU report retained in preparation archive; installed trace exact SHA binds that unchanged AST')
        return result
    import torch
    runtime=B/'job0/runtime/isaac/mod4';permpath=runtime/'e1_rough_reset_tensor.py'
    if H(permpath)!=PERMUTATION_SHA:raise RuntimeError('Original joint_permutation source changed')
    _module('e1_rough_reset_tensor',permpath)
    cachemod=_module('owned_acceleration_e3_cache_CPU_check',runtime/'e3_reset_bank_cache_v1.py')
    bankpath=runtime/'MOD4_RESET_COLLISION_BANK.npz'
    st=bankpath.stat()
    if st.st_size!=BANK_BYTES:raise RuntimeError('New-payload bank size mismatch')
    raw=bankpath.read_bytes()  # Exactly one byte read of the NEW payload bank.
    if hashlib.sha256(raw).hexdigest()!=BANK_SHA:raise RuntimeError('New-payload bank SHA mismatch')
    after=bankpath.stat()
    if (st.st_size,st.st_mtime_ns,st.st_ino,st.st_ctime_ns)!=(after.st_size,after.st_mtime_ns,after.st_ino,after.st_ctime_ns):
        raise RuntimeError('Bank changed during new-payload CPU validation')
    with np.load(io.BytesIO(raw),allow_pickle=False) as bank:
        names=list(bank['joint_names']);pick=int(np.argmin(abs(bank['root_height']-.25)))
        points=torch.as_tensor(bank['points_root'][pick],device='cpu',dtype=torch.float32)
        bank_q=bank['q'][pick].copy()
    before_rng=torch.random.get_rng_state().clone();cpu_threads=torch.get_num_threads();torch.set_num_threads(1)
    old_read=Path.read_bytes;memory_read_requests=0
    def cached_read(path):
        nonlocal memory_read_requests
        if path.resolve()==bankpath.resolve():memory_read_requests+=1;return raw
        return old_read(path)
    cases=[]
    try:
        with mock.patch.object(Path,'read_bytes',cached_read):
            for robot_names in (names,list(reversed(names))):
                recipe=torch.arange(520,device='cpu',dtype=torch.long)%13
                expected_geometry=_original_geometry(torch,points,recipe)
                perm=[names.index(x) for x in robot_names]
                expected_q=torch.as_tensor(bank_q[perm],device='cpu',dtype=torch.float32)[None].repeat(len(recipe),1)
                for inference_ctor in (False,True):
                    with torch.inference_mode(inference_ctor):cache=cachemod.E3ResetBankCache(bankpath,robot_names,'cpu')
                    with torch.inference_mode():values=cache.selected_geometry(recipe,robot_names)
                    assert all(a.shape==b.shape and a.dtype==b.dtype and torch.equal(a,b) for a,b in zip(values,(expected_q,*expected_geometry)))
                    cache.validate(robot_names)
                    assert cache.pick==pick and cache.source_sha==BANK_SHA
                    assert all(value._version>=0 for value in (cache._q,cache._quat,cache._minimum,cache._initial))
                    cases.append(dict(joint_order='bank' if robot_names==names else 'reverse',inference_constructor=inference_ctor,
                                      inference_selection=True,selected=520,original_per_selected_geometry_and_q_exact=True))
        assert torch.equal(before_rng,torch.random.get_rng_state())
    finally:torch.set_num_threads(cpu_threads)
    result.update(passed=True,status='CPU_exact_installed_sources_and_fresh_bank_geometry_context_passed',
                  bank_SHA=BANK_SHA,bank_bytes=BANK_BYTES,fresh_bank_physical_read_count=1,
                  constructor_memory_read_requests=memory_read_requests,points_per_pose=len(points),selected_bank_pose=pick,
                  normal_and_inference_cases=cases,global_CPU_torch_RNG_unchanged=True,
                  original_margin_m=.0001,selected_reset_SDK_calls_unchanged_by_exact_source_AST=True,
                  real_CUDA_or_live_SDK_validation_remaining=True)
    return result


if __name__=='__main__':
    import argparse,time
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True);parser.add_argument('--key',choices=['h1','recovery'],required=True);parser.add_argument('--report')
    args=parser.parse_args();receipt=check(args.root,args.key);receipt['epoch']=time.time()
    if args.report:
        with Path(args.report).open('x',encoding='utf8') as f:json.dump(receipt,f,indent=2)
    print(json.dumps(receipt))
