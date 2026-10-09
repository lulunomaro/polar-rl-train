"""Read immutable D7 source and actual evaluator identity; no training mutation."""
from pathlib import Path
import sys,json,hashlib,time,base64
D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect();w=connect_eval()
try:
 with c.open_sftp() as f,w.open_sftp() as wf:
  E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007'
  p=D/'d7-original-frozen.zip'
  if not p.exists():f.get(E+'/artifacts/d7-clock2500-solver32-chassisPD277-closedloop-frozen.zip',str(p))
  assert hashlib.sha256(p.read_bytes()).hexdigest()=='8a964c1d0cfa291ea8faf72d978464daa8b2a8e90834554c435d528ffb222871'
  for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOE_PLAN_EXECUTION_CURRENT.json','LATEST_HANDOFF.md'):
   try:raw=f.open(E+'/reports/'+name).read()
   except FileNotFoundError:continue
   (R/name).write_bytes(raw)
  raw=f.open(E+'/eval_queue/clk2500-closure-episode-d3-98-d7-com-pd-anchor-flat.json').read();(R/'template.json').write_bytes(raw)
  worker={}
  W='D:/MOD4_async_eval/closure_episode_clock2500_v15'
  for name in ('SDK_PREPARATION_ISOLATION_WORKER_STARTED.json','SDK_PREPARATION_ISOLATION_WORKER_STATE.json','SDK_PREPARATION_ISOLATION_WORKER_ATTENTION.json'):
   try:worker[name]=json.loads(wf.open(W+'/'+name).read())
   except FileNotFoundError:pass
  (R/'EVALUATOR_IDENTITY.json').write_text(json.dumps(worker,indent=2),encoding='utf8')
  start=worker['SDK_PREPARATION_ISOLATION_WORKER_STARTED.json'];pid=start['pid']
  ps=f"Get-CimInstance Win32_Process -Filter \"ProcessId={pid}\" | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"
  _,o,e=w.exec_command('powershell -NoProfile -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=30)
  actual=o.read().decode('utf8',errors='replace');err=e.read();assert o.channel.recv_exit_status()==0,err
  (R/'EVALUATOR_PROCESS.json').write_text(actual,encoding='utf8')
  print(json.dumps(dict(source_package_verified=True,evaluator_actual=json.loads(actual),current_attention=worker.get('SDK_PREPARATION_ISOLATION_WORKER_ATTENTION.json'),master_read=True)))
finally:c.close();w.close()
