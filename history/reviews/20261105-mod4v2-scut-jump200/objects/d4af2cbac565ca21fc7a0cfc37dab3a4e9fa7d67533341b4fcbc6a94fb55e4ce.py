"""Isolated fixed Newton toolchain; no active-run, ledger or peer changes."""
from pathlib import Path
import json
import time
from shared_control_access import connection

N=Path(__file__).resolve().parent
R=N/'reports/newton_setup01';R.mkdir(exist_ok=True)

code='''from pathlib import Path
import json,subprocess,psutil,time,sys
b=Path('/home/lc01/Zonglin Li/zonglin2');r=b/'toolchains/mod4v2_newton17';r.mkdir(parents=True,exist_ok=False)
setup="""from pathlib import Path
import json,os,subprocess,sys,time,traceback,venv
r=Path(sys.argv[1]);error=None
try:
 venv.EnvBuilder(system_site_packages=True,with_pip=True).create(r/'venv')
 py=r/'venv/bin/python'
 cmd=[str(py),'-m','pip','install','newton[sim]==1.7.0','warp-lang==1.17.0']
 subprocess.run(cmd,check=True)
 result=subprocess.check_output([str(py),'-c','import json,newton,warp,mujoco,mujoco_warp,torch;print(json.dumps(dict(newton=newton.__version__,warp=warp.__version__,mujoco=mujoco.__version__,torch=torch.__version__)))'],text=True)
 (r/'READY.json').write_text(json.dumps(dict(epoch=time.time(),versions=result,python=str(py))))
except BaseException:
 error=traceback.format_exc();(r/'ERROR.json').write_text(json.dumps(dict(epoch=time.time(),error=error)))
finally:(r/'CLOSED.json').write_text(json.dumps(dict(epoch=time.time(),error=error)))
"""
(r/'setup.py').write_text(setup)
with(r/'SETUP.log').open('xb')as log:
 p=subprocess.Popen([str(b/'run-python.sh'),'-u','-B',str(r/'setup.py'),str(r)],cwd=r,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
q=psutil.Process(p.pid)
print(json.dumps(dict(epoch=time.time(),root=str(r),PID=p.pid,creation=q.create_time(),original_shared_env_unchanged=True,canonical_reads=0,canonical_writes=0)))'''
assert not(R/'SETUP_ONCE.json').exists()
with connection(R,'NEWTON_TOOLCHAIN_SETUP')as(c,t):
    value=t.code(c,t.PY72,code,{},timeout=45)
with(R/'SETUP_ONCE.json').open('x',encoding='utf8')as f:json.dump(value,f,indent=2)
print(json.dumps(value))
