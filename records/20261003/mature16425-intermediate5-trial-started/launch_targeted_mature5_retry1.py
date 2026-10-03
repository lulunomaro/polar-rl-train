import shlex,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
D=Path(__file__).resolve().parent;R='/home/egde/rl_candidates/MOD4_RATE6_TARGETED_REPAIR_20261003';PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
c=connect()
try:
 with c.open_sftp() as s:s.put(str(D/'recover_targeted_mature5_guardian_args.py'),R+'/recover_targeted_mature5_guardian_args.py')
 _,o,e=c.exec_command(PY+' '+shlex.quote(R+'/recover_targeted_mature5_guardian_args.py'),timeout=40);raw=o.read().decode();error=e.read().decode();assert o.channel.recv_exit_status()==0,error
 (D/'TARGETED_MATURE5_RETRY1_LAUNCHED.json').write_text(raw);print(raw)
finally:c.close()
