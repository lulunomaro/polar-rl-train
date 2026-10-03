"""Read-only verification of the applied authority and running controller."""
import json, shlex, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
D=Path(__file__).parent
CODE=r'''
import hashlib,json,os,sys,time
from pathlib import Path
root=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
sys.path.insert(0,str(root/'isaac/mod4'))
from budget_authority import validate_budget
status=json.loads((root/'status.json').read_text());state=json.loads((root/'reports/AUTONOMY_STATE.json').read_text())
budget=json.loads(Path(status['canonical_budget']).read_text());total=validate_budget(budget)
assert total==252000
extensions=budget['budget_extensions'];assert len([e for e in extensions if e['extension_id']=='USER_ADD20H_20261003_3RD'])==1
frozen=json.loads((root/'reports/SPIN_SOURCE_FREEZE.json').read_text())['sha256'];mismatch=[]
for name,expected in frozen.items():
 p=Path(name) if Path(name).is_absolute() else root/name
 actual=hashlib.sha256(p.read_bytes()).hexdigest()
 if actual!=expected:mismatch.append(dict(path=str(p),expected=expected,actual=actual))
assert not mismatch
processes=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  argv=p.joinpath('cmdline').read_bytes().decode().strip('\0').split('\0')
  if '-c' in argv or not any(str(root) in x for x in argv):continue
  fields=p.joinpath('stat').read_text().split(') ',1)[1].split()
  processes.append(dict(pid=int(p.name),state=fields[0],ppid=int(fields[1]),session=int(fields[3]),start_ticks=int(fields[19]),cwd=os.readlink(p/'cwd'),argv=argv))
 except (OSError,ValueError):pass
parents=[p for p in processes if any(x.endswith('/supervise_autonomy.py') for x in p['argv']) and '--resume' in p['argv']]
assert len(parents)==1 and parents[0]['pid']==status['supervisor_pid']
assert len([p for p in processes if any(x.endswith('/train_mod4_ppo.py') for x in p['argv'])])<=1
active=budget.get('active_segment');now=time.time()
charged=float(budget['charged_training_seconds'])
runtime_remaining=status.get('remaining_training_seconds')
keys=['stage','supervisor_pid','training_pid','evaluation_pid','active_log','budget_seconds','authorized_training_seconds','autonomy_version','profile','yaw_limit_rad_s','iteration','latest_checkpoint','last_health_check','updated_at']
log=Path(status['active_log']).read_text(errors='replace')[-150000:]
errors=[x for x in log.splitlines() if any(t in x for t in ('Traceback (most recent call last)','CUDA out of memory','PhysX error','PxError','Xid','NaN'))]
result=dict(epoch=now,canonical_budget=status['canonical_budget'],authorized_training_seconds=total,charged_training_seconds=charged,remaining_training_seconds_status=runtime_remaining,remaining_at_last_settlement=total-charged,active_segment=active,budget_extensions=extensions,status={k:status.get(k) for k in keys},processes=processes,source_checked=len(frozen),source_mismatches=mismatch,controller_sha256=frozen['isaac/mod4/supervise_autonomy.py'],rate_rejected=state.get('rate_rejected'),chosen_checkpoint=state.get('chosen_checkpoint'),recent_active_log_errors=errors[-15:])
print(json.dumps(result))
'''
c=connect()
try:
 _,out,err=c.exec_command('python3 -c '+shlex.quote(CODE),timeout=45)
 raw=out.read().decode();errors=err.read().decode();exit_code=out.channel.recv_exit_status()
 if errors:print(errors,file=sys.stderr)
 assert exit_code==0,raw
 result=json.loads(raw)
 (D/'VERIFIED.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({k:result[k] for k in ['authorized_training_seconds','charged_training_seconds','remaining_training_seconds_status','status','source_checked','source_mismatches','recent_active_log_errors']}))
 print(json.dumps({'runtime_processes':[{k:p[k] for k in ('pid','state','start_ticks','ppid','session')} for p in result['processes']],'extension_ids':[e['extension_id'] for e in result['budget_extensions']]}))
finally:c.close()
