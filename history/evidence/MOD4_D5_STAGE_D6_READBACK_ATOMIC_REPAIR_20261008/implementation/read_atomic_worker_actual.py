"""Read new worker identity, demand-task triggers and actual candidate progress."""
from pathlib import Path
import sys,json,base64,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect_eval();root='D:/MOD4_async_eval/closure_episode_clock2500_v15'
try:
 code="$rows=@(Get-CimInstance Win32_Process|Where-Object {$_.CommandLine -like '*closure_episode_clock2500_v15*' -and $_.Name -like 'python*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}});$name='MOD4_AsyncFrozenEvaluation_v15_atomic_retry_review';$xml=Export-ScheduledTask -TaskName $name;[pscustomobject]@{rows=$rows;newtask=(Get-ScheduledTask -TaskName $name).State.ToString();triggers=([xml]$xml).Task.Triggers.ChildNodes.Count;oldtask=(Get-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_spring_audit_review').State.ToString()}|ConvertTo-Json -Compress -Depth 6"
 _,o,e=c.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(code.encode('utf-16le')).decode(),timeout=20)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw);v['epoch']=time.time()
 with c.open_sftp() as f:
  for name in ('ATOMIC_RETRY_WORKER_STARTED.json','ATOMIC_RETRY_WORKER_STATE.json','ATOMIC_RETRY_WORKER_ATTENTION.json','ATOMIC_RETRY_WORKER_ADMITTED.json'):
   try:
    with f.open(root+'/'+name) as inp:v[name]=json.loads(inp.read())
   except FileNotFoundError:v[name]=None
  for name in ('resilient_json_atomic.py','eval_worker_atomic_retry_review.py'):
   with f.open(root+'/'+name) as inp:raw=inp.read()
   assert raw==(D/name).read_bytes()
  jobs={}
  for k in ('flat','spin','world'):
   path=root+'/jobs/clk2500-closure-episode-d3-75-d5-b1-'+k
   try:
    with f.open(path+'/complete.json') as inp:jobs[k]=json.loads(inp.read())
   except FileNotFoundError:jobs[k]=dict(complete=False)
  v['D5_block1_evaluation']=jobs
 s=v['ATOMIC_RETRY_WORKER_STARTED.json'];rows=v['rows'];assert isinstance(rows,list)
 own=[r for r in rows if r['ProcessId']==s['pid'] and 'eval_worker_atomic_retry_review.py' in r['CommandLine']];assert len(own)==1
 assert v['newtask']=='Running' and v['triggers']==0 and v['oldtask']=='Disabled'
 assert not v['ATOMIC_RETRY_WORKER_ATTENTION.json']
 assert v['ATOMIC_RETRY_WORKER_STATE.json']['pid']==s['pid'] and v['ATOMIC_RETRY_WORKER_STATE.json']['epoch']>=s['epoch']
 v['current_attention']=None;v['own_actual_identity']=own[0];v['actual_source_SHA_exact']=True;v['no_GPU_PPO_canonical_launch_or_replay_mutation_by_reader']=True
 (R/'ATOMIC_RETRY_WORKER_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(dict(epoch=v['epoch'],worker=own[0],children=[r for r in rows if r['ProcessId'] not in (own[0]['ProcessId'],own[0]['ParentProcessId'])],candidate=v['D5_block1_evaluation'],current_attention=None,oldtask=v['oldtask'],triggers=v['triggers'])))
finally:c.close()
