"""Read completed G1 cases and own final only; never dispatch or mutate a ledger."""
from pathlib import Path
import base64, hashlib, json, os, shlex, sys, time, traceback
D=Path(__file__).resolve().parent; W=D.parent; R=D/'reports'; R.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'))
from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003')); from remote_io import connect
sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007')); from eval_remote_io import connect_eval
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_G1_REPAIR_20261009'
CENTRAL='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007'
WIN='D:/MOD4_async_eval/closure_episode_clock2500_v15'
sha=lambda b:hashlib.sha256(b).hexdigest()
def save(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==b,('Immutable evidence differs',str(p))
 else:p.write_bytes(b)
def main():
 for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):
  value,_=recover(name);assert value,'Authorized task transport unavailable';os.environ[name]=value
 n=connect();w=connect_eval();files=[];cases={};pending=[]
 try:
  with n.open_sftp() as nf,w.open_sftp() as wf:
   def get(remote,local):
    b=nf.open(remote).read();save(R/local,b);files.append(dict(source=remote,local=local,bytes=len(b),sha256=sha(b)));return json.loads(b)
   passed=get(ROOT+'/reports/e1_G1_repair_observation_PASSED.json','own/PASSED.json')
   assert passed==get(ROOT+'/reports/e1_G1_repair_observation_SAVED_EXIT.json','own/SAVED_EXIT.json')
   ready=get(ROOT+'/reports/E1_REVIEW_READY.json','own/REVIEW_READY.json')
   freeze=get(ROOT+'/reports/SOURCE_FREEZE.json','own/SOURCE_FREEZE.json');assert len(freeze['sha256'])==321
   pubs=[get(ROOT+'/reports/E1_'+p+'_ASYNC_PUBLISHED.json','own/'+p+'_PUBLISHED.json') for p in ('117-e1-g1-anchor','118-e1-g1-repair')]
   run=passed['run'];ck=passed['checkpoint'];receipt=passed['own_PID_bound_receipt']
   assert receipt['checkpoint']==ck['path'] and ck['finite_tensors']==96 and pubs[1]['source']['sha256']==ck['sha256']
   manifest=get(run+'/run_manifest.json','own/run_manifest.json')
   rolling=get(run+'/rolling_source_freeze.json','own/rolling_source_freeze.json')
   assert rolling['sha256']==manifest['source_map']==freeze['sha256']
   assert get(run+'/latest_complete.json','own/latest_complete.json')==receipt
   for name in ('E1_TERRAIN_RESUME_STARTUP_VERIFIED','CHASSIS_PD_RESUME_STARTUP_VERIFIED','GAS_DAMPING_RESUME_STARTUP_VERIFIED','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED','ACTION_DELAY_RESUME_STARTUP_VERIFIED','CLOCK_TRAINING_HEALTH'):
    get(run+'/'+name+'.json','own/'+name+'.json')
   code="""from pathlib import Path
import hashlib,json,os,time
root=Path(ROOT);run=Path(RUN);ck=Path(CK);j=lambda p:json.loads(p.read_text())
f=j(root/'reports/SOURCE_FREEZE.json')['sha256'];m=j(run/'run_manifest.json')
assert all(hashlib.sha256((root/p).read_bytes()).hexdigest()==h for p,h in f.items())
assert all(hashlib.sha256((run/'e1_source_snapshot'/p).read_bytes()).hexdigest()==h for p,h in f.items())
assert all(hashlib.sha256((run/'src_snapshot'/p).read_bytes()).hexdigest()==h for p,h in m['src_sha256'].items())
budget=j(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'))
segments=[s for s in budget['completed_segments'] if s['pid']==PID];assert len(segments)==1
state=j(root/'reports/E1_STATE.json');guard=j(root/'reports/E1_GUARDIAN_STARTED.json')
pids=[state['owner']['pid'],guard['pid'],PID]
actual={str(pid):Path('/proc',str(pid)).exists() for pid in pids};assert not any(actual.values())
assert state['phase']=='E1_G1_repair_saved_review_ready' and state['child'] is None
print(json.dumps(dict(epoch=time.time(),checkpoint_sha256=hashlib.sha256(ck.read_bytes()).hexdigest(),source_count=len(f),snapshot_count=len(m['src_sha256']),unique_completed_segment=segments,actual_old_processes_exist=actual,state=state,canonical_total_seconds=budget['authorized_training_seconds'],canonical_active=budget['active_segment'],remaining=budget['authorized_training_seconds']-budget['charged_training_seconds'],read_only=True)))
""".replace('ROOT',repr(ROOT)).replace('RUN',repr(run)).replace('CK',repr(ck['path'])).replace('PID',str(receipt['pid']))
   _,out,err=n.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);b=out.read();e=err.read();assert out.channel.recv_exit_status()==0,(b+e).decode(errors='replace')
   proof=json.loads(b);assert proof['checkpoint_sha256']==ck['sha256'] and proof['snapshot_count']==62 and proof['unique_completed_segment']==passed['unique_completed_segment']
   save(R/'own/STATIC_OWN_SOURCE_VERIFIED.json',json.dumps(proof,indent=2).encode())
   receipts={}
   for name in ('STARTED','STATE','ATTENTION','ADMITTED'):
    remote=WIN+'/E1_CURRICULUM_INTERFACE_WORKER_'+name+'.json'
    try:b=wf.open(remote).read()
    except FileNotFoundError:receipts[name]=None;continue
    receipts[name]=json.loads(b)
   ps="$ErrorActionPreference='Stop';[pscustomobject]@{processes=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -match '^python' -and $_.CommandLine -like '*closure_episode_clock2500_v15*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}})}|ConvertTo-Json -Depth 6 -Compress"
   _,out,err=w.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=45)
   b=out.read();e=err.read();assert out.channel.recv_exit_status()==0,(b+e).decode(errors='replace')
   procs=json.loads(b)['processes'];started=receipts['STARTED']
   worker=next(p for p in procs if p['ProcessId']==started['pid'] and 'eval_worker_e1_curriculum_interface_review.py' in p['CommandLine'])
   assert abs(worker['creation_epoch']-started.get('creation_epoch',started['epoch']))<2
   workerproof=dict(epoch=time.time(),receipts=receipts,worker=worker,processes=procs,source_sha256=sha(wf.open(WIN+'/eval_worker_e1_curriculum_interface_review.py').read()))
   for pub in pubs:
    for m in pub['jobs']:
     jid=m['job_id'];folder=R/'cases'/jid
     try:b=wf.open(WIN+'/jobs/'+jid+'/result.json').read();result=json.loads(b)
     except FileNotFoundError:pending.append(dict(job_id=jid,phase='result_not_yet_generated'));continue
     if result['phase']!='complete':pending.append(dict(job_id=jid,result=result));continue
     assert result['exit_code']==0 and not result['errors'] and not result['error_files'],(jid,result)
     row={'manifest':m};save(folder/'manifest.json',json.dumps(m,indent=2).encode())
     for name in ('probe.json','result.json'):
      b=wf.open(WIN+'/jobs/'+jid+'/'+name).read();returned=nf.open(CENTRAL+'/eval_results/'+jid+'/'+name).read()
      assert b==returned,(jid,name,'bridge bytes differ');save(folder/name,b);row[name[:-5]]=json.loads(b)
      files.append(dict(source=WIN+'/jobs/'+jid+'/'+name,returned_source=CENTRAL+'/eval_results/'+jid+'/'+name,local=str((folder/name).relative_to(R)),bytes=len(b),sha256=sha(b),bridge_bytes_exact=True))
     if 'full_route_raw' in row['probe']:
      raw=row['probe']['full_route_raw'];path=folder/raw['name'];original=WIN+'/jobs/'+jid+'/'+raw['name']
      if not path.exists():wf.get(original,str(path))
      assert path.stat().st_size==raw['bytes'] and sha(path.read_bytes())==raw['sha256']
      files.append(dict(source=original,local=str(path.relative_to(R)),bytes=raw['bytes'],sha256=raw['sha256'],large_artifact_SHA_only_in_Git=True));row['raw_SHA_exact']=True
     cases[jid]=row
   v=dict(epoch=time.time(),trial_id='E1-G1-ACTUAL-REVIEW-20261010',passed=passed,publications=pubs,static_own_proof=proof,cases=cases,pending=pending,files=files,evaluator=workerproof,no_GPU_PPO_queue_or_canonical_write=True,new_budget_seconds=0)
   target=R/('COLLECTED_'+str(int(v['epoch']))+'.json');save(target,json.dumps(v,indent=2).encode())
   print(json.dumps(dict(snapshot=str(target),complete_cases=list(cases),pending=pending,current_attention=receipts['ATTENTION'],own_final=ck,unique_duration=proof['unique_completed_segment'][0],remaining=proof['remaining']),ensure_ascii=True))
 finally:
  n.close();w.close()
  for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):os.environ.pop(name,None)
if __name__=='__main__':
 try:main()
 except Exception:
  save(R/('COLLECTOR_ERROR_'+str(int(time.time()))+'.json'),json.dumps(dict(epoch=time.time(),trial_id='E1-G1-ACTUAL-COLLECTOR-01',error=traceback.format_exc(),read_only_no_production_change=True),indent=2).encode());raise
