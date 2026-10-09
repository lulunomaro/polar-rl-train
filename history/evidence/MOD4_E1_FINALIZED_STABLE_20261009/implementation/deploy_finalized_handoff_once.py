from pathlib import Path
import sys,json,shlex,time,hashlib
D=Path(__file__).resolve().parent;B=D.parent;R=D/'reports';assert not (R/'FINALIZED_HANDOFF_DEPLOYED.json').exists()
sys.path.insert(0,str(B/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/'+D.name;old='/home/egde/rl_candidates/MOD4_S3_E1_ROUTE_BEHAVIOR_CONTINUATION_20261009';cpu='/home/egde/rl_candidates/MOD4_E1_FINALIZED_ADMISSION_CPU_20261009'
def run(code,py='/usr/bin/python3'):
 _,o,e=c.exec_command(py+' -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');return raw.decode()
try:
 code='''
from pathlib import Path
import json,hashlib,shutil,sys
O=Path(OLD);D=Path(ROOT);C=Path(CPU);assert not D.exists() and not C.exists();(D/'reports').mkdir(parents=True);(C/'reports').mkdir(parents=True)
sys.path.insert(0,str(O));import supervise_e1_behavior_stable_continuation as w
w.verify();w.wait_existing();assert w.identity(1709220) is None and w.identity(1712884) is None
attention=w.read(O/'reports/E1_BEHAVIOR_SCOPE_ATTENTION.json');assert 'hashlib.sha256' in attention['error']
assert w.read(O/'reports/E1_REVIEW_READY.json')['actual_behavior_attention_hold'];before=w.s.q.ctl.CANONICAL.read_bytes()
freeze=w.read(O/'reports/SOURCE_FREEZE.json');assert len(freeze['sha256'])==311
for n,h in freeze['sha256'].items():
 assert hashlib.sha256((O/n).read_bytes()).hexdigest()==h
 p=D/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(O/n,p)
for n in ('REUSED_E1_COMPLETE_PPO_PREFLIGHT_PASSED.json','REUSED_E1_NATIVE20K_PASSED.json','E1_ROUTE_HEALTH_CPU_PASSED.json'):
 shutil.copy2(O/'reports'/n,D/'reports'/n)
shutil.copy2(O/'reports/E1_BEHAVIOR_SCOPE_ATTENTION.json',D/'reports/PREDECESSOR_CPU_TRANSFER_REJECTION.json')
shutil.copy2(O/'reports/E1_REVIEW_READY.json',D/'reports/PREDECESSOR_REVIEW_HOLD.json')
assert before==w.s.q.ctl.CANONICAL.read_bytes()
print('Old CPU authority naturally closed, no child or active, all311 source exact; no budget mutation')
'''.replace('Path(OLD)','Path('+repr(old)+')').replace('Path(ROOT)','Path('+repr(root)+')').replace('Path(CPU)','Path('+repr(cpu)+')')
 print(run(code,'/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'))
 with c.open_sftp() as f:
  copies=[(D/'supervise_e1_finalized_behavior_continuation.py',root+'/supervise_e1_finalized_behavior_continuation.py'),(D/'cpu_behavior_finalized_admission.py',cpu+'/cpu_behavior_admission.py'),(D/'review_completed_behavior.py',cpu+'/review_completed_behavior.py')]
  for n in ('E1_FIRST_TASK_COMPLETE_ACTUAL_REVIEW.json','E1_PLANNED_BEHAVIOR_PUBLISHED.json'):copies.append((R/n,root+'/reports/'+n))
  copies.append((R/'E1_PLANNED_BEHAVIOR_PUBLISHED.json',cpu+'/reports/E1_PLANNED_BEHAVIOR_PUBLISHED.json'))
  for src,dst in copies:f.put(str(src),dst);assert f.open(dst).read()==src.read_bytes()
 code='''
from pathlib import Path
import sys,json,time,hashlib,subprocess,ast,torch
D=Path(ROOT);O=Path(OLD);C=Path(CPU);torch.set_num_threads(1)
f=json.loads((O/'reports/SOURCE_FREEZE.json').read_text());f.update(epoch=time.time(),candidate_root=str(D),source_count=312,all311_predecessor_source_bytes_exact=True)
n='supervise_e1_finalized_behavior_continuation.py';ast.parse((D/n).read_text());f['sha256'][n]=hashlib.sha256((D/n).read_bytes()).hexdigest();(D/'reports/SOURCE_FREEZE.json').write_text(json.dumps(f,indent=2))
sys.path.insert(0,str(D));import supervise_e1_finalized_behavior_continuation as w
w.verify();w.wait_existing();assert not torch.cuda.is_initialized();before=w.s.q.ctl.CANONICAL.read_bytes()
with (C/'controller.log').open('x') as out:p=subprocess.Popen([w.s.q.base.PY,str(C/'cpu_behavior_admission.py')],cwd=C,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
ci=w.identity(p.pid)
with (D/'controller.log').open('x') as out:p=subprocess.Popen([w.s.q.base.PY,str(D/n)],cwd=w.s.q.P,env=w.runtime(),stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
pi=w.identity(p.pid)
row=dict(epoch=time.time(),root=str(D),source_count=312,CPU_review_root=str(C),CPU_review_identity=ci,CPU_parent=pi,all311_predecessor_source_bytes_exact=True,old_CPU_and_parent_actual_exited=True,no_native_PPO_clock_or_case_replay=True,canonical_bytes_exact_at_CPU_dispatch=before==w.s.q.ctl.CANONICAL.read_bytes(),new_budget_seconds=0)
w.write('FINALIZED_HANDOFF_DEPLOYED.json',row);print(json.dumps(row))
'''.replace('Path(ROOT)','Path('+repr(root)+')').replace('Path(OLD)','Path('+repr(old)+')').replace('Path(CPU)','Path('+repr(cpu)+')')
 raw=run(code,'/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python');v=json.loads(raw);(R/'FINALIZED_HANDOFF_DEPLOYED.json').write_text(json.dumps(v,indent=2));print(raw)
finally:c.close()
