"""Phase-aware read-only audit. Each continuation uses the preceding own passed save."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,time,re,subprocess
D=Path('/home/egde/rl_candidates/MOD4_EPISODE_SUPERVISION_REPAIR_20261007');sys.path.insert(0,str(D));import supervise_episode_repair as w
w.verify_repair();s=w.s;read=s.q.w.read;R=D/'reports';st=read(R/'SOLVER32_TRAINING_STATE.json')
started=read(R/'REPAIR_STARTED.json')['owner'];gr=read(R/'SOLVER32_GUARDIAN_STARTED.json')
parent=s.identity(started['pid']);guardian=s.identity(gr['pid'])
def bound(actual,receipt):return bool(actual and actual['start_ticks']==receipt['start_ticks'] and actual['state']!='Z')
child=s.identity(st['child']['pid']) if st.get('child') else None
if child and (child['state']=='Z' or child['start_ticks']!=st['child']['start_ticks']):child=None
own=None;f=read(R/'SOURCE_FREEZE.json')['sha256'];b=s.q.base.budget_state()
if child:
 args=child['argv'];assert args[1]==str(D/'isaac/mod4/train_sensor_resume_ppo.py')
 assert child['ppid']==started['pid'] and bound(parent,started) and bound(guardian,gr)
 name=args[args.index('--run_name')+1];block=int(re.fullmatch(r'episode_repaired_block(\d+)_(\d+)',name).group(1))
 init=Path(args[args.index('--init_checkpoint')+1]);init_sha=s.q.base.sha(init)
 expected=w.SOURCE_SHA if block==1 else read(R/('episode_repaired_block'+str(block-1)+'_PASSED.json'))['checkpoint']['sha256']
 assert init_sha==expected,'Actual continuation init must match preceding complete passed source'
 runs=list(Path(args[args.index('--log_root')+1]).glob('*_'+name));assert len(runs)<=1
 if runs:
  run=runs[0];m=read(run/'run_manifest.json');assert m['source_map']==f and m['init_checkpoint_sha256']==init_sha
  for n,h in m['src_sha256'].items():assert s.q.base.sha(run/'src_snapshot'/n)==h,n
  rec=read(run/'latest_complete.json') if (run/'latest_complete.json').exists() else None
  if rec:assert rec['pid']==child['pid'] and rec['log_dir']==str(run)
  rf=read(run/'rolling_source_freeze.json') if (run/'rolling_source_freeze.json').exists() else None
  if rf:assert rf['sha256']==f
  startup=read(run/'SENSOR_RESUME_STARTUP_VERIFIED.json') if (run/'SENSOR_RESUME_STARTUP_VERIFIED.json').exists() else None
  if startup:assert startup['source_sha256']==init_sha and startup['new_physical_episode'] and not startup['PhysX_exact_resume_claimed']
  own=dict(run=str(run),block=block,init_checkpoint=str(init),init_sha256=init_sha,manifest=m,receipt=rec,fullsave=s.fullsave(Path(rec['checkpoint'])) if rec else None,source_freeze_present=bool(rf),startup=startup,health=read(run/'CLOCK_TRAINING_HEALTH.json') if (run/'CLOCK_TRAINING_HEALTH.json').exists() else None)
blocks={p.name:read(p) for p in R.glob('episode_repaired_block*_PASSED.json')}
active=b['active_segment'];Sactive=read(s.q.ctl.STATE_PATH).get('active_training')
v=dict(epoch=time.time(),phase=st['phase'],state=st,parent=parent,guardian=guardian,trainer=child,own=own,completed_blocks=blocks,
       budget={k:b[k] for k in ('authorized_training_seconds','charged_training_seconds','remaining_training_seconds','active_segment')},S_active_training=Sactive,remaining_actual=s.left(),
       attention=read(R/'SOLVER32_ATTENTION.json') if (R/'SOLVER32_ATTENTION.json').exists() else None,
       GPU=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.used,power.draw','--format=csv,noheader'],capture_output=True,text=True).stdout,
       logfile_tail=Path(st['active_log']).read_text(errors='replace')[-1700:] if st.get('active_log') and Path(st['active_log']).is_file() else None,
       no_training_or_budget_mutation=True,review_ready_without_parent_is_legal=True)
print(json.dumps(v))
'''
 _,out,err=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=45);raw,errors=out.read(),err.read();assert out.channel.recv_exit_status()==0,(raw+errors).decode()
 v=json.loads(raw);(R/'REPAIR_BLOCKS_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(dict(epoch=v['epoch'],phase=v['phase'],parent=v['parent'],guardian=v['guardian'],trainer=v['trainer'],budget=v['budget'],remaining_actual=v['remaining_actual'],GPU=v['GPU'],attention=v['attention'],own={k:v['own'][k] for k in ('run','block','init_sha256','fullsave','source_freeze_present','health')} if v['own'] else None)))
finally:c.close()
