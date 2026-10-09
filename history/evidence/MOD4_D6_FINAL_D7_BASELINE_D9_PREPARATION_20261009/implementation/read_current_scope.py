"""Read current central instructions and byte-verified frozen results; no remote mutation."""
from pathlib import Path
import json, sys, time, base64, hashlib
D=Path(__file__).resolve().parent; R=D/'reports'; R.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'))
from eval_remote_io import connect_eval
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007'
W='D:/MOD4_async_eval/closure_episode_clock2500_v15'
names=('PLAN_APPROVAL','EXECUTION_TRACKS','MOE_PLAN_EXECUTION_CURRENT','LATEST_HANDOFF',
'MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION','MOD4_PLAN_ANNOTATIONS','RM_TERRAIN_SCOPE_GIT_RECORDED','RM_TERRAIN_SCOPE_METADATA_SYNCED',
'MOD4_S2_D7_CHASSIS_COM_EXPLICIT_PD_IMPLEMENTATION','D6_CLOSEOUT_D7_FORMAL_REVIEW','D7_FULL_CONTRACT_GIT_RECORDED','D7_ACTUAL_METADATA_SYNCED','D7_EVALUATOR_CURRENT_ACTUAL','NEXT_D9_COMBINATION_WORK_ORDER')
n=connect(); w=connect_eval()
try:
 with n.open_sftp() as nf, w.open_sftp() as wf:
  def get(f,p):
   try:return json.loads(f.open(p).read())
   except FileNotFoundError:return None
  central={}
  for name in names:
   for ext in ('.json','.md'):
    try:raw=nf.open(E+'/reports/'+name+ext).read()
    except FileNotFoundError:continue
    (R/('CENTRAL_'+name+ext)).write_bytes(raw)
    central[name+ext]=hashlib.sha256(raw).hexdigest()
  jobs=[]
  prefixes=('85-d6-gas-anchor-','86-d6-gas-b','98-d7-com-pd-anchor-','99-d7-com-pd-b')
  for file in sorted(nf.listdir(E+'/eval_queue')):
   if not file.endswith('.json') or not any(file.startswith('clk2500-closure-episode-d3-'+x) for x in prefixes):continue
   jid=file[:-5]; m=get(nf,E+'/eval_queue/'+file); v=get(nf,E+'/eval_results/'+jid+'/result.json'); files={}
   target='MOD4_D6_FULL_CONTRACT_20261009' if '-d6-gas-' in jid else 'MOD4_D7_FULL_CONTRACT_20261009'
   folder=D.parent/target/'reports/stage_scope'/jid
   if v and v.get('phase')=='complete':
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'manifest.json').write_text(json.dumps(m,indent=2),encoding='utf8')
    for name in ('probe.json','result.json'):
     raw=nf.open(E+'/eval_results/'+jid+'/'+name).read()
     orig=wf.open(W+'/jobs/'+jid+'/'+name).read()
     assert raw==orig,(jid,name,'bridge bytes differ')
     (folder/name).write_bytes(raw)
     files[name]=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),bridge_bytes_exact=True,bridge_return_bytes_exact=True)
   jobs.append(dict(id=jid,manifest=m,result=v,files=files))
  authority='SDK_PREPARATION_ISOLATION'
  started=get(wf,W+'/'+authority+'_WORKER_STARTED.json')
  attention=get(wf,W+'/'+authority+'_WORKER_ATTENTION.json')
  state=get(wf,W+'/'+authority+'_WORKER_STATE.json')
 ps="$p=@(Get-CimInstance Win32_Process|Where-Object {$_.CommandLine -like '*closure_episode_clock2500_v15*' -and $_.Name -like 'python*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}});[pscustomobject]@{processes=$p}|ConvertTo-Json -Depth 5 -Compress"
 _,o,e=w.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=30)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 processes=json.loads(raw)['processes']
 identity=[p for p in processes if started and p['ProcessId']==started['pid'] and 'eval_worker_sdk_preparation_isolation.py' in p['CommandLine'] and abs(p['creation_epoch']-started['epoch'])<2]
 v=dict(epoch=time.time(),central_files=central,worker_started=started,worker_actual=identity,attention=attention,worker_state=state,processes=processes,jobs=jobs,no_GPU_PPO_or_budget_write=True)
 (R/'CURRENT_SCOPE_READ.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 for target,token in (('MOD4_D6_FULL_CONTRACT_20261009','-d6-gas-'),('MOD4_D7_FULL_CONTRACT_20261009','-d7-com-pd-')):
  subset=dict(v,jobs=[j for j in jobs if token in j['id']])
  (D.parent/target/'reports/STAGE_EVALUATOR_CURRENT_ACTUAL.json').write_text(json.dumps(subset,indent=2),encoding='utf8')
 print(json.dumps(dict(epoch=v['epoch'],central_files=list(central),worker=identity,attention=attention,jobs=[dict(id=j['id'],phase=(j['result'] or {}).get('phase'),errors=(j['result'] or {}).get('errors')) for j in jobs])))
finally:w.close();n.close()
