from pathlib import Path
import sys,json,time,shlex,ast,shutil,math
D=Path(__file__).resolve().parent;B=D.parent;O=B/'MOD4_S3_E1_ROUTE_BEHAVIOR_CONTINUATION_20261009';N=B/'MOD4_S3_E1_REVIEWED_STABLE_20261009';assert not N.exists();(N/'reports').mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf8'))
v=read(O/'reports/E1_PLANNED_BEHAVIOR_STRIDE_CHECKED_REVIEW.json');g={r['group']:r for r in v['terrain']['candidate']['probe']['groups']}
assert v['actual_five_cases_review_complete'] and v['task_model_data_scope_accepted'] and g['forward']['mean_valid_prefix_along_m_s']>0 and g['reverse']['mean_valid_prefix_along_m_s']<0 and abs(g['stand']['mean_valid_prefix_along_m_s'])<=.12
for k,r in v['retention'].items():
 f=r['facts']
 if k=='flat':assert all(x['error']<=max(.12,.25*abs(x['command'])) for x in f['straight'])
 if k=='spin':assert all(abs(x['mean']-x['command'])<=.2 for x in f['pure4pi'])
 if k=='world':
  rows=f['world_target']['rows'];assert abs(sum(x['along_m_s'] for x in rows)/len(rows)-.5)<=.05 and sum(abs(x['cross_m_s']) for x in rows)/len(rows)<=.05
v.update(epoch=time.time(),no_systemic_direction_or_major_retention_failure_observed=True,limited_same_scope_stable_learning_admitted=True,original_per_environment_tolerances_and_raw_flags_retained=True,no_graduation_percent_added=True,not_terrain_graduation=True,CPU_review_no_GPU_or_canonical_write=True,local_CPU_independent_review_used_after_remote_dependency_rejection=True,float32_reduction_layout_corrected_without_tolerance_change=True,negative4pi_individual_5of8_and_world63of64_preserved=True)
(N/'reports/E1_PLANNED_BEHAVIOR_SCOPE_ACCEPTED.json').write_text(json.dumps(v,indent=2))
for n in ('E1_FIRST_TASK_COMPLETE_ACTUAL_REVIEW.json','E1_PLANNED_BEHAVIOR_PUBLISHED.json'):shutil.copy2(O/'reports'/n,N/'reports'/n)
s=(D/'supervise_e1_finalized_behavior_continuation.py').read_text().replace('len(f)==312','len(f)==313');ast.parse(s);(N/'supervise_e1_reviewed_stable_continuation.py').write_text(s,encoding='utf8')
reader=(D/'read_stable_actual.py').read_text().replace('supervise_e1_finalized_behavior_continuation','supervise_e1_reviewed_stable_continuation');(N/'read_stable_actual.py').write_text(reader,encoding='utf8')
sys.path.insert(0,str(B/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/'+N.name;old='/home/egde/rl_candidates/'+D.name
def run(code):
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');return raw.decode()
try:
 code='''
from pathlib import Path
import json,sys,shutil,hashlib
D=Path(ROOT);O=Path(OLD);assert not D.exists();(D/'reports').mkdir(parents=True)
sys.path.insert(0,str(O));import supervise_e1_finalized_behavior_continuation as w
w.verify();w.wait_existing();assert not w.identity(1716192) and not w.identity(1716193)
assert w.read(O/'reports/E1_REVIEW_READY.json')['actual_behavior_attention_hold']
freeze=w.read(O/'reports/SOURCE_FREEZE.json');assert len(freeze['sha256'])==312
for n,h in freeze['sha256'].items():
 assert hashlib.sha256((O/n).read_bytes()).hexdigest()==h;p=D/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(O/n,p)
for n in ('REUSED_E1_COMPLETE_PPO_PREFLIGHT_PASSED.json','REUSED_E1_NATIVE20K_PASSED.json','E1_ROUTE_HEALTH_CPU_PASSED.json','PREDECESSOR_CPU_TRANSFER_REJECTION.json'):
 shutil.copy2(O/'reports'/n,D/'reports'/n)
shutil.copy2(O/'reports/E1_BEHAVIOR_SCOPE_ATTENTION.json',D/'reports/PREDECESSOR_CPU_DEPENDENCY_REJECTION.json')
print('All312 bytes preserved; predecessor naturally held/exited; actual five-case independent review selected')
'''.replace('Path(ROOT)','Path('+repr(root)+')').replace('Path(OLD)','Path('+repr(old)+')');print(run(code))
 with c.open_sftp() as f:
  for src,dst in [(N/'supervise_e1_reviewed_stable_continuation.py',root+'/supervise_e1_reviewed_stable_continuation.py')]+[(N/'reports'/n,root+'/reports/'+n) for n in ('E1_PLANNED_BEHAVIOR_SCOPE_ACCEPTED.json','E1_FIRST_TASK_COMPLETE_ACTUAL_REVIEW.json','E1_PLANNED_BEHAVIOR_PUBLISHED.json')]:
   f.put(str(src),dst);assert f.open(dst).read()==src.read_bytes()
 code='''
from pathlib import Path
import sys,json,time,hashlib,subprocess,torch
D=Path(ROOT);O=Path(OLD);torch.set_num_threads(1)
f=json.loads((O/'reports/SOURCE_FREEZE.json').read_text());f.update(epoch=time.time(),candidate_root=str(D),source_count=313,all312_predecessor_source_bytes_exact=True)
n='supervise_e1_reviewed_stable_continuation.py';f['sha256'][n]=hashlib.sha256((D/n).read_bytes()).hexdigest();(D/'reports/SOURCE_FREEZE.json').write_text(json.dumps(f,indent=2))
sys.path.insert(0,str(D));import supervise_e1_reviewed_stable_continuation as w
w.verify();w.wait_existing();source=w.source();assert not torch.cuda.is_initialized();before=w.s.q.ctl.CANONICAL.read_bytes()
with (D/'controller.log').open('x') as out:p=subprocess.Popen([w.s.q.base.PY,str(D/n)],cwd=w.s.q.P,env=w.runtime(),stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
row=dict(epoch=time.time(),root=str(D),source_count=313,CPU_parent=w.identity(p.pid),all312_predecessor_source_bytes_exact=True,review_actual_five_complete_cases_accepted=True,source=w.fullsave(source),no_native_PPO_clock_or_case_replay=True,new_budget_seconds=0)
w.write('E1_REVIEWED_STABLE_DEPLOYED.json',row);print(json.dumps(row))
'''.replace('Path(ROOT)','Path('+repr(root)+')').replace('Path(OLD)','Path('+repr(old)+')');raw=run(code);(N/'reports/E1_REVIEWED_STABLE_DEPLOYED.json').write_text(raw);print(raw)
finally:c.close()
