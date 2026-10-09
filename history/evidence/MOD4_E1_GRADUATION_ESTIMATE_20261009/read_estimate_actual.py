"""Read actual E1 progress and budget for ETA; no launch/stop/ledger mutation."""
from pathlib import Path
import base64,hashlib,json,os,shlex,sys,time
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
assert not (R/'E1_ETA_ACTUAL.json').exists(),'Preserve saved observations; use a new version for another read'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
secret,_=recover('RM_SSH_PASSWORD');assert secret,'Existing authorized transport unavailable'
os.environ['RM_SSH_PASSWORD']=secret
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
code=r'''
from pathlib import Path
import hashlib,json,os,re,time,statistics
D=Path('/home/egde/rl_candidates/MOD4_S3_E1_REVIEWED_STABLE_20261009');R=D/'reports'
def read(p):return json.loads(p.read_bytes()) if p.is_file() else None
def identity(pid):
 p=Path('/proc')/str(pid)
 try:
  stat=(p/'stat').read_text().rsplit(')',1)[1].split();argv=(p/'cmdline').read_bytes().decode().rstrip('\0').split('\0')
  return dict(pid=pid,start_ticks=int(stat[19]),state=stat[0],ppid=int(stat[1]),cwd=os.readlink(p/'cwd'),argv=argv)
 except (FileNotFoundError,ProcessLookupError):return None
st=read(R/'E1_STATE.json');assert st
parent=identity(st['owner']['pid']);child=identity(st['child']['pid']) if st.get('child') else None
if parent:assert parent['start_ticks']==st['owner']['start_ticks'] and str(D/'supervise_e1_reviewed_stable_continuation.py') in parent['argv']
if child:assert child['start_ticks']==st['child']['start_ticks'] and str(D/'isaac/mod4/train_e1_route_health_resume_ppo.py') in child['argv']
now=time.time();budget=read(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'))
assert budget['authorized_training_seconds']==828000
act=budget.get('active_segment');tail=max(0,now-act['accounted_through_epoch']) if act else 0
segments=[x for x in budget['completed_segments'] if 'S3_E1' in x.get('kind','') or 'MOD4_S3_E1' in x.get('log','')]
completed_used=sum(x['accounted_through_epoch']-x['started_epoch'] for x in segments)
active_used=now-act['started_epoch'] if act and ('S3_E1' in act.get('kind','') or 'MOD4_S3_E1' in act.get('log','')) else 0
v=dict(epoch=now,phase=st['phase'],state=st,actual_parent=parent,actual_child=child,
 attention=read(R/'E1_ATTENTION.json'),review_ready=read(R/'E1_REVIEW_READY.json'),
 budget=dict(authorized_seconds=budget['authorized_training_seconds'],charged_seconds=budget['charged_training_seconds'],remaining_ledger_seconds=budget['remaining_training_seconds'],tail_unaccounted_seconds=tail,remaining_tail_adjusted_seconds=budget['remaining_training_seconds']-tail,active_segment=act,E1_completed_segments=segments,E1_completed_accounted_seconds=completed_used,E1_active_elapsed_seconds=active_used,E1_total_used_seconds=completed_used+active_used,S3_planning_cap_seconds=108000,S3_planning_cap_remaining_seconds=108000-completed_used-active_used),
 own_run=None,stable_receipts={},no_GPU_PPO_process_or_canonical_mutation=True)
for p in sorted(R.glob('e1_gentle_stable_*')):
 if p.suffix=='.json':v['stable_receipts'][p.name]=read(p)
if child:
 argv=child['argv'];name=argv[argv.index('--run_name')+1];logs=Path(argv[argv.index('--log_root')+1]);runs=list(logs.glob('*_'+name));assert len(runs)==1
 run=runs[0];manifest=read(run/'run_manifest.json');latest=read(run/'latest_complete.json');health=read(run/'CLOCK_TRAINING_HEALTH.json')
 assert manifest and manifest['source_map']==read(R/'SOURCE_FREEZE.json')['sha256']
 snapshot_count=len(manifest['src_sha256']);assert snapshot_count==57
 if latest:
  assert latest['pid']==child['pid'];ck=Path(latest['checkpoint']);h=hashlib.sha256(ck.read_bytes()).hexdigest()
  latest=dict(latest,actual_file_sha256=h)
 v['own_run']=dict(path=str(run),manifest=manifest,latest_complete=latest,health=health,snapshot_count=snapshot_count,
  terrain_startup=read(run/'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json'))
 if st.get('active_log'):
  log=Path(st['active_log']);size=log.stat().st_size
  with log.open('rb') as f:f.seek(max(0,size-40000));text=f.read().decode(errors='replace')
  durations=[float(x) for x in re.findall(r'Iteration time:\s*([\d.]+)s',text)]
  v['recent_log']=dict(bytes=size,iteration_seconds=durations,mean_iteration_seconds=statistics.mean(durations) if durations else None,
   env_policy_steps_per_second_estimate=480000/statistics.mean(durations) if durations else None,tail=text[-4000:],PPO_iteration_labels=re.findall(r'Learning iteration\s+(\d+)',text))
print(json.dumps(v))
'''
c=connect()
try:
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:
  (R/'E1_ETA_READER_REJECTED.json').write_text(json.dumps(dict(epoch=time.time(),exit_code=rc,error=(raw+err).decode(errors='replace'),read_only_no_training_change=True),ensure_ascii=False,indent=2),encoding='utf8')
  raise RuntimeError('Read-only ETA observation rejected; preserve error')
 v=json.loads(raw);(R/'E1_ETA_ACTUAL.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(dict(epoch=v['epoch'],phase=v['phase'],actual_child=v['actual_child'],budget=v['budget'],attention=v['attention'],recent_log=v.get('recent_log'),own_latest=(v.get('own_run') or {}).get('latest_complete')),ensure_ascii=True))
finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
