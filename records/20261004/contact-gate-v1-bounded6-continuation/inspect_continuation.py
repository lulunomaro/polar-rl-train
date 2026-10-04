"""Read actual contact-controller phase and exact PID-bound receipts; no mutation."""
import argparse,json,shlex,sys
from pathlib import Path
D=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--receipt',required=True);a=p.parse_args()
assert Path(a.receipt).name==a.receipt and a.receipt.endswith('.json')
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
code=r'''import json,sys,subprocess,time
from pathlib import Path
import torch
torch.set_num_threads(1)
P=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002');C=Path('/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004');R=C/'reports'
sys.path.insert(0,str(P/'isaac/mod4'));import supervise_autonomy as ctl
read=ctl.read;status=read(P/'status.json');state=read(R/'CONTACT_CONTINUATION_STATE.json')
launch=read(R/'CONTACT_CONTINUATION_LAUNCHED.json');parent=ctl.helpers.identity(launch['pid'])
assert parent and parent['start_ticks']==launch['start_ticks'] and parent['cwd']==str(C) and str(C/'supervise_contact_gate_continue.py') in parent['argv']
g=read(R/'CONTACT_GUARDIAN_STARTED.json');guardian=ctl.helpers.identity(g['pid'])
assert guardian and guardian['start_ticks']==g['start_ticks'] and '--guardian' in guardian['argv']
ids={k:ctl.helpers.identity(status.get(k+'_pid')) for k in ('training','evaluation','validation')}
old=read(P/'reports/SPIN_SOURCE_FREEZE.json');new=read(R/'SOURCE_FREEZE.json')
for name,h in old['sha256'].items():
 q=Path(name);q=q if q.is_absolute() else P/q
 assert ctl.base.sha(q)==h,name
for name,h in new['sha256'].items():assert ctl.base.sha(C/name)==h,name
budget=ctl.base.budget_state();assert budget['authorized_training_seconds']==252000
trainer=ids['training'];run=None;saved=None;manifest=None;freeze=None;ck=None;pending=False
if trainer:
 assert str(C/'isaac/mod4/train_mod4_ppo.py') in trainer['argv'] and ctl.base.trainers()==[trainer['pid']]
 assert budget['active_segment']['pid']==trainer['pid']
 for logs in (P/'logs',P/'autonomy_preflight_logs'):
  try:run=ctl.rate.trainer_run(logs,trainer['pid']);break
  except AssertionError:pass
 if run:
  saved=read(run/'latest_complete.json');assert saved['pid']==trainer['pid'];ck=Path(saved['checkpoint'])
  manifest=read(run/'run_manifest.json') if (run/'run_manifest.json').exists() else None
  freeze=read(run/'rolling_source_freeze.json') if (run/'rolling_source_freeze.json').exists() else None
 else:
  pending=True;ck=Path(trainer['argv'][trainer['argv'].index('--init_checkpoint')+1])
else:
 assert not ctl.base.trainers() and budget.get('active_segment') is None
 child=ids['evaluation'] or ids['validation']
 if child and '--checkpoint' in child['argv']:ck=Path(child['argv'][child['argv'].index('--checkpoint')+1])
info=ctl.base.checkpoint(ck) if ck else None
if info:assert info['finite_tensors']==68
def tail(path,n):
 q=Path(path);return q.read_text(errors='replace')[-n:] if q.exists() else ''
gpu=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.used,temperature.gpu','--format=csv,noheader'],capture_output=True,text=True)
x=dict(epoch=time.time(),status=status,continuation_state=state,parent=parent,guardian=guardian,processes=ids,
       run=str(run) if run else None,latest_complete=saved,run_manifest=manifest,rolling_source_freeze=freeze,
       checkpoint=info,own_trainer_receipt_pending=pending,source_counts=dict(original=len(old['sha256']),candidate=len(new['sha256'])),
       budget=budget,S_active_training=read(ctl.STATE_PATH).get('active_training'),TUI=ctl.helpers.identity(1551130),
       gpu=gpu.stdout.strip(),active_log_tail=tail(status.get('active_log',''),5000),
       supervisor_log_tail=tail(C/'supervisor_contact_gate_continue.log',7000),
       no_launch_settlement_or_config_mutation=True)
print(json.dumps(x))
'''
c=connect()
try:
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=45)
 raw=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,err+raw
 x=json.loads(raw);(D/a.receipt).write_text(json.dumps(x,indent=2),encoding='utf8')
 print(json.dumps({k:x[k] for k in ('epoch','continuation_state','processes','run','checkpoint','own_trainer_receipt_pending','source_counts','gpu','supervisor_log_tail')}))
 print(json.dumps(dict(stage=x['status']['stage'],active_log=x['status'].get('active_log'),remaining=x['budget']['remaining_training_seconds'],budget_active=x['budget'].get('active_segment'))))
finally:c.close()
