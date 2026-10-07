"""Read only own PID/save/source manifests; health file is terminal, never guessed."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,time
D=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007');sys.path.insert(0,str(D));import supervise_sensor_stable_continuation as s
s.verify();state=s.q.w.read(D/'reports/SENSOR_STABLE_STATE.json');child=s.identity(state['child']['pid']);assert child and child['start_ticks']==state['child']['start_ticks']
owner=s.identity(state['owner']['pid']);guardian=s.identity(s.q.w.read(D/'reports/SENSOR_STABLE_GUARDIAN_STARTED.json')['pid']);assert owner['ppid']==1
sessions={}
for role,i in [('owner',owner),('guardian',guardian),('trainer',child)]:
 stat=(Path('/proc')/str(i['pid'])/'stat').read_text().rsplit(')',1)[1].split();sessions[role]=int(stat[3])
assert len(set(sessions.values()))==3
run=s.q.w.rate.trainer_run(D/'learning_logs',child['pid']);r=s.q.w.read(run/'latest_complete.json');assert r['pid']==child['pid'];p=Path(r['checkpoint']);ck=s.q.base.checkpoint(p);assert ck['finite_tensors']==74
m=s.q.w.read(run/'run_manifest.json');f=s.q.w.read(D/'reports/SOURCE_FREEZE.json')['sha256'];rf=s.q.w.read(run/'rolling_source_freeze.json');assert rf['sha256']==m['source_map']==f and len(f)==206
for n,h in f.items():assert s.q.base.sha(D/n)==h and s.q.base.sha(run/'sensor_source_snapshot'/n)==h,n
for n,h in m['src_sha256'].items():assert s.q.base.sha(run/'src_snapshot'/n)==h,n
assert m['init_checkpoint_sha256']=='6457195e25682c8059e2a9be7c7fb4531299216874ab8100014a9cf75f7f8b7b'
assert m['robot_usd_sha256']=='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87' and m['sensor_recipe']['profile']=='noise_bias_mild_v1'
v=dict(epoch=time.time(),owner=owner,guardian=guardian,trainer=child,sessions_independent=sessions,own_run=str(run),own_PID_bound_receipt=r,checkpoint=ck,own206_sources_and_runfreeze_exact=True,actual_src_snapshot_exact=True,actual_snapshot_count=len(m['src_sha256']),manifest_init_exact=True,startup=s.q.w.read(run/'SENSOR_RESUME_STARTUP_VERIFIED.json'),not_behavior_validation=True,terminal_health_file_present=(run/'CLOCK_TRAINING_HEALTH.json').exists(),missing_active_health_not_zero_or_failure=True)
print(json.dumps(v))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw)
 (R/'SENSOR_STABLE_OWN_SOURCE_VERIFIED.json').write_text(json.dumps(v,indent=2))
 with c.open_sftp() as sf:
  for root in ('/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007','/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007'):
   dest=root+'/reports/SENSOR_STABLE_OWN_SOURCE_VERIFIED.json';sf.put(str(R/'SENSOR_STABLE_OWN_SOURCE_VERIFIED.json'),dest+'.source_review');sf.posix_rename(dest+'.source_review',dest)
  out=R/'stable_native_evidence';out.mkdir(exist_ok=True);root='/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007'
  for p in sf.listdir_attr(root+'/reports'):
   if p.filename.endswith('.json') and p.st_size<3000000:sf.get(root+'/reports/'+p.filename,str(out/p.filename))
 print(json.dumps(dict(own_source=v['checkpoint'],source_exact=True,actual_snapshots=v['actual_snapshot_count'],sessions=v['sessions_independent'],startup=True,not_behavior_validation=True,terminal_health_file_present=v['terminal_health_file_present'])))
finally:c.close()
