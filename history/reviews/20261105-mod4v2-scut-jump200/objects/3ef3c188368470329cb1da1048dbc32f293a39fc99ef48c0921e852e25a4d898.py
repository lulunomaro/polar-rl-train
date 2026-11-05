"""One direct Newton launch/FIRST and its sole formal postround receiver."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,time,traceback
from shared_control_access import connection
N=Path(__file__).resolve().parent
CONTROL='C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda raw:hashlib.sha256(raw).hexdigest()
A=R=None

def put(name,value):
 with(R/name).open('x',encoding='utf8')as f:json.dump(value,f,indent=2)

READ=r'''from pathlib import Path
import json,time,hashlib,psutil
j=Path(v['job']);out={}
names=['GO_PRODUCTION.json','ROOT_ADMISSION_ACTUAL.json','OWNER_STARTED.json','OWNER_CURRENT.json',
 'WORKER_IDENTITY.json','OWNER_ERROR.json','OWNER_EXIT.json','TRAIN_CLOSED.json','EVAL_WAITED.json',
 'production/STARTUP.json','production/FULL_STATE_RESTORE.json','production/FIRST_UPDATED.json',
 'production/LATEST_PROGRESS.json','production/FINAL.json','production/ERROR.json','production/APP_CLOSE_INTENT.json',
 'evaluation/RESULT.json','evaluation/NATIVE_STARTUP.json','evaluation/APP_CLOSE_INTENT.json','evaluation/ERROR.json']
for name in names:
 p=j/name
 if p.exists():
  try:out[name]=json.loads(p.read_bytes())
  except json.JSONDecodeError:pass
closed='OWNER_EXIT.json'in out
first='production/FIRST_UPDATED.json'in out
for name in ['OWNER.log','WORKER.log','EVAL.log']:
 p=j/name
 if p.exists():
  raw=p.read_bytes();full=closed or(name=='WORKER.log'and first)
  out[name]=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),
                 complete=full,text=(raw if full else raw[-5000:]).decode('utf8','replace'))
if closed and v.get('full'):
 for name in ['evaluation/ALL80.json','evaluation/CONTROL_CURVES.json']:
  p=j/name
  if p.exists():out[name]=json.loads(p.read_bytes())
owner=out.get('OWNER_STARTED.json',{}).get('identity',{})
alive=False
if owner and psutil.pid_exists(owner['pid']):
 p=psutil.Process(owner['pid']);alive=p.create_time()==owner['creation'] and p.status()!=psutil.STATUS_ZOMBIE
print(json.dumps(dict(epoch=time.time(),files=out,exact_owner_alive=alive)))'''

def launch():
 assert not(R/'LAUNCH_ONCE.json').exists()
 plan=read(A/'PLAN.json');job=plan['remote_root'];prepared=read(A/'SOURCE_PREPARED.json')
 with connection(R,'NEWTON_FRESH_DIRECT_LAUNCH')as(c,t):
  code='''from pathlib import Path
import json,subprocess,time,psutil,shutil
b=Path('/home/lc01/Zonglin Li/zonglin2')
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,name,memory.free,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True)
print(json.dumps(dict(epoch=time.time(),gpu=gpu,apps=apps,ram=psutil.virtual_memory().available,disk=shutil.disk_usage(b).free,canonical_reads=0,canonical_writes=0)))'''
  resource=t.code(c,t.PY72,code,{},timeout=40);put('FRESH_RESOURCE_ADMISSION.json',resource)
  choices=[]
  for line in resource['gpu'].splitlines():
   row=[x.strip()for x in line.split(',')]
   if row[1]=='NVIDIA GeForce RTX 4090'and int(row[2])>15669 and row[0]not in resource['apps']:choices.append((int(row[2]),row[0]))
  assert choices and resource['ram']>64*1024**3 and resource['disk']>50*1024**3
  plan['GPU_UUID']=max(choices)[1];(A/'PLAN.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
  rows=list(prepared['files']);raw=(A/'PLAN.json').read_bytes()
  rows.append(dict(path=str(A/'PLAN.json'),relative='PLAN.json',bytes=len(raw),SHA=H(raw)))
  for row in rows:assert H(Path(row['path']).read_bytes())==row['SHA']
  put('LAUNCH_ONCE.json',dict(epoch=time.time(),root=job,source_SHA=plan['source_checkpoint']['SHA']))
  t.code(c,t.PY72,"from pathlib import Path;import json;p=Path(v['job']);p.mkdir(exist_ok=False);print(json.dumps(dict(created=str(p))))",dict(job=job),timeout=30)
  sf=c.open_sftp()
  try:
   for row in rows:
    cursor=job
    for part in row['relative'].split('/')[:-1]:
     cursor+='/'+part
     try:sf.mkdir(cursor)
     except OSError:sf.stat(cursor)
    with sf.file(job+'/'+row['relative'],'wx')as f:f.write(Path(row['path']).read_bytes());f.flush()
   manifest=dict(files=[{k:r[k]for k in ['relative','bytes','SHA']}for r in rows],shared_text=prepared['shared_text'])
   with sf.file(job+'/INSTALL_MANIFEST.json','wx')as f:f.write(json.dumps(manifest,indent=2).encode());f.flush()
   sf.chmod(job+'/run-newton.sh',0o700)
  finally:sf.close()
  with(A/'INDEX_SOURCE_FROZEN.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),files=rows,shared_text=prepared['shared_text']),f,indent=2)
  start='''from pathlib import Path
import subprocess,json,psutil,time
j=Path(v['job'])
with(j/'OWNER.log').open('xb')as f:
 p=subprocess.Popen([str(j/'run-newton.sh'),'-u','-B',str(j/'owner.py')],cwd=j,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
q=psutil.Process(p.pid);print(json.dumps(dict(epoch=time.time(),pid=p.pid,creation=q.create_time())))'''
  owner=t.code(c,t.PY72,start,dict(job=job),timeout=30);put('OWNER_LAUNCH.json',owner)
  put('FIRST_ONCE.json',dict(epoch=time.time(),owner=owner,read_only=True))
  for count in range(100):
   result=t.code(c,t.PY72,READ,dict(job=job),timeout=40);f=result['files']
   if 'production/FIRST_UPDATED.json'in f or 'production/FINAL.json'in f or 'OWNER_EXIT.json'in f:break
   if count%4==0:print(json.dumps(dict(wait=count,files=list(f),tail=f.get('WORKER.log',{}).get('text','')[-1200:])),flush=True)
   time.sleep(15)
  else:put('FIRST_PENDING.json',result);raise RuntimeError('Original Newton owner still responsible, no duplicate launch')
  put('FIRST_ACTUAL_RETURNED.json',result)
 f=result['files'];first=f.get('production/FIRST_UPDATED.json',{});restore=f.get('production/FULL_STATE_RESTORE.json',{})
 if plan.get('learner')=='SuperMimic':
  valid=bool(first.get('verified_BPTT')and first.get('full_save')and first.get('horizon')==32
      and first.get('bptt',{}).get('verified_bptt_optimizer_step')
      and first.get('bptt',{}).get('wm_path_grad_norm',0)>0
      and f.get('production/STARTUP.json',{}).get('reward_family')=='FUDAN_JUMP'
      and not f.get('production/ERROR.json'))
 else:
  source_iteration=plan['source_checkpoint']['iteration']
  valid=bool(first.get('iteration')==source_iteration+1 and first.get('actual_onpolicy_samples')==480000
     and first.get('gradient',{}).get('steps')==20 and first['gradient']['actor_norm']>0 and first['gradient']['critic_norm']>0
     and restore.get('optimizer_steps')==source_iteration*20 and restore.get('all7_components_and_RNG_queues_restored')
     and f.get('production/STARTUP.json',{}).get('actual_Newton_MuJoCo_Warp')and not f.get('production/ERROR.json'))
 put('FIRST_VALIDATION.json',dict(epoch=time.time(),valid=valid,FIRST=first,restore=restore))
 if not valid:
  # The original owner still controls fullsave/close/eval. Bind its only
  # receiver even if no verified BPTT step occurred; do not lose the final.
  put('FIRST_NOT_VALID_KEEP_ORIGINAL_OWNER.json',dict(epoch=time.time(),files=list(f),valid=False))
 put('POSTROUND_BIND_ONCE.json',dict(epoch=time.time()))
 with(R/'POSTROUND_STDOUT.log').open('xb')as out,(R/'POSTROUND_STDERR.log').open('xb')as err:
  p=subprocess.Popen([CONTROL,'-B','-X','utf8',str(Path(__file__)),'collect','--root',str(A)],
       cwd=N,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
 query='Get-CimInstance Win32_Process -Filter "ProcessId = '+str(p.pid)+'" | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json'
 cim=subprocess.check_output(['pwsh','-NoProfile','-Command',query],text=True,encoding='utf8')
 put('POSTROUND_EXACT_CIM.json',dict(epoch=time.time(),row=json.loads(cim)))
 print(json.dumps(dict(valid_FIRST=first,collector=read(R/'POSTROUND_EXACT_CIM.json'))),flush=True)

def collect():
 put('POSTROUND_ONCE.json',dict(epoch=time.time(),pid=os.getpid()))
 plan=read(A/'PLAN.json');job=plan['remote_root']
 go=read(R/'FIRST_ACTUAL_RETURNED.json')['files']['GO_PRODUCTION.json']
 already_closed='OWNER_EXIT.json'in read(R/'FIRST_ACTUAL_RETURNED.json')['files']
 while not already_closed and time.time()<go['save_deadline']+45:time.sleep(min(10.,go['save_deadline']+45-time.time()))
 with connection(R,'NEWTON_FORMAL_POSTROUND_RETURN')as(c,t):
  for count in range(90):
   result=t.code(c,t.PY72,READ,dict(job=job,full=True),timeout=60)
   if 'OWNER_EXIT.json'in result['files']and not result['exact_owner_alive']:break
   time.sleep(10)
  else:put('POSTROUND_PENDING.json',result);raise RuntimeError('Original owner still responsible; receiver incomplete')
  put('POSTROUND_FULL_RETURNED.json',result)
  f=result['files']
  if f['OWNER_EXIT.json']['error']:
   assert f['OWNER_EXIT.json']['all_own_waited']and f['OWNER_EXIT.json']['original_leases_released']
   put('POSTROUND_FAILED_COMPLETED.json',dict(epoch=time.time(),complete_failure_return=True,
       passed_training=False,owner=f['OWNER_EXIT.json'],original_errors_preserved=True))
   print(json.dumps(dict(completed_failure_return=True,owner=f['OWNER_EXIT.json'])),flush=True)
   return
  assert f['TRAIN_CLOSED.json']['passed_execution']
  assert f.get('evaluation/RESULT.json',{}).get('passed_execution')
  sf=c.open_sftp();rows=[]
  try:
   refs=[f['production/FINAL.json']['checkpoint'],f['evaluation/RESULT.json']['all80_manifold'],f['evaluation/RESULT.json']['actual_poses']]
   for row in refs:
    target=A/('production'if row['path'].endswith('.pt')else'evaluation')/Path(row['path']).name
    target.parent.mkdir(exist_ok=True);assert not target.exists()
    sf.get(row['path'],str(target))
    with target.open('rb')as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
    assert sha==row['SHA'] and target.stat().st_size==row['bytes']
    rows.append(dict(row,local_path=str(target),SHA_verified=True))
  finally:sf.close()
  put('FORMAL_TRANSFERS.json',dict(epoch=time.time(),files=rows))
 put('POSTROUND_COMPLETED.json',dict(epoch=time.time(),complete=True))
 print(json.dumps(dict(completed=True,result=f['evaluation/RESULT.json'])),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['launch','collect']);p.add_argument('--root',type=Path,required=True);a=p.parse_args()
 A=a.root.resolve();assert A.is_relative_to(N);R=A/'reports'
 try:globals()[a.mode]()
 except BaseException:put('CONTROL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
