"""Read exact central approvals/current evidence and completed D6 returned scope."""
from pathlib import Path
import json,sys,time,base64,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
n=connect();w=connect_eval();E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';W='D:/MOD4_async_eval/closure_episode_clock2500_v15'
names=('PLAN_APPROVAL','EXECUTION_TRACKS','MOE_PLAN_EXECUTION_CURRENT','LATEST_HANDOFF','D6_MATCHED_D5_RETENTION_D7_PREPARATION_REVIEW','D6_MATCHED_D5_RETENTION_D7_PREPARATION_GIT_RECORDED','D6_MATCHED_D5_RETENTION_D7_METADATA_SYNCED','D7_COM_ROUNDTRIP_PD_ADAPTER_REVIEW','D7_COM_ROUNDTRIP_PD_ADAPTER_GIT_RECORDED','D7_COM_ROUNDTRIP_PD_METADATA_SYNCED','D7_ACTUAL_INTERFACE_SCOPE_REVIEW','NEXT_D7_FULL_LEARNING_WORK_ORDER')
try:
 with n.open_sftp() as nf,w.open_sftp() as wf:
  def get(f,p):
   try:return json.loads(f.open(p).read())
   except FileNotFoundError:return None
  central={}
  for name in names:
   for ext in ('.json','.md'):
    try:raw=nf.open(E+'/reports/'+name+ext).read()
    except FileNotFoundError:continue
    (R/('CENTRAL_'+name+ext)).write_bytes(raw);central[name+ext]=hashlib.sha256(raw).hexdigest()
  jobs=[]
  for file in sorted(nf.listdir(E+'/eval_queue')):
   if not file.endswith('.json') or not any(file.startswith('clk2500-closure-episode-d3-'+x) for x in ('85-d6-gas-anchor-','86-d6-gas-b')):continue
   jid=file[:-5];m=get(nf,E+'/eval_queue/'+file);v=get(nf,E+'/eval_results/'+jid+'/result.json');folder=D.parent/'MOD4_D6_FULL_CONTRACT_20261009/reports/windows'/jid;folder.mkdir(parents=True,exist_ok=True)
   files={}
   if v:
    for name in ('probe.json','result.json'):
     raw=nf.open(E+'/eval_results/'+jid+'/'+name).read();orig=wf.open(W+'/jobs/'+jid+'/'+name).read();assert raw==orig
     (folder/name).write_bytes(raw);files[name]=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),bridge_bytes_exact=True)
   jobs.append(dict(id=jid,manifest=m,result=v,files=files))
  authority='SDK_PREPARATION_ISOLATION';started=get(wf,W+'/'+authority+'_WORKER_STARTED.json');attention=get(wf,W+'/'+authority+'_WORKER_ATTENTION.json')
 ps="$p=@(Get-CimInstance Win32_Process|Where-Object {$_.CommandLine -like '*closure_episode_clock2500_v15*' -and $_.Name -like 'python*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}});[pscustomobject]@{processes=$p}|ConvertTo-Json -Depth 5 -Compress"
 _,o,e=w.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');processes=json.loads(raw)['processes']
 identity=[p for p in processes if p['ProcessId']==started['pid'] and 'eval_worker_sdk_preparation_isolation.py' in p['CommandLine'] and abs(p['creation_epoch']-started['epoch'])<2]
 v=dict(epoch=time.time(),central_files=central,worker_started=started,worker_actual=identity,attention=attention,processes=processes,jobs=jobs,no_GPU_PPO_or_budget_write=True)
 (D.parent/'MOD4_D6_FULL_CONTRACT_20261009/reports/STAGE_EVALUATOR_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 (R/'CURRENT_PLAN_D6_SCOPE_READ.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(dict(epoch=v['epoch'],central_files=list(central),worker=identity,attention=attention,jobs=[dict(id=j['id'],phase=(j['result'] or {}).get('phase'),errors=(j['result'] or {}).get('errors')) for j in jobs])))
finally:w.close();n.close()
