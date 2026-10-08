"""New immutable real D5 evaluator, all three skills including corrected D4 world."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'D5_CLOSEDLOOP_PACKAGE_PUBLISHED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008'
try:
    code=r'''
from pathlib import Path
import json,zipfile,hashlib,os,time,ast
D=Path('/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008');R=D/'reports';E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not (R/'D5_CLOSEDLOOP_PACKAGE_PUBLISHED.json').exists()
a=read(E/'reports/PLAN_APPROVAL.json');assert a['approved'] and 'S2' in a['allowed_stages']
base=read(E/'eval_queue/clk2500-closure-episode-d3-45-d4world-anchor-world.json')['artifacts']['runtime'];assert base['sha256']=='347ca4183e4f4cfa4ab98492637718996b62b9d4b1cb9f7f4119514484356ce5'==sha(base['path'])
with zipfile.ZipFile(base['path']) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
assert all(hashlib.sha256(payload[n]).hexdigest()==h for n,h in m['files'].items())
for name in ('spring_pressure_component.py','spring_pressure_index_runtime.py','spring_pressure_audit_runtime.py','spring_nominal_sdk_readback.py','spring_pressure_training_env.py'):
 payload['runtime/isaac/mod4/'+name]=(D/'isaac/mod4'/name).read_bytes()
env=json.loads(payload['runtime/isaac/mod4/env.json']);env['RM_SPRING_PRESSURE_PROFILE']='gas_stiffness_independent_episode_090_110_v1';payload['runtime/isaac/mod4/env.json']=json.dumps(env,indent=2).encode()
for name in ('frozen_history_flat.py','frozen_history_spin.py','frozen_history_world.py'):
 key='runtime/isaac/mod4/'+name;s=payload[key].decode()
 old='from action_delay_training_env import ActionDelayMod4Env';assert s.count(old)==1
 s=s.replace(old,'from spring_pressure_training_env import SpringPressureMod4Env as ActionDelayMod4Env' if 'as Mod4Env' not in s.split(old,1)[1].splitlines()[0] else 'from spring_pressure_training_env import SpringPressureMod4Env')
 # Only the import path changes; the existing wrapper/manual command and
 # actual D4 physical target adapter remain inherited for every skill.
 lines=s.splitlines(keepends=True);indices=[i for i,line in enumerate(lines) if line.lstrip().startswith('initial_action_assignments=') or 'env.reset();initial_action_assignments=' in line]
 assert len(indices)==1,(name,indices)
 i=indices[0];lines.insert(i+1,"    spring_initial_assignments=dict(factor=env._spring_pressure.component.factor.cpu().tolist(),episode=env._spring_pressure.component.episode.cpu().tolist(),actual_stiffness_N_m=env._spring_pressure.component.actual_stiffness(env._spring_pressure.nominal).cpu().tolist())\n")
 s=''.join(lines);anchor="    result['D4_closed_loop_actual_physical_target_delay']=True";assert s.count(anchor)==1
 extra="    result['D5_closed_loop_stiffness_engineering_pressure']=True\n    result['spring_pressure_recipe']=env.spring_pressure_recipe()\n    result['spring_pressure_audit']=env._spring_pressure.audit()\n    result['spring_pressure_initial_episode_assignments']=spring_initial_assignments\n    result['spring_pressure_final_episode_assignments']=dict(factor=env._spring_pressure.component.factor.cpu().tolist(),episode=env._spring_pressure.component.episode.cpu().tolist(),actual_stiffness_N_m=env._spring_pressure.component.actual_stiffness(env._spring_pressure.nominal).cpu().tolist())\n"
 s=s.replace(anchor,extra+anchor);ast.parse(s);payload[key]=s.encode()
 # Imports must actually use the D5 environment even in standalone world.
 imports=[n for n in ast.parse(s).body if isinstance(n,ast.ImportFrom) and n.module=='spring_pressure_training_env'];assert len(imports)==1 and imports[0].names[0].name=='SpringPressureMod4Env' and imports[0].names[0].asname in ('Mod4Env','ActionDelayMod4Env')
manifest=dict(m,files={n:hashlib.sha256(b).hexdigest() for n,b in payload.items()},base_corrected_D4_world_archive_SHA=base['sha256'],D5_actual_stiffness_episode_pressure=True,nominal_model_unchanged=True,hardware_force_stroke_calibration=False,world_uses_true_D5_and_D4_environment=True,full_learning_save_state_not_restored_in_frozen_evaluation=True)
dest=E/'artifacts/d5-clock2500-solver32-spring255-closedloop-frozen.zip';assert not dest.exists()
with zipfile.ZipFile(str(dest)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
os.replace(str(dest)+'.partial',dest)
package=dict(path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size)
descriptors={kind:package for kind in ('flat','spin','world')};(R/'D5_FROZEN_BEHAVIOR_PACKAGES.json').write_text(json.dumps(descriptors,indent=2))
v=dict(epoch=time.time(),package=package,all_three_real_D5_D4_dispatchers=True,baseline_candidate_scope_pending=True,source_count=len(read(R/'SOURCE_FREEZE.json')['sha256']),no_GPU_PPO_canonical_write=True)
(R/'D5_CLOSEDLOOP_PACKAGE_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
    _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=40);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw);(R/'D5_CLOSEDLOOP_PACKAGE_PUBLISHED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
    with c.open_sftp() as f:f.get(root+'/reports/D5_FROZEN_BEHAVIOR_PACKAGES.json',str(R/'D5_FROZEN_BEHAVIOR_PACKAGES.json'))
    print(json.dumps(v))
finally:c.close()
