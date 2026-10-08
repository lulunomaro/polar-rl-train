"""Freeze exact D5 assets with real gas damping for flat, spin and world."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'D6_CLOSEDLOOP_PACKAGE_PUBLISHED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
    code=r'''
from pathlib import Path
import json,zipfile,hashlib,os,time,ast
D=Path('/home/egde/rl_candidates/MOD4_D6_FULL_CONTRACT_20261009');R=D/'reports';E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not (R/'D6_CLOSEDLOOP_PACKAGE_PUBLISHED.json').exists()
base=read(Path('/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008/reports/D5_FROZEN_BEHAVIOR_PACKAGES.json'))['world']
assert base['sha256']=='fe8dc6bcb027215739a9edf7a8b5fa46240326b402e05ae0d0463db87044452c'==sha(base['path'])
with zipfile.ZipFile(base['path']) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
assert all(hashlib.sha256(payload[n]).hexdigest()==h for n,h in m['files'].items())
new=('gas_damping_factor.py','gas_damping_sdk_adapter.py','gas_damping_training_env.py','gas_damping_checkpoint.py')
for n in new:payload['runtime/isaac/mod4/'+n]=(D/'isaac/mod4'/n).read_bytes()
env=json.loads(payload['runtime/isaac/mod4/env.json']);env['RM_GAS_DAMPING_PROFILE']='gas_damping_independent_episode_090_110_v1';payload['runtime/isaac/mod4/env.json']=json.dumps(env,indent=2).encode()
for n in ('frozen_history_flat.py','frozen_history_spin.py','frozen_history_world.py'):
 key='runtime/isaac/mod4/'+n;t=payload[key].decode();old='from spring_pressure_training_env import SpringPressureMod4Env';assert t.count(old)==1
 t=t.replace(old,'from gas_damping_training_env import GasDampingMod4Env')
 lines=t.splitlines(keepends=True);indices=[i for i,line in enumerate(lines) if line.lstrip().startswith('spring_initial_assignments=')];assert len(indices)==1
 lines.insert(indices[0]+1,"    gas_initial_assignments=dict(factor=env._gas_damping.component.factor.cpu().tolist(),episode=env._gas_damping.component.episode.cpu().tolist(),actual_damping_Ns_m=env._gas_damping.component.actual_damping_Ns_per_m().cpu().tolist())\n")
 t=''.join(lines);anchor="    result['D5_closed_loop_stiffness_engineering_pressure']=True";assert t.count(anchor)==1
 extra="    result['D6_closed_loop_gas_damping_engineering_pressure']=True\n    result['gas_damping_recipe']=env.gas_damping_recipe()\n    result['gas_damping_audit']=env._gas_damping.audit()\n    result['gas_damping_initial_episode_assignments']=gas_initial_assignments\n    result['gas_damping_final_episode_assignments']=dict(factor=env._gas_damping.component.factor.cpu().tolist(),episode=env._gas_damping.component.episode.cpu().tolist(),actual_damping_Ns_m=env._gas_damping.component.actual_damping_Ns_per_m().cpu().tolist())\n"
 t=t.replace(anchor,extra+anchor);tree=ast.parse(t)
 imports=[x for x in tree.body if isinstance(x,ast.ImportFrom) and x.module=='gas_damping_training_env'];assert len(imports)==1 and imports[0].names[0].name=='GasDampingMod4Env' and imports[0].names[0].asname in ('Mod4Env','ActionDelayMod4Env')
 payload[key]=t.encode()
manifest=dict(m,files={n:hashlib.sha256(b).hexdigest() for n,b in payload.items()},base_D5_archive_SHA=base['sha256'],D6_actual_gas_damping_only=True,all_three_skills_use_complete_D0_D6_environment=True,full_learning_save_state_not_restored_in_frozen_evaluation=True,hardware_calibrated=False,friction_randomization=False)
dest=E/'artifacts/d6-clock2500-solver32-gas265-closedloop-frozen.zip';assert not dest.exists()
with zipfile.ZipFile(str(dest)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
os.replace(str(dest)+'.partial',dest)
package=dict(path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size)
(R/'D6_FROZEN_BEHAVIOR_PACKAGES.json').write_text(json.dumps({k:package for k in ('flat','spin','world')},indent=2))
v=dict(epoch=time.time(),package=package,all_three_real_D6_gas_D5_D4_dispatchers=True,baseline_candidate_scope_pending=True,source_count=265,no_GPU_PPO_canonical_write=True)
(R/'D6_CLOSEDLOOP_PACKAGE_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
    _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw);(R/'D6_CLOSEDLOOP_PACKAGE_PUBLISHED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
    with c.open_sftp() as f:f.get('/home/egde/rl_candidates/MOD4_D6_FULL_CONTRACT_20261009/reports/D6_FROZEN_BEHAVIOR_PACKAGES.json',str(R/'D6_FROZEN_BEHAVIOR_PACKAGES.json'))
    print(json.dumps(v))
finally:c.close()
