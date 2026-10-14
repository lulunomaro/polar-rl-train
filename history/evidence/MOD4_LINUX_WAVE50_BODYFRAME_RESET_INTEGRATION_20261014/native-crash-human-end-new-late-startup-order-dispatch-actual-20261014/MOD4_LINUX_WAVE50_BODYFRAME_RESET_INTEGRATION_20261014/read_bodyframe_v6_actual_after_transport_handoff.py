"""Single actual read after finite collector handoff; no GPU/mutation/kill."""
from pathlib import Path
import json,time,sys
import transport_bodyframe_pipeline_v6 as t
CODE=r'''
from pathlib import Path
import json,time,psutil,os,fcntl,subprocess,hashlib
r=Path(CONTEXT['root'])
def read(p):
 try:return json.loads(p.read_bytes())
 except (FileNotFoundError,json.JSONDecodeError):return None
v=read(r/'CURRENT_STAGE.json');owner=read(r/'PARENT_IDENTITY.json');procs=[]
for who in [owner,(v or {}).get('child')]:
 if not who:continue
 try:
  p=psutil.Process(who['pid']);actual=dict(pid=p.pid,created=p.create_time(),argv=p.cmdline(),cwd=p.cwd(),status=p.status(),RSS=p.memory_info().rss,CPU_times=list(p.cpu_times()),actual_same_identity=p.create_time()==who['created']);pp=Path('/proc')/str(p.pid)
  for f in ('wchan','status'):
   try:actual[f]=(pp/f).read_text()[-4000:]
   except OSError:pass
  actual['children']=[dict(pid=c.pid,created=c.create_time(),argv=c.cmdline(),status=c.status()) for c in p.children(recursive=True)];procs.append(actual)
 except psutil.Error:procs.append(dict(pid=who['pid'],actual_absent=True))
logs=[]
for q in [r/'pipeline_parent.log']+list(r.glob('*/attempt/worker_stdout.log')):
 if q.is_file():
  with q.open('rb') as f:f.seek(max(0,q.stat().st_size-24000));tail=f.read().decode('utf8',errors='replace')
  logs.append(dict(path=str(q),bytes=q.stat().st_size,tail=tail))
files={}
for p in r.rglob('*.json'):
 if p.name in ('EXIT_RECEIPT.json','GUARDIAN_CURRENT.json','STOP_AFTER_SAVE.json','CLOCK_TRAINING_HEALTH.json','BODYFRAME_NATIVE_PROGRESS.json','BIRTH_BODYFRAME_RESUME_STARTUP_VERIFIED.json','OWN_STAGE_POSTEXIT_PASSED.json','PIPELINE_COMPLETE_REVIEW_READY.json','PIPELINE_ORIGINAL_ERROR.json','GUARDIAN_EXIT.json','latest_complete.json') or p.name.endswith('STARTUP_VERIFIED.json'):files[str(p.relative_to(r))]=read(p)
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');d=read(B);locks=[]
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r+b') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:locks.append(dict(path=str(p),held=True))
  else:fcntl.flock(f,fcntl.LOCK_UN);locks.append(dict(path=str(p),held=False))
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader'],text=True)
apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'],text=True)
print(json.dumps(dict(epoch=time.time(),root=str(r),current=v,processes=procs,files=files,logs=logs,locks=locks,canonical_active=d['active_segment'],canonical_remaining=d['remaining_training_seconds'],GPU=gpu,GPU_apps=apps,no_signal_or_newGPU_or_budget_action=True)))
'''
def main():
 c=None
 try:
  c=t.connect();value,p=t.run(c,CODE,dict(root=t.ROOT),'BODYFRAME_V6_ACTUAL_PROCESS_STAGE_LOG_HANDOFF',timeout=120)
  print(json.dumps(dict(report=str(p),current=value['current'],processes=value['processes'],files=value['files'],logs=value['logs'],GPU=value['GPU'],GPU_apps=value['GPU_apps'])))
 finally:t.close(c)
if __name__=='__main__':main()
