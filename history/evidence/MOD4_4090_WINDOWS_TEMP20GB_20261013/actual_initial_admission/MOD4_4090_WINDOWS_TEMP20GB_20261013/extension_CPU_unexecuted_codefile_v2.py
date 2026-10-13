from pathlib import Path,PurePosixPath;import json,zipfile,hashlib,os,shutil,time,psutil,msvcrt
r=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013');old=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/temporary_scope2048_memory20GB_left_repair_20261013');new=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/temporary_scope2048_memory20GB_extension_ready_v2_20261013');p=r/'packages/EXACT_TESTED_SDK_MIMIC_EXTENSION_MISSING_COMPLETION_20261013.zip'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='1409286e9b3d94ed123de169ddc109989153453efee04685f92f2295735c13f1'
err=json.loads((old/'attempts/temporary2048_sdk_v1/output/ORIGINAL_ERROR.json').read_bytes());exitrow=json.loads((old/'attempts/temporary2048_sdk_v1/EXIT_RECEIPT.json').read_bytes())
assert err['prePPO'] and exitrow['no_PPO'] and exitrow['worker_exitcode']==1 and exitrow['own_child_and_descendants_actual_absent']
for x in (exitrow['child'],exitrow['parent']):
 try:proc=psutil.Process(x['pid']);assert proc.create_time()!=x['created']
 except psutil.NoSuchProcess:pass
with (r/'WINDOWS4090_GPU_EXCLUSIVE.lock').open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
target=r/'sdk_exact/source/isaaclab_mimic';assert not target.exists();target.mkdir()
refs=[]
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
with zipfile.ZipFile(p) as z:
 m=json.loads(z.read('EXACT_EXTENSION_MANIFEST.json'));assert z.testzip() is None
 for row in m['file_rows']:
  n=PurePosixPath(row['archive']);assert '..' not in n.parts and not n.is_absolute();b=z.read(row['archive']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
  q=target/Path(*n.parts);q.parent.mkdir(parents=True,exist_ok=True)
  with q.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
  refs.append(ref(q))
assert not new.exists();new.mkdir();shutil.copytree(old/'runtime2048',new/'runtime2048');shutil.copytree(old/'payload',new/'payload');(new/'reports').mkdir();(new/'attempts').mkdir()
strict=r/'temporary_state_binding_strict_v2.py';assert H(strict)=='78d09b93008d6ab884f224479cf1772c808682305edc65905284a8faa425720e';shutil.copy2(strict,new/'payload/temporary_state_binding.py');
mf=json.loads((old/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json').read_bytes());mf['scope_root']=str(new);mf['epoch']=time.time();mf['new_missing_Kit_extension_source_files']=refs;mf['old_zero_control_SDK_failure_retained']=str(old);mf['new_plugin_resolution_contract_requires_actual_SDK_pass']=True
original=json.loads(Path(mf['target_CPU_receipt']['path']).read_bytes());assert original['passed']
cpu=dict(original,epoch=time.time(),scope=str(new),actual_target_environment_root=str(r),reused_prior_projection_CPU_actual=True,prior_CPU_receipt=mf['target_CPU_receipt'],new_missing_extension_files=refs,no_GPU_or_PPO=True)
cp=new/'reports/TARGET_TEMP2048_EXTENSION_READY_CPU_ACTUAL.json';cp.write_text(json.dumps(cpu,indent=2),encoding='utf8');mf['target_CPU_receipt']=ref(cp)
mf['sourcefreeze_files']=[ref(p) for base in (new/'runtime2048',new/'payload') for p in sorted(base.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]+refs
f=new/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json';f.write_text(json.dumps(mf,indent=2),encoding='utf8')
lease=dict(epoch=time.time(),case_id='temporary2048_memory20GB_extension_ready_sequence_v2',approved_GPU_scope=True,mode='sdk',scope_root=str(new),environment_root=str(r),shared_gpu_lock=str(r/'WINDOWS4090_GPU_EXCLUSIVE.lock'),manifest_sha256=H(f),human20GB_temporary_branch_authorized=True,new_missing_extension_contract=True)
l=new/'TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json';l.write_text(json.dumps(lease,indent=2),encoding='utf8')
report=dict(epoch=time.time(),passed_CPU_only=True,new_scope=str(new),exact_extension_source_files=refs,old_failure=err,old_EXIT=exitrow,old_task_not_replayed=True,original_four_SDK_sources_and21apps_not_modified=True,missing_extension_not_new_teacher_training=True,target_CPU=cpu,manifest=ref(f),lease=ref(l),GPU_not_started=True)
(new/'reports/MISSING_KIT_EXTENSION_ACTUAL_CPU_COMPLETED.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
