from pathlib import Path
import sys,json,time,traceback,importlib.util
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''from pathlib import Path
import json,time,fcntl,psutil
root=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_NATIVE_2610v90');owner=root/'owner';node=root/'node_h1';job=root/'h1'
read=lambda p:json.loads(p.read_bytes());start=time.time()
while not all((owner/x).is_file() for x in ('COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json')) or not (node/'NODE_EXIT_ACTUAL.json').is_file():
 assert time.time()-start<180;time.sleep(2)
cohort=read(owner/'COHORT_FINAL.json');terminal=read(node/'NODE_TERMINAL_ACTUAL.json')['row'];assert cohort['original_cost_settled'] and terminal['original_error'] and terminal['terminal_all_own_children_waited'] and terminal['final'] is None
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw);assert c['active_segment'] is None
g=cohort['go']['h1'];seg=[x for x in c['completed_segments'] if x['owner_parent_pid']==549149 and x['experts']['h1']['started_epoch']==g['learning_started_epoch']];assert len(seg)==1
own=[]
for r in v['own']:
 try:
  p=psutil.Process(r['pid']);creation=p.create_time()
  assert creation!=r['creation'] or p.status()==psutil.STATUS_ZOMBIE,'original own process still executing'
  own.append(dict(pid=r['pid'],out_or_nonexecuting=True,no_other_identity_read=True))
 except psutil.NoSuchProcess:own.append(dict(pid=r['pid'],out=True))
for p in (C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock',C.parent.parent/'finite_environment_validation.lock'):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
texts=[]
for directory in (owner,node,job):
 for p in directory.iterdir():
  if p.is_file() and p.suffix in ('.json','.log') and p.stat().st_size<1000000:texts.append(dict(path=str(p),text=p.read_text(errors='replace')))
for p in (job/'job0').glob('production*'):
 if p.is_file() and p.suffix in ('.json','.log') and p.stat().st_size<1000000:texts.append(dict(path=str(p),text=p.read_text(errors='replace')))
assert C.read_bytes()==raw
print(json.dumps(dict(actual_early_error_original_fee_allout=True,cohort=cohort,terminal=terminal,segment=seg[0],fee=seg[0]['charged_expert_seconds'],closing=c['remaining_training_seconds'],canonical_None=True,locks_free=True,own=own,texts=texts,no_model_GPU_or_account_write=True)))'''
def main():
 put('FLAT90_EARLY_ERROR_FORENSIC_STARTED_ACTUAL.json',dict(epoch=time.time()))
 a=json.loads((R/'FLAT90_ACTUAL_OWNER_NODE_DETACHED_RETURNED.json').read_bytes());own=[a['owner'],a['node']]
 v=json.loads((R/'FLAT90_FIRST_ACTUAL_NATIVE_POLICY_RETURNED_ACTUAL.json').read_bytes());r=v['node_current']['row'].get('worker')
 if r:own.append(r)
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('flat90error_secretmemory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=None
 try:
  c=d.connect72(secret);secret=None;q=d.code(c,d.PY72,CODE,dict(own=own),timeout=240);put('FLAT90_EARLY_WORKER_ERROR_FEE_ALLOUT_ACTUAL.json',q)
  print(json.dumps(dict(fee=q['fee'],closing=q['closing'],errors=[x for x in q['texts'] if 'H1_PHASE_ORIGINAL_ERROR' in x['path'] or 'production_WORKER.log' in x['path'] ])))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('FLAT90_EARLY_FORENSIC_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc()));raise
