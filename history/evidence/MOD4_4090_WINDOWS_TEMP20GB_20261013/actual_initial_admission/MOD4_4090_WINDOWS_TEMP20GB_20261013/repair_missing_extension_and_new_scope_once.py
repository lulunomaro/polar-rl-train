"""Preserve failed zero-control scope; append exact missing Kit extension, new scope."""
from pathlib import Path
import json,zipfile,hashlib,time,sys,base64,traceback
D=Path(__file__).resolve().parent;W=D.parent
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
OLD=R+'/temporary_scope2048_memory20GB_left_repair_20261013'
NEW=R+'/temporary_scope2048_memory20GB_extension_ready_v2_20261013'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def py(code,timeout=40):
 b=base64.b64encode(code.encode()).decode();return powershell(connect(),"[Console]::OutputEncoding=[System.Text.Encoding]::UTF8;& '"+R+"/env/python.exe' -c \"import base64;exec(base64.b64decode('"+b+"'))\"",timeout=timeout)
def main():
 receipt=D/'reports/MISSING_MIMIC_EXTENSION_NEW_SCOPE_ACTUAL.json';assert not receipt.exists()
 source=Path('F:/isaacsim/IsaacLab/source/isaaclab_mimic');files=[p for p in source.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p) and p.suffix not in ('.pyc','.pyo')]
 package=D/'EXACT_TESTED_SDK_MIMIC_EXTENSION_MISSING_COMPLETION_20261013.zip';assert not package.exists();rows=[]
 with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(files):
   n=p.relative_to(source).as_posix();row=dict(archive=n,bytes=p.stat().st_size,sha256=H(p));rows.append(row);z.write(p,n)
  z.writestr('EXACT_EXTENSION_MANIFEST.json',json.dumps(dict(file_rows=rows,original_tested_source=str(source),extension_version='1.0.16',only_missing_extension_package_no_learning_teleop_teacher_or_data_generation_invoked=True),indent=2))
 remote=R+'/packages/'+package.name;upload(package,remote,timeout=60)
 assert powershell(connect(),"(Get-FileHash -LiteralPath '"+remote+"' -Algorithm SHA256).Hash.ToLower()",timeout=30)==H(package)
 code="""from pathlib import Path,PurePosixPath;import json,zipfile,hashlib,os,shutil,time,psutil,msvcrt
r=Path('"""+R+"""');old=Path('"""+OLD+"""');new=Path('"""+NEW+"""');p=r/'packages/"""+package.name+"""'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='"""+H(package)+"""'
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
"""
 actual=json.loads(py(code,90))
 ps="& '"+NEW+"/payload/register_windows4090_demand_task_audited_v6_once.ps1' -LeasePath '"+NEW+"/TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json' -ManifestPath '"+NEW+"/TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json' -AttemptPath '"+NEW+"/attempts/temporary2048_sdk_v1' -PythonPath '"+R+"/env/python.exe' -RuntimePath '"+NEW+"/runtime2048' -StageMode sdk -TrainSeconds 3600 -StartApprovedLease"
 powershell(connect(),ps,timeout=35)
 receipt.write_text(json.dumps(dict(epoch=time.time(),actual=actual,new_task_requested_once=True,package=dict(path=str(package),bytes=package.stat().st_size,sha256=H(package))),indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(receipt),new_scope=NEW,missing_extension_files=len(rows),newSDK_task_started=True,PPO_not_claimed=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('MISSING_EXTENSION_REPAIR_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),unknownoutcome_inspect_no_replay=True),indent=2),encoding='utf8');raise
