from pathlib import Path
import sys,json,time,shlex,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';B=D.parent
assert not (R/'E1_GATED_STABLE_ENTRY_DEPLOYED.json').exists()
read=lambda p:json.loads(p.read_text(encoding='utf8'))
pub=read(R/'E1_PLANNED_BEHAVIOR_PUBLISHED.json');assert len(pub['jobs'])==5
sys.path.insert(0,str(B/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/'+D.name;old='/home/egde/rl_candidates/MOD4_S3_E1_ROUTE_HEALTH_REVIEW_20261009'
try:
 code='''
from pathlib import Path
import json,shutil,hashlib
D=Path(ROOT);OLD=Path(OLDROOT);assert not D.exists();(D/'reports').mkdir(parents=True)
freeze=json.loads((OLD/'reports/SOURCE_FREEZE.json').read_text());assert len(freeze['sha256'])==310
for n,h in freeze['sha256'].items():
 assert hashlib.sha256((OLD/n).read_bytes()).hexdigest()==h,n
 p=D/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/n,p)
for n in ('E1_ROUTE_HEALTH_CPU_PASSED.json','E1_COMPLETE_PPO_PREFLIGHT_PASSED.json','E1_NATIVE20K_PASSED.json'):
 name='REUSED_'+n if n!='E1_ROUTE_HEALTH_CPU_PASSED.json' else n
 shutil.copy2(OLD/'reports'/n,D/'reports'/name)
print('All310 immutable original source files preserved; no training entry executed')
'''.replace('OLDROOT',repr(old)).replace('ROOT',repr(root))
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 with c.open_sftp() as f:
  for src,dst in [(D/'supervise_e1_behavior_stable_continuation.py',root+'/supervise_e1_behavior_stable_continuation.py'),(R/'E1_FIRST_TASK_COMPLETE_ACTUAL_REVIEW.json',root+'/reports/E1_FIRST_TASK_COMPLETE_ACTUAL_REVIEW.json'),(R/'E1_PLANNED_BEHAVIOR_PUBLISHED.json',root+'/reports/E1_PLANNED_BEHAVIOR_PUBLISHED.json')]:
   f.put(str(src),dst);assert f.open(dst).read()==src.read_bytes()
 code='''
from pathlib import Path
import sys,json,time,hashlib,ast,subprocess,torch
D=Path(ROOT);OLD=Path(OLDROOT);R=D/'reports';torch.set_num_threads(1)
freeze=json.loads((OLD/'reports/SOURCE_FREEZE.json').read_text());freeze.update(epoch=time.time(),candidate_root=str(D))
for n,h in freeze['sha256'].items():assert hashlib.sha256((D/n).read_bytes()).hexdigest()==h
n='supervise_e1_behavior_stable_continuation.py';ast.parse((D/n).read_text());freeze['sha256'][n]=hashlib.sha256((D/n).read_bytes()).hexdigest();freeze['source_count']=311;freeze['all_original310_source_bytes_exact']=True
(R/'SOURCE_FREEZE.json').write_text(json.dumps(freeze,indent=2));sys.path.insert(0,str(D));import supervise_e1_behavior_stable_continuation as w
w.verify();w.wait_existing();assert not torch.cuda.is_initialized();before=w.s.q.ctl.CANONICAL.read_bytes()
with (D/'controller.log').open('x') as out:p=subprocess.Popen([w.s.q.base.PY,str(D/n)],cwd=w.s.q.P,env=w.runtime(),stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
identity=w.identity(p.pid);assert identity and str(D/n) in identity['argv']
row=dict(epoch=time.time(),root=str(D),CPU_parent=identity,source_count=311,all310_predecessor_source_bytes_exact=True,entry=n,actual_behavior_gated_no_GPU_or_canonical_write_before_scope_review=True,no_preflight_or_clock_replay=True,new_budget_seconds=0,canonical_bytes_exact_at_CPU_dispatch=before==w.s.q.ctl.CANONICAL.read_bytes())
w.write('E1_GATED_STABLE_ENTRY_DEPLOYED.json',row);print(json.dumps(row))
'''.replace('OLDROOT',repr(old)).replace('ROOT',repr(root))
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
 (R/'E1_GATED_STABLE_ENTRY_DEPLOYED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
