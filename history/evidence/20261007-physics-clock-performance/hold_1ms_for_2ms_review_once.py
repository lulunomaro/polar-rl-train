from pathlib import Path
import sys,shlex,json
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
assert not (R/'DT2000_HOLD_LAUNCH_PERMISSION.json').exists()
code=r'''
from pathlib import Path
import sys,os,signal,time,json
D=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT1000_FALLBACK_20261007');sys.path.insert(0,str(D));import supervise_clock1000_fallback as q
assert q.base.budget_state()['active_segment'] is None and not q.w.read(q.ctl.STATE_PATH).get('active_training') and not q.base.trainers()
p=q.helpers.identity(690939);assert p and p['start_ticks']==46934422 and str(D/'supervise_clock1000_fallback.py') in p['argv']
s=q.w.read(D/'reports/SELECTED_CLOCK_STATE.json');assert s['phase']=='frozen_flat'
os.kill(p['pid'],signal.SIGSTOP)
for _ in range(100):
 a=q.helpers.identity(p['pid'])
 if a and a['state']=='T':break
 time.sleep(.02)
else:raise RuntimeError('Parent stop acknowledgement absent')
v=dict(epoch=time.time(),human_message='你直接验证吧，磨刀不误砍柴工',requested_candidate_physics_dt_s=.002,
 owner_before=p,owner_stop_ack=a,existing_frozen_child=q.helpers.identity(s['child']['pid']),existing_output=s['output'],
 active_segment=None,no_GPU_child_signal=True,no_new_PPO=True,no_budget_mutation=True,next='Let current1msflat finish naturally; preserve real evidence; retire launch authority at no-active boundary, then isolated2ms cross-bin review')
q.write('DT2000_HOLD_LAUNCH_PERMISSION.json',v);print(json.dumps(v))
'''
c=connect()
try:
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,err.decode();v=json.loads(raw)
 (R/'DT2000_HOLD_LAUNCH_PERMISSION.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
