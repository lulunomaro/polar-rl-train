"""Independent explicit Namespace binding; failed V1 source and output are retained."""
from pathlib import Path
import ast,hashlib,json,time,shutil,zipfile
D=Path(__file__).resolve().parent;W=D.parent
OLD=W/'MOD4_3060_FULL80_CURRENT_LINUX_FINAL_20261014';R=W/'MOD4_3060_FULL80_PARAMETER_BOUND_20261014';assert not R.exists();R.mkdir();(R/'reports').mkdir()
j=json.loads(sorted((OLD/'reports').glob('REFERENCE17B_CURRENT_ACTUAL_*.json'))[-1].read_bytes())
error=j['outputs']['ORIGINAL_ERROR.json'];assert error and "no attribute 'dr_profile'" in error['error']
assert j['shared_actual_OS_lock_free'] and all(not p['running'] for p in j['actual_PID_identities']) and j['outputs']['COMPLETE_ACTUAL.json'] is None
Q=R/'payload';shutil.copytree(OLD/'payload',Q)
s=(Q/'paired_full80_native_v1.py').read_text().replace('MOD4_3060_FULL80_CURRENT_LINUX_FINAL_20261014','MOD4_3060_FULL80_PARAMETER_BOUND_20261014')
s=s.replace(" a.pitch_deg=0.;a.roll_deg=0.;a.height_m=.25", " a.dr_profile='white_v3';a.pitch_deg=0.;a.roll_deg=0.;a.height_m=.25")
assert "a.dr_profile='white_v3'" in s
q=Q/'paired_full80_parameter_bound_v2.py';q.write_text(s,encoding='utf8');compile(s,str(q),'exec')
parent=(Q/'run_full80_native_parent_v1.py').read_text().replace('paired_full80_native_v1.py','paired_full80_parameter_bound_v2.py')
(Q/'run_full80_parameter_bound_parent_v2.py').write_text(parent,encoding='utf8');compile(parent,'run_full80_parameter_bound_parent_v2.py','exec')
attrs={x.attr for x in ast.walk(ast.parse((Q/'full80_runtime_native_v1.py').read_text())) if isinstance(x,ast.Attribute) and isinstance(x.value,ast.Name) and x.value.id=='args'}
assert attrs <= {'num_envs','seed','steps','dr_profile','device','checkpoint','output','case_id'},attrs
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert H(Q/'full80_runtime_native_v1.py')==H(OLD/'payload/full80_runtime_native_v1.py')
m=Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json';rows=[dict(relative=str(p.relative_to(Q)).replace('\\','/'),bytes=p.stat().st_size,sha256=H(p)) for p in Q.rglob('*') if p.is_file() and p!=m and '__pycache__' not in p.parts]
m.write_text(json.dumps(dict(protocol='approved_E1_G4_derived50mm_worldmesh_actualray_approach040_fullroute_behavior_v2',original_failed_scope=str(OLD),only_new_explicit_dr_profile_Namespace_binding=True,all_original_full80_physics_runtime_bytes_exact=True,file_rows=rows),indent=2),encoding='utf8')
pack=R/'FULL80_NATIVE_SOURCE_V2.zip'
with zipfile.ZipFile(pack,'w',zipfile.ZIP_DEFLATED) as z:
 for p in Q.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:z.write(p,str(p.relative_to(Q)).replace('\\','/'))
proof=dict(epoch=time.time(),CPU_prepared=True,source_SHA=H(Q/'source/model_32411_17b.pt'),worker=dict(path=str(q),sha256=H(q)),runtime=dict(path=str(Q/'full80_runtime_native_v1.py'),sha256=H(Q/'full80_runtime_native_v1.py')),manifest=dict(path=str(m),sha256=H(m)),package=dict(path=str(pack),bytes=pack.stat().st_size,sha256=H(pack)),all_runtime_args_attributes_explicitly_bound=sorted(attrs),V1_AttributeError_before_environment_creation_retained=True,V1_native_No_physical_or_PPO_pass_claimed=True,V1_actual_all_processes_exit_and_shared_OSlockfree=True,physical_protocol_and_runtime_bytes_unchanged=True,native120_and_full1500_still_NOT_passed=True,no_GPU_or_budget_action=True,qualified50=False)
(R/'reports/FULL80_NATIVE_CPU_PORT_PREPARED_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
deploy=(OLD/'deploy_full80_native120_unique_once.py').read_text().replace('MOD4_3060_FULL80_CURRENT_LINUX_FINAL_20261014','MOD4_3060_FULL80_PARAMETER_BOUND_20261014').replace('native3060_Linux20k_final_full80_native120_v1','native3060_Linux20k_final_full80_parameter_bound_native120_v2').replace('MOD4_Linux20kFinalFull80_20261014_Native120_v1','MOD4_Linux20kFinalFull80ParameterBound_20261014_Native120_v2').replace('FULL80_NATIVE_SOURCE_V1.zip','FULL80_NATIVE_SOURCE_V2.zip').replace('paired_full80_native_v1.py','paired_full80_parameter_bound_v2.py').replace('run_full80_native_parent_v1.py','run_full80_parameter_bound_parent_v2.py')
compile(deploy,'deploy_full80_parameter_bound_native120_once.py','exec');(R/'deploy_full80_parameter_bound_native120_once.py').write_text(deploy,encoding='utf8')
collect=(OLD/'collect_full80_native120_actual_readonly.py').read_text().replace('MOD4_3060_FULL80_CURRENT_LINUX_FINAL_20261014','MOD4_3060_FULL80_PARAMETER_BOUND_20261014').replace('native3060_Linux20k_final_full80_native120_v1','native3060_Linux20k_final_full80_parameter_bound_native120_v2')
(R/'collect_full80_parameter_bound_native120_readonly.py').write_text(collect,encoding='utf8')
print(json.dumps(dict(CPU_prepared=True,root=str(R),package_SHA=H(pack),old_failure_retained=True,new_GPU_NOT_started=True)))
