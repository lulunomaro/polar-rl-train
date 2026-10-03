"""Read actual stage, process identities, current log, ledger, and full save."""
import json,shlex,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
D=Path(__file__).resolve().parent
code=r'''import json,hashlib,subprocess,time
from pathlib import Path
root=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002');reports=root/'reports';code=root/'isaac/mod4'
def read(p):return json.loads(p.read_text())
def ident(pid):
 try:
  p=Path('/proc')/str(pid);s=(p/'stat').read_text().split(') ',1)[1].split()
  return dict(pid=pid,start_ticks=s[19],state=s[0],cwd=str((p/'cwd').resolve()),argv=(p/'cmdline').read_bytes().decode().split('\0'))
 except OSError:return None
x=read(root/'status.json');state=read(reports/'AUTONOMY_STATE.json');ledger=read(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'))
rows=[]
for p in Path('/proc').iterdir():
 if p.name.isdigit():
  a=ident(int(p.name))
  if a and a['state']!='Z' and a['cwd']==str(root) and '-c' not in a['argv'] and Path(a['argv'][0]).name in ('python','python3'):rows.append(a)
log=Path(x.get('active_log',''))
remaining=ledger['authorized_training_seconds']-ledger['charged_training_seconds']
if ledger.get('active_segment'):remaining-=max(0,time.time()-ledger['active_segment']['accounted_through_epoch'])
out=dict(epoch=time.time(),status={k:x.get(k) for k in ['stage','yaw_limit_rad_s','profile','autonomy_version','training_pid','evaluation_pid','validation_pid','active_log','latest_checkpoint','training_phase','trainer_deadline_epoch']},processes=rows,pending_intermediate5=state.get('pending_intermediate5'),consecutive=state.get('consecutive'),failed_blocks=state.get('failed_blocks'),rate_rejected=state.get('rate_rejected'),budget=dict(total=ledger['authorized_training_seconds'],charged=ledger['charged_training_seconds'],remaining_live=remaining,active_segment=ledger.get('active_segment')),log_tail=log.read_text(errors='replace')[-2400:] if log.is_file() else None,gpu=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.used,temperature.gpu','--format=csv,noheader'],capture_output=True,text=True).stdout.strip())
if x.get('stage')=='training' and float(x.get('yaw_limit_rad_s',0))==5.:
 pid=x['training_pid'];runs=[]
 for m in (root/'logs').glob('*/run_manifest.json'):
  manifest=read(m)
  saved=m.parent/'latest_complete.json'
  if saved.exists() and read(saved).get('pid')==pid:runs.append((m.parent,manifest))
 if len(runs)==1:
  run,manifest=runs[0];out['run_manifest']=manifest
  if (run/'latest_complete.json').exists():
   receipt=read(run/'latest_complete.json');assert receipt['pid']==pid
   checkpoint=Path(receipt['checkpoint']);checkpoint=checkpoint if checkpoint.is_absolute() else run/checkpoint
   sys=__import__('sys');sys.path.insert(0,str(code));import supervise_native_floor as base
   out['full_checkpoint']=base.checkpoint(checkpoint);out['latest_complete']=receipt
   entry=reports/'TARGETED_MATURE5_ENTRY_20261003.json'
   if x.get('training_phase')=='intermediate5_trial45':
    source=read(entry)['source'] if entry.exists() else read(reports/'INTERMEDIATE5_CONTROLLER_HANDOVER_20261003.json')['source']
   else:
    trainer=ident(pid);assert trainer and trainer['cwd']==str(root)
    args=trainer['argv'];source=base.checkpoint(Path(args[args.index('--init_checkpoint')+1]))
   assert out['full_checkpoint']['finite_tensors']==68 and manifest['start_iteration']==source['iteration_stored'] and manifest['env']['RM_KEEP_STD']=='1'
   assert float(manifest['env']['RM_SPIN_MAX_RAD_S'])==5. and manifest['env']['RM_MILD_DR_PROFILE']=='white_v2'
   assert manifest['init_checkpoint_sha256']==source['sha256'] and manifest['init_checkpoint']==source['path']
   freeze=read(reports/'SPIN_SOURCE_FREEZE.json')
   for name,digest in freeze['sha256'].items():assert hashlib.sha256((Path(name) if Path(name).is_absolute() else root/name).read_bytes()).hexdigest()==digest,name
   out['source_count_verified']=len(freeze['sha256']);out['formal_trial_started_and_complete_save_verified']=True
   dest=reports/('TARGETED_MATURE5_PRODUCTION_VERIFIED_20261003.json' if entry.exists() else 'INTERMEDIATE5_PRODUCTION_VERIFIED_20261003.json')
   if x.get('training_phase')=='intermediate5_trial45' and not dest.exists():dest.write_text(json.dumps(out,indent=2))
print(json.dumps(out))
'''
c=connect()
try:
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60)
 raw=o.read().decode();error=e.read().decode();assert o.channel.recv_exit_status()==0,error
 (D/'INTERMEDIATE5_RUNTIME_ACTUAL.json').write_text(raw)
 x=json.loads(raw);print(json.dumps({k:v for k,v in x.items() if k!='run_manifest'},ensure_ascii=False,indent=2))
finally:c.close()
