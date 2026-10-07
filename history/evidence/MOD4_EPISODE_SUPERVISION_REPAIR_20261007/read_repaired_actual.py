from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';ROOT='/home/egde/rl_candidates/MOD4_EPISODE_SUPERVISION_REPAIR_20261007'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,time,subprocess
D=Path('/home/egde/rl_candidates/MOD4_EPISODE_SUPERVISION_REPAIR_20261007');sys.path.insert(0,str(D));import supervise_episode_repair as w
w.verify_repair();s=w.s;read=s.q.w.read
st=read(D/'reports/SOLVER32_TRAINING_STATE.json');parent=s.identity(read(D/'reports/REPAIR_STARTED.json')['owner']['pid']);g=s.identity(read(D/'reports/SOLVER32_GUARDIAN_STARTED.json')['pid']);child=s.identity(st['child']['pid']) if st.get('child') else None
assert parent and g and child and parent['ppid']==1
b=s.q.base.budget_state();own=None
if child:
 args=child['argv'];logs=Path(args[args.index('--log_root')+1]);name=args[args.index('--run_name')+1];runs=list(logs.glob('*_'+name))
 if len(runs)==1:
  run=runs[0];m=read(run/'run_manifest.json');f=read(D/'reports/SOURCE_FREEZE.json')['sha256'];assert m['source_map']==f and m['init_checkpoint_sha256']==w.SOURCE_SHA
  for n,h in m['src_sha256'].items():assert s.q.base.sha(run/'src_snapshot'/n)==h,n
  rec=read(run/'latest_complete.json') if (run/'latest_complete.json').exists() else None
  if rec:assert rec['pid']==child['pid']
  freeze=read(run/'rolling_source_freeze.json') if (run/'rolling_source_freeze.json').exists() else None
  if freeze:assert freeze['sha256']==f
  own=dict(path=str(run),manifest=m,own_full_save=s.fullsave(Path(rec['checkpoint'])) if rec else None,latest_complete=rec,source_freeze_present=bool(freeze),startup=read(run/'SENSOR_RESUME_STARTUP_VERIFIED.json') if (run/'SENSOR_RESUME_STARTUP_VERIFIED.json').exists() else None,health=read(run/'CLOCK_TRAINING_HEALTH.json') if (run/'CLOCK_TRAINING_HEALTH.json').exists() else None)
log=Path(st['active_log']);v=dict(epoch=time.time(),parent=parent,guardian=g,trainer=child,phase=st['phase'],state=st,own=own,budget={k:b[k] for k in ('authorized_training_seconds','charged_training_seconds','remaining_training_seconds','active_segment')},remaining_actual=s.left(),GPU=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.used,power.draw','--format=csv,noheader'],capture_output=True,text=True).stdout,log_tail=log.read_text(errors='replace')[-3000:],CPU=read(D/'reports/STAGING_FINALIZED.json'),SDK=read(D/'reports/SUPERVISION_SDK_PASSED.json'),source_freeze=read(D/'reports/SOURCE_FREEZE.json'),AUTHORIZATION=read(D/'reports/AUTHORIZATION.json'))
print(json.dumps(v))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw);(R/'REPAIR_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 with c.open_sftp() as sf:
  for n in ('SUPERVISION_SDK_PASSED.json','SOURCE_FREEZE.json','REPAIR_INSTALL_BOUNDARY.json','REPAIR_STARTED.json','SOLVER32_GUARDIAN_STARTED.json','DISPLAY_SOURCE_REVIEW.json'):sf.get(ROOT+'/reports/'+n,str(R/n))
 print(json.dumps({k:v[k] for k in ('epoch','parent','guardian','trainer','phase','budget','remaining_actual','GPU','log_tail')}|{'own':{k:v['own'][k] for k in ('path','own_full_save','source_freeze_present','startup','health')} if v['own'] else None},ensure_ascii=False))
finally:c.close()
