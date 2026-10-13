from pathlib import Path;import json,time,hashlib,shutil,psutil,msvcrt,ast
r=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013');old=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/capacity512_own128_expanded_benchmark_v1_20261013');new=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/capacity512_own128_expanded_benchmark_v2_20261013')
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
x=json.loads((old/'attempts/temporary2048_native_v1/EXIT_RECEIPT.json').read_bytes());e=json.loads((old/'attempts/temporary2048_native_v1/output/ORIGINAL_ERROR.json').read_bytes());assert x['no_PPO'] and x['worker_exitcode']==1 and "'_env_prim_paths'" in e['error']
for row in (x['parent'],x['child']):
 try:p=psutil.Process(row['pid']);assert p.create_time()!=row['created']
 except psutil.NoSuchProcess:pass
with (r/'WINDOWS4090_GPU_EXCLUSIVE.lock').open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
scene=r/'sdk_exact/source/isaaclab/isaaclab/scene/interactive_scene.py';assert 'self.env_prim_paths = ' in scene.read_text(encoding='utf8') and 'self._env_prim_paths = ' not in scene.read_text(encoding='utf8')
assert not new.exists();new.mkdir();shutil.copytree(old/'payload',new/'payload');shutil.copytree(old/'runtime2048',new/'runtime2048');(new/'reports').mkdir();(new/'attempts').mkdir()
p=new/'payload/temporary_probe_contract_base.py';before=ref(p);s=p.read_text(encoding='utf8');assert s.count('env.scene._env_prim_paths')==1;s=s.replace('env.scene._env_prim_paths','env.scene.env_prim_paths');p.write_text(s,encoding='utf8');compile(s,str(p),'exec')
m=json.loads((old/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json').read_bytes());m.update(scope_root=str(new),epoch=time.time(),public_scene_API_CPU_proof=dict(actual_source=ref(scene),old_observer=before,new_observer=ref(p),no_physics_or_source_change=True))
cpu=json.loads(Path(m['target_CPU_receipt']['path']).read_bytes());cpu.update(scope=str(new),public_scene_env_prim_paths_CPU_source_exact=True);q=new/'reports/TARGET_CAPACITY512_PUBLIC_SCENE_CPU_ACTUAL.json';q.write_text(json.dumps(cpu,indent=2),encoding='utf8');m['target_CPU_receipt']=ref(q)
m['sourcefreeze_files']=[ref(p) for b in (new/'payload',new/'runtime2048',r/'sdk_exact/source',r/'sdk_exact/apps') for p in sorted(b.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p)]
q=new/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json';q.write_text(json.dumps(m,indent=2),encoding='utf8');l=new/'TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json';l.write_text(json.dumps(dict(epoch=time.time(),case_id='capacity512_own128_expanded_benchmark_v2_20261013',approved_GPU_scope=True,mode='native',scope_root=str(new),environment_root=str(r),shared_gpu_lock=str(r/'WINDOWS4090_GPU_EXCLUSIVE.lock'),manifest_sha256=H(q)),indent=2),encoding='utf8')
proof=dict(epoch=time.time(),CPU_only=True,old_error=e,old_EXIT=x,new_manifest=ref(q),source_fix=m['public_scene_API_CPU_proof'],new_native_only_after_actual_exit=True);(new/'reports/PUBLIC_SCENE_API_CPU_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
