"""Explicit review of staged file-name mapping; original rejected entry is not repeated."""
from pathlib import Path
import sys,shlex,json,ast
D=Path(__file__).resolve().parent;R=D/'reports';root='/home/egde/rl_candidates/MOD4_PHYSICS_DT2000_CROSSBIN_REVIEW_20261007'
assert (R/'DT2000_STAGING_ERROR.txt').exists()
text=(D/'stage_clock2000_review_once.py').read_text(encoding='utf8')
code=text.split(" code=r'''",1)[1].split("'''.replace",1)[0]
files=['physics_clock.py','physics_clock2000.py','isaac/mod4/contact_capture.py','isaac/mod4/mod4_env.py','isaac/mod4/train_mod4_ppo.py','isaac/mod4/clock_training_health.py','supervise_clock2000_review.py','physics_speed2000_probe.py','contact_crossbin_sdk.py','contact_bin_oracle.py','test_clock2000_cpu.py']
code=code.replace('ROOT',root).replace('CHANGES',repr(files))
code=code.replace("D/'review_changes'/Path(n).name", "D/'review_changes'/('physics_clock2000.py' if n=='physics_clock.py' else Path(n).name)")
code=code.replace("f=json.loads((J/'reports/SOURCE_FREEZE.json').read_text());assert len(f['sha256'])==175", "assert not (R/'SELECTED_CLOCK_LAUNCHED.json').exists()\nassert not (R/'STAGING_PATH_REVIEW_STARTED.json').exists()\n(R/'STAGING_PATH_REVIEW_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),original_rejection='Uploadedphysics_clock2000.py addressed by runtimealiasphysics_clock.py before authority change',reviewed_alias_mapping=True)))\nf=json.loads((J/'reports/SOURCE_FREEZE.json').read_text());assert len(f['sha256'])==175")
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect;c=connect()
try:
 with c.open_sftp() as s:s.put(str(R/'DT2000_STAGING_ERROR.txt'),root+'/reports/INITIAL_STAGING_PATH_ERROR.txt')
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:(R/'DT2000_PATH_REVIEW_ERROR.txt').write_bytes(err);raise RuntimeError(err.decode())
 print(raw.decode())
 with c.open_sftp() as s:
  for n in ['SOURCE_FREEZE.json','DT2000_SAFE_BOUNDARY.json','SELECTED_CLOCK_LAUNCHED.json','CLOCK2000_CPU.txt']:s.get(root+'/reports/'+n,str(R/('DT2000_'+n)))
finally:c.close()
