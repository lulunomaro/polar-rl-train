"""Read current admission evidence and installed SDK source; no remote mutation."""
from pathlib import Path
import base64,hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';OLD='/home/egde/rl_candidates/MOD4_S3_E1_G3_REVIEWED_20261010'
WIN='D:/MOD4_async_eval/closure_episode_clock2500_v15'
def main():
 for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):
  secret,_=recover(name);assert secret;os.environ[name]=secret
 n=connect();w=connect_eval()
 try:
  code=r'''from pathlib import Path
import json,hashlib,fcntl,os,time
E=Path(E_VALUE);D=Path(OLD_VALUE);H=lambda b:hashlib.sha256(b).hexdigest();j=lambda p:json.loads(p.read_bytes())
def actual(pid):
 q=Path('/proc')/str(pid)
 if not q.exists():return None
 try:
  s=(q/'stat').read_text().split(') ',1)[1].split();return dict(pid=pid,state=s[0],start_ticks=int(s[19]),cwd=os.readlink(q/'cwd'),argv=(q/'cmdline').read_bytes().decode().split('\0'))
 except OSError:return None
names=('PLAN_APPROVAL.json','E1_G3_127_COMPLETE_MATCHED_ACTUAL_REVIEW.json','E1_G3_127_PREFIX_RETENTION_DECISION.json','SCUT_E1_RETENTION_MATCHED_FINDINGS.json','E1_G3_128_COMPLETE_MATCHED_ACTUAL_REVIEW.json','E1_G3_128_COMPLETE_RETENTION_DECISION.json','E1_G3_128_COMPLETE_METADATA_SYNCED.json','NEXT_E1_G3_COMMAND_RETENTION_REPAIR_WORK_ORDER_V2.json')
context={}
for name in names:
 p=E/'reports'/name;b=p.read_bytes();context[name]=dict(path=str(p),bytes=len(b),sha256=H(b),content=j(p))
master=(E/'reports/MOD4_MOE_MASTER_PLAN.md').read_bytes();assert H(master)=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
s=j(D/'reports/E1_STATE.json');g=j(D/'reports/E1_GUARDIAN_STARTED.json');p=j(D/'reports/e1_G3_reviewed_observation_PASSED.json')
locators=(s['owner'],g,dict(pid=p['own_PID_bound_receipt']['pid'],start_ticks=74243664));procs=[actual(v['pid']) for v in locators]
assert s['phase']=='E1_G3_reviewed_saved_review_ready' and s['child'] is None
assert all(not a or a['state']=='Z' or a['start_ticks']!=v['start_ticks'] for a,v in zip(procs,locators))
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');b=B.read_bytes();l=json.loads(b)
assert l['authorized_training_seconds']==828000 and l['active_segment'] is None
own=[x for x in l['completed_segments'] if x['pid']==p['own_PID_bound_receipt']['pid']];assert len(own)==1
locks=[]
for q in (Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),B.parent/'native_floor_supervisor.lock'):
 with q.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(str(q))
sdk={}
base=Path('/home/egde')
for q in base.glob('*/source/isaaclab/isaaclab/terrains/terrain_generator.py'):
 sdk[str(q)]=q.read_text()
if not sdk:
 for root in (base/'IsaacLab',base/'isaaclab',base/'IsaacLab-2.3.0'):
  q=root/'source/isaaclab/isaaclab/terrains/terrain_generator.py'
  if q.exists():sdk[str(q)]=q.read_text()
sources={name:(D/'isaac/mod4'/name).read_text() for name in ('e1_terrain_state.py','e1_terrain_training_env.py','e1_reset_evidence_training_env.py','e1_scene_query_resource.py','chassis_pd_checkpoint.py','sensor_checkpoint.py') if (D/'isaac/mod4'/name).exists()}
print(json.dumps(dict(epoch=time.time(),context=context,closed_state=s,actual_old_processes=procs,own_segment=own,locks_free=locks,canonical=dict(path=str(B),sha256=H(b),remaining=l['authorized_training_seconds']-l['charged_training_seconds'],active=l['active_segment']),sdk=sdk,sources=sources,source_freeze=j(D/'reports/SOURCE_FREEZE.json'),queue_ids=[x.name for x in (E/'eval_queue').glob('*.json') if x.name.startswith('clk2500-closure-episode-d3-129')],master_SHA_verified=True,read_only=True)))
'''.replace('E_VALUE',repr(E)).replace('OLD_VALUE',repr(OLD))
  _,o,e=n.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
  with w.open_sftp() as f:
   try:attention=json.loads(f.open(WIN+'/E1_G3_PACKAGE_REVIEW_WORKER_ATTENTION.json').read())
   except FileNotFoundError:attention=None
   started=json.loads(f.open(WIN+'/E1_G3_PACKAGE_REVIEW_WORKER_STARTED.json').read())
   v['worker']=dict(attention=attention,started=started,source_sha256=hashlib.sha256(f.open(WIN+'/eval_worker_e1_g3_package_review.py').read()).hexdigest())
  ps="[pscustomobject]@{rows=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -like 'python*' -and $_.CommandLine -like '*closure_episode_clock2500_v15*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}})}|ConvertTo-Json -Depth 6 -Compress"
  _,o,e=w.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v['worker']['actual_processes']=json.loads(raw)['rows']
  p=R/('SCOPE_ACTUAL_'+str(int(v['epoch']))+'.json');assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
  S=D/'inherited_source';S.mkdir(exist_ok=True)
  for name,s in v['sources'].items():(S/name).write_text(s,encoding='utf8')
  for source,s in v['sdk'].items():(S/'installed_terrain_generator.py').write_text(s,encoding='utf8')
  print(json.dumps(dict(report=str(p),old_processes=v['actual_old_processes'],remaining=v['canonical']['remaining'],locks=v['locks_free'],worker=v['worker'],sdk_sources=list(v['sdk']),source_count=len(v['source_freeze']['sha256']),new129_ids=v['queue_ids'])))
 finally:
  n.close();w.close()
  for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):os.environ.pop(name,None)
if __name__=='__main__':
 try:main()
 except Exception:
  (R/('SCOPE_READER_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),read_only=True,no_remote_mutation=True)),encoding='utf8');raise
