"""Read actual processes and immutable runtime when a display-source guard refuses."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,time,subprocess,traceback,difflib,hashlib
D=Path('/home/egde/rl_candidates/MOD4_E0_DT2500_ENV20K_CONTINUATION_20261007');sys.path.insert(0,str(D));import supervise_dt2500_env20k_continuation as w
s=w.s;read=s.q.w.read
v={'epoch':time.time(),'root':str(D),'reader_only_no_authority_or_source_changes':True}
try:w.verify_continuation();v['original_guard_passed']=True
except Exception:v['original_guard_passed']=False;v['original_guard_error']=traceback.format_exc()
f=read(D/'reports/SOURCE_FREEZE.json')['sha256'];v['actual213_runtime_differences']={n:{'expected':h,'actual':s.q.base.sha(D/n)} for n,h in f.items() if s.q.base.sha(D/n)!=h};assert not v['actual213_runtime_differences']
st=read(D/'reports/SOLVER32_TRAINING_STATE.json');v['state']=st
v['parent']=s.identity(read(D/'reports/CONTINUATION_STARTED.json')['owner']['pid']);v['guardian']=s.identity(read(D/'reports/SOLVER32_GUARDIAN_STARTED.json')['pid']);v['child']=s.identity(st['child']['pid']) if st.get('child') else None
v['attention']=read(D/'reports/SOLVER32_ATTENTION.json') if (D/'reports/SOLVER32_ATTENTION.json').exists() else None
b=s.q.base.budget_state();v['budget']={k:b[k] for k in ('authorized_training_seconds','charged_training_seconds','remaining_training_seconds','active_segment')};v['remaining_actual']=s.left()
v['GPU']=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.used,power.draw','--format=csv,noheader'],capture_output=True,text=True).stdout
log=Path(st.get('active_log') or D/'controller.log');v['log_tail']=log.read_text(errors='replace')[-4500:] if log.exists() else None
v['own_run']=None
child=v['child']
if child:
 a=child['argv'];logs=Path(a[a.index('--log_root')+1]);name=a[a.index('--run_name')+1];runs=list(logs.glob('*_'+name))
 if len(runs)==1:
  run=runs[0];m=read(run/'run_manifest.json');receipt=read(run/'latest_complete.json');assert receipt['pid']==child['pid'] and m['source_map']==f
  assert m['init_checkpoint_sha256']==w.SOURCE_SHA
  for n,h in m['src_sha256'].items():assert s.q.base.sha(run/'src_snapshot'/n)==h,n
  freeze=read(run/'rolling_source_freeze.json');assert freeze['sha256']==f
  v['own_run']=dict(path=str(run),own_checkpoint_CPU=s.fullsave(Path(receipt['checkpoint'])),receipt=receipt,manifest=m,source_freeze_exact=True,clock_health=read(run/'CLOCK_TRAINING_HEALTH.json') if (run/'CLOCK_TRAINING_HEALTH.json').exists() else None)
for n in ('SOLVER32_REVIEW_READY.json','env20k_S2_D1D2_stable2h_SAVED_EXIT.json'):
 if (D/'reports'/n).exists():v[n]=read(D/'reports'/n)
p=s.q.P/'isaac/mod4/tui_spin_rate.py';frozen=D/'isaac/mod4/tui_spin_rate.py'
v['display_review']=dict(P_path=str(p),P_sha256=s.q.base.sha(p),candidate_path=str(frozen),candidate_sha256=s.q.base.sha(frozen),diff=list(difflib.unified_diff(frozen.read_text().splitlines(),p.read_text().splitlines(),fromfile='actual_training_candidate',tofile='current_P_display',n=3)))
pub=Path('/home/egde/rl_candidates/MOD4_DT2500_ASYNC_PUBLICATION_20261007/reports');v['publisher']={n:read(pub/n) for n in ('STARTED.json','STATE.json','PUBLISHED.json','ATTENTION.json') if (pub/n).exists()}
v['central_current']=read(s.q.ER/'MOE_PLAN_EXECUTION_CURRENT.json')
print(json.dumps(v))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode()
 v=json.loads(raw);(R/'DISPLAY_GUARD_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 own=v['own_run'];print(json.dumps({'epoch':v['epoch'],'phase':v['state']['phase'],'parent':v['parent'],'child':v['child'],'guardian':v['guardian'],'GPU':v['GPU'],'budget':v['budget'],'runtime_differences':v['actual213_runtime_differences'],'own_source':own['own_checkpoint_CPU'] if own else None,'clock_health':own['clock_health'] if own else None,'attention':v['attention'],'guard_passed':v['original_guard_passed'],'display_SHA':v['display_review']['P_sha256'],'display_diff':v['display_review']['diff'][:100],'publisher':v['publisher'],'log_tail':v['log_tail']},ensure_ascii=False))
finally:c.close()
