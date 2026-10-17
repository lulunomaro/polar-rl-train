"""New isolated scope binds both public probe and owned environment periodic audit; no installed edits."""
from pathlib import Path
import ast,hashlib,json,shutil,sys,time,types,zipfile
D=Path(__file__).resolve().parent;R=D/'reports';E=D/'e2_closed109_frozen_prepared_v6';Q=E/'payload';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prior=json.loads((R/'E2_CLOSED109_NATIVE120_V5_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json').read_bytes());assert prior['parent_child_launcher_actual_absent'] and prior['shared_OS_lock_free'] and prior['complete'] is None and 'mod4_env.py' in prior['original_error']['error'];assert not E.exists();E.mkdir();shutil.copytree(D/'e2_closed109_frozen_prepared_v5/payload',Q,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
p=Q/'frozen_shared/runtime/isaac/mod4/spin_commands.py';s=p.read_text('utf8');shutil.copy2(p,Q/'historical_original_components/V5_spin_commands.py');old='from directional_spin_runtime import audit as world_audit';assert s.count(old)==1;s=s.replace(old,'from e2_closed109_signed4_audit_v5 import audit as world_audit');ast.parse(s);p.write_text(s,encoding='utf8',newline='\n')
envsource=(Q/'frozen_shared/runtime/isaac/mod4/mod4_env.py').read_text('utf8');assert 'from spin_commands import audit as audit_spin' in envsource
world=Q/'retention_world_native_v8.py';s=world.read_text('utf8');assert 'from e2_closed109_signed4_audit_v5 import audit' in s
text="""    import spin_commands,hashlib
    from retention_native_witness_v8 import CONTEXT
    wrapper=Path(spin_commands.__file__);assert 'e2_closed109_signed4_audit_v5' in spin_commands.audit.__code__.co_names
    CONTEXT['save']('ACTUAL_SIGNED4_AUDIT_BINDINGS_BEFORE_PHYSICS.json',dict(periodic_owned_wrapper_path=str(wrapper),periodic_owned_wrapper_SHA=hashlib.sha256(wrapper.read_bytes()).hexdigest(),public_probe_audit_module=audit.__module__,owned_periodic_and_public_both_bound_signed4=True,no_installed_SDK_edit=True,no_actor_or_RNG_draw=True))
"""
marker='    torch.manual_seed(args.seed)';assert s.count(marker)==1;s=s.replace(marker,text+marker);ast.parse(s);world.write_text(s,encoding='utf8',newline='\n')
# Execute the exact wrapper audit, not a string-only check; reject changed stage as original.
node=next(n for n in ast.parse(p.read_text('utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='audit');calls=[];fake=types.ModuleType('e2_closed109_signed4_audit_v5');fake.audit=lambda env:calls.append(env) or {'moving_yaw_max_rad_s':4.};previous=sys.modules.get(fake.__name__);sys.modules[fake.__name__]=fake
import os
before=os.environ.get('RM_SPIN_STAGE');os.environ['RM_SPIN_STAGE']='world_directional_v1'
try:
 scope={'os':os};exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual periodic owned audit dispatch CPU>','exec'),scope);token=object();assert scope['audit'](token)=={'moving_yaw_max_rad_s':4.} and calls==[token]
finally:
 if before is None:os.environ.pop('RM_SPIN_STAGE',None)
 else:os.environ['RM_SPIN_STAGE']=before
 if previous is None:sys.modules.pop(fake.__name__,None)
 else:sys.modules[fake.__name__]=previous
worker=(Q/'e2_frozen_worker_v5.py').read_text('utf8').replace('MANIFEST_V5','MANIFEST_V6').replace('FROZEN_V5_20261017','FROZEN_V6_20261017');ast.parse(worker);(Q/'e2_frozen_worker_v6.py').write_text(worker,encoding='utf8',newline='\n');parent=(Q/'e2_frozen_parent_v5.py').read_text('utf8').replace('e2_frozen_worker_v5.py','e2_frozen_worker_v6.py').replace('MANIFEST_V5','MANIFEST_V6');ast.parse(parent);(Q/'e2_frozen_parent_v6.py').write_text(parent,encoding='utf8',newline='\n')
manifest=json.loads((Q/'E2_CLOSED109_FROZEN_COMPLETE_MANIFEST_V5.json').read_bytes());rows=[]
for p in sorted(x for x in Q.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.suffix!='.pyc'):
 if p.suffix=='.py':ast.parse(p.read_text('utf8'))
 rows.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
manifest.update(version=6,files=rows,package_files_v8=[dict(relative=x['relative'],bytes=x['bytes'],sha256=x['SHA']) for x in rows],both_owned_public_and_periodic_audit_entrypoints_explicit_signed4=True,no_installed_SDK_or_other_live_scope_edit=True)
mf=Q/'E2_CLOSED109_FROZEN_COMPLETE_MANIFEST_V6.json';mf.write_text(json.dumps(manifest,indent=2),encoding='utf8');bundle=E/'E2_CLOSED109_COMPLETE_FROZEN_PAYLOAD_V6.zip'
with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for row in rows:z.write(Q/row['relative'],row['relative'])
 z.write(mf,mf.name)
v=dict(epoch=time.time(),passed_complete_payload_CPU_only=True,source=manifest['source'],manifest=dict(path=str(mf),bytes=mf.stat().st_size,SHA=H(mf)),package=dict(path=str(bundle),bytes=bundle.stat().st_size,SHA=H(bundle)),files=len(rows),worker=dict(path=str(Q/'e2_frozen_worker_v6.py'),SHA=H(Q/'e2_frozen_worker_v6.py')),parent=dict(path=str(Q/'e2_frozen_parent_v6.py'),SHA=H(Q/'e2_frozen_parent_v6.py')),actual_owned_periodic_wrapper_AST_function_CPU_executed=True,both_entrypoints_verified=True,old_V4_zero_controls_and_V5_zero_controls_four_physics_saved_original_errors_retained=True,no_installed_SDK_physics_actor_command_generator_DR_reward_change=True,new_native_scope_still_unused=True)
with (R/'E2_CLOSED109_COMPLETE_FROZEN_V6_ALL_OWNED_AUDIT_BINDINGS_CPU_PREPARED.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(dict(CPU_actual_periodic_binding=True,public_binding=True,files=len(rows),no_GPU_yet=True)))
