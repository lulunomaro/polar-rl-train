"""Deliver a new single-angle frozen job at actual404 saved/settled/idle boundary."""
from slope_io import *
from prepare_slope8_frozen136_once import ROOT,CP_SHA
sys.path.insert(0,str(W/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011'))
from curb_io import WIN
from publish_curb132_frozen_once import worker_actual
import traceback

def main():
 prepared=json.loads((R/'SLOPE8_FROZEN136_PREPARED.json').read_bytes());pkg=prepared['package']
 assert H(Path(pkg['path']).read_bytes())==pkg['sha256'] and json.loads((R/'SLOPE135_COMPLETE_SCOPE_DECISION.json').read_bytes())['scoped_5degree_mirrored_traversal_accepted']
 save('SLOPE136_PUBLISH_GUARD_REVIEWED_STARTED.json',dict(epoch=time.time(),trial_id='E1-SLOPE8-FROZEN136-PUBLISH-01',frozen_only=True))
 n,w=connect_both()
 try:
  authority=linux_json(n,r'''from pathlib import Path
import json,hashlib,fcntl,time
SHA=__CHECKPOINT_SHA__
D=Path(ROOT);E=Path(CENTRAL);B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes())
s=j(D/'reports/E1_STATE.json');passed=j(D/'reports/e1_SLOPE5_independent_observation_PASSED.json');budget=B.read_bytes();b=json.loads(budget)
assert s['phase']=='E1_SLOPE5_independent_saved_review_ready' and s['child'] is None
assert passed['checkpoint']['sha256']==SHA and not passed['discarded_preflight'] and passed['source_count']==404
cp=Path(passed['checkpoint']['path']);assert hashlib.sha256(cp.read_bytes()).hexdigest()==SHA and cp.stat().st_size==17615794
assert len(passed['unique_completed_segment'])==1 and passed['unique_completed_segment']==[x for x in b['completed_segments'] if x['pid']==2588230]
assert b['authorized_training_seconds']==828000 and b['active_segment'] is None
locators=[s['owner'],j(D/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=2588230,start_ticks=83699658)];rows=[]
for loc in locators:
 q=Path('/proc')/str(loc['pid']);actual=None
 if q.exists():
  st=(q/'stat').read_text().split(') ',1)[1].split();actual=dict(state=st[0],start_ticks=int(st[19]));assert actual['state']=='Z' or actual['start_ticks']!=loc['start_ticks']
 rows.append(dict(locator=loc,actual=actual))
locks=[]
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(str(p))
v=j(E/'reports/MOE_PLAN_EXECUTION_CURRENT.json')['terrain_subexpert_revision004'];assert v['approved'] and v['active_next_expert']=='E1_SLOPE' and v['slope5_independent_scope']['root']==str(D)
assert hashlib.sha256((E/'reports/MOD4_MOE_MASTER_PLAN.md').read_bytes()).hexdigest()=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
print(json.dumps(dict(epoch=time.time(),actual_processes=rows,two_actual_OS_locks_free=locks,own_final=passed['checkpoint'],unique_completed_segment=passed['unique_completed_segment'],canonical_SHA=hashlib.sha256(budget).hexdigest(),remaining_seconds=b['authorized_training_seconds']-b['charged_training_seconds'],active_segment=None,source_count=404,no_runtime_or_budget_mutation=True)))
'''.replace('ROOT',repr(ROOT)).replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)).replace('__CHECKPOINT_SHA__',repr(CP_SHA)))
  with n.open_sftp() as nf,w.open_sftp() as wf:
   actual=worker_actual(w,wf);assert not [p for p in actual['processes'] if 'frozen_history_' in p.get('CommandLine','')]
   job=dict(prepared['jobs'][0]);jid=job['job_id'];assert jid+'.json' not in nf.listdir(E+'/eval_queue') and jid not in wf.listdir(WIN+'/jobs')
   budget=nf.open(B).read();assert H(budget)==authority['canonical_SHA']
   prior=json.loads(sorted(R.glob('SLOPE135_COLLECTED_[0-9]*.json'))[-1].read_bytes());sourcecase=next(x for k,x in prior['cases'].items() if k.endswith('-terrain-flat'))
   cp=sourcecase['manifest']['artifacts']['checkpoint'];raw=nf.open(cp['path']).read();assert len(raw)==cp['bytes']==17615794 and H(raw)==CP_SHA==cp['sha256']
   job['artifacts']=dict(job['artifacts']);job['artifacts']['checkpoint']=cp
   job.update(published_epoch=time.time(),revision004_approval_SHA=H(nf.open(E+'/reports/MOE_TERRAIN_SUBEXPERT_REVISION_004_APPROVAL.json').read()),
    source404_complete135_selected=True,frozen_only_source_fullstate_not_restored=True,source404_own5deg_weight_not_updated=True,
    prepared_checkpoint_delivery_name_replaced_by_existing_same_SHA_135_artifact=True)
   remote=job['artifacts']['runtime']['path'];assert Path(remote).name not in nf.listdir(E+'/artifacts')
   nf.put(pkg['path'],remote+'.partial');assert H(nf.open(remote+'.partial').read())==pkg['sha256'];nf.rename(remote+'.partial',remote)
   raw=json.dumps(job,indent=2).encode();path=E+'/eval_queue/'+jid+'.json'
   with nf.open(path+'.partial','wbx') as f:f.write(raw)
   assert nf.open(path+'.partial').read()==raw;nf.rename(path+'.partial',path)
   assert nf.open(path).read()==raw and nf.open(B).read()==budget
   receipt=dict(epoch=time.time(),trial_id='E1-SLOPE8-FROZEN136-PUBLISH-01',jobs=[job],package=pkg,actual_authority=authority,actual_worker=actual,
    canonical_bytes_preserved=True,no_4090_launch_or_PPO=True,source5deg_and_other_experts_unchanged=True,actual_complete_review_pending=True,new_budget_seconds=0)
   save('SLOPE136_PUBLISHED.json',receipt);print(json.dumps(dict(job_id=jid,package_SHA=pkg['sha256'],source_SHA=CP_SHA,published=True,actual_complete_pending=True,worker=actual['worker'],canonical_unchanged=True)))
 finally:cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('SLOPE136_PUBLISH_GUARD_REVIEWED_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_blind_replay=True));raise
