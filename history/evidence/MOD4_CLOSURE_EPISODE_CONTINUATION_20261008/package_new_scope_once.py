from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'FROZEN_PACKAGE_INSTALLED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,zipfile,hashlib,os,time
D=Path('/home/egde/rl_candidates/MOD4_CLOSURE_EPISODE_CONTINUATION_20261008');R=D/'reports';E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));import supervise_closure_episode_continuation as w
w.verify();assert not (R/'FROZEN_PACKAGE_INSTALLED.json').exists()
base=E/'artifacts/d3-clock1000-closedloop231-frozen.zip';assert w.s.q.base.sha(base)=='30476d366b22281ecd680a521a6145ad66b707c9c3e2f888ce01afc12705317e'
f=w.read(R/'SOURCE_FREEZE.json')['sha256'];assert len(f)==234
payload={'runtime/'+n:(D/n).read_bytes() for n in f}
with zipfile.ZipFile(base) as z:
 original=json.loads(z.read('SOURCE_MANIFEST.json'))
 for n,h in original['files'].items():
  if n.startswith('assets/') or n.startswith('runtime/isaac/mod4/frozen_history_'):
   raw=z.read(n);assert hashlib.sha256(raw).hexdigest()==h;payload[n]=raw
for kind in ('flat','spin','world'):
 n='runtime/isaac/mod4/frozen_history_'+kind+'.py';raw=payload[n].decode();old='env.physics_dt==.001';assert raw.count(old)==1;raw=raw.replace(old,'env.physics_dt==.0025');compile(raw,n,'exec');payload[n]=raw.encode()
cfgname='runtime/isaac/mod4/env.json';cfg=json.loads(payload[cfgname]);assert cfg['RM_PHYSICS_DT_S']=='0.0025' and cfg['RM_SOLVER_POS']=='32';cfg['RM_FEEDBACK_DELAY_PROFILE']='control_0_10ms_v1';cfg['RM_SENSOR_PROFILE']='noise_bias_mild_v1';payload[cfgname]=json.dumps(cfg,indent=2).encode()
assert hashlib.sha256(payload['assets/robot.usd']).hexdigest()=='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87'
target=E/'artifacts/d3-clock2500-solver32-closure234-frozen.zip';assert not target.exists()
clock=dict(original['clock']);clock.update(physics_dt_s=.0025,decimation=4,policy_dt_s=.01,contact_bin_s=.005,solver_position_iterations=32,solver_velocity_iterations=4)
manifest=dict(files={n:hashlib.sha256(v).hexdigest() for n,v in payload.items()},clock=clock,source_count=234,source_map=f,allowed_windows_adapter=['RM_MOD4_USD'],asset_originals_unchanged=True,feedback_delay_profile='control_0_10ms_v1',fixed_clean_actions=False,actual_delayed_actor_feedback_closed_loop=True,closedloop_skill_scope_not_yet_accepted=True,global_closure_policy_version=3,task_closure_reset_threshold_m=.002)
with zipfile.ZipFile(str(target)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
 for n,v in payload.items():z.writestr(n,v)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
os.replace(str(target)+'.partial',target)
v=dict(epoch=time.time(),path=str(target),bytes=target.stat().st_size,sha256=w.s.q.base.sha(target),source_count=234,new_closedloop_scope_pending_actual_behavior=True,no_GPU_or_budget_operation=True)
w.s.q.base.atomic_json(R/'D3_FROZEN_BEHAVIOR_PACKAGE.json',v);w.s.q.base.atomic_json(R/'FROZEN_PACKAGE_INSTALLED.json',v);print(json.dumps(v))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw)
 (R/'FROZEN_PACKAGE_INSTALLED.json').write_text(json.dumps(v,indent=2),encoding='utf8');(R/'D3_FROZEN_BEHAVIOR_PACKAGE.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
