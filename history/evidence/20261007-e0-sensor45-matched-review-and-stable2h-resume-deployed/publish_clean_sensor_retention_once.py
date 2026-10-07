"""Publish clean-feedback anchor/candidate matches; immutable206 training is untouched."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import json,zipfile,hashlib,time,copy,os
E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');R=E/'reports'
assert not (R/'SENSOR_CLEAN_RETENTION_JOBS_PUBLISHED.json').exists()
a=json.loads((R/'PLAN_APPROVAL.json').read_text());assert a['approved'] and {'S0E','S2'}.issubset(a['allowed_stages'])
old=json.loads((R/'SENSOR_COMPLETE_ASYNC_PACKAGE_AND_JOBS.json').read_text());src=old['package'];p=Path(src['path'])
def sha(raw):return hashlib.sha256(raw).hexdigest()
assert sha(p.read_bytes())==src['sha256']
out=E/'artifacts/clock1000-s2-sensor202-clean-frozen.zip';assert not out.exists()
with zipfile.ZipFile(p) as z:entries={n:z.read(n) for n in z.namelist()}
cfgpath='runtime/isaac/mod4/env.json';cfg=json.loads(entries[cfgpath]);prior=copy.deepcopy(cfg);cfg['RM_SENSOR_PROFILE']='off'
entries[cfgpath]=json.dumps(cfg,indent=2).encode()
manifest=json.loads(entries['SOURCE_MANIFEST.json']);manifest['files'][cfgpath]=sha(entries[cfgpath]);manifest.update(sensor_profile='off',clean_feedback_only=True,noise_source_package_sha256=src['sha256'],only_profile_config_changed=True)
entries['SOURCE_MANIFEST.json']=json.dumps(manifest,indent=2).encode()
with zipfile.ZipFile(str(out)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
 for n,data in entries.items():z.writestr(n,data)
os.replace(str(out)+'.partial',out)
package=dict(path=str(out),bytes=out.stat().st_size,sha256=sha(out.read_bytes()))
for n,h in manifest['files'].items():assert sha(entries[n])==h,n
assert all(entries[n]==zipfile.ZipFile(p).read(n) for n in entries if n not in (cfgpath,'SOURCE_MANIFEST.json'))
pub=json.loads((R/'SENSOR_COMPLETE_ASYNC_CANDIDATE_PUBLISHED.json').read_text());sources={'anchor':old['checkpoint'],'candidate':pub['jobs'][0]['artifacts']['checkpoint']}
jobs=[]
for role,ck in sources.items():
 assert sha(Path(ck['path']).read_bytes())==ck['sha256']
 for kind in ('flat','spin','world'):
  job='clk1000-s2complete-'+('11' if role=='anchor' else '12')+'-clean-'+role+'-'+kind;path=E/'eval_queue'/(job+'.json');assert not path.exists()
  row=dict(job_id=job,stage='S0E',immutable=True,plan_id=a['plan_id'],plan_sha256=a['approved_plan_sha256'],published_epoch=time.time(),kind=kind,profile='white_v3',sensor_profile='off',seed=20261002,num_envs=80 if kind=='flat' else 88,steps=1500,max_wall_seconds=1800,architecture_variant='A0',role='S2 old clean feedback retention '+role,physics_dt_s=.001,control_dt_s=.01,protocol='Clean actor feedback only, exact202 plant/inference files and native off SDK proof; anchor-candidate same3060 fullroot/q/parameters. No new learning or training authority.',artifacts=dict(runtime=package,checkpoint=ck),no_learning=True,canonical_write_authority=False,GPU_concurrency=1,new_clean_platform_scope_requires_actual_review=True)
  tmp=path.with_suffix('.json.partial');tmp.write_text(json.dumps(row,indent=2));os.replace(tmp,path);jobs.append(row)
proof=dict(epoch=time.time(),package=package,previous_noisy_package=src,only_changes=[cfgpath,'SOURCE_MANIFEST.json'],six_jobs=jobs,all_other_bytes_exact=True,no_new_GPU_on4090=True,no_canonical_writes=True,existing_worker_unchanged=True,actual_native_off_SDK_reused=True)
(R/'SENSOR_CLEAN_RETENTION_JOBS_PUBLISHED.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw)
 (R/'SENSOR_CLEAN_RETENTION_JOBS_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(dict(package=v['package'],jobs=[x['job_id'] for x in v['six_jobs']],only_changes=v['only_changes'],GPU4090=0,budget_writes=0)))
finally:c.close()
