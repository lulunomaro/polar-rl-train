"""Publish only new approved independent5deg frozen scope; unchanged demand worker."""
from review133_io import *
from curb_io import WIN
from publish_curb132_frozen_once import worker_actual
import traceback
SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'

def main():
 prepared=json.loads((R/'SLOPE5_FROZEN_PREPARED.json').read_bytes());pkg=prepared['package'];assert H(Path(pkg['path']).read_bytes())==pkg['sha256']
 save('SLOPE134_PUBLISH_STARTED.json',dict(epoch=time.time(),trial_id='E1-SLOPE5-FROZEN-PUBLISH-01',once=True,no_learning=True))
 n,w=connect_both()
 try:
  authority=linux_json(n,r'''from pathlib import Path
import json,hashlib,fcntl,time
D=Path(ROOT);E=Path(CENTRAL);B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes());s=j(D/'reports/E1_STATE.json');p=j(D/'reports/e1_CURB20_independent_observation_PASSED.json');b=j(B)
assert s['phase']=='E1_CURB20_independent_saved_review_ready' and s['child'] is None and len(p['unique_completed_segment'])==1
assert p['checkpoint']['sha256']=='df0c141d444a6a85b983e49eedad10e91e0b7b264f627bff972dbd7cb1f2c753'
assert hashlib.sha256(Path(p['checkpoint']['path']).read_bytes()).hexdigest()==p['checkpoint']['sha256']
locators=[(2447069,81560593),(2447143,81560729),(2447175,81560752)];rows=[]
for pid,start in locators:
 q=Path('/proc')/str(pid);a=None
 if q.exists():
  st=(q/'stat').read_text().split(') ',1)[1].split();a=dict(state=st[0],start_ticks=int(st[19]));assert a['state']=='Z' or a['start_ticks']!=start
 rows.append(dict(pid=pid,start_ticks=start,actual=a))
locks=[]
for q in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with q.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(str(q))
assert b['active_segment'] is None and b['authorized_training_seconds']==828000
assert j(E/'reports/MOE_PLAN_EXECUTION_CURRENT.json')['terrain_subexpert_revision004']['approved']
assert hashlib.sha256((E/'reports/MOD4_MOE_MASTER_PLAN.md').read_bytes()).hexdigest()=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
print(json.dumps(dict(epoch=time.time(),own_final=p['checkpoint'],actual_processes=rows,OS_locks_free=locks,canonical_SHA=hashlib.sha256(B.read_bytes()).hexdigest(),remaining_seconds=b['authorized_training_seconds']-b['charged_training_seconds'],active_segment=None,unique_segment=p['unique_completed_segment'],new_budget_seconds=0)))
'''.replace('ROOT',repr(NEW)).replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)))
  with n.open_sftp() as nf,w.open_sftp() as wf:
   actual=worker_actual(w,wf);assert not [x for x in actual['processes'] if 'frozen_history_' in x.get('CommandLine','')]
   job=prepared['jobs'][0];jid=job['job_id'];assert jid+'.json' not in nf.listdir(E+'/eval_queue') and jid not in wf.listdir(WIN+'/jobs')
   budget=nf.open(B).read();assert H(budget)==authority['canonical_SHA']
   cp=job['artifacts']['checkpoint'];raw=nf.open(cp['path']).read();assert len(raw)==cp['bytes'] and H(raw)==SHA==cp['sha256']
   remote=job['artifacts']['runtime']['path'];assert Path(remote).name not in nf.listdir(E+'/artifacts')
   job.update(published_epoch=time.time(),revision004_approval_SHA=H(nf.open(E+'/reports/MOE_TERRAIN_SUBEXPERT_REVISION_004_APPROVAL.json').read()),frozen_only_source_fullstate_not_restored=True,source364_complete129_selected=True,no_CURB389_weight_update=True)
   nf.put(pkg['path'],remote+'.partial');assert H(nf.open(remote+'.partial').read())==pkg['sha256'];nf.rename(remote+'.partial',remote)
   path=E+'/eval_queue/'+jid+'.json';raw=json.dumps(job,indent=2).encode()
   with nf.open(path+'.partial','wbx') as f:f.write(raw)
   assert nf.open(path+'.partial').read()==raw;nf.rename(path+'.partial',path)
   assert nf.open(path).read()==raw and nf.open(B).read()==budget
   receipt=dict(epoch=time.time(),trial_id='E1-SLOPE5-FROZEN-PUBLISH-01',jobs=[job],package=pkg,actual_authority=authority,actual_worker=actual,
    canonical_bytes_preserved=True,new_budget_seconds=0,no_4090_launch_or_learning=True,actual_completion_pending=True)
   save('SLOPE134_PUBLISHED.json',receipt);print(json.dumps(dict(job_id=jid,published=True,source_SHA=SHA,package_SHA=pkg['sha256'],actual_worker=actual['worker'],pending_actual_result=True,canonical_unchanged=True)))
 finally:cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('SLOPE134_PUBLISH_ERROR.json',dict(error=traceback.format_exc(),no_blind_replay=True));raise
