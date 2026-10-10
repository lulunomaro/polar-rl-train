"""Read current CURB authority and exact inherited source; no GPU/ledger/write API."""
from pathlib import Path
import sys,json,time,hashlib,traceback
D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(D.parent/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011'))
from curb_io import connect_both,cleanup,linux_json,E,B,H
OLD='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_INDEPENDENT_20261011'
def main():
 n,w=connect_both()
 try:
  code=r'''from pathlib import Path
import json,hashlib,time,fcntl
D=Path(ROOT);E=Path(CENTRAL);B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes())
s=j(D/'reports/CURB_NATIVE_SCOPE_STATE.json');passed=j(D/'reports/CURB_NATIVE_SCOPE_PASSED.json');l=j(B)
assert s['phase']=='CURB_new_native_contract_complete_review_ready' and s['child'] is None
def proc(v):
 p=Path('/proc')/str(v['pid'])
 if not p.exists():return None
 st=(p/'stat').read_text().split(') ',1)[1].split();a=dict(state=st[0],start_ticks=int(st[19]),argv=(p/'cmdline').read_bytes().split(b'\0')[:-1])
 a['argv']=[x.decode(errors='replace') for x in a['argv']]
 assert a['state']=='Z' or a['start_ticks']!=v['start_ticks'];return a
loc=[s['owner']]+[j(D/('reports/'+k+'_PID_RECEIPT.json'))['child'] for k in ('CURB_SDK10','CURB_NATIVE20K')]
actual=[dict(locator=v,actual=proc(v)) for v in loc]
locks=[]
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(str(p))
assert l['active_segment'] is None and l['authorized_training_seconds']==828000
names=['E1_CURB20_132_COMPLETE_ACTUAL_REVIEW.json','E1_CURB20_132_COMPLETE_NATIVE_SCOPE_DECISION.json','E1_CURB20_NATIVE_FINAL_CURRENT_ACTUAL.json','E1_CURB20_NATIVE_TARGET_CPU_VERIFIED.json','E1_CURB20_NATIVE_DISPATCH_ACTUAL_RECEIPT.json','E1_CURB20_132_COMPLETE_NATIVE_METADATA_SYNCED.json','MOE_PLAN_EXECUTION_CURRENT.json','MOE_TERRAIN_SUBEXPERT_REVISION_004_APPROVAL.json']
reports={}
for name in names:
 p=E/'reports'/name;assert p.is_file(),str(p);raw=p.read_bytes();reports[name]=dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),data=json.loads(raw))
assert reports['MOE_PLAN_EXECUTION_CURRENT.json']['data']['terrain_subexpert_revision004']['approved']
print(json.dumps(dict(epoch=time.time(),reports=reports,phase=s['phase'],actual_exited=actual,native_passed=passed,canonical_SHA=hashlib.sha256(B.read_bytes()).hexdigest(),remaining_seconds=l['authorized_training_seconds']-l['charged_training_seconds'],active_segment=l['active_segment'],two_OS_locks_free=locks,source_freeze=j(D/'reports/SOURCE_FREEZE.json'),source_selected=j(D/'reports/SOURCE_SELECTED.json'),read_only=True)))
'''.replace('ROOT',repr(OLD)).replace('CENTRAL',repr(E)).replace('BUDGET',repr(B))
  value=linux_json(n,code);stamp=str(time.time_ns())
  p=R/('CONTEXT_ACTUAL_'+stamp+'.json');p.write_bytes(json.dumps(value,ensure_ascii=False,indent=2).encode())
  names=['supervise_e1_command_retention_episode_reviewed_once.py','supervise_e1_wave_isolated_revision004_once.py','supervise_dt2500_solver32_training_test.py','isaac/mod4/e1_terrain_checkpoint.py','isaac/mod4/sensor_resume_contract.py','isaac/mod4/train_e1_retention_episode_reviewed_resume_ppo.py','isaac/mod4/train_e1_retention_named_owned_fresh_preflight_ppo.py','isaac/mod4/retention_flat_runtime.py','isaac/mod4/retention_flat_runtime_named_owned.py','isaac/mod4/retention_checkpoint_episode_reviewed.py','isaac/mod4/curb20_current_state.py','isaac/mod4/curb20_retention_runtime.py','isaac/mod4/g3_terrain_checkpoint.py','isaac/mod4/chassis_pd_checkpoint.py','isaac/mod4/rescue_training.py']
  with n.open_sftp() as f:
   for name in names:
    h=value['source_freeze']['sha256'][name];raw=f.open(OLD+'/'+name).read();assert H(raw)==h,name
    q=D/'inherited_source'/name;q.parent.mkdir(parents=True,exist_ok=True)
    if q.exists():assert q.read_bytes()==raw
    else:q.write_bytes(raw)
  print(json.dumps(dict(epoch=value['epoch'],phase=value['phase'],native_passed=True,current_revision004=value['reports']['MOE_PLAN_EXECUTION_CURRENT.json']['data']['terrain_subexpert_revision004'],source_count=len(value['source_freeze']['sha256']),two_OS_locks_free=True,remaining_seconds=value['remaining_seconds'],active_segment=value['active_segment'],exact_inherited_source_downloaded=len(names),report=str(p)),ensure_ascii=True))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:
  (R/('CONTEXT_READ_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),read_only=True,original_error_preserved=True),indent=2));raise
