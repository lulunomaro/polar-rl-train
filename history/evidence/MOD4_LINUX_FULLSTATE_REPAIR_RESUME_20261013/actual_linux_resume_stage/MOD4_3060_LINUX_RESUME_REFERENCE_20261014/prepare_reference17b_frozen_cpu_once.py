"""New immutable frozen17b fixture: copy backend, no DR projection/init/PPO."""
from pathlib import Path
import json, hashlib, shutil, torch, time
P = Path(__file__).resolve().parent; W = P.parent
OLD = W / 'MOD4_3060_DIRECT_FACTOR_20261013/payload'
Q = P / 'payload'
SOURCE = W / 'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/RECOVERED_WINDOWS512_28UPDATE/model_32411.pt'
SHA = '17b2271644bbe02ae195a16ea97b2d7442bc957a02662fb6737b81eb64f865e9'
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not Q.exists() and H(SOURCE) == SHA and not torch.cuda.is_initialized()
cpu_rng = torch.get_rng_state().clone()
ck = torch.load(SOURCE, map_location='cpu', weights_only=False)

def finite_count(v):
    if isinstance(v, torch.Tensor):
        assert v.device.type == 'cpu'
        if v.is_floating_point(): assert torch.isfinite(v).all(); return 1
        return 0
    if isinstance(v, dict): return sum(finite_count(x) for x in v.values())
    if isinstance(v, (list, tuple)): return sum(finite_count(x) for x in v)
    return 0

assert finite_count(ck) == 107 and ck['E1_terrain_state']['num_envs'] == 512
actor = ck['actor_state_dict']
assert len(actor) == 9 and actor['mlp.0.weight'].shape == (256, 35) and actor['mlp.6.weight'].shape == (6, 64)
assert ck['WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL']['initializer_repeated_on_this_resume'] is False
shutil.copytree(OLD, Q, ignore=shutil.ignore_patterns('__pycache__'))
dest = Q / 'source/model_32411_17b.pt'; assert not dest.exists(); shutil.copyfile(SOURCE, dest)
assert H(dest) == SHA
runtime = (OLD / 'factor_runtime_3060_native_v2.py').read_text()
anchor = " assert observer.checkpoint_sha256==args.checkpoint_sha\n"
assert runtime.count(anchor) == 1
addition = """ assert observer.checkpoint_sha256==args.checkpoint_sha
 actual_actor=policy.__closure__[0].cell_contents
 actual_state=actual_actor.state_dict();expected_state=source['actor_state_dict']
 assert list(actual_state)==list(expected_state) and len(actual_state)==9
 actor_rows=[]
 for key,value in actual_state.items():
  observed=value.detach().cpu();expected=expected_state[key]
  assert observed.dtype==expected.dtype and observed.shape==expected.shape and torch.equal(observed,expected)
  actor_rows.append(dict(name=key,shape=list(observed.shape),dtype=str(observed.dtype),sha256=hashlib.sha256(observed.contiguous().numpy().tobytes()).hexdigest()))
 def source_float_count(value):
  if isinstance(value,torch.Tensor):
   assert value.device.type=='cpu'
   if value.is_floating_point():assert torch.isfinite(value).all();return 1
   return 0
  if isinstance(value,dict):return sum(source_float_count(x) for x in value.values())
  if isinstance(value,(tuple,list)):return sum(source_float_count(x) for x in value)
  return 0
 assert source_float_count(source)==107 and source['E1_terrain_state']['num_envs']==512
 save('FROZEN_POLICY_SOURCE107_ACTUAL.json',dict(checkpoint_sha256=args.checkpoint_sha,source_floating107=True,source_saved_envs=512,fixture_envs=N,actual_GPU_actor_nine_tensors_source_byteexact=actor_rows,only_actor_loaded_for_frozen_inference=True,no_training_perenv_DR_projection_or_restore=True,no_initializer_or_PPO=True))
"""
runtime = runtime.replace(anchor, addition)
rname = 'factor_runtime_3060_reference17b_v1.py'
(Q / rname).write_text(runtime, encoding='utf8')
worker = (OLD / 'paired_direct3060_factor_v2.py').read_text()
worker = worker.replace('91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4', SHA)
worker = worker.replace('MOD4_3060_DIRECT_FACTOR_20261013', 'MOD4_3060_LINUX_RESUME_REFERENCE_20261014')
worker = worker.replace('factor_runtime_3060_native_v2.py', rname).replace('from factor_runtime_3060_native_v2 import', 'from factor_runtime_3060_reference17b_v1 import')
worker = worker.replace('SOURCE_BUNDLE_V2_MANIFEST.json', 'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json')
wname = 'paired_direct3060_reference17b_v1.py'; (Q / wname).write_text(worker, encoding='utf8')
parent = (OLD / 'run_direct3060_factor_parent_v2.py').read_text()
parent = parent.replace('paired_direct3060_factor_v2.py', wname).replace('factor_runtime_3060_native_v2.py', rname)
parent = parent.replace('SOURCE_BUNDLE_V2_MANIFEST.json', 'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json')
pname = 'run_direct3060_reference17b_parent_v1.py'; (Q / pname).write_text(parent, encoding='utf8')
for name in (rname, wname, pname): compile((Q / name).read_text(), str(Q / name), 'exec')
original = json.loads((OLD / 'SOURCE_BUNDLE_V2_MANIFEST.json').read_bytes())
for row in original['file_rows']:
    assert H(Q / row['relative']) == row['sha256'], row['relative']
rows = [dict(relative=p.relative_to(Q).as_posix(), bytes=p.stat().st_size, sha256=H(p))
        for p in sorted(Q.rglob('*')) if p.is_file()]
manifest = dict(profile='3060_latest17b_frozen_reference_white3_fixture_v1', file_rows=rows,
                prior_actual_sourcefreeze_sha256=H(OLD / 'SOURCE_BUNDLE_V2_MANIFEST.json'),
                only_four_new_files_source_actor_audit_and_new_lease_identity=True,
                checkpoint_sha256=SHA, checkpoint_source_envs=512, fixture_envs=8,
                no_source_perenv_DR_projection_or_training_restore=True,
                original_geometry_DR_pose_clock_health_protocol_exact=True,
                planned_single_BODYpos_worldpos1500_diagnostic_only=True)
m = Q / 'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'; m.write_text(json.dumps(manifest, indent=2), encoding='utf8')
assert torch.equal(cpu_rng, torch.get_rng_state()) and not torch.cuda.is_initialized()
report = dict(epoch=time.time(), passed_sourceCPU_and_compile_only=True,
              checkpoint=dict(path=str(SOURCE), bytes=SOURCE.stat().st_size, sha256=SHA, saved_envs=512, floating107=True),
              manifest=dict(path=str(m), sha256=H(m), bytes=m.stat().st_size, files=len(rows)),
              worker=dict(name=wname, sha256=H(Q / wname)), runtime=dict(name=rname, sha256=H(Q / rname)),
              parent=dict(name=pname, sha256=H(Q / pname)),
              actual_actor_nine_CPU_rows=[dict(name=k, shape=list(v.shape), dtype=str(v.dtype),
                                             sha256=hashlib.sha256(v.contiguous().numpy().tobytes()).hexdigest()) for k,v in actor.items()],
              original475_files_all_exact=True, zero_new_RNG=True, no_GPU_or_remote_mutation=True,
              no_projection_of_training512_DR_into_frozen8=True, not_80env_qualification=True)
q = P / 'reports/REFERENCE17B_SOURCE_FROZEN_CPU_PREPARED_ACTUAL.json'
assert not q.exists(); q.write_text(json.dumps(report, indent=2), encoding='utf8')
print(json.dumps(dict(passed_CPU=True, report=str(q), manifest_SHA=H(m), worker_SHA=H(Q / wname), runtime_SHA=H(Q / rname), GPU=False)))
