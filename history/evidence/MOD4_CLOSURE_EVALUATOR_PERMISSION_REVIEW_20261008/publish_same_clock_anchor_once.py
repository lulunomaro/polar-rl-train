from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'SAME_CLOCK_ANCHOR_PUBLISHED.json').exists();sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,time
D=Path('/home/egde/rl_candidates/MOD4_CLOSURE_EPISODE_CONTINUATION_20261008');R=D/'reports';sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));import supervise_closure_episode_continuation as w
import torch;torch.set_num_threads(1);w.verify();assert not (R/'SAME_CLOCK_ANCHOR_PUBLISHED.json').exists()
src=Path(w.read(R/'SAVED_BOUNDARY_SOURCE.json')['checkpoint']['path']);v=w.fullsave(src);assert v['sha256']=='b88b66e974e6f4a5e17fa6bcc7f2311224d09c9b63ef0ff8c7c5e69ea2402e1b'
w.publish(src,'10-anchor');row=w.read(R/'D3_10-anchor_ASYNC_PUBLISHED.json');assert len(row['jobs'])==3
v=dict(epoch=time.time(),source=v,package=w.read(R/'D3_FROZEN_BEHAVIOR_PACKAGE.json'),same_candidate_clock_solver_delay_recipe=True,new_2point5_D3_behavior_scope_pending=True,source_is_transition_baseline_not_graduated_expert=True,jobs=row['jobs'],no_new_4090_probe_or_PPO=True,no_canonical_write=True);w.s.q.base.atomic_json(R/'SAME_CLOCK_ANCHOR_PUBLISHED.json',v);print(json.dumps(dict(epoch=v['epoch'],source=v['source']['sha256'],jobs=[j['job_id'] for j in v['jobs']],no_4090_training_interruption=True)))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode()
 with c.open_sftp() as sf:sf.get('/home/egde/rl_candidates/MOD4_CLOSURE_EPISODE_CONTINUATION_20261008/reports/SAME_CLOCK_ANCHOR_PUBLISHED.json',str(R/'SAME_CLOCK_ANCHOR_PUBLISHED.json'))
 print(raw.decode())
finally:c.close()
