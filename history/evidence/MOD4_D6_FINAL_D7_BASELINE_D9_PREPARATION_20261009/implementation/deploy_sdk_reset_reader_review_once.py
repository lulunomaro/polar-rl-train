"""Retain exited first CPU reader; correct only SDK selected-reset interpretation."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'D9_RESET_REVIEW_LAUNCHED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D9_COMBINATION_PREPARE_20261009'
try:
 with c.open_sftp() as f:f.put(str(D/'supervise_combination_sdk_reset_review.py'),root+'/supervise_combination_sdk_reset_review.py')
 code=r'''
from pathlib import Path
import subprocess,json,time,ast
D=Path(ROOT);R=D/'reports';assert not (R/'REVIEW_STARTED.json').exists();old=json.loads((R/'STARTED.json').read_text())
assert not (Path('/proc')/str(old['pid'])).exists(),'first reader must actually exit'
assert (R/'ATTENTION.json').exists() and not (R/'PUBLISHED.json').exists()
ast.parse((D/'supervise_combination_sdk_reset_review.py').read_text())
with (D/'reset_reader_review.log').open('x') as f:p=subprocess.Popen(['/usr/bin/python3',str(D/'supervise_combination_sdk_reset_review.py')],cwd=D,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
s=(Path('/proc')/str(p.pid)/'stat').read_text().rsplit(')',1)[1].split();v=dict(epoch=time.time(),pid=p.pid,start_ticks=int(s[19]),root=str(D),original_reader_error_retained=True,existing_SDK_result_reused_no_GPU_rerun=True,no_GPU_PPO_canonical_training_launch_authority=True)
(R/'REVIEW_STARTED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT',repr(root))
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code));raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
 (R/'D9_RESET_REVIEW_LAUNCHED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
