"""Read current identities, source-bound save and active canonical tail only."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,time,subprocess
D=Path('/home/egde/rl_candidates/MOD4_VALIDATED_1MS_EPISODE_RECOVERY_20261008');sys.path.insert(0,str(D));import supervise_validated_1ms_runtime_review as w
w.verify();s=w.s;read=s.q.w.read;R=D/'reports';st=read(R/'RECOVERY_STATE.json');launch=read(R/'RECOVERY_LAUNCHED.json');a=s.identity(launch['owner']['pid']);parent=a if a and a['start_ticks']==launch['owner']['start_ticks'] and a['state']!='Z' else None
gr=read(R/'RECOVERY_GUARDIAN_STARTED.json') if (R/'RECOVERY_GUARDIAN_STARTED.json').exists() else None;g=s.identity(gr['pid']) if gr else None;guardian=g if g and g['start_ticks']==gr['start_ticks'] and g['state']!='Z' else None
cr=st.get('child');t=s.identity(cr['pid']) if cr else None;child=t if t and t['start_ticks']==cr['start_ticks'] and t['state']!='Z' else None
own=None
if child and 'train_sensor_resume_ppo.py' in Path(child['argv'][1]).name:
 args=child['argv'];assert args[1]==str(D/'isaac/mod4/train_sensor_resume_ppo.py') and child['ppid']==parent['pid'] and guardian
 init=Path(args[args.index('--init_checkpoint')+1]);name=args[args.index('--run_name')+1];assert name.startswith('validated1ms_recovery_block')
 assert s.q.base.sha(init)==st['source']['sha256']
 runs=list((D/'learning_logs').glob('*_'+name));assert len(runs)<=1
 if runs:
  run=runs[0];m=read(run/'run_manifest.json');f=read(R/'SOURCE_FREEZE.json')['sha256'];assert m['source_map']==f and m['init_checkpoint_sha256']==s.q.base.sha(init)
  assert m['env']['RM_PHYSICS_DT_S']=='0.001' and m['env']['RM_SOLVER_POS']=='16'
  for n,h in m['src_sha256'].items():assert s.q.base.sha(run/'src_snapshot'/n)==h,n
  rec=read(run/'latest_complete.json') if (run/'latest_complete.json').exists() else None
  if rec:assert rec['pid']==child['pid'] and rec['log_dir']==str(run)
  rf=read(run/'rolling_source_freeze.json') if (run/'rolling_source_freeze.json').exists() else None
  if rf:assert rf['sha256']==f
  own=dict(run=str(run),init_sha256=s.q.base.sha(init),manifest=m,receipt=rec,CPU_complete=s.fullsave(Path(rec['checkpoint'])) if rec else None,rolling_freeze_present=bool(rf),startup=read(run/'SENSOR_RESUME_STARTUP_VERIFIED.json') if (run/'SENSOR_RESUME_STARTUP_VERIFIED.json').exists() else None,health=read(run/'CLOCK_TRAINING_HEALTH.json') if (run/'CLOCK_TRAINING_HEALTH.json').exists() else None)
b=s.q.base.budget_state();v=dict(epoch=time.time(),phase=st['phase'],state=st,parent=parent,guardian=guardian,child=child,own=own,budget={k:b[k] for k in ('authorized_training_seconds','charged_training_seconds','remaining_training_seconds','active_segment')},remaining_actual=s.left(),SDK=read(R/'HEALTH_1MS_SDK_PASSED.json') if (R/'HEALTH_1MS_SDK_PASSED.json').exists() else None,attention=read(R/'SOLVER32_ATTENTION.json') if (R/'SOLVER32_ATTENTION.json').exists() else None,controller_tail=(D/'controller.log').read_text(errors='replace')[-1600:],active_log_tail=Path(st['active_log']).read_text(errors='replace')[-1400:] if st.get('active_log') else None,GPU=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.used,power.draw','--format=csv,noheader'],capture_output=True,text=True).stdout,no_mutation=True)
print(json.dumps(v))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=40);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode()
 v=json.loads(raw);(R/'RECOVERY_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps({k:v[k] for k in ('epoch','phase','parent','guardian','child','budget','remaining_actual','SDK','attention','controller_tail','active_log_tail','GPU')}))
 print(json.dumps(dict(own={k:v['own'][k] for k in ('run','init_sha256','receipt','CPU_complete','rolling_freeze_present','startup','health')} if v['own'] else None)))
finally:c.close()
