"""Stream a read-only remote capture; authentication stays in the environment."""
import os
import sys
from pathlib import Path
import shlex
import paramiko

root=Path(__file__).resolve().parents[1]
supplement='--supplement' in sys.argv
output=root/('.staging/remote_supplement.zip' if supplement else '.staging/remote_capture.zip')
output.parent.mkdir(parents=True,exist_ok=True)
code=(root/'archive_tools/capture_history.py').read_text(encoding='utf8')
c=paramiko.SSHClient();c.load_system_host_keys()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(os.environ.get('RM_SSH_HOST','10.24.4.210'),username=os.environ.get('RM_SSH_USER','egde'),
          password=os.environ['RM_SSH_PASSWORD'],timeout=15)
_,stdout,stderr=c.exec_command('python3 -c '+shlex.quote(code)+' --site remote'+(' --supplement' if supplement else ''),timeout=600)
total=0
with output.open('wb') as f:
    while True:
        block=stdout.read(1024*1024)
        if not block:break
        f.write(block);total+=len(block)
rc=stdout.channel.recv_exit_status()
err=stderr.read().decode('utf8',errors='replace')
c.close()
if rc:
    raise RuntimeError('Remote capture failed with exit '+str(rc)+'; stderr omitted to protect credentials')
print('Remote capture complete:',total,'compressed bytes')
