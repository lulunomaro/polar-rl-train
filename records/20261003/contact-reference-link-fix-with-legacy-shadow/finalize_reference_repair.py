"""Verify a completed repair and synchronize its evidence; never starts simulation."""
import hashlib, json, shlex, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
D=Path(__file__).resolve().parent
ROOT='/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002'
MARKER='CONTACT_REFERENCE_LINK_FIX_COMPLETED_20261003'
code=r'''
import hashlib,json,time
from pathlib import Path
R=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
def read(p):return json.loads(p.read_text())
def ident(pid):
 p=Path('/proc')/str(pid)
 if not p.exists():return None
 try:
  fields=(p/'stat').read_text().split(') ',1)[1].split()
  return dict(pid=int(pid),state=fields[0],start_ticks=fields[19],cwd=str((p/'cwd').resolve()),argv=(p/'cmdline').read_bytes().decode().replace(chr(0),' ').strip())
 except (FileNotFoundError,ProcessLookupError,PermissionError):return None
receipt=read(R/'reports/CONTACT_REFERENCE_FIX_FROZEN_V2_20261003.json')
assert receipt['stage']=='reference_fix_applied' and receipt['charged_unchanged_in_frozen_window']
freeze=read(R/'reports/SPIN_SOURCE_FREEZE.json')
bad=[]
for name,expected in freeze['sha256'].items():
 p=Path(name) if Path(name).is_absolute() else R/name
 if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:bad.append(name)
assert not bad,bad
status=read(R/'status.json');state=read(R/'reports/AUTONOMY_STATE.json')
ledger=read(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'))
parent=ident(2490960);guardian=ident(2490993)
assert parent and parent['start_ticks']=='17250655' and parent['state'] not in ('T','Z') and parent['cwd']==str(R)
assert guardian and guardian['start_ticks']=='17250722' and guardian['state']!='Z'
assert ledger['authorized_training_seconds']==252000 and 6.0 in state['rate_rejected']
trainers=[];evaluators=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 x=ident(int(p.name))
 if not x or x['cwd']!=str(R) or x['state']=='Z':continue
 if '/train_mod4_ppo.py' in x['argv']:trainers.append(x)
 elif '/spin_rate_probe.py' in x['argv'] or '/validate_speed.py' in x['argv']:evaluators.append(x)
assert len(trainers)<=1 and len(evaluators)<=1
current_env=read(R/'isaac/mod4/env.json')
assert float(current_env['RM_SPIN_MAX_RAD_S'])==4 and current_env['RM_MILD_DR_PROFILE']=='white_v2'
proof=dict(marker='CONTACT_REFERENCE_LINK_FIX_COMPLETED_20261003',epoch=time.time(),stage=status['stage'],profile='white_v2',yaw_limit_rad_s=4.0,parent=parent,guardian=guardian,trainers=trainers,evaluators=evaluators,source_count=len(freeze['sha256']),all_source_hashes_match=True,evaluation_reference_version='wheel_link_support_velocity_v2',repaired_files=receipt['source_hashes'],rate_rejected=state['rate_rejected'],canonical_budget=status.get('canonical_budget'),authorized_seconds=ledger['authorized_training_seconds'],charged_seconds=ledger['charged_training_seconds'],active_segment=ledger.get('active_segment'),settled_remaining_seconds=ledger['authorized_training_seconds']-ledger['charged_training_seconds'],saved_checkpoint=receipt['complete_saved_checkpoint'],frozen_budget_unchanged=receipt['charged_unchanged_in_frozen_window'],physics_reward_PPO_DR_hardware_unchanged=True)
print(json.dumps(proof))
'''
c=connect()
try:
 _,out,err=c.exec_command('python3 -c '+shlex.quote(code),timeout=60)
 data=out.read();error=err.read().decode();assert out.channel.recv_exit_status()==0,error
 proof=json.loads(data)
 (D/'CONTACT_REFERENCE_PRODUCTION_VERIFIED.json').write_text(json.dumps(proof,indent=2,ensure_ascii=False),encoding='utf8')
 with c.open_sftp() as s:
  for name in ['SPIN_SOURCE_FREEZE.json','auto_0022_assessment_cap4_white_v2_decision.json']:
   try:s.get(ROOT+'/reports/'+name,str(D/name))
   except FileNotFoundError:pass
  for name in ['contact_geometry.py','spin_rate_probe.py','validate_speed.py','SPIN_SOURCE_FREEZE.json']:
   s.get(ROOT+'/reports/contact_reference_fix_before_20261003/'+name,str(D/('BEFORE_'+name)))
  for remote in [ROOT+'/reports/CONTACT_REFERENCE_PRODUCTION_VERIFIED.json',ROOT+'/reports/CONTACT_REFERENCE_REPAIR_20261003.md','/home/egde/rl_candidates/MOD4_RATE6_SLIP_REPAIR_20261003/REPORT.md']:
   try:s.stat(remote)
   except FileNotFoundError:pass
   else:raise RuntimeError('Completed receipt already exists; do not repeat: '+remote)
   local=D/('CONTACT_REFERENCE_PRODUCTION_VERIFIED.json' if remote.endswith('.json') else 'REPORT.md')
   s.put(str(local),remote)
  note='\n\n'+(D/'HANDOFF_APPEND.md').read_text(encoding='utf8')
  for remote in [ROOT+'/PLAN_AUTONOMY_SLEEP_20261003.md','/home/egde/rl_candidates/MOD4_AUTONOMY_SLEEP_20261003/PLAN_AND_HANDOFF.md']:
   with s.open(remote,'r') as f:previous=f.read().decode('utf8')
   assert MARKER not in previous,'Handoff already synchronized'
   with s.open(remote,'w') as f:f.write((previous+note).encode('utf8'))
 local= D.parent/'MOD4_AUTONOMY_SLEEP_20261003/PLAN_AND_HANDOFF.md'
 previous=local.read_text(encoding='utf8');assert MARKER not in previous
 local.write_text(previous+'\n\n'+(D/'HANDOFF_APPEND.md').read_text(encoding='utf8'),encoding='utf8')
 print(json.dumps({k:proof[k] for k in ['stage','profile','yaw_limit_rad_s','source_count','all_source_hashes_match','rate_rejected','authorized_seconds','charged_seconds','settled_remaining_seconds','trainers','evaluators']},ensure_ascii=False))
finally:c.close()
