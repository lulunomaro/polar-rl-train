"""Publish frozen jobs to the single new evaluator after its idle-safe handover."""
from pathlib import Path
import sys,json,shlex,time
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
assert not (R/'CLOCK1000_JOBS_PUBLISHED.json').exists()
worker=json.loads((R/'CLOCK1000_WORKER_DEPLOYED.json').read_text());assert worker['old_worker_actual_exited'] and not worker['new_learning']
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 with c.open_sftp() as s:s.put(str(R/'CLOCK1000_WORKER_DEPLOYED.json'),'/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports/CLOCK1000_WORKER_DEPLOYED.json')
 code=r'''
from pathlib import Path
import json,hashlib,time,os
E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');R=E/'reports';Q=E/'eval_queue'
receipt=R/'CLOCK1000_JOBS_PUBLISHED.json';assert not receipt.exists()
approval=json.loads((R/'PLAN_APPROVAL.json').read_text());assert approval['approved'] and 'S0E' in approval['allowed_stages']
pack=json.loads((R/'CLOCK1000_PACKAGE_STAGED.json').read_text());worker=json.loads((R/'CLOCK1000_WORKER_DEPLOYED.json').read_text())
assert worker['old_worker_actual_exited'] and worker['new_task']['triggerCount']==0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
runtime=pack['package'];assert sha(Path(runtime['path']))==runtime['sha256']
rows=[('sdk-a1-flat','A1','flat',300,10),('sdk-a2-flat','A2','flat',300,10)]
rows += [(role.lower()+'-'+kind,role,kind,1500,80 if kind=='flat' else 88) for role in ('anchor','A0','A1','A2') for kind in ('flat','spin','world')]
jobs=[]
for i,(name,role,kind,steps,count) in enumerate(rows):
 source=pack['sources'][role];assert sha(Path(source['path']))==source['sha256']
 job='clk1000-'+str(i).zfill(2)+'-'+name;target=Q/(job+'.json');assert not target.exists()
 row=dict(job_id=job,stage='S0E',immutable=True,plan_id=approval['plan_id'],plan_sha256=approval['approved_plan_sha256'],
  published_epoch=time.time(),kind=kind,profile='white_v3',seed=20261002,num_envs=count,steps=steps,max_wall_seconds=1800,
  architecture_variant=source['architecture_variant'],role=role,physics_dt_s=.001,control_dt_s=.01,
  protocol='New1ms/history inference SDK and platform functional comparison; firstseed-white3 architecture behavior remains provisional until actual review',
  artifacts=dict(runtime=runtime,checkpoint={k:source[k] for k in ('path','bytes','sha256')}),
  no_learning=True,canonical_write_authority=False,GPU_concurrency=1,platform_scope_not_yet_accepted=True)
 temp=target.with_suffix('.json.partial');temp.write_text(json.dumps(row,indent=2));os.replace(temp,target);jobs.append(row)
proof=dict(epoch=time.time(),jobs=jobs,total_jobs=len(jobs),first_two_SDK_only=True,next_three_platform_anchor=True,last_nine_first_matched_behavior=True,
 new_learning=False,new_budget_seconds=0,old_s0e_results_and_scope_preserved=True)
receipt.write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=30)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,err.decode()
 v=json.loads(raw);(R/'CLOCK1000_JOBS_PUBLISHED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(dict(epoch=v['epoch'],job_count=v['total_jobs'],job_ids=[x['job_id'] for x in v['jobs']],new_learning=False)))
finally:c.close()
