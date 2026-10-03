import json,shlex,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
D=Path(__file__).resolve().parent;STAGE='/home/egde/rl_candidates/MOD4_RATE6_TARGETED_REPAIR_20261003';ROOT='/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002';PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
c=connect()
try:
 with c.open_sftp() as s:
  for n in ['supervise_targeted_mature5.py','test_targeted_mature5_evidence.py']:s.put(str(D/n),STAGE+'/'+n)
 code=f'''import ast,hashlib,json,subprocess
from pathlib import Path
s=Path({STAGE!r});root=Path({ROOT!r});code=root/'isaac/mod4'
assert not (root/'reports/TARGETED_MATURE5_ENTRY_20261003.json').exists() and not (root/'supervisor_targeted_mature5_20261003.log').exists()
r=subprocess.run([{PY!r},str(s/'test_targeted_mature5_evidence.py')],cwd=s,capture_output=True,text=True);assert r.returncode==0,r.stderr
data=(s/'supervise_targeted_mature5.py').read_bytes();ast.parse(data.decode());p=code/'supervise_targeted_mature5.py';assert not p.exists();p.write_bytes(data)
freeze=json.loads((root/'reports/SPIN_SOURCE_FREEZE.json').read_text());freeze['sha256']['isaac/mod4/supervise_targeted_mature5.py']=hashlib.sha256(data).hexdigest()
(root/'reports/SPIN_SOURCE_FREEZE.json').write_text(json.dumps(freeze,indent=2))
with (root/'supervisor_targeted_mature5_20261003.log').open('x') as f:child=subprocess.Popen([{PY!r},'-u',str(p)],cwd=root,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps(dict(new_parent_pid=child.pid,CPU_checks=r.stdout,source_count=len(freeze['sha256']),entry_sha256=hashlib.sha256(data).hexdigest())))'''
 _,o,e=c.exec_command('python3 -c '+shlex.quote(code));raw=o.read().decode();error=e.read().decode();assert o.channel.recv_exit_status()==0,error
 (D/'TARGETED_MATURE5_LAUNCHED.json').write_text(raw);print(raw)
finally:c.close()
