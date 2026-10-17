"""One actual backend source read; no import of SDK/GPU, no installed-file mutation."""
from pathlib import Path
import sys,time,json,getpass,hashlib,traceback
B=Path(__file__).resolve().parent;R=B/'reports';P=B.parent/'MOD4_H1_HUMAN_REQUESTED_SAME_SCOPE_RESTART_20261017';sys.path.insert(0,str(P));from deploy_human_requested_H1_new_finite_strict_native_reuse_once import a
CODE=r'''
from pathlib import Path
import json,time,hashlib
root=Path('/home/lc01/Zonglin Li/zonglin2');site=root/'envs/mod4/lib/python3.12/site-packages';rsl=site/'rsl_rl';lab=root/'src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab_rl/isaaclab_rl/rsl_rl';assert rsl.is_dir() and lab.is_dir();rows=[]
for base,label in ((rsl,'rsl_rl'),(lab,'isaaclab_rl/rsl_rl')):
 for p in sorted(base.rglob('*.py')):
  s=p.read_text('utf8')
  if any(k in s for k in ('std_param','GaussianDistribution','handle_deprecated_rsl_rl_cfg','clip_actions')) or p.name in ('ppo.py','on_policy_runner.py'):
   raw=p.read_bytes();rows.append(dict(path=str(p),relative=label+'/'+p.relative_to(base).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=s))
assert next(x['SHA'] for x in rows if x['relative']=='rsl_rl/algorithms/ppo.py')=='a2d35e7ad7b884c80b7434e7d2ce785a6da1e18d93c96f1179fbd3a208669f8c';assert next(x['SHA'] for x in rows if x['relative']=='rsl_rl/runners/on_policy_runner.py')=='39358a0a60219fdb360df7acddf80f6a382837aa58e2ec0ccf875df4afee4825'
print(json.dumps(dict(epoch=time.time(),files=rows,readonly_actual_installed_sources=True,no_SDK_GPU_or_training_import=True,original_completed_run_runner_PPO_SHA_exact=True)))
'''
def main():
 with (R/'RSL_DISTRIBUTION_READONLY_SOURCE_COLLECTOR_STARTED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),pid=__import__('os').getpid(),argv=sys.argv,actual_alive_only_exclusive_transport=True,one72readonly_connection_no_GPU_or_budget=True),f,indent=2)
 pw=getpass.getpass('Host72 actual RSL distribution/clip source audit only (hidden): ');c=None
 try:
  c=a.connect72(pw);pw=None;v=a.code(c,a.PY,CODE,timeout=90);out=B/'actual_installed_RSL72_readonly_sources_v1';out.mkdir()
  for row in v['files']:
   p=out/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);raw=row['text'].encode();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA'];p.write_bytes(raw);row['local_path']=str(p)
  with (R/'ACTUAL_INSTALLED_RSL72_DISTRIBUTION_CLIP_READONLY_SOURCE_COMPLETE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
  print(json.dumps(dict(actual_readonly_RSL_files=len(v['files']),paths=[x['relative'] for x in v['files']],no_GPU_or_training_or_budget_mutation=True)),flush=True)
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('RSL_READONLY_SOURCE_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_installed_source_change=True),f,indent=2)
  raise
