"""Root sequential transport; first new native task only, no H1 learning launch."""
from pathlib import Path
import os,sys,json,time,hashlib,shlex,paramiko,getpass,traceback,subprocess
D=Path(__file__).resolve().parent;W=D.parent;P=D/'payload';R=D/'reports';ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name;OLD='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_HOST72_E2_MOVING4_AND_H1_JUMP_ADMISSION_20261016';PY='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v,append=False):
 p=R/n
 if append:
  q=p.with_suffix('.json.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
 else:
  with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def code(c,py,text,*args,timeout=120):
 si,so,se=c.exec_command(shlex.quote(py)+' -B - '+' '.join(shlex.quote(x) for x in args),timeout=timeout);si.write(text);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,dict(stderr=err.decode(errors='replace'),stdout=raw.decode(errors='replace')[-2000:]);return json.loads(raw)
def main():
 put('H1_NEW_FULLSTATE_NATIVE_FINITE_TRANSPORT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),creation_UTC=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Process -Id %d).StartTime.ToUniversalTime().ToString('o')"%os.getpid()]).decode().strip(),max_own_collection_seconds=900,actual_alive_only_sole_source210_target72_249_transport_owner=True,no_second_monitor=True));c=None;sf=None
 try:
  c=t.connect();v=code(c,t.PY,r'''
from pathlib import Path
import json,time,fcntl
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');b=json.loads(C.read_bytes());locks=[]
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 f=p.open('rb+')
 try:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:held=True
  else:held=False;fcntl.flock(f,fcntl.LOCK_UN)
  locks.append(dict(path=str(p),actual_held=held))
 finally:f.close()
print(json.dumps(dict(epoch=time.time(),canonical_active=b['active_segment'],authorized=b['authorized_training_seconds'],charged=b['charged_training_seconds'],remaining=b['remaining_training_seconds'],extensions=len(b['budget_extensions']),locks=locks,read_only_no_budget_write=True,H1_native_PPO0=True)))
''');put('H1_ORIGINAL_SOURCE_CANONICAL_READONLY_BEFORE_NATIVE_ACTUAL.json',v)
 finally:t.close(c)
 pw=getpass.getpass('Host72 new full20k H1 native admission password (hidden): ');c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,look_for_keys=False,allow_agent=False);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  m=json.loads((P/'PAYLOAD_H1_FULLSTATE_MANIFEST_V2.json').read_bytes());created=code(c,PY,r'''
from pathlib import Path
import sys,json,time,psutil,shutil,subprocess,fcntl
B=Path(sys.argv[1]);A=Path(sys.argv[2]);owned=Path('/home/lc01/Zonglin Li/zonglin2').resolve();assert not B.exists() and B.resolve().is_relative_to(owned)
assert (A/'NODE_EXIT_ACTUAL.json').exists();old=json.loads((A/'NODE_IDENTITY.json').read_bytes())
if psutil.pid_exists(old['pid']):
 p=psutil.Process(old['pid']);assert abs(p.create_time()-old['creation'])>.01 or p.cmdline()!=old['argv']
cal=A/'h1_flat_XYZW_fullpose_calibration_v3';assert json.loads((cal/'PARENT_FINAL.json').read_bytes())['passed'] and (cal/'PARENT_EXIT_ACTUAL.json').exists()
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(x for x in gpu.splitlines() if 'c27eecbd-6838-7290-1cd2-37e34522213d' in x);assert int(line.split(',')[-1])>=7000,line;assert psutil.virtual_memory().available>=8*1024**3 and shutil.disk_usage(owned).free>=25*1024**3
lock=owned/'state/finite_environment_validation.lock'
with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
B.mkdir();j=B/'job0';j.mkdir()
for name in ('runtime','source','assets'):
 for p in (A/'job1'/name).rglob('*'):assert p.resolve().is_relative_to(owned)
 shutil.copytree(A/'job1'/name,j/name)
shutil.copy2(A/'job1/original_run_manifest.json',j/'original_run_manifest.json');shutil.copytree(A/'lib',B/'lib')
print(json.dumps(dict(epoch=time.time(),new_root=str(B),actual_GPU1_resource=line,available_RAM=psutil.virtual_memory().available,durable_free=shutil.disk_usage(owned).free,actual_existing_validation_fcntl_free=True,old_node_and_H1_diagnostic_scope_actualclosed=True,no_GPU_or_PPO_launched_yet=True)))
''',ROOT,OLD);put('H1_ACTUAL_RESOURCE_OLD_EXIT_NEW_OWNED_ROOT_BEFORE_NATIVE.json',created)
  sf=c.open_sftp();sf.get_channel().settimeout(90);sf.put(str(P/'PAYLOAD_H1_FULLSTATE_MANIFEST_V2.json'),ROOT+'/PAYLOAD_H1_FULLSTATE_MANIFEST_V2.json')
  diff=code(c,PY,"from pathlib import Path;import json,sys,hashlib;B=Path(sys.argv[1]);m=json.loads((B/'PAYLOAD_H1_FULLSTATE_MANIFEST_V2.json').read_bytes());missing=[]\nfor r in m['files']:\n p=B/r['relative'];assert p.resolve().is_relative_to(B.resolve());\n if not p.is_file() or p.stat().st_size!=r['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=r['SHA']:missing.append(r)\nprint(json.dumps(dict(missing=missing,reused_files=len(m['files'])-len(missing))))",ROOT);put('H1_NEW_PAYLOAD_EXACT_MISSING_BYTES_ONLY_ACTUAL.json',diff)
  for row in diff['missing']:sf.put(str(P/row['relative']),ROOT+'/'+row['relative'])
  sf.close();sf=None
  verified=code(c,PY,r'''
from pathlib import Path
import sys,json,hashlib,os,time
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(sys.argv[1]);m=json.loads((B/'PAYLOAD_H1_FULLSTATE_MANIFEST_V2.json').read_bytes())
for r in m['files']:
 p=B/r['relative'];assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA'],r['relative']
sdk=Path('/home/lc01/Zonglin Li/zonglin2/src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/utils/math.py');assert hashlib.sha256(sdk.read_bytes()).hexdigest()==m['SDK_math_actual_SHA'];sys.path.insert(0,str(B));from h1_public_request_phase_v1 import H1PublicRequestPhase
s=torch.load(B/'job0/source/E0_full_source.pt',map_location='cpu',weights_only=False)
def finite(x):
 if torch.is_tensor(x):return not x.is_floating_point() or bool(torch.isfinite(x).all())
 if isinstance(x,dict):return all(finite(v) for v in x.values())
 if isinstance(x,(tuple,list)):return all(finite(v) for v in x)
 return True
assert finite(s);assert len(s['actor_state_dict'])==9 and len(s['critic_state_dict'])==8 and len(s['optimizer_state_dict']['state'])==17 and {int(v['step']) for v in s['optimizer_state_dict']['state'].values()}=={639560};p=H1PublicRequestPhase(20000,'cpu');q=H1PublicRequestPhase(20000,'cpu');q.load_state_dict(p.state_dict());assert all(torch.equal(q.tensors()[k],v) for k,v in p.tensors().items()) and not torch.cuda.is_initialized()
result=dict(epoch=time.time(),all_target_payload_SHA_exact=True,files=len(m['files']),original_E0_actor9critic8STD17Adam_fullsource_finite_step639560=True,source_SHA=hashlib.sha256((B/'job0/source/E0_full_source.pt').read_bytes()).hexdigest(),actual_SDK_XYZW_math_source_SHA_exact=True,H1_phase_actual_CPU_import_and20k_schema_passed=True,no_CUDA_or_optimizer_call=True,not_native_GPU_or_full20k_restore_pass=True);(B/'TARGET_CPU_SOURCE_SHA_ADMITTED_ACTUAL.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
''',ROOT);put('H1_ACTUAL_TARGET_CPU_FULLSOURCE_PHASE_SCHEMA_AND_ALL_PACKAGE_SHA.json',verified)
  si,so,se=c.exec_command(shlex.quote(PY)+' -u -B '+shlex.quote(ROOT+'/h1_native_finite_parent_v1.py'),timeout=35);si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();dispatch=json.loads(raw)
  actual=code(c,PY,"import sys,time,psutil,json;p=psutil.Process(int(sys.argv[1]));print(json.dumps(dict(epoch=time.time(),pid=p.pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())))",str(dispatch['detached_pid']));put('H1_FULL20K_NATIVE_ACTUAL_DURABLE_DISPATCH.json',dict(epoch=time.time(),dispatch=dispatch,actual_parent=actual,source_SHA=verified['source_SHA'],native0PPO_only=True,no_learning_lease_or_original_canonical_write=True))
  start=time.monotonic();script='ROOT='+repr(ROOT)+'\n'+r'''
from pathlib import Path
import json,time,psutil,hashlib
B=Path(ROOT);files=[]
for p in list(B.glob('*.json'))+list((B/'job0/native').glob('*.json')):
 if p.stat().st_size<15000000:
  try:files.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),value=json.loads(p.read_bytes())))
  except (OSError,ValueError):pass
scripts={str(B/n) for n in ('h1_native_finite_parent_v1.py','h1_fullstate_native_worker_v1.py','review_H1_full20k_native_allrows_CPU_v1.py')};procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(x in scripts for x in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
p=B/'worker.log';tail=''
if p.exists():
 with p.open('rb') as f:f.seek(max(0,p.stat().st_size-2000));tail=f.read().decode(errors='replace')
print(json.dumps(dict(epoch=time.time(),files=files,actual_processes=procs,parent_final=(B/'PARENT_FINAL.json').exists(),parent_exit=(B/'PARENT_EXIT_ACTUAL.json').exists(),errors=[r for r in files if 'ORIGINAL_ERROR' in r['path']],worker_tail=tail)))
'''
  while True:
   v=code(c,PY,script);put('H1_NATIVE_FINITE_LOCAL_CURRENT_ACTUAL.json',v,append=True)
   if (v['parent_exit'] and not v['actual_processes']) or time.monotonic()-start>=900:break
   time.sleep(15)
  models=[]
  if v['parent_exit'] and not v['actual_processes']:
   complete=next((x['value'] for x in v['files'] if x['path'].endswith('/NATIVE300_COMPLETE_ACTUAL.json')),None)
   if complete:
    sf=c.open_sftp();sf.get_channel().settimeout(120);outdir=D/'actual_complete_native_models';outdir.mkdir()
    for key in ('initial','saved'):
     row=complete[key];out=outdir/(key+'.pt');part=out.with_suffix('.pt.partial');sf.get(row['path'],str(part));assert part.stat().st_size==row['bytes'] and H(part)==row['SHA'];part.replace(out);models.append(dict(path=str(out.resolve()),bytes=out.stat().st_size,SHA=H(out),remote=row['path'],twohost_bytes_SHA_exact=True))
    sf.close();sf=None
  v['local_models']=models;put('H1_FULL20K_NATIVE_FINITE_ACTUAL_BOUND_COLLECTION.json',v);print(json.dumps(dict(parent_final=next((x['value'] for x in v['files'] if x['path'].endswith('/PARENT_FINAL.json')),None),errors=v['errors'],actual_processes=v['actual_processes'],complete_models=models)),flush=True)
 finally:
  pw=None
  if sf:sf.close()
  c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_FULLSTATE_NATIVE_DEPLOY_COLLECT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_relaunch_or_GPU_replay=True));raise
