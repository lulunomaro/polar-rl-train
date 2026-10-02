"""Create an isolated candidate. Never overwrites or restarts the active task."""
from pathlib import Path
import argparse,json,hashlib,shutil
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--destination',required=True);a=p.parse_args()
src=Path(a.source).resolve();dst=Path(a.destination).resolve();pkg=Path(__file__).resolve().parents[1]
if dst.exists() or dst==src or src in dst.parents:raise SystemExit('Destination must be a new sibling directory')
expected=json.loads((pkg/'evidence/source_sha256.json').read_text())
for name,digest in expected.items():
 if hashlib.sha256((src/name).read_bytes()).hexdigest()!=digest:raise SystemExit('Source changed: '+name+'; re-audit before installation')
dst.mkdir(parents=True)
shutil.copytree(src/'isaac',dst/'isaac',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for name in ['train','cad','incoming','scripts']:
 if (src/name).exists():(dst/name).symlink_to((src/name).resolve(),target_is_directory=True)
for name in ['logs','reports']:(dst/name).mkdir()
shutil.copytree(pkg/'profiles',dst/'profiles')
for name in ['mod4_dr_profiles.py','candidate_entry.py','run_paired.py','acceptance.py']:
 shutil.copy2(pkg/'code'/name,dst/'isaac/mod4'/name)
task=dst/'isaac/mod4/mod4_task.py';s=task.read_text()
needle='                                    enable_external_forces_every_iteration=True)'
if s.count(needle)!=1:raise SystemExit('Unexpected task cfg hook')
s=s.replace(needle,needle+'\n        from mod4_dr_profiles import configure\n        configure(self)')
task.write_text(s)
for name in ['validate_speed.py','validate_rescue.py']:
 f=dst/'isaac/mod4'/name;s=f.read_text();needle="    result['strict_pass']=result['physics_pass']"
 if s.count(needle)!=1:raise SystemExit('Unexpected validator hook')
 additions="    from mod4_dr_profiles import audit\n    result['DR_audit']=audit(env)\n"
 if name=='validate_speed.py':
  additions+="    result['per_environment']={k:v.detach().cpu().tolist() for k,v in per.items()}\n    result['per_environment'].update(alive=alive.cpu().tolist(),group_ids=group_ids.cpu().tolist(),first_failure_step=firstdone.cpu().tolist())\n"
 s=s.replace(needle,additions+needle)
 f.write_text(s)
f=dst/'isaac/mod4/train_mod4_ppo.py';s=f.read_text();needle='    env = build_env()'
if s.count(needle)!=1:raise SystemExit('Unexpected train audit hook')
s=s.replace(needle,needle+"\n    env.reset()\n    from mod4_dr_profiles import audit\n    import os as _audit_os\n    Path(REPO,'reports',f'profile_audit_{_audit_os.getpid()}.json').write_text(json.dumps(audit(env),indent=2))")
f.write_text(s)
(dst/'candidate_contract.json').write_text(json.dumps({'active_source':str(src),'source_sha256':expected,
 'changes':['explicit profile hook in config','DR readback in evaluation','isolated entry and paired runner'],
 'training_enabled':False,'friction_profile_enabled':False,'asset_copies':'external symlinks; do not edit'},indent=2))
for f in (dst/'isaac/mod4').glob('*.py'):compile(f.read_text(),str(f),'exec')
print(dst)
