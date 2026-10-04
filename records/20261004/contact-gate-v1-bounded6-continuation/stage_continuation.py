"""Prepare the separate continuation sources; no production install or launch."""
import json,shlex,sys
from pathlib import Path
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
DEST='/home/egde/rl_candidates/MOD4_CONTACT_GATE_CONTINUATION_20261004'
names=['supervise_contact_gate_continue.py','contact_gate.py','continuation_contract.py','test_contact_gate.py','test_continuation_contract.py','contact_calibration_probe.py','substep_contact_readback.py']
code=r'''import hashlib,json,subprocess,sys
from pathlib import Path
D=Path('/home/egde/rl_candidates/MOD4_CONTACT_GATE_CONTINUATION_20261004')
assert not (D/'PREPARED.json').exists()
tests={}
for name in ('test_contact_gate.py','test_continuation_contract.py'):
 p=subprocess.run([sys.executable,str(D/name)],cwd=D,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr
 tests[name]=p.stdout.strip()
compile((D/'supervise_contact_gate_continue.py').read_text(),str(D/'supervise_contact_gate_continue.py'),'exec')
x=dict(source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in D.glob('*.py')},CPU_contract_tests=tests,production_installed=False,PPO_started=False,budget_changed=False)
(D/'PREPARED.json').write_text(json.dumps(x,indent=2));print(json.dumps(x))
'''
receipt='CONTINUATION_PREPARED.json'
if len(sys.argv)>1:
 assert sys.argv[1]=='source_role_review_v2'
 previous=DEST;DEST+='/source_role_review_v2'
 code=code.replace("D=Path('"+previous+"')","D=Path('"+DEST+"')")
 receipt='CONTINUATION_ROLE_V2_PREPARED.json'
c=connect()
try:
 with c.open_sftp() as s:
  try:s.stat(DEST)
  except FileNotFoundError:s.mkdir(DEST)
  else:raise AssertionError('Continuation already staged; inspect, do not repeat')
  for name in names:s.put(str(D/name),DEST+'/'+name)
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30)
 raw=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,err+raw
 (D/receipt).write_text(raw,encoding='utf8');print(raw.strip())
finally:c.close()
