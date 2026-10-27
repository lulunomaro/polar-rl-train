"""One actual new E2 source copy + first target SDK CPU. No owner/GPU/ledger/GO."""
from pathlib import Path,PurePosixPath
import hashlib,importlib.util,json,os,sys,time,traceback
HERE=Path(__file__).resolve().parent;W=HERE.parents[2];L=HERE.parent;REPORTS=HERE/'reports'
JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E2_PPO50_GAS400_2610v93/e2'
GPU='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
MANIFEST=HERE/'E2_COMPLETE_INSTALL_MANIFEST_V1.json'
PRE=r"""from pathlib import Path
import os,json,subprocess,shutil,psutil,time
B=Path(v['job']);owned=Path('/home/lc01/Zonglin Li/zonglin2');tasks=owned/'tasks'
assert tasks.is_dir() and not B.parent.exists() and B.resolve().is_relative_to(tasks.resolve())
C=owned/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json';raw=C.read_bytes();c0=json.loads(raw)
assert c0['active_segment'] is None and c0['remaining_training_seconds']==546762.1692283154 and c0['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c0.get('budget_mode',c0.get('mode'))=='finite_original_limits_restored_after_single4090_return' and c0['remaining_training_seconds']>86412.86069250107
assert c0['authorized_training_seconds']==2268000 and c0['historical_budget_extension_count']==9 and c0['new_authority_budget_extensions']==[]
g=subprocess.check_output(['nvidia-smi','-i',v['GPU'],'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
c=subprocess.check_output(['nvidia-smi','-i',v['GPU'],'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
a=[x.strip() for x in g.split(',')];assert a[0]==v['GPU'] and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669 and v['GPU'] not in c
assert psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(tasks).free>25*1024**3
B.parent.mkdir();B.mkdir()
print(json.dumps(dict(passed=True,job_root=str(B),GPU_line=g,selected_compute_UUID_rows=0,RAM_available=psutil.virtual_memory().available,disk_free=shutil.disk_usage(tasks).free,epoch=time.time(),no_account_or_GPU_load=True,canonical_None=True,remaining=c0['remaining_training_seconds'],canonical_SHA=__import__('hashlib').sha256(raw).hexdigest())))
"""
VERIFY_AND_CPU=r"""from pathlib import Path
import os,json,hashlib,time,subprocess,psutil,importlib.metadata as md
B=Path(v['job']);assert B.is_dir()
def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(name,value):
 with (B/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
assert H(B/'E2_COMPLETE_INSTALL_MANIFEST_V1.json')=='0e27157ce13a88748504c02a5702b7d6027ca14ca3224e4c6d4d5bcbe52175fd'
manifest=json.loads((B/'E2_COMPLETE_INSTALL_MANIFEST_V1.json').read_bytes())
rows=[]
for r in v['rows']:
 p=(B/r['relative']).resolve();assert p.is_relative_to(B.resolve()) and not p.is_symlink() and p.stat().st_size==r['bytes'] and H(p)==r['SHA']
 rows.append(r)
put('E2_ACTUAL_POSTCOPY_ALL_SOURCE_SHA_VERIFIED.json',dict(passed=True,files=rows,one_actual_deployment_integrity_read=True,no_model_deserialization_yet=True))
dep=manifest['dependency_install_receipt_required'].copy();dep['job_root']=str(B);dep['actual_postcopy_fullSHA_verified']=True
put('E2_INSTALLED_BINARY_DEPENDENCIES_VERIFIED.json',dep)
import subprocess
line=subprocess.check_output(['nvidia-smi','-i',v['GPU'],'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
apps=subprocess.check_output(['nvidia-smi','-i',v['GPU'],'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
fields=[x.strip() for x in line.split(',')];assert fields[0]==v['GPU'] and fields[1]=='NVIDIA GeForce RTX 4090' and int(fields[2])>15669 and v['GPU'] not in apps
assert psutil.virtual_memory().available>8*1024**3 and __import__('shutil').disk_usage(B).free>25*1024**3
postcopy=dict(epoch=time.time(),GPU_UUID=v['GPU'],GPU_name=fields[1],GPU_line=line,compute_UUID_only_rows=0,RAM_available=psutil.virtual_memory().available,disk_free=__import__('shutil').disk_usage(B).free,no_unknown_PID_inspection=True,no_GPU_import=True)
put('E2_POSTCOPY_SELECTED_UUID_RESOURCE_ACTUAL.json',postcopy)
versions={k:md.version(k) for k in ['torch','isaacsim','isaaclab','rsl-rl-lib']}
assert versions=={'torch':'2.10.0+cu128','isaacsim':'6.0.1.0','isaaclab':'6.1.14','rsl-rl-lib':'5.0.1'}
env=dict(os.environ)
for n in ['home','tmp','cache','config','data']:(B/n).mkdir()
env.update(CUDA_VISIBLE_DEVICES='',HOME=str(B/'home'),TMPDIR=str(B/'tmp'),XDG_CACHE_HOME=str(B/'cache'),XDG_CONFIG_HOME=str(B/'config'),XDG_DATA_HOME=str(B/'data'),PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1')
argv=['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(B/'E2_target_source_SDK_CPU_admission_v1.py'),'--job-root',str(B)]
with (B/'E2_SOURCE_SDK_CPU_CONSOLE.log').open('xb') as log:
 child=subprocess.Popen(argv,env=env,cwd=B,stdout=log,stderr=subprocess.STDOUT)
 q=psutil.Process(child.pid);identity=dict(pid=child.pid,exe=q.exe(),argv=q.cmdline(),creation=q.create_time(),root=q.cwd())
 put('E2_SOURCE_CPU_OWNED_PROCESS_ACTUAL.json',identity)
 # A CPU reader timeout is recorded; only this exact owned handle is terminated/waited.
 timeout_error=False
 try:rc=child.wait(timeout=90)
 except subprocess.TimeoutExpired:
  timeout_error=True;child.terminate()
  try:rc=child.wait(timeout=10)
  except subprocess.TimeoutExpired:child.kill();rc=child.wait(timeout=10)
report=B/'E2_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json'
proof=dict(actual_waited=True,returncode=rc,timeout_original_error=timeout_error,actual_identity=identity,job_root=str(B),source_SHA=v['source_SHA'],worker_SHA=v['worker_SHA'],execution_backend='target72',report_SHA=H(report) if report.is_file() else None)
put('E2_SOURCE_CPU_WAITED_ACTUAL_V1.json',proof)
small={n:dict(text=(B/n).read_text(),SHA=H(B/n)) for n in ['E2_ACTUAL_POSTCOPY_ALL_SOURCE_SHA_VERIFIED.json','E2_INSTALLED_BINARY_DEPENDENCIES_VERIFIED.json','E2_SOURCE_CPU_WAITED_ACTUAL_V1.json','E2_SOURCE_CPU_OWNED_PROCESS_ACTUAL.json','E2_SOURCE_SDK_CPU_CONSOLE.log','E2_POSTCOPY_SELECTED_UUID_RESOURCE_ACTUAL.json']}
for p in sorted(B.glob('E2_SOURCE_SDK_CPU_*ACTUAL*.json')):
 if p.name not in small:small[p.name]=dict(text=p.read_text(),SHA=H(p))
for p in sorted(B.glob('E2_SOURCE_SDK_CPU_ORIGINAL_ERROR*.json')):
 small[p.name]=dict(text=p.read_text(),SHA=H(p))
print(json.dumps(dict(passed=rc==0 and report.is_file(),actual_finite_returned=True,actual_returncode=rc,job_root=str(B),versions=versions,source_CPU_SHA=proof['report_SHA'],CPU_waited_proof_SHA=H(B/'E2_SOURCE_CPU_WAITED_ACTUAL_V1.json'),small_reports=small,no_GPU_scene_or_GO_or_owner_or_ledger=True)))
"""
def save(n,v):
 with (REPORTS/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert len(sys.argv)==1
 save('E2_EXISTING72_SOURCE_SDK_CPU_ENTERED_ACTUAL_V1.json',dict(epoch=time.time(),own_pid=os.getpid(),script=str(Path(__file__).resolve()),new_unused_job=JOB,no_GPU_GO_or_account=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('same_authorized72_memory_recovery_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec)
 sp=importlib.util.spec_from_file_location('E2_same_authorized_compressed_transport_install_only',W/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);transport,previous=m.install()
 secret=sec.recover();client=None
 try:
  client=d.connect72(secret);secret=None
  pre=d.code(client,d.PY72,PRE,dict(job=JOB,GPU=GPU),timeout=30);save('E2_EXISTING72_PREINSTALL_RESOURCE_ACTUAL_V1.json',pre)
  assert hashlib.sha256(MANIFEST.read_bytes()).hexdigest()=='0e27157ce13a88748504c02a5702b7d6027ca14ca3224e4c6d4d5bcbe52175fd'
  manifest=json.loads(MANIFEST.read_bytes());rows=[]
  for r in manifest['files']:rows.append(dict(local=r['local_path'],relative=r['relative'],bytes=r['bytes'],SHA=r['SHA']))
  sftp=client.open_sftp();sftp.get_channel().settimeout(30);made={JOB};started=time.time()
  try:
   def upload(src,relative):
    p=PurePosixPath(JOB)/relative;assert '..' not in p.parts and str(p).startswith(JOB+'/')
    parent=p.parent;chain=[]
    while str(parent) not in made:chain.append(parent);parent=parent.parent
    for q in reversed(chain):sftp.mkdir(str(q),mode=0o700);made.add(str(q))
    with Path(src).open('rb') as inp,sftp.open(str(p),'wx') as out:
     out.set_pipelined(True)
     while True:
      raw=inp.read(1024*1024)
      if not raw:break
      assert time.time()-started<90,'finite_source_upload_timeout'
      out.write(raw)
   for r in rows:upload(r['local'],r['relative'])
   upload(MANIFEST,'E2_COMPLETE_INSTALL_MANIFEST_V1.json')
  finally:sftp.close()
  save('E2_EXISTING72_SOURCE_UPLOAD_FINISHED_ACTUAL_V1.json',dict(files=len(rows),elapsed_seconds=time.time()-started,job_root=JOB,no_model_deserialization_by_uploader=True))
  result=d.code(client,d.PY72,VERIFY_AND_CPU,dict(job=JOB,rows=[{k:r[k] for k in ['relative','bytes','SHA']} for r in rows],GPU=GPU,source_SHA='5b5d1ee88bf9f56f865378d82d9f8864fa5ec2859f636c9b33b07558323d7f6e',worker_SHA='6945d96b88da874a7c83311620b3a329366d33c9a5c97c887510223241f0754e'),timeout=135)
  for name,r in result.pop('small_reports').items():
   assert PurePosixPath(name).name==name and hashlib.sha256(r['text'].encode()).hexdigest()==r['SHA']
   with (REPORTS/name).open('x',encoding='utf8',newline='') as f:f.write(r['text'])
  result['epoch']=time.time();save('E2_EXISTING72_SOURCE_SDK_CPU_RETURNED_ACTUAL_V1.json',result);print(json.dumps(result))
 finally:
  secret=None
  if client:client.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:save('E2_EXISTING72_SOURCE_SDK_CPU_ORIGINAL_ERROR_ACTUAL_V1.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry_GPU_GO_owner_or_account=True));raise
