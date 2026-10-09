"""Collect new120 frozen results only when actual complete, with bridge-byte/raw SHA proof."""
from pathlib import Path
import base64,hashlib,json,os,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';sha=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
WIN='D:/MOD4_async_eval/closure_episode_clock2500_v15';E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007'
def save(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==b,str(p)
 else:p.write_bytes(b)
def main():
 for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):
  secret,_=recover(name);assert secret;os.environ[name]=secret
 n=connect();w=connect_eval();cases={};pending=[];files=[]
 try:
  with n.open_sftp() as nf,w.open_sftp() as wf:
   try:attention=json.loads(wf.open(WIN+'/E1_G3_PACKAGE_REVIEW_WORKER_ATTENTION.json').read())
   except FileNotFoundError:attention=None
   ps="[pscustomobject]@{processes=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -match '^python' -and $_.CommandLine -like '*closure_episode_clock2500_v15*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}})}|ConvertTo-Json -Depth 6 -Compress"
   _,o,e=w.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');procs=json.loads(raw)['processes']
   started=json.loads(wf.open(WIN+'/E1_G3_PACKAGE_REVIEW_WORKER_STARTED.json').read());worker=[p for p in procs if p['ProcessId']==started['pid'] and 'eval_worker_e1_g3_package_review.py' in p['CommandLine'] and abs(p['creation_epoch']-started.get('creation_epoch',started['epoch']))<2]
   actual=json.loads(sorted(R.glob('G3_ACTUAL_*.json'))[-1].read_bytes());published=actual['reports'].get('E1_127-e1-g3-observation_ASYNC_PUBLISHED.json')
   if not published:pending.append(dict(phase='awaiting_own_formal_fullsave_and_publication'))
   for m in published['jobs'] if published else []:
    jid=m['job_id'];folder=R/'cases'/jid
    try:r=json.loads(wf.open(WIN+'/jobs/'+jid+'/result.json').read())
    except FileNotFoundError:pending.append(dict(job_id=jid,phase='result_not_yet_generated'));continue
    if r['phase']!='complete' or r['exit_code'] or r['errors'] or r['error_files']:pending.append(dict(job_id=jid,result=r,not_passed=True));continue
    row={'manifest':m};save(folder/'manifest.json',json.dumps(m,indent=2).encode())
    for name in ('probe.json','result.json'):
     raw=wf.open(WIN+'/jobs/'+jid+'/'+name).read();returned=nf.open(E+'/eval_results/'+jid+'/'+name).read();assert raw==returned,(jid,name,'bridge bytes differ')
     save(folder/name,raw);row[name[:-5]]=json.loads(raw);files.append(dict(job_id=jid,name=name,bytes=len(raw),sha256=sha(raw),Windows_source=WIN+'/jobs/'+jid+'/'+name,returned_source=E+'/eval_results/'+jid+'/'+name,bridge_bytes_exact=True))
    if 'full_route_raw' in row['probe']:
     info=row['probe']['full_route_raw'];p=folder/info['name']
     if not p.exists():wf.get(WIN+'/jobs/'+jid+'/'+info['name'],str(p))
     assert p.stat().st_size==info['bytes'] and sha(p.read_bytes())==info['sha256'];row['raw_SHA_exact']=True
     files.append(dict(job_id=jid,path=str(p.resolve()),source=WIN+'/jobs/'+jid+'/'+info['name'],bytes=info['bytes'],sha256=info['sha256'],large_original_index_only=True))
    cases[jid]=row
   report=dict(epoch=time.time(),trial_id='E1-G3-300S-127-ACTUAL-COLLECT-01',cases=cases,pending=pending,files=files,passed=actual['reports'].get('e1_G3_reviewed_observation_PASSED.json'),current_attention=attention,worker_actual=worker,processes=procs,no_learning_or_canonical_or_queue_write=True,new_budget_seconds=0)
   p=R/('CANDIDATE_127_COLLECTED_'+str(int(report['epoch']))+'.json');save(p,json.dumps(report,indent=2).encode());print(json.dumps(dict(report=str(p),complete=list(cases),pending=pending,attention=attention,processes=procs),ensure_ascii=True))
 finally:
  n.close();w.close()
  for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):os.environ.pop(name,None)
if __name__=='__main__':
 try:main()
 except Exception:
  save(R/('CANDIDATE_127_COLLECT_ERROR_'+str(int(time.time()))+'.json'),json.dumps(dict(epoch=time.time(),trial_id='E1-G3-300S-127-ACTUAL-COLLECT-01',error=traceback.format_exc(),read_only=True),indent=2).encode());raise
