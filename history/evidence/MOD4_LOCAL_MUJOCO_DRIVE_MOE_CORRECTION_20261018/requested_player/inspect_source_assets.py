from pathlib import Path
import sys, json, shlex
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
c=connect()
try:
    code=r'''
from pathlib import Path
import hashlib,json
root=Path('/home/egde/fangzhen_linux/incoming')
paths=[]
for folder in ('_from_target_20260928','rm2025_mod4','mod4_fixed_20260912/chassis_mod4','chassis_mod4_mjcf_usd_20260910/chassis_mod4'):
 for name in ('robot_hifi.xml','source_robot_hifi.xml','isaac/import_contract.json'):
  p=root/folder/name
  if p.is_file():paths.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size))
print(json.dumps(paths))
'''
    _,o,e=c.exec_command('python3 -c '+shlex.quote(code),timeout=20)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode()
    print(raw.decode())
finally:c.close()
