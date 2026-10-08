"""Collect returned immutable SDK evidence and actual evaluator identity; read-only."""
from pathlib import Path
import base64,hashlib,json,sys,time
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
n=connect();w=connect_eval();E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';W='D:/MOD4_async_eval/closure_episode_clock2500_v15'
try:
 with n.open_sftp() as nf,w.open_sftp() as wf:
  def get(f,path):
   try:return json.loads(f.open(path).read())
   except FileNotFoundError:return None
  authority='SDK_PREPARATION_ISOLATION'
  started=get(wf,W+'/'+authority+'_WORKER_STARTED.json');attention=get(wf,W+'/'+authority+'_WORKER_ATTENTION.json')
  held=get(wf,W+'/SDK_PREPARATION_HELD_JOBS.json')
  jobs=[];queued=[]
  for job in sorted(nf.listdir(E+'/eval_queue')):
   if not any(job.startswith('clk2500-closure-episode-d3-'+label+'-d7-') for label in ('88','89','90','91','92')) or not job.endswith('.json'):continue
   jid=job[:-5];queued.append(jid)
   manifest=get(nf,E+'/eval_queue/'+job);result=get(nf,E+'/eval_results/'+jid+'/result.json')
   if result is None:jobs.append(dict(id=jid,manifest=manifest,result=None));continue
   folder=R/'windows'/jid;folder.mkdir(parents=True,exist_ok=True)
   (folder/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
   proof={}
   for name in ('probe.json','result.json'):
    try:raw=nf.open(E+'/eval_results/'+jid+'/'+name).read(); original=wf.open(W+'/jobs/'+jid+'/'+name).read()
    except FileNotFoundError:proof[name]=dict(missing=True);continue
    assert raw==original
    (folder/name).write_bytes(raw);proof[name]=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),bridge_bytes_exact=True)
   for name in ('probe.log','probe.json.error.txt'):
    try:raw=wf.open(W+'/jobs/'+jid+'/'+name).read()
    except FileNotFoundError:continue
    (folder/name).write_bytes(raw)
   jobs.append(dict(id=jid,manifest=manifest,result=result,files=proof))
 ps="$p=@(Get-CimInstance Win32_Process|Where-Object {$_.CommandLine -like '*closure_episode_clock2500_v15*' -and $_.Name -like 'python*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}});[pscustomobject]@{processes=$p}|ConvertTo-Json -Depth 5 -Compress"
 _,o,e=w.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=30)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 processes=json.loads(raw)['processes'];identity=[p for p in processes if p['ProcessId']==started['pid'] and 'eval_worker_sdk_preparation_isolation.py' in p['CommandLine'] and abs(p['creation_epoch']-started['epoch'])<2]
 v=dict(epoch=time.time(),worker_started=started,worker_actual=identity,attention=attention,processes=processes,jobs=jobs,queued=queued,
        held_preparations=held,no_GPU_PPO_or_budget_write=True)
 (R/'D7_SDK_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(dict(epoch=v['epoch'],identity=identity,attention=attention,jobs=[dict(id=j['id'],phase=(j['result'] or {}).get('phase'),errors=(j['result'] or {}).get('errors')) for j in jobs])))
finally:w.close();n.close()
