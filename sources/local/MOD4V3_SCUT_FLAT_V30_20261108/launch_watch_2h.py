import os, subprocess, sys
from pathlib import Path
root=Path('/mnt/mod4_linux_durable_20261013/mod4v3_scut_target_native_20261107')
watch=root/'watch_and_launch_2h.py'
log=root/'watch_2h.log'
env=dict(os.environ)
with open(log,'ab',buffering=0) as out:
    child=subprocess.Popen([sys.executable,'-B','-u',str(watch)],cwd=str(root),env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
(root/'watch_2h.pid').write_text(str(child.pid)+'\n')
print('WATCH_PID',child.pid)
