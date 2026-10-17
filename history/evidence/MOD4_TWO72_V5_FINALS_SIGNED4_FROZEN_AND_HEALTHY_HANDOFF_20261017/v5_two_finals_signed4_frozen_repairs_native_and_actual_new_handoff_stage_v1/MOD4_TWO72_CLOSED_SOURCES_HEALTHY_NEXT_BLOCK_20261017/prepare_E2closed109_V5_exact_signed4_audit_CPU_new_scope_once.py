"""Bind evaluator audit to the approved source signed4 task; preserve V4 zero-control rejection."""
from pathlib import Path
import ast,copy,hashlib,json,shutil,sys,time,types,zipfile
import torch
D=Path(__file__).resolve().parent;R=D/'reports';E=D/'e2_closed109_frozen_prepared_v5';Q=E/'payload';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
oldcase=json.loads((R/'E2_CLOSED109_NATIVE120_V4_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json').read_bytes());assert oldcase['parent_child_launcher_actual_absent'] and oldcase['shared_OS_lock_free'] and oldcase['complete'] is None and 'World-to-body reference or moving yaw bound mismatch' in oldcase['original_error']['error'];assert not E.exists()
task=json.loads((D/'payload/e2/job0/TASK.json').read_bytes());assert task['kind']=='E2_WORLD_MOVING_SIGNED4' and task['first_E2_moving_yaw_signed_rad_s']==4 and task['world_speed_goal_m_s']==.5
E.mkdir();shutil.copytree(D/'e2_closed109_frozen_prepared_v4/payload',Q,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
original=Q/'frozen_shared/runtime/isaac/mod4/directional_spin_runtime.py';tree=ast.parse(original.read_text('utf8'));node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='audit');old=ast.unparse(node);assert old.count('2.00001')==1 and old.count("'moving_yaw_max_rad_s': 2.0")==1
new=old.replace('2.00001','4.00001').replace("'moving_yaw_max_rad_s': 2.0","'moving_yaw_max_rad_s': 4.0")
module="\"\"\"Owned frozen-evaluation signed4 audit; original cap2 runtime source remains unchanged.\"\"\"\nimport torch\nfrom directional_spin_runtime import DirectionalSpinCommand\nfrom spin_translation_math import body_command\n"+new+'\n';ast.parse(module);(Q/'e2_closed109_signed4_audit_v5.py').write_text(module,encoding='utf8',newline='\n')
p=Q/'retention_world_native_v8.py';s=p.read_text('utf8');assert s.count('from spin_commands import audit')==1;shutil.copy2(p,Q/'historical_original_components/V4_retention_world_native_v8.py');s=s.replace('from spin_commands import audit','from e2_closed109_signed4_audit_v5 import audit');ast.parse(s);p.write_text(s,encoding='utf8',newline='\n')
sys.path.insert(0,str(Q/'frozen_shared/runtime/isaac/mod4'));from spin_translation_math import body_command
class Command:pass
def fixture():
 t=Command();t.cfg=types.SimpleNamespace(heading_command=False);t.is_heading_env=torch.zeros(4,dtype=torch.bool);t.is_pure_spin=torch.zeros(4,dtype=torch.bool);t.is_moving_spin=torch.ones(4,dtype=torch.bool);t.is_transition_spin=torch.zeros(4,dtype=torch.bool);t.is_standing_env=torch.zeros(4,dtype=torch.bool);t.manual_evaluation_mode=False;t.pure_max=4.;t.progress_goal=.5;t.body_limit=1.5;t.pure_fraction=.3;t.moving_fraction=.2;t.world_direction=torch.tensor([0.,.5,1.,2.]);t.robot=types.SimpleNamespace(data=types.SimpleNamespace(heading_w=types.SimpleNamespace(torch=torch.tensor([.4,.3,-.2,2.4]))));t.command=torch.zeros(4,3);t.command[:,0]=body_command(t.progress_goal,t.world_direction,t.robot.data.heading_w.torch,t.body_limit)[0];t.command[:,2]=torch.tensor([4.,-4.,4.,-4.]);return t
ns=dict(torch=torch,DirectionalSpinCommand=Command,body_command=body_command);exec(compile(new,'<actual source-derived signed4 audit CPU>','exec'),ns);legacy=dict(ns);exec(compile(old,'<unchanged legacy cap2 audit CPU>','exec'),legacy)
t=fixture();env=lambda t:types.SimpleNamespace(command_manager=types.SimpleNamespace(get_term=lambda name:t));assert ns['audit'](env(t))['moving_yaw_max_rad_s']==4
try:legacy['audit'](env(t))
except RuntimeError:legacy_false=True
else:raise AssertionError('Old cap2 source unexpectedly accepted signed4')
negative=[]
for mode in ('heading_override','nonfinite','overlap','standing_overlap','pure_translation','lateral','yaw_above4','projection_mismatch'):
 t=fixture()
 if mode=='heading_override':t.cfg.heading_command=True
 elif mode=='nonfinite':t.command[0,0]=float('nan')
 elif mode=='overlap':t.is_pure_spin[0]=True
 elif mode=='standing_overlap':t.is_standing_env[0]=True
 elif mode=='pure_translation':t.is_pure_spin[0]=True;t.is_moving_spin[0]=False
 elif mode=='lateral':t.command[0,1]=.001
 elif mode=='yaw_above4':t.command[0,2]=4.001
 else:t.command[0,0]+=.001
 try:ns['audit'](env(t))
 except RuntimeError:negative.append(mode)
 else:raise AssertionError(mode)
worker=(Q/'e2_frozen_worker_v4.py').read_text('utf8').replace('MANIFEST_V4','MANIFEST_V5').replace('FROZEN_V4_20261017','FROZEN_V5_20261017');ast.parse(worker);(Q/'e2_frozen_worker_v5.py').write_text(worker,encoding='utf8',newline='\n')
parent=(Q/'e2_frozen_parent_v4.py').read_text('utf8').replace('e2_frozen_worker_v4.py','e2_frozen_worker_v5.py').replace('MANIFEST_V4','MANIFEST_V5')
parent=parent.replace('sys.exit(child.returncode)',"sys.exit(child.returncode if child.returncode else (1 if any((O/n).exists() for n in ('ORIGINAL_ERROR.json','ORIGINAL_ERROR_BEFORE_APP_CLOSE.json','FAILED_PREFIX_SAVER_ORIGINAL_ERROR.json','APP_CLOSE_ORIGINAL_ERROR.json')) else 0))")
ast.parse(parent);(Q/'e2_frozen_parent_v5.py').write_text(parent,encoding='utf8',newline='\n')
manifest=json.loads((Q/'E2_CLOSED109_FROZEN_COMPLETE_MANIFEST_V4.json').read_bytes());rows=[]
for p in sorted(x for x in Q.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.suffix!='.pyc'):
 if p.suffix=='.py':ast.parse(p.read_text('utf8'))
 rows.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
manifest.update(version=5,files=rows,package_files_v8=[dict(relative=x['relative'],bytes=x['bytes'],sha256=x['SHA']) for x in rows],explicit_frozen_signed4_audit_source_SHA=H(Q/'e2_closed109_signed4_audit_v5.py'),original_runtime_cap2_audit_SHA_preserved=H(original),no_source_actor_command_generator_physics_DR_reward_or_installed_SDK_change=True)
mf=Q/'E2_CLOSED109_FROZEN_COMPLETE_MANIFEST_V5.json';mf.write_text(json.dumps(manifest,indent=2),encoding='utf8');bundle=E/'E2_CLOSED109_COMPLETE_FROZEN_PAYLOAD_V5.zip'
with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for row in rows:z.write(Q/row['relative'],row['relative'])
 z.write(mf,mf.name)
v=dict(epoch=time.time(),passed_complete_payload_CPU_only=True,source=manifest['source'],manifest=dict(path=str(mf),bytes=mf.stat().st_size,SHA=H(mf)),package=dict(path=str(bundle),bytes=bundle.stat().st_size,SHA=H(bundle)),files=len(rows),worker=dict(path=str(Q/'e2_frozen_worker_v5.py'),SHA=H(Q/'e2_frozen_worker_v5.py')),parent=dict(path=str(Q/'e2_frozen_parent_v5.py'),SHA=H(Q/'e2_frozen_parent_v5.py')),source_task_declared_signed4_worldVpoint5=True,old_cap2_CPU_false_preserved=legacy_false,exact_original_audit_only_two_scope_constants_changed=True,negative_cases=negative,original_V4_actual_precontrol_failure_and_EXIT0_with_original_error_not_pass=True,new_parent_preserves_child_exit0_but_returns_failure_if_original_error=True,original_SDK_sources_unchanged=True,new_native_scope_still_unused=True)
with (R/'E2_CLOSED109_COMPLETE_FROZEN_V5_SIGNED4_AUDIT_CPU_PREPARED.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(dict(CPU_signed4_scope_audit_passed=True,oldcap2_false_preserved=True,negative_cases=len(negative),files=len(rows),no_GPU_yet=True)))
