from pathlib import Path
import sys,json,time,hashlib,importlib.util,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';B=N/'payload'
REMOTE='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_NATIVE_2610v90/h1'
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)

PRE=r'''from pathlib import Path,PurePosixPath
import json,hashlib,fcntl,psutil,subprocess,shutil,time
B=Path(v['root']);old=Path('/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_own_step_gas400_native_2610v88c/recovery')
owned=Path('/home/lc01/Zonglin Li/zonglin2/tasks');assert str(B)==v['root'] and B.resolve().is_relative_to(owned.resolve()) and not B.exists()
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['budget_mode']=='finite_original_limits_restored_after_single4090_return'
assert c['remaining_training_seconds']==558113.8296625614 and c['remaining_training_seconds']>86412.86069250107
locks=[C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock',C.parent.parent/'finite_environment_validation.lock']
for path in locks:
 with path.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
e0=owned/'MOD4_E0_PPO50_GAS400_2610v89d';final=json.loads((e0/'owner/COHORT_FINAL.json').read_bytes());node=json.loads((e0/'node_e0/NODE_TERMINAL_ACTUAL.json').read_bytes())['row']
assert final['original_cost_settled'] and node['terminal_all_own_children_waited'] and node['original_error'] is False and node['returncode']==0 and node['final']['passed']
go=final['go']['e0'];assert go['original_owner_pid']==544164 and go['original_owner_creation']==1793101424.86
segments=[x for x in c['completed_segments'] if x['owner_parent_pid']==544164 and x['experts']['e0']['started_epoch']==go['learning_started_epoch']];assert len(segments)==1 and segments[0]['charged_expert_seconds']==3664.132122516632
own=[]
for row in v['known_own']:
 try:
  p=psutil.Process(row['pid']);creation=p.create_time()
  if creation==row['creation']:assert p.status()==psutil.STATUS_ZOMBIE,'known original own process still executing'
  own.append(dict(pid=row['pid'],out_or_nonexecuting=True,no_foreign_identity_read=True))
 except psutil.NoSuchProcess:own.append(dict(pid=row['pid'],out=True))
gpu='GPU-c27eecbd-6838-7290-1cd2-37e34522213d';line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free','--format=csv,noheader,nounits'],text=True).strip().split(',');apps=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
assert line[0].strip()==gpu and line[1].strip()=='NVIDIA GeForce RTX 4090' and int(line[2])>15669 and gpu not in apps
assert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(owned).free>25*1024**3
oldrows={r['relative']:r for r in json.loads((old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']}
B.mkdir(parents=True);need=[];copied=0
for row in v['manifest']['files']:
 rel=row['relative'];r=PurePosixPath(rel);dest=B/rel;src=old/rel;prior=oldrows.get(rel)
 assert not r.is_absolute() and '..' not in r.parts and '\\' not in rel and dest.resolve().is_relative_to(B.resolve())
 dest.parent.mkdir(parents=True,exist_ok=True)
 if prior and prior['bytes']==row['bytes'] and prior['SHA']==row['SHA'] and src.is_file() and not src.is_symlink() and src.stat().st_size==row['bytes']:
  shutil.copy2(src,dest);copied+=1
 else:need.append(row)
for name in ('home','tmp','cache','config','data'):(B/'job0'/name).mkdir(exist_ok=True)
assert shutil.disk_usage(B).free>25*1024**3 and C.read_bytes()==raw
print(json.dumps(dict(root=str(B),need_upload=need,files_reused=copied,resource=dict(GPU_UUID=gpu,free_MiB=int(line[2]),RAM_available=psutil.virtual_memory().available,disk_after_copy=shutil.disk_usage(B).free),C_SHA=hashlib.sha256(raw).hexdigest(),remaining=c['remaining_training_seconds'],own=own,no_account_write=True,no_GO=True)))'''

CPU=r'''from pathlib import Path
import json,hashlib,os,subprocess,time,psutil,traceback,shutil
B=Path(v['root']);m=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
assert hashlib.sha256((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==v['manifest_SHA']
for row in m['files']:
 p=B/row['relative'];assert p.resolve().is_relative_to(B.resolve()) and not p.is_symlink() and p.is_file() and p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA'],row['relative']
assert shutil.disk_usage(B).free>25*1024**3
e=dict(os.environ);e.update(CUDA_VISIBLE_DEVICES='',HOME=str(B/'job0/home'),TMPDIR=str(B/'job0/tmp'),XDG_CACHE_HOME=str(B/'job0/cache'),XDG_CONFIG_HOME=str(B/'job0/config'),XDG_DATA_HOME=str(B/'job0/data'),OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',PYTHONDONTWRITEBYTECODE='1')
script=B/'target_native_flat90_source_sdk_CPU_once.py';args=['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(script)]
p=subprocess.Popen(args,cwd=B,env=e,stdout=(B/'job0/FLAT90_SOURCE_CPU.log').open('xb'),stderr=subprocess.STDOUT,close_fds=True)
loader='/home/lc01/Zonglin Li/zonglin2/compat/glibc240/ld-linux-x86-64.so.2';py='/home/lc01/Zonglin Li/zonglin2/envs/mod4/bin/python';lib='/home/lc01/Zonglin Li/zonglin2/compat/glibc240:/home/lc01/Zonglin Li/zonglin2/envs/mod4/lib'
expected=[loader,'--library-path',lib,py,'-B','-u','-B',str(script)];until=time.monotonic()+10;identity=None;previous=None
while True:
 assert p.poll() is None,'CPU child exited before exact identity admission'
 q=psutil.Process(p.pid);row=dict(pid=p.pid,creation=q.create_time(),argv=q.cmdline(),exe=q.exe(),cwd=q.cwd())
 if row['exe']==loader and row['argv']==expected and row['cwd']=='/home/lc01/Zonglin Li/zonglin2':
  if row==previous:identity=row;break
  previous=row
 assert time.monotonic()<until,dict(expected=expected,actual=row)
 time.sleep(.05)
rc=p.wait();report=B/'job0/FLAT90_SOURCE_SDK_CPU_ACTUAL.json'
proof=dict(actual_waited=True,returncode=rc,actual_identity=identity,payload_manifest_SHA=v['manifest_SHA'],epoch=time.time(),report_SHA=hashlib.sha256(report.read_bytes()).hexdigest() if report.is_file() else None)
with (B/'job0/FLAT90_SOURCE_CPU_WAITED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(proof,f,indent=2)
errors=[dict(path=str(x),text=x.read_text()) for x in (B/'job0').glob('FLAT90_SOURCE_CPU_ORIGINAL_ERROR_*.json')]
print(json.dumps(dict(passed=rc==0 and report.is_file(),actual_CPU_waited_EXIT0=rc==0,proof=proof,proof_SHA=hashlib.sha256((B/'job0/FLAT90_SOURCE_CPU_WAITED_ACTUAL.json').read_bytes()).hexdigest(),value=json.loads(report.read_bytes()) if report.is_file() else None,errors=errors,stdout_tail=(B/'job0/FLAT90_SOURCE_CPU.log').read_text(errors='replace')[-16000:],no_GO=True)))'''

def main():
 put('FLAT90_INSTALL_CPU_V2_CONSUMED_ACTUAL.json',dict(epoch=time.time(),new_actual_source_CPU_purpose=True,no_GO=True))
 prep=json.loads((R/'FLAT90_PAYLOAD_CORRECTED_SOURCE_PREPARED_V2_ACTUAL.json').read_bytes());manifest=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
 first=json.loads((T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89D_20261027/reports/E0_FIRST_ACTUAL_4090_PPO_V5_FULLRESTORE_CLOCK_GAS400_RETURNED_ACTUAL.json').read_bytes())
 known=[dict(pid=x['pid'],creation=x['creation']) for x in first['snapshot']['known_own_processes']]
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('flat90_secret_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec)
 secret=sec.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  resource=d.code(c,d.PY72,PRE,dict(root=REMOTE,manifest=manifest,known_own=known),timeout=120);put('FLAT90_ACTUAL_PRECOPY_RESOURCE_V2_RETURNED.json',resource)
  sf=c.open_sftp();sf.get_channel().settimeout(300)
  try:
   for row in resource['need_upload']:sf.put(str(B/row['relative']),REMOTE+'/'+row['relative'])
   sf.put(str(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),REMOTE+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
  finally:sf.close()
  result=d.code(c,d.PY72,CPU,dict(root=REMOTE,manifest_SHA=prep['manifest_SHA']),timeout=720)
  put('FLAT90_ACTUAL_SOURCE_SDK_CPU_AND_RESOURCE_V2_RETURNED_ACTUAL.json',dict(**result,resource=resource,actual_finite_returned=True))
  assert result['passed'],result
  print(json.dumps(dict(actual_CPU_passed=True,CPU_SHA=result['proof']['report_SHA'],CPU_proof_SHA=result['proof_SHA'],no_GO=True)))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('FLAT90_INSTALL_CPU_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_retry_or_GO=True));raise
