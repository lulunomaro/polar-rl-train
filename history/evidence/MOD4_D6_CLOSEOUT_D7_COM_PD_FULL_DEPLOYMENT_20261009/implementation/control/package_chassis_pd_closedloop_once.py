"""Freeze all three actual D7 dispatchers; old packages and live sources retained."""
from pathlib import Path
import json,sys,shlex
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'D7_CLOSEDLOOP_PACKAGE_PUBLISHED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import json,zipfile,hashlib,os,time,ast
D=Path('/home/egde/rl_candidates/MOD4_D7_FULL_CONTRACT_20261009');R=D/'reports';E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not (R/'D7_CLOSEDLOOP_PACKAGE_PUBLISHED.json').exists()
base=E/'artifacts/d6-clock2500-solver32-gas265-closedloop-frozen.zip';assert sha(base)=='0f51e024c9f5c2cc7448b814203e2f21c810618fb246138c7cdcab92a5dbb3c7'
with zipfile.ZipFile(base) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
assert all(hashlib.sha256(payload[n]).hexdigest()==h for n,h in m['files'].items())
for n in ('chassis_com_component.py','chassis_com_pose_roundtrip_sdk_adapter.py','chassis_pd_nominal_readback.py','explicit_pd_component.py','explicit_pd_sdk_adapter.py','chassis_pd_training_env.py','chassis_pd_checkpoint.py'):
 payload['runtime/isaac/mod4/'+n]=(D/'isaac/mod4'/n).read_bytes()
env=json.loads(payload['runtime/isaac/mod4/env.json']);env.update(RM_CHASSIS_COM_PROFILE='chassis_link_local_independent_xyz_5mm_v1',RM_EXPLICIT_PD_PROFILE='explicit_motor_PD_independent_095_105_v1');payload['runtime/isaac/mod4/env.json']=json.dumps(env,indent=2).encode()
assignment="dict(COM=dict(delta_m=env._chassis_com.component.delta_m.cpu().tolist(),episode=env._chassis_com.component.episode.cpu().tolist()),PD=dict(factors={k:v.cpu().tolist() for k,v in env._explicit_pd.component.factor.items()},episode=env._explicit_pd.component.episode.cpu().tolist(),actual_coefficients={k:v.cpu().tolist() for k,v in env._explicit_pd.component.coefficients().items()}))"
for n in ('frozen_history_flat.py','frozen_history_spin.py','frozen_history_world.py'):
 key='runtime/isaac/mod4/'+n;t=payload[key].decode();old='from gas_damping_training_env import GasDampingMod4Env';assert t.count(old)==1;t=t.replace(old,'from chassis_pd_training_env import ChassisPDMod4Env')
 lines=t.splitlines(keepends=True);idx=[i for i,l in enumerate(lines) if l.lstrip().startswith('gas_initial_assignments=')];assert len(idx)==1;lines.insert(idx[0]+1,'    chassis_pd_initial_assignments='+assignment+'\n');t=''.join(lines)
 anchor="    result['D6_closed_loop_gas_damping_engineering_pressure']=True";assert t.count(anchor)==1
 extra="    result['D7_closed_loop_chassis_COM_explicit_PD_engineering_pressure']=True\n    result['chassis_PD_recipe']=env.chassis_pd_recipe()\n    result['chassis_PD_audit']=env.chassis_pd_audit()\n    result['chassis_PD_initial_episode_assignments']=chassis_pd_initial_assignments\n    result['chassis_PD_final_episode_assignments']="+assignment+'\n'
 t=t.replace(anchor,anchor+'\n'+extra.rstrip());tree=ast.parse(t);imports=[x for x in tree.body if isinstance(x,ast.ImportFrom) and x.module=='chassis_pd_training_env'];assert len(imports)==1 and imports[0].names[0].name=='ChassisPDMod4Env' and imports[0].names[0].asname in ('Mod4Env','ActionDelayMod4Env');payload[key]=t.encode()
manifest=dict(m,files={n:hashlib.sha256(b).hexdigest() for n,b in payload.items()},base_D6_archive_SHA=sha(base),D7_chassis_only_COM5mm_explicit_motor_PD095_105=True,all_three_dispatchers_use_real_complete_D0_D7_environment=True,learning_state_not_restored_in_frozen_evaluation=True,hardware_calibrated=False)
dest=E/'artifacts/d7-clock2500-solver32-chassisPD277-closedloop-frozen.zip';assert not dest.exists()
with zipfile.ZipFile(str(dest)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
os.replace(str(dest)+'.partial',dest);package=dict(path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size)
(R/'D7_FROZEN_BEHAVIOR_PACKAGES.json').write_text(json.dumps({k:package for k in ('flat','spin','world')},indent=2));v=dict(epoch=time.time(),package=package,all_three_real_COM_PD_dispatchers=True,scope_pending=True,source_count=277,canonical_or_GPU_write=False)
(R/'D7_CLOSEDLOOP_PACKAGE_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
 (R/'D7_CLOSEDLOOP_PACKAGE_PUBLISHED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 with c.open_sftp() as f:f.get('/home/egde/rl_candidates/MOD4_D7_FULL_CONTRACT_20261009/reports/D7_FROZEN_BEHAVIOR_PACKAGES.json',str(R/'D7_FROZEN_BEHAVIOR_PACKAGES.json'))
 print(json.dumps(v))
finally:c.close()
