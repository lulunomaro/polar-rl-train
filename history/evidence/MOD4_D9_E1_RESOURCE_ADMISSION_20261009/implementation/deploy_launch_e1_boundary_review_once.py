"""New exact boundary reader authority after pre-GPU admission path rejection."""
from pathlib import Path
import sys,json,shlex,time
D=Path(__file__).resolve().parent;R=D/'reports';root='/home/egde/rl_candidates/MOD4_S3_E1_FULL_CONTRACT_20261009'
assert not (R/'E1_PATH_REVIEW_LAUNCHED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 with c.open_sftp() as sf:
  target=root+'/supervise_e1_boundary_path_review.py'
  try:sf.stat(target);raise AssertionError('New entry already deployed')
  except FileNotFoundError:pass
  sf.put(str(D/'supervise_e1_boundary_path_review.py'),target)
  assert sf.open(target).read()==(D/'supervise_e1_boundary_path_review.py').read_bytes()
 code=r'''
from pathlib import Path
import sys,json,hashlib,subprocess,time,torch,ast
D=Path(ROOT);R=D/'reports';sys.path.insert(0,str(D));torch.set_num_threads(1)
assert not (R/'E1_DISPATCH_STARTED.json').exists() and not (R/'E1_LAUNCHED.json').exists() and not (R/'E1_PATH_REVIEW_LAUNCHED.json').exists() and not (D/'controller.log').exists()
f=json.loads((R/'SOURCE_FREEZE.json').read_text());assert len(f['sha256'])==295
for n,h in f['sha256'].items():assert hashlib.sha256((D/n).read_bytes()).hexdigest()==h
(R/'SOURCE_FREEZE_BEFORE_BOUNDARY_PATH_REVIEW.json').write_text(json.dumps(f,indent=2))
name='supervise_e1_boundary_path_review.py';ast.parse((D/name).read_text());f['sha256'][name]=hashlib.sha256((D/name).read_bytes()).hexdigest();f['source_count']=296;f['epoch']=time.time();f['only_new_boundary_reader_added']=True
(R/'SOURCE_FREEZE.json').write_text(json.dumps(f,indent=2))
import supervise_e1_boundary_path_review as reviewed
w=reviewed.w;w.verify();src=w.source();reviewed.wait_actual_D7_boundary();assert not torch.cuda.is_initialized()
reject=dict(epoch=time.time(),error='Original admission reader used inherited D6_STATE.json/D6_GUARDIAN names for actual D7 boundary; FileNotFound before Popen/GPU/segment.',old_source_retained=True,old_entry_not_rerun=True,new_entry=name,before_GPU_PPO_and_budget_transaction=True)
w.write('E1_ORIGINAL_BOUNDARY_PATH_REJECTED.json',reject)
before=w.s.q.ctl.CANONICAL.read_bytes()
with (D/'controller_path_review.log').open('x') as out:
 p=subprocess.Popen([w.s.q.base.PY,str(D/name)],cwd=w.s.q.P,env=w.runtime(),stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
ident=w.identity(p.pid);assert ident and str(D/name) in ident['argv']
row=dict(epoch=time.time(),parent=ident,source=w.fullsave(src,require_e1=False),source_count=296,all295_original_staged_bytes_exact=True,all277_D7_predecessor_exact=True,old_D7_boundary_actual_verified=True,first_new_terrain_task_seconds=2700,repeated45min_clock_trial=False,native_then_complete_new_scope_PPO_required=True,formal_learning_not_yet_claimed=True,new_budget_seconds=0,budget_bytes_exact_at_dispatch=before==w.s.q.ctl.CANONICAL.read_bytes())
w.write('E1_PATH_REVIEW_LAUNCHED.json',row);print(json.dumps(dict(parent=ident,source_SHA=row['source']['sha256'],source_count=296,native_then_PPO=True,new_budget_seconds=0)))
'''.replace('ROOT',repr(root))
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=120)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 with c.open_sftp() as sf:
  for n in ('SOURCE_FREEZE.json','SOURCE_FREEZE_BEFORE_BOUNDARY_PATH_REVIEW.json','E1_ORIGINAL_BOUNDARY_PATH_REJECTED.json','E1_PATH_REVIEW_LAUNCHED.json'):sf.get(root+'/reports/'+n,str(R/n))
 print(raw.decode())
finally:c.close()
