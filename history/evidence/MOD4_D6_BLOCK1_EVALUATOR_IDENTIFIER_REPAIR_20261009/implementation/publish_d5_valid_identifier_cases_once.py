"""Replace nine never-executable queue IDs; retain actual evaluation conditions."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'D5_RETENTION_JOB_IDENTIFIERS_REPLACED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import json,hashlib,time,sys
E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');D=Path('/home/egde/rl_candidates/MOD4_D6_FULL_CONTRACT_20261009');R=D/'reports';sys.path.insert(0,str(E))
import artifact_service as bridge
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'D5_RETENTION_JOB_IDENTIFIERS_REPLACED.json').exists()
rows=[]
for seed in (20261002,20261003):
 for profile,slug in (('white_v2','white2'),('white_v3','white3')):
  if seed==20261002 and profile=='white_v3':continue
  for kind in ('flat','spin','world'):
   old='clk2500-closure-episode-d3-95-d5-retention-'+str(seed)+'-'+profile+'-'+kind;p=E/'eval_queue'/(old+'.json');row=read(p)
   try:bridge.key(old)
   except ValueError:pass
   else:raise AssertionError('Old ID unexpectedly valid')
   assert not (E/'eval_results'/old/'result.json').exists(),'Do not rerun completed result'
   assert row['job_id']==old and row['seed']==seed and row['profile']==profile and row['kind']==kind
   for artifact in row['artifacts'].values():assert sha(Path(artifact['path']))==artifact['sha256']
   job='clk2500-closure-episode-d3-97-d5-retention-'+str(seed)+'-'+slug+'-'+kind;bridge.key(job);q=E/'eval_queue'/(job+'.json');assert not q.exists()
   new=dict(row,job_id=job,published_epoch=time.time(),role='Bridge-valid replacement of never-executable ID; exact checkpoint/runtime/seed/profile/kind/count/steps/recipes reused; original invalid manifest retained')
   differing={k for k in row.keys()|new.keys() if row.get(k)!=new.get(k)};assert differing=={'job_id','published_epoch','role'}
   t=Path(str(q)+'.partial');t.write_text(json.dumps(new,indent=2));t.replace(q)
   assert bridge.manifest(job)==new
   rows.append(dict(old_job=old,old_manifest_SHA=sha(p),new_job=job,new_manifest_SHA=sha(q),checkpoint_SHA=new['artifacts']['checkpoint']['sha256'],runtime_SHA=new['artifacts']['runtime']['sha256'],profile_unchanged=profile,all_evaluation_conditions_exact=True,old_immutable_manifest_preserved=True,old_job_never_executed=True))
assert len(rows)==9
v=dict(epoch=time.time(),replacements=rows,nominal_six_replacements_owned_by_existing_SDK_publisher=True,three_valid_firstseed_white3_cases_reused=True,total_planned_conditions=18,bridge_contract_unchanged=True,no_GPU_PPO_canonical_or_training_launch_authority=True)
(R/'D5_RETENTION_JOB_IDENTIFIERS_REPLACED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);(R/'D5_RETENTION_JOB_IDENTIFIERS_REPLACED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(dict(replacements=len(v['replacements']),all_actual_profiles_runtime_source_conditions_unchanged=True,old_invalid_manifests_preserved=True,no_GPU_PPO_or_budget_write=True)))
finally:c.close()
