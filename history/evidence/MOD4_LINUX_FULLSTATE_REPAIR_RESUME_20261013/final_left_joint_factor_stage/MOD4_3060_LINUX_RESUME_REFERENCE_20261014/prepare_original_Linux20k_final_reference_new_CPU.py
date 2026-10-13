"""Fresh frozen8env reference of actual complete Linux20k final; no training-state projection."""
from pathlib import Path
import json,hashlib,shutil,time,zipfile,torch
D=Path(__file__).resolve().parent;W=D.parent;N=W/'MOD4_3060_LINUX20K_FINAL_REFERENCE_20261014';Q=N/'payload';R=N/'reports'
assert not N.exists();Q.mkdir(parents=True);R.mkdir();H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/ORIGINAL_LINUX20K_OWN_ACTIVE_SAVE/model_32447.pt';SHA=H(source)
assert SHA=='1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06'
ck=torch.load(source,map_location='cpu',weights_only=False);assert ck['E1_terrain_state']['num_envs']==20000
assert ck['independent_terrain_expert']=='E1_WAVE50' and ck['E1_WAVE50_initial_source_sha256']=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
old=json.loads((D/'payload/REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json').read_bytes())
for x in old['file_rows']:
 p=D/'payload'/x['relative'];assert H(p)==x['sha256'];q=Q/x['relative'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
shutil.copy2(D/'payload/EXPECTED_INSTALLED_3060_BACKEND_V2.json',Q/'EXPECTED_INSTALLED_3060_BACKEND_V2.json')
shutil.copy2(source,Q/'source/model_32411_17b.pt')
oldSHA='17b2271644bbe02ae195a16ea97b2d7442bc957a02662fb6737b81eb64f865e9'
for n in ('paired_direct3060_reference17b_v1.py','factor_runtime_3060_reference17b_v1.py','run_direct3060_reference17b_parent_v1.py'):
 p=Q/n;s=p.read_text(encoding='utf8').replace(oldSHA,SHA).replace('MOD4_3060_LINUX_RESUME_REFERENCE_20261014','MOD4_3060_LINUX20K_FINAL_REFERENCE_20261014')
 s=s.replace("source['E1_terrain_state']['num_envs']==512","source['E1_terrain_state']['num_envs']==20000").replace('source_saved_envs=512','source_saved_envs=20000')
 compile(s,n,'exec');p.write_bytes(s.encode())
rows=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,sha256=H(p)) for p in sorted(Q.rglob('*')) if p.is_file()]
mf=Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json';mf.write_text(json.dumps(dict(epoch=time.time(),file_rows=rows,actual_source_full_envs=20000,checkpoint_SHA=SHA,actual_legacy_filename_does_not_change_source_identity=True,original_unchanged3060_frozen8_protocol=True,no_training_perenv_restore_or_projection=True),indent=2),encoding='utf8')
z=N/'REFERENCE17B_FROZEN3060_V1_SOURCE_PACKAGE.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:
 for p in sorted(Q.rglob('*')):
  if p.is_file():f.write(p,p.relative_to(Q).as_posix())
actorrows=[dict(name=k,shape=list(v.shape),dtype=str(v.dtype),sha256=hashlib.sha256(v.contiguous().numpy().tobytes()).hexdigest()) for k,v in ck['actor_state_dict'].items()]
proof=dict(epoch=time.time(),CPU_prepared_only=True,manifest=dict(path=str(mf),sha256=H(mf)),worker=dict(path=str(Q/'paired_direct3060_reference17b_v1.py'),sha256=H(Q/'paired_direct3060_reference17b_v1.py')),runtime=dict(path=str(Q/'factor_runtime_3060_reference17b_v1.py'),sha256=H(Q/'factor_runtime_3060_reference17b_v1.py')),actual_actor_nine_CPU_rows=actorrows,actual_source_envs=20000,actual_source_SHA=SHA,not_trained512_source=True,only_actor_for_frozen_inference=True,not_full80_qualification=True)
(R/'REFERENCE17B_SOURCE_FROZEN_CPU_PREPARED_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8');(R/'REFERENCE17B_ACTUAL_SOURCE_PACKAGE_SHA.json').write_text(json.dumps(dict(path=str(z),bytes=z.stat().st_size,sha256=H(z)),indent=2),encoding='utf8')
for filename in ('deploy_reference17b_frozen1500_unique_once.py','collect_reference17b_actual_readonly.py','review_reference17b_fullraw_direct91d_actual_cpu.py'):
 s=(D/filename).read_text(encoding='utf8')
 if filename.startswith('deploy'):
  s=s.replace('import transport_249_only as t',"import sys\nsys.path.insert(0,str(Path(__file__).resolve().parent.parent/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014'))\nimport transport_249_only as t\nt.ROOT='D:/MOD4_async_eval/MOD4_3060_LINUX20K_FINAL_REFERENCE_20261014'")
 if filename.startswith('collect'):
  s=s.replace('import transport_249_only as t',"sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014'))\nimport transport_249_only as t\nt.ROOT='D:/MOD4_async_eval/MOD4_3060_LINUX20K_FINAL_REFERENCE_20261014'")
 s=s.replace('MOD4_3060_LINUX_RESUME_REFERENCE_20261014','MOD4_3060_LINUX20K_FINAL_REFERENCE_20261014').replace("parent/'MOD4_3060_LINUX20K_FINAL_REFERENCE_20261014'","parent/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014'")
 s=s.replace('native3060_17b_bodypos_worldpos_reference1500_v1','native3060_Linux20k_final_bodypos_worldpos_reference1500_v1').replace('MOD4_LinuxResumeReference_20261014_17b1500_v1','MOD4_Linux20kFinalReference_20261014_Frozen1500_v1')
 s=s.replace(oldSHA,SHA).replace("source['E1_terrain_state']['num_envs']==512","source['E1_terrain_state']['num_envs']==20000").replace("actorproof['source_saved_envs']==512","actorproof['source_saved_envs']==20000")
 if filename.startswith('review'):
  s=s.replace('source17b_SHA=c[','source_Linux20k_final_SHA=c[').replace('REFERENCE17B_FULL1500_COMPLETE_PAIRED91D_CPU_ACTUAL_REVIEW.json','LINUX20K_FINAL_FULL1500_COMPLETE_PAIRED91D_CPU_ACTUAL_REVIEW.json')
 compile(s,filename,'exec');(N/filename).write_bytes(s.encode())
assert not torch.cuda.is_initialized();print(json.dumps(dict(newroot=str(N),actual_source_SHA=SHA,source_envs=20000,package_bytes=z.stat().st_size,GPU_not_started=True)))
