"""Inspect the new native copy and preserve actual ABI/import errors without changing it."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time

ROOT = Path('/home/lc01/Zonglin Li/zonglin2')
CODE = r'''
import sys,json,importlib.metadata as m,importlib.util,traceback
v=dict(python=sys.executable,prefix=sys.prefix,version=sys.version,packages={},imports={},origins={})
for name in ('torch','tensordict','rsl-rl-lib','isaacsim','isaaclab'):
 try:v['packages'][name]=m.version(name)
 except Exception as e:v['packages'][name]=dict(error=type(e).__name__+': '+str(e))
for name in ('torch','tensordict','rsl_rl'):
 try:
  x=__import__(name);v['imports'][name]=dict(passed=True,path=x.__file__)
 except BaseException:v['imports'][name]=dict(passed=False,error=traceback.format_exc())
for name in ('isaaclab','isaacsim'):
 try:
  s=importlib.util.find_spec(name);v['origins'][name]=None if s is None else dict(origin=s.origin,locations=list(s.submodule_search_locations or []))
 except BaseException:v['origins'][name]=dict(error=traceback.format_exc())
try:
 from isaacsim import SimulationApp
 v['SDK_SimulationApp_import']=dict(passed=True,app_not_constructed=True)
except BaseException:v['SDK_SimulationApp_import']=dict(passed=False,error=traceback.format_exc())
print(json.dumps(v))
'''


def main():
    report = ROOT / 'audit/COMPAT_CPU_ABI_AND_SOURCE_V2_ACTUAL.json'
    assert not report.exists()
    env = dict(os.environ)
    env['CUDA_VISIBLE_DEVICES'] = ''
    env['ISAACSIM_ACCEPT_EULA'] = 'Y'
    env['OMNI_KIT_ACCEPT_EULA'] = 'YES'
    p = subprocess.run([str(ROOT / 'run-python-compat.sh'), '-c', CODE], cwd=ROOT,
        env=env, capture_output=True, text=True, timeout=120)
    result = None
    for line in reversed(p.stdout.splitlines()):
        try:
            result = json.loads(line)
            break
        except ValueError:
            pass
    v = dict(epoch=time.time(), returncode=p.returncode, stdout=p.stdout, stderr=p.stderr,
        result=result, no_CUDA_context_SimulationApp_construction_PPO_or_budget=True,
        all_owned_environment_and_cache_under_zonglin2=True,
        not_fullstate_or_MOD4_physics_admission=True)
    with report.open('x') as f:
        json.dump(v, f, indent=2)
    print(json.dumps(v), flush=True)


if __name__ == '__main__':
    main()
