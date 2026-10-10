"""Capture actual central review context and own exited PID/OS-lock boundary."""
from review133_io import *
import traceback
def main():
 n,w=connect_both()
 try:
  names=['PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOE_PLAN_EXECUTION_CURRENT.json','LATEST_HANDOFF.md','MOD4_MOE_MASTER_PLAN.md','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','MOE_TERRAIN_SUBEXPERT_REVISION_004_APPROVAL.json','E1_CURB20_FORMAL_REVIEWED_FORMAL_FINAL_ACTUAL_REVIEW.json','E1_CURB20_FORMAL_REVIEWED_OWN_FINAL_CPU_VERIFIED.json','E1_CURB20_FORMAL_REVIEWED_FORMAL_FINAL_CURRENT_ACTUAL.json','E1_CURB20_FORMAL_REVIEWED_FORMAL_CLOSEOUT_METADATA_SYNCED.json','E1_CURB20_133_ACTUAL_COLLECTION_SCHEMA_REVIEWED.json','E1_CURB20_133_PARTIAL_ACTUAL_SCHEMA_REVIEW.json','E1_CURB20_133_ACTUAL_SCHEMA_READER_REVIEW.json','NEXT_E1_CURB20_133_ACTUAL_REVIEW_WORK_ORDER_V2.md']
  files=[];folder=D/'central_actual'/str(time.time_ns());folder.mkdir(parents=True)
  with n.open_sftp() as f:
   for name in names:
    raw=f.open(E+'/reports/'+name).read();p=folder/name;p.write_bytes(raw)
    files.append(dict(source=E+'/reports/'+name,local_path=str(p),bytes=len(raw),sha256=H(raw),capture='complete_exact_bytes'))
  v=linux_json(n,r'''from pathlib import Path
import json,time,hashlib,fcntl
R=Path(CENTRAL)/'reports';B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes());l=j(B);cur=j(R/'MOE_PLAN_EXECUTION_CURRENT.json');cpu=j(R/'E1_CURB20_FORMAL_REVIEWED_OWN_FINAL_CPU_VERIFIED.json')
assert cpu['passed'] and cpu['checkpoint']['sha256']=='df0c141d444a6a85b983e49eedad10e91e0b7b264f627bff972dbd7cb1f2c753'
assert hashlib.sha256(Path(cpu['checkpoint']['path']).read_bytes()).hexdigest()==cpu['checkpoint']['sha256']
rev=cur['terrain_subexpert_revision004'];assert rev['approved'] and rev['curb20_formal_reviewed_scope']['root']==ROOT
locs=[dict(pid=2447069,start_ticks=81560593),dict(pid=2447143,start_ticks=81560729),dict(pid=2447175,start_ticks=81560752)];procs=[]
for v in locs:
 p=Path('/proc')/str(v['pid']);actual=None
 if p.exists():
  a=(p/'stat').read_text().split(') ',1)[1].split();actual=dict(state=a[0],start_ticks=int(a[19]));assert actual['state']=='Z' or actual['start_ticks']!=v['start_ticks']
 procs.append(dict(locator=v,actual=actual))
locks=[]
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(p),held=False))
assert l['active_segment'] is None and l['authorized_training_seconds']==828000
assert hashlib.sha256((R/'MOD4_MOE_MASTER_PLAN.md').read_bytes()).hexdigest()=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
print(json.dumps(dict(epoch=time.time(),revision004=rev,own_final_checkpoint=cpu['checkpoint'],actual_processes=procs,OS_locks=locks,canonical_sha256=hashlib.sha256(B.read_bytes()).hexdigest(),remaining_seconds=l['authorized_training_seconds']-l['charged_training_seconds'],active_segment=l['active_segment'],authorized_seconds=l['authorized_training_seconds'],original_master_SHA_verified=True,new_budget_seconds=0)))
'''.replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)).replace('ROOT',repr(NEW)))
  v.update(files=files,no_GPU_queue_or_canonical_mutation=True);p=save('CENTRAL133_ACTUAL_CONTEXT_'+str(time.time_ns())+'.json',v)
  print(json.dumps(dict(report=str(p),active_next_expert=v['revision004']['active_next_expert'],remaining_seconds=v['remaining_seconds'],all_three_own_processes_exited=True,two_original_OS_locks_free=True,master_verified=True)))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('CENTRAL133_CONTEXT_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only=True,no_blind_mutation=True));raise
