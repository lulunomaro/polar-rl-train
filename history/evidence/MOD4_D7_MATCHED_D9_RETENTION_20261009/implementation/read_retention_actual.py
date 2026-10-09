"""Reusable read-only collection of the 18 actual D9 development cases."""
from pathlib import Path
import sys,json,hashlib,time,base64
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
n=connect();w=connect_eval();E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';W='D:/MOD4_async_eval/closure_episode_clock2500_v15';root='/home/egde/rl_candidates/MOD4_D9_COMBINATION_PREPARE_20261009'
try:
 with n.open_sftp() as nf,w.open_sftp() as wf:
  pub=json.loads(nf.open(root+'/reports/PUBLISHED.json').read());assert pub['total_development_conditions']==18 and len(pub['fifteen_new_cases'])==15 and len(pub['three_exact_cases_reused'])==3
  h=pub['source']['source']['sha256'];rows=[]
  ids=pub['three_exact_cases_reused']+[x['job_id'] for x in pub['fifteen_new_cases']]
  for jid in ids:
   raw=nf.open(E+'/eval_queue/'+jid+'.json').read();m=json.loads(raw)
   assert m['no_learning'] and not m['canonical_write_authority'] and m['artifacts']['checkpoint']['sha256']==h
   assert m['seed'] in (20261002,20261003) and m['profile'] in ('nominal','white_v2','white_v3') and m['kind'] in ('flat','spin','world')
   assert m['steps']==1500 and m['num_envs']==(80 if m['kind']=='flat' else 88)
   try:res=json.loads(nf.open(E+'/eval_results/'+jid+'/result.json').read())
   except FileNotFoundError:res=None
   files={}
   if res and res.get('phase')=='complete':
    assert res['exit_code']==0 and not res['errors'] and not res['error_files']
    assert res['checkpoint']['sha256']==h and res['runtime_archive_sha256']==m['artifacts']['runtime']['sha256']
    folder=R/'retention_scope'/jid;folder.mkdir(parents=True,exist_ok=True);(folder/'manifest.json').write_bytes(raw)
    for name in ('probe.json','result.json'):
     data=nf.open(E+'/eval_results/'+jid+'/'+name).read();assert data==wf.open(W+'/jobs/'+jid+'/'+name).read();(folder/name).write_bytes(data)
     files[name]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),bridge_return_bytes_exact=True)
   rows.append(dict(job_id=jid,seed=m['seed'],profile=m['profile'],kind=m['kind'],source_sha256=h,runtime_sha256=m['artifacts']['runtime']['sha256'],reused=jid in pub['three_exact_cases_reused'],result=res,files=files))
  assert len({(r['seed'],r['profile'],r['kind']) for r in rows})==18
  state={}
  for name in ('SDK_PREPARATION_ISOLATION_WORKER_STARTED.json','SDK_PREPARATION_ISOLATION_WORKER_STATE.json','SDK_PREPARATION_ISOLATION_WORKER_ATTENTION.json'):
   try:state[name]=json.loads(wf.open(W+'/'+name).read())
   except FileNotFoundError:state[name]=None
  ps="$ErrorActionPreference='Stop'; @(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^python' -and $_.CommandLine -like '*closure_episode_clock2500_v15*'} | ForEach-Object {[pscustomobject]@{ProcessId=$_.ProcessId;ParentProcessId=$_.ParentProcessId;CommandLine=$_.CommandLine;creation_epoch=([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}}) | ConvertTo-Json -Compress"
  _,o,e=w.exec_command('powershell -NoProfile -EncodedCommand '+base64.b64encode(ps.encode('utf-16-le')).decode(),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
  processes=json.loads(raw) if raw.strip() else [];processes=processes if isinstance(processes,list) else [processes]
  completed=sum(bool(r['result'] and r['result'].get('phase')=='complete') for r in rows)
  v=dict(epoch=time.time(),source_sha256=h,published=pub,actual_processes=processes,worker_receipts=state,cases=rows,completed_conditions=completed,pending_conditions=18-completed,actual_manifest_conditions_unique=True,development_not_clean_or_heldout=True,no_GPU_PPO_canonical_or_launch_mutation=True)
  (R/'D9_RETENTION_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
  print(json.dumps(dict(epoch=v['epoch'],completed=completed,pending=18-completed,actual_processes=processes,attention=state['SDK_PREPARATION_ISOLATION_WORKER_ATTENTION.json'],new_GPU_or_training_transactions=0)))
finally:w.close();n.close()
