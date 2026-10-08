"""Complete the planned 18-condition review on3060; reuse three exact valid cases."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'D5_FULL_RETENTION_PUBLISHED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
    code=r'''
from pathlib import Path
import json,hashlib,time,shutil
D=Path('/home/egde/rl_candidates/MOD4_D6_FULL_CONTRACT_20261009');R=D/'reports';E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');OLD=Path('/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008/reports')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not (R/'D5_FULL_RETENTION_PUBLISHED.json').exists()
sel=read(R/'SELECTED_D5_BEHAVIOR_SOURCE.json');src=Path(sel['checkpoint']['path']);assert sel['behavior_scope_accepted'] and sha(src)==sel['checkpoint']['sha256']
package=read(OLD/'D5_FROZEN_BEHAVIOR_PACKAGES.json')['world'];assert sha(package['path'])==package['sha256']
reused=[]
for kind in ('flat','spin','world'):
 job='clk2500-closure-episode-d3-75-d5-b1-'+kind;desc=read(E/'eval_queue'/(job+'.json'));res=read(E/'eval_results'/job/'result.json')
 assert desc['artifacts']['checkpoint']['sha256']==sel['checkpoint']['sha256'] and desc['artifacts']['runtime']==package
 assert desc['seed']==20261002 and desc['profile']=='white_v3' and desc['steps']==1500 and desc['num_envs']==(80 if kind=='flat' else 88)
 assert res['phase']=='complete' and res['exit_code']==0 and not res['errors'] and res['checkpoint']['sha256']==sel['checkpoint']['sha256']
 reused.append(dict(job_id=job,result_sha256=sha(E/'eval_results'/job/'result.json'),probe_sha256=sha(E/'eval_results'/job/'probe.json'),source_SHA=sel['checkpoint']['sha256'],condition_exact=True))
template=read(E/'eval_queue/clk2500-closure-episode-d3-75-d5-b1-flat.json');jobs=[]
for seed in (20261002,20261003):
 for profile in ('nominal','white_v2','white_v3'):
  for kind in ('flat','spin','world'):
   if seed==20261002 and profile=='white_v3':continue
   job='clk2500-closure-episode-d3-95-d5-retention-'+str(seed)+'-'+profile+'-'+kind;p=E/'eval_queue'/(job+'.json');assert not p.exists()
   row=dict(template,job_id=job,published_epoch=time.time(),seed=seed,profile=profile,kind=kind,num_envs=80 if kind=='flat' else 88,role='D5 selected source planned two-development-seed x three original D0 profiles x three old skills; full D1-D5 recipes remain on; no allDR or clean-distribution claim',no_learning=True)
   temp=Path(str(p)+'.partial');temp.write_text(json.dumps(row,indent=2));temp.replace(p);jobs.append(row)
v=dict(epoch=time.time(),selected_source=sel['checkpoint'],scope='Two development seeds20261002/20261003 x nominal/white_v2/white_v3 D0 profiles x flat/spin/world; D1-D5 on; not heldout seeds or complete hardware DR',total_cases=18,new_cases=15,reused_cases=reused,jobs=jobs,results_pending=True,no_GPU_canonical_or_training_launch_authority=True,not_a_training_wait_dependency=True)
(R/'D5_FULL_RETENTION_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
    _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
    (R/'D5_FULL_RETENTION_PUBLISHED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(new_cases=v['new_cases'],exact_reused=len(v['reused_cases']),results_pending=True,training_wait=False)))
finally:c.close()
