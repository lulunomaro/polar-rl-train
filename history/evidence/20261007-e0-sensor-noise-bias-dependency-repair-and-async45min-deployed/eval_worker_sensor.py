"""Windows frozen evaluator: pull immutable jobs, verify, evaluate, upload evidence."""
from pathlib import Path
import base64,hashlib,json,os,subprocess,sys,time,traceback,zipfile
ROOT=Path(__file__).resolve().parent
BRIDGE_ROOT=ROOT.parent
CHUNK=262144
PY=r'D:\claude2\fangzhen\.venv-isaaclab\Scripts\python.exe'
class BridgeUnavailable(ConnectionError):pass
CLIENT=None
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(p,d):
 t=p.with_suffix(p.suffix+'.partial');t.write_text(json.dumps(d,indent=2),encoding='utf8');os.replace(t,p)
def rpc(req):
 global CLIENT
 sys.path.insert(0,str(BRIDGE_ROOT/'vendor'))
 import paramiko,socket
 try:
  if CLIENT is None or not CLIENT.get_transport() or not CLIENT.get_transport().is_active():
   if CLIENT is not None:CLIENT.close()
   CLIENT=paramiko.SSHClient();CLIENT.load_host_keys(str(BRIDGE_ROOT/'secrets/known_hosts'))
   CLIENT.set_missing_host_key_policy(paramiko.RejectPolicy())
   CLIENT.connect('10.24.4.210',username='egde',key_filename=str(BRIDGE_ROOT/'secrets/eval_ed25519'),allow_agent=False,look_for_keys=False,timeout=15,banner_timeout=15,auth_timeout=15)
  i,o,e=CLIENT.exec_command('mod4-artifact-rpc',timeout=45)
  i.write(json.dumps(req)+'\n');i.flush();i.channel.shutdown_write()
  raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc and not raw:raise BridgeUnavailable('Forced artifact request failed: '+err.decode(errors='replace')[-700:])
  d=json.loads(raw)
 except (socket.timeout,OSError,EOFError,paramiko.SSHException) as ex:
  if CLIENT is not None:CLIENT.close();CLIENT=None
  raise BridgeUnavailable('Artifact bridge transport unavailable: '+type(ex).__name__) from ex
 if not d.get('ok'):raise ValueError(d.get('error','Invalid bridge response'))
 return d['result']
def fetch(job,alias,row,p):
 if p.is_file() and sha(p)==row['sha256']:return
 part=p.with_suffix(p.suffix+'.partial');p.parent.mkdir(parents=True,exist_ok=True)
 offset=part.stat().st_size if part.is_file() else 0
 if offset>row['bytes']:raise ValueError('Oversized incomplete artifact')
 with part.open('ab') as f:
  while offset<row['bytes']:
   r=rpc({'op':'artifact_part','job_id':job,'artifact':alias,'offset':offset,'count':CHUNK})
   data=base64.b64decode(r['data']);assert r['offset']==offset and data and hashlib.sha256(data).hexdigest()==r['part_sha256']
   f.write(data);f.flush();offset+=len(data)
 assert part.stat().st_size==row['bytes'] and sha(part)==row['sha256'],'Downloaded snapshot SHA mismatch'
 os.replace(part,p)
def upload(job,p):
 status=rpc({'op':'result_status','job_id':job,'name':p.name})
 if not status['finalized']:
  offset=status['bytes']
  if offset>p.stat().st_size:raise ValueError('Result remote partial oversized')
  with p.open('rb') as f:
   f.seek(offset)
   while raw:=f.read(CHUNK):
    rpc({'op':'result_part','job_id':job,'name':p.name,'offset':offset,'data':base64.b64encode(raw).decode(),'part_sha256':hashlib.sha256(raw).hexdigest()});offset+=len(raw)
 return rpc({'op':'finalize_result','job_id':job,'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p)})
def validate_checkpoint(p):
 import torch
 d=torch.load(p,map_location='cpu',weights_only=False)
 if 'optimizer_state_dict' not in d or 'iter' not in d or not ('model_state_dict' in d or ('actor_state_dict' in d and 'critic_state_dict' in d)):raise ValueError('Incomplete checkpoint')
 count=0
 def walk(v):
  nonlocal count
  if torch.is_tensor(v) and (v.is_floating_point() or v.is_complex()):
   if not torch.isfinite(v).all():raise ValueError('Nonfinite checkpoint')
   count+=1
  elif isinstance(v,dict):
   for x in v.values():walk(x)
  elif isinstance(v,(list,tuple)):
   for x in v:walk(x)
 walk(d);model=d.get('actor_state_dict',d.get('model_state_dict',{}))
 if not any('std' in k.lower() for k in model):raise ValueError('Missing std')
 return {'iteration_stored':int(d['iter']),'finite_tensors':count,'sha256':sha(p)}

class ObservedMemoryPeak:
 def __init__(self):
  import threading
  self.event=threading.Event();self.peak=0.;self.thread=threading.Thread(target=self.loop,daemon=True)
 def loop(self):
  while not self.event.is_set():
   p=subprocess.run(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],capture_output=True,text=True,creationflags=0x08000000)
   try:self.peak=max(self.peak,float(p.stdout.strip().splitlines()[0]))
   except (ValueError,IndexError):pass
   self.event.wait(2.)
 def start(self):self.thread.start()
 def stop(self):self.event.set();self.thread.join(timeout=5)

def execute(job):
 manifest=rpc({'op':'manifest','job_id':job});folder=ROOT/'jobs'/job;folder.mkdir(parents=True,exist_ok=True)
 completion=folder/'complete.json'
 if completion.is_file():return
 if (folder/'PHYSICS_COMPLETE.json').is_file():
  result=json.loads((folder/'PHYSICS_COMPLETE.json').read_text(encoding='utf8'))
  finish_upload(job,folder,result);return
 assert manifest['immutable'] and manifest['stage']=='S0E' and manifest['kind'] in ['flat','spin','world']
 assert manifest['plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
 assert manifest['profile'] in ['nominal','white_v2','white_v3']
 assert manifest['num_envs']==(10 if manifest['steps']==300 else 80) if manifest['kind']=='flat' else manifest['num_envs']==88
 assert manifest['architecture_variant'] in ['A0','A1','A2'] and manifest['physics_dt_s']==.001
 assert manifest['steps'] in [300,1500] and 0<manifest['max_wall_seconds']<=1800
 start=time.time();atomic(folder/'manifest.json',manifest)
 for alias,row in manifest['artifacts'].items():fetch(job,alias,row,folder/(alias+'.bin'))
 transfer_done=time.time();package=folder/'runtime.bin'
 runtime=ROOT/'runtimes'/manifest['artifacts']['runtime']['sha256'];runtime.mkdir(parents=True,exist_ok=True)
 if not (runtime/'PACKAGE_READY.json').is_file():
  with zipfile.ZipFile(package) as z:
   for info in z.infolist():
    out=(runtime/info.filename).resolve()
    if not out.is_relative_to(runtime.resolve()) or info.filename.startswith(('/', '\\')) or (info.external_attr>>16)&0o170000==0o120000:raise ValueError('Unsafe runtime archive path')
   z.extractall(runtime)
  original=json.loads((runtime/'SOURCE_MANIFEST.json').read_text(encoding='utf8'))
  for name,digest in original['files'].items():assert sha(runtime/name)==digest,name
  assert sha(runtime/'assets/robot.usd')=='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87'
  cfg_path=runtime/'runtime/isaac/mod4/env.json';cfg=json.loads(cfg_path.read_text(encoding='utf8'))
  assert float(cfg['RM_PHYSICS_DT_S'])==.001 and original['clock']['decimation']==10
  cfg['RM_MOD4_USD']=str(runtime/'assets/robot.usd')
  before=cfg_path.read_bytes();atomic(cfg_path,cfg)
  atomic(runtime/'PATH_ADAPTER.json',{'only_env_key_changed':'RM_MOD4_USD','original_env_sha256':hashlib.sha256(before).hexdigest(),'adapted_env_sha256':sha(cfg_path),'no_robot_or_reward_source_changes':True})
  atomic(runtime/'PACKAGE_READY.json',{'archive_sha256':sha(package),'source_files_verified':len(original['files']),'actual_training_USD_sha256':sha(runtime/'assets/robot.usd')})
 adapter=json.loads((runtime/'PATH_ADAPTER.json').read_text(encoding='utf8'));original=json.loads((runtime/'SOURCE_MANIFEST.json').read_text(encoding='utf8'))
 for name,digest in original['files'].items():
  actual=sha(runtime/name)
  if name=='runtime/isaac/mod4/env.json':assert actual==adapter['adapted_env_sha256']
  else:assert actual==digest,name
 ck=folder/'checkpoint.bin';source=validate_checkpoint(ck);assert source['finite_tensors']>=68
 data=__import__('torch').load(ck,map_location='cpu',weights_only=False)
 variant=data.get('history_architecture',{}).get('variant','A0');assert variant==manifest['architecture_variant']
 if variant!='A0':assert data['history_architecture']['actual_updates']==275 and not data['history_architecture']['teacher_is_actor_input']
 assert source['sha256']==manifest['artifacts']['checkpoint']['sha256']
 if (folder/'ACTIVE.json').exists():raise ValueError('Prior evaluation launch has no completion receipt; audit its process and log before any replay')
 output=folder/'probe.json';log=folder/'probe.log'
 probe={'flat':'frozen_history_flat.py','spin':'frozen_history_spin.py','world':'frozen_history_world.py'}[manifest['kind']]
 args=[PY,str(runtime/'runtime/isaac/mod4'/probe),'--headless','--device','cuda:0','--checkpoint',str(ck),'--output',str(output),
  '--steps',str(manifest['steps']),'--num_envs',str(manifest['num_envs']),'--seed',str(manifest['seed']),'--dr-profile',manifest['profile']]
 if manifest['kind']=='flat':args+=['--speed_limit','1.5','--ramp_suite']
 else:args+=['--max-rate','12.566370614359172','--contact-readback']
 env={k:v for k,v in os.environ.items() if not k.startswith('RM_')}
 env.update(PYTHONPATH=str(runtime/'runtime')+os.pathsep+str(runtime/'runtime/isaac/mod4'),ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1',TMP=str(ROOT/'cache'),TEMP=str(ROOT/'cache'))
 (ROOT/'cache').mkdir(exist_ok=True)
 launch=time.time();memory=ObservedMemoryPeak();memory.start()
 with log.open('wb') as f:
  child=subprocess.Popen(args,cwd=runtime/'runtime',env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=0x08000000)
  atomic(folder/'ACTIVE.json',{'pid':child.pid,'started_epoch':launch,'job_id':job,'manifest':manifest,'checkpoint_CPU':source,'new_learning':False})
  try:rc=child.wait(timeout=manifest['max_wall_seconds'])
  except subprocess.TimeoutExpired:
   child.terminate();child.wait(timeout=30);rc=-99
 memory.stop()
 text=log.read_text(encoding='utf8',errors='replace');error_files=list(folder.glob('*.error.txt'))
 bad_lines=[l for l in text.splitlines() if any(s in l.lower() for s in ['traceback (most recent call last)','cuda out of memory','gpu collision stack overflow','physx error','nan tensor'])]
 raw=json.loads(output.read_text(encoding='utf8')) if output.is_file() else None
 result={'job_id':job,'plan_sha256':manifest['plan_sha256'],'host':'10.24.4.249','phase':'complete' if rc==0 and raw and not error_files and not bad_lines else 'retained_failed',
  'exit_code':rc,'checkpoint':source,'runtime_archive_sha256':sha(package),'probe_kind':manifest['kind'],'num_envs':manifest['num_envs'],'steps':manifest['steps'],
  'seed':manifest['seed'],'profile':manifest['profile'],'transfer_seconds':transfer_done-start,'physics_process_wall_seconds':time.time()-launch,
  'physics_dt_s':.001,'architecture_variant':variant,'observed_GPU_memory_mib':memory.peak,'memory_sampling_period_s':2.,'observed_peak_not_continuous_peak':True,
  'errors':bad_lines,'error_files':[p.name for p in error_files],'result_present':raw is not None,'formal_cross_host_equivalence_confirmed':False,'new_learning':False}
 atomic(folder/'result.json',result)
 atomic(folder/'PHYSICS_COMPLETE.json',result)
 finish_upload(job,folder,result)
def finish_upload(job,folder,result):
 for p in folder.iterdir():
  if p.is_file() and p.name not in ['manifest.json','ACTIVE.json'] and p.suffix in ['.json','.log','.txt','.npz']:upload(job,p)
 atomic(folder/'complete.json',result)
 if result['phase']=='retained_failed':raise RuntimeError('Frozen evaluation failed; retained and returned evidence')
def main():
 lock_path=BRIDGE_ROOT/'worker.lock'
 import msvcrt
 lock=lock_path.open('a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
 atomic(ROOT/'WORKER_STARTED.json',{'pid':os.getpid(),'epoch':time.time(),'role':'frozen_eval_only','canonical_write_authority':False,'GPU_concurrency':1,'uses_forced_command_key':True})
 while True:
  try:
   jobs=[j for j in rpc({'op':'list_jobs'})['jobs'] if j.startswith('clk1000-s2complete-')];atomic(ROOT/'WORKER_STATE.json',{'phase':'polling','epoch':time.time(),'pid':os.getpid(),'jobs':jobs})
   for job in jobs:execute(job)
  except BridgeUnavailable:
   atomic(ROOT/'WORKER_STATE.json',{'phase':'network_retry','epoch':time.time(),'pid':os.getpid(),'error':traceback.format_exc(),'partial_transfer_retained':True})
   time.sleep(30);continue
  except Exception:
   atomic(ROOT/'WORKER_ATTENTION.json',{'epoch':time.time(),'error':traceback.format_exc(),'no_production_process_or_budget_mutation':True})
   return 2
  time.sleep(30)
if __name__=='__main__':sys.exit(main())
