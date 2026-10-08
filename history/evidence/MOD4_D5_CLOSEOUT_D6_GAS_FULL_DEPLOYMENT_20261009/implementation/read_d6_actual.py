"""Read real phase/PID identity and own immutable receipts. No launch or ledger write."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
    code=r'''
from pathlib import Path
import sys,json,time,re
D=Path('/home/egde/rl_candidates/MOD4_D6_FULL_CONTRACT_20261009');R=D/'reports';sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'))
import supervise_d6_gas_full_contract as w
w.verify();read=w.read;st=read(R/'D6_STATE.json');owner=w.identity(st['owner']['pid']);assert owner and owner['start_ticks']==st['owner']['start_ticks'] or (R/'D6_REVIEW_READY.json').exists() or (R/'D6_ATTENTION.json').exists()
child=w.identity(st['child']['pid']) if st.get('child') else None
if child:assert child['start_ticks']==st['child']['start_ticks']
guard=read(R/'D6_GUARDIAN_STARTED.json') if (R/'D6_GUARDIAN_STARTED.json').exists() else None;guardian=w.identity(guard['pid']) if guard else None
b=w.s.q.base.budget_state();attention=read(R/'D6_ATTENTION.json') if (R/'D6_ATTENTION.json').exists() else None
completed={p.stem:read(p) for p in R.glob('d6_*_PASSED.json')}
for label,row in completed.items():
 run=Path(row['run']);m=read(run/'run_manifest.json');rec=read(run/'latest_complete.json');count=m['num_envs']
 assert row['health']['pid']==rec['pid']==row['own_PID_bound_receipt']['pid']
 assert w.learning_health_pass(row['health']);ck=w.fullsave(Path(rec['checkpoint']),count=count);assert ck['sha256']==row['checkpoint']['sha256']
 assert m['source_map']==read(R/'SOURCE_FREEZE.json')['sha256']==read(run/'rolling_source_freeze.json')['sha256']
 for n,h in m['src_sha256'].items():assert w.s.q.base.sha(run/'src_snapshot'/n)==h
 seg=[x for x in read(w.s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==rec['pid']];assert len(seg)==1 and seg==row['unique_completed_segment']
current=None
if child and child['state']!='Z' and any('train_gas_' in arg for arg in child['argv']):
 assert guardian and guardian['start_ticks']==guard['start_ticks']
 assert b['active_segment']['pid']==child['pid'] and read(w.s.q.ctl.STATE_PATH)['active_training']['pid']==child['pid']
 runs=[]
 for root in (D/'discard_logs',D/'learning_logs'):
  if root.exists():
   for run in root.iterdir():
    if (run/'latest_complete.json').exists() and read(run/'latest_complete.json')['pid']==child['pid']:runs.append(run)
 if runs:
  assert len(runs)==1;run=runs[0];m=read(run/'run_manifest.json');rec=read(run/'latest_complete.json');ck=w.fullsave(Path(rec['checkpoint']),count=m['num_envs'])
  assert m['source_map']==read(R/'SOURCE_FREEZE.json')['sha256']==read(run/'rolling_source_freeze.json')['sha256']
  for n,h in m['src_sha256'].items():assert w.s.q.base.sha(run/'src_snapshot'/n)==h
  assert m['init_checkpoint_sha256']==st['source']['sha256']
  startup=read(run/'GAS_DAMPING_RESUME_STARTUP_VERIFIED.json') if (run/'GAS_DAMPING_RESUME_STARTUP_VERIFIED.json').exists() else None
  if m['num_envs']==20000:
   assert startup and startup['source_sha256']==m['init_checkpoint_sha256'] and startup['actual_CUDA_gas_state_disk_roundtrip_exact'] and startup['gas_episode_incremented_once'] and startup['complete_D1_D5_optimizer_global_named_streams_verified'] and not startup['PhysX_exact_resume_claimed']
  log=Path(st['active_log']).read_text(errors='replace');current=dict(run=str(run),checkpoint=ck,receipt=rec,manifest=m,snapshot_count=len(m['src_sha256']),startup=startup,PPO_log_updates=len(re.findall(r'Learning iteration\s+(\d+)',log)),live_health=read(run/'CLOCK_TRAINING_HEALTH.json') if (run/'CLOCK_TRAINING_HEALTH.json').exists() else None,not_behavior_or_final_health=True)
epoch=time.time();tail=max(0,epoch-b['active_segment']['accounted_through_epoch']) if b['active_segment'] else 0
reports={n:read(R/n) for n in ('D6_INSTALL_BOUNDARY.json','D6_NATIVE20K_PASSED.json','D6_COMPLETE_PPO_PREFLIGHT_PASSED.json','D6_REVIEW_READY.json') if (R/n).exists()}
old=Path('/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008/reports');oldst=read(old/'D5_STATE.json');oldowner=w.identity(oldst['owner']['pid'])
v=dict(epoch=epoch,state=st,actual_owner=owner,actual_child=child,actual_guardian=guardian,current=current,completed=completed,reports=reports,attention=attention,budget={k:b[k] for k in ('authorized_training_seconds','charged_training_seconds','remaining_training_seconds','active_segment')},actual_tail_adjusted_remaining_seconds=b['remaining_training_seconds']-tail,old_D5_phase=oldst['phase'],old_D5_owner_actual=oldowner,log_tail=Path(st['active_log']).read_text(errors='replace')[-1800:] if st.get('active_log') else None,no_GPU_PPO_or_budget_write=True)
print(json.dumps(v))
'''
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
    (R/'D6_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
    with c.open_sftp() as f:
        for n in ('D6_STATE.json','D6_GUARDIAN_STARTED.json','D6_NATIVE20K_PASSED.json','D6_COMPLETE_PPO_PREFLIGHT_PASSED.json','D6_INSTALL_BOUNDARY.json','D6_ATTENTION.json','D6_REVIEW_READY.json'):
            try:f.get('/home/egde/rl_candidates/MOD4_D6_FULL_CONTRACT_20261009/reports/'+n,str(R/n))
            except FileNotFoundError:pass
    print(json.dumps(dict(epoch=v['epoch'],phase=v['state']['phase'],owner=v['actual_owner'],child=v['actual_child'],completed=list(v['completed']),reports=list(v['reports']),attention=v['attention'],own_save=v['current']['checkpoint']['sha256'] if v['current'] else None,PPO_log_updates=v['current']['PPO_log_updates'] if v['current'] else None,old_D5_phase=v['old_D5_phase'],remaining=v['actual_tail_adjusted_remaining_seconds'],log_tail=v['log_tail'])))
finally:c.close()
