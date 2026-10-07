"""Read-only native audit of the failed second repaired block and safe fallback."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,time,hashlib,fcntl,subprocess
D=Path('/home/egde/rl_candidates/MOD4_EPISODE_SUPERVISION_REPAIR_20261007');sys.path.insert(0,str(D));import supervise_episode_repair as w
s=w.s;read=s.q.w.read;E=s.q.ER
central={n:read(E/n) for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOE_PLAN_EXECUTION_CURRENT.json')}
handoff=(E/'LATEST_HANDOFF.md').read_text()
assert central['PLAN_APPROVAL.json']['approved'] and central['PLAN_APPROVAL.json']['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
w.verify_repair();row=read(D/'reports/episode_repaired_block2_SAVED_EXIT.json');run=Path(row['run']);p=Path(row['checkpoint']['path']);cpu=s.fullsave(p)
assert cpu==row['checkpoint']
m=read(run/'run_manifest.json');freeze=read(D/'reports/SOURCE_FREEZE.json')['sha256'];rf=read(run/'rolling_source_freeze.json')
assert m['source_map']==freeze and rf['sha256']==freeze
for n,h in m['src_sha256'].items():assert s.q.base.sha(run/'src_snapshot'/n)==h,n
receipt=read(run/'latest_complete.json');assert receipt==row['own_PID_bound_receipt']
assert receipt['pid']==1002022 and receipt['checkpoint']==str(p)
health=read(run/'CLOCK_TRAINING_HEALTH.json');assert health==row['health'] and not w.learning_health_pass(health)
assert health['integrity_task_reset_events']==1 and health['reason_counts']['closure']==1 if 'reason_counts' in health else health['integrity_task_reset_events']==1
b=read(s.q.ctl.CANONICAL);segments=[x for x in b['completed_segments'] if x['pid']==receipt['pid']]
assert len(segments)==1 and segments==row['unique_completed_segment']
assert b['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training') and not s.trainers()
identities={}
for n in ('REPAIR_STARTED.json','SOLVER32_GUARDIAN_STARTED.json'):
 r=read(D/'reports'/n);r=r.get('owner',r);actual=s.identity(r['pid']);assert not actual or actual['state']=='Z' or actual['start_ticks']!=r['start_ticks'];identities[n]=actual
actual=s.identity(receipt['pid']);assert not actual or actual['state']=='Z';identities['trainer']=actual
locks=[]
for path in (s.q.P/'autonomy_controller.lock',s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock'):
 with path.open('a') as f:
  fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(str(path));fcntl.flock(f,fcntl.LOCK_UN)
T=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007')
fallback={p.name:read(p) for p in (T/'reports').glob('*.json') if any(k in p.name for k in ('COMPLETE','PASSED','SOURCE','REVIEW_READY','BASE_ENV'))}
for path in T.glob('learning_logs/*/latest_complete.json'):
 rec=read(path)
 if s.q.base.sha(Path(rec['checkpoint']))=='5abd2a912f5c717849c25de09448581c226e6c9e79581f4a44e0e4a8f27261c1':
  rr=path.parent;fallback['validated24827']={'cpu':s.fullsave(Path(rec['checkpoint'])),'receipt':rec,'manifest':read(rr/'run_manifest.json'),'freeze':read(rr/'rolling_source_freeze.json'),'health':read(rr/'CLOCK_TRAINING_HEALTH.json'),'startup':read(rr/'SENSOR_RESUME_STARTUP_VERIFIED.json')}
assert 'validated24827' in fallback
v=dict(epoch=time.time(),central=central,handoff=handoff,failed=row,failed_manifest=m,failed_source_freeze=rf,failed_startup=read(run/'SENSOR_RESUME_STARTUP_VERIFIED.json'),actual_updates=health['control_steps']//24,actual_environment_steps=health['control_steps']*20000,identities=identities,two_locks_available=locks,budget={k:b[k] for k in ('authorized_training_seconds','charged_training_seconds','remaining_training_seconds','active_segment')},canonical_sha256=s.q.base.sha(s.q.ctl.CANONICAL),fallback=fallback,all_raw_and_weights_retained=True,no_budget_or_training_mutation=True)
print(json.dumps(v))
'''
 _,out,err=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=90)
 raw,errors=out.read(),err.read();assert out.channel.recv_exit_status()==0,(raw+errors).decode()
 v=json.loads(raw);(R/'FAILURE_AND_FALLBACK_BOUNDARY.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps({k:v[k] for k in ('epoch','actual_updates','actual_environment_steps','identities','two_locks_available','budget')}))
 print(json.dumps(dict(failed_checkpoint=v['failed']['checkpoint'],health=v['failed']['health'],fallback_checkpoint=v['fallback']['validated24827']['cpu'],fallback_health=v['fallback']['validated24827']['health'])))
finally:c.close()
