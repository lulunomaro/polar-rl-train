"""New full15s consumer, gated by the actual independent native120 admission."""
from pathlib import Path
import json,hashlib,time,shutil,zipfile,ast
D=Path(__file__).resolve().parent;W=D.parent
OLD=W/'MOD4_3060_FULL80_PARAMETER_BOUND_20261014';proof=OLD/'reports/FULL80_NATIVE120_INDEPENDENT_CPU_DATA_ADMISSION_PASSED.json';v=json.loads(proof.read_bytes());assert v['passed'] and v['controls']==120 and v['no_PPO_or_budgetaction']
R=W/'MOD4_3060_FULL80_FROZEN_CURRENT_20261014';assert not R.exists();R.mkdir();(R/'reports').mkdir();Q=R/'payload';shutil.copytree(OLD/'payload',Q)
worker=(Q/'paired_full80_parameter_bound_v2.py').read_text().replace('MOD4_3060_FULL80_PARAMETER_BOUND_20261014','MOD4_3060_FULL80_FROZEN_CURRENT_20261014')
(Q/'paired_full80_parameter_bound_v2.py').write_text(worker,encoding='utf8')
# Preserve the legacy pre-wrapper snapshot and add a separately labelled first-physics snapshot.
p=Q/'full80_runtime_native_v1.py';s=p.read_text();original=s
anchor='    cap = e._integrated_contact';assert s.count(anchor)==1
s=s.replace(anchor,"    initial_pre_wrapper=initial\n    initial=dict(root=js(r.data.root_state_w),q=js(r.data.joint_pos),parameters=e.chassis_pd_audit(),assignments=assignments(e),reset=e._rough_probe_reset_receipt,actual_all_physical_parameters=params(e))\n    save('FIRST_PHYSICS_INITIAL_ACTUAL.json',dict(phase='after RSL wrapper reset and policy construction, before first physical control',values=initial,legacy_pre_wrapper_values=initial_pre_wrapper,readonly_no_setters_or_RNG=True))\n    cap = e._integrated_contact")
before=ast.parse(original);after=ast.parse(s)
loop=lambda t:next(x for x in ast.walk(t) if isinstance(x,ast.For) and ast.unparse(x.target)=='step')
assert ast.dump(loop(before),include_attributes=False)==ast.dump(loop(after),include_attributes=False)
p.write_text(s,encoding='utf8');compile(s,str(p),'exec');compile(worker,'paired_full80_parameter_bound_v2.py','exec')
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();m=Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'
rows=[dict(relative=str(p.relative_to(Q)).replace('\\','/'),bytes=p.stat().st_size,sha256=H(p)) for p in Q.rglob('*') if p.is_file() and p!=m and '__pycache__' not in p.parts]
m.write_text(json.dumps(dict(protocol='approved_E1_G4_derived50mm_worldmesh_actualray_approach040_fullroute_behavior_v2',actual_native120_admission=dict(path=str(proof),sha256=H(proof)),only_new_firstphysics_readonly_initial_snapshot=True,physical_control_loop_AST_exact=True,file_rows=rows),indent=2),encoding='utf8')
pack=R/'FULL80_FROZEN1500_SOURCE_V1.zip'
with zipfile.ZipFile(pack,'w',zipfile.ZIP_DEFLATED) as z:
 for p in Q.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:z.write(p,str(p.relative_to(Q)).replace('\\','/'))
metadata=dict(epoch=time.time(),CPU_prepared=True,source_SHA=H(Q/'source/model_32411_17b.pt'),worker=dict(path=str(Q/'paired_full80_parameter_bound_v2.py'),sha256=H(Q/'paired_full80_parameter_bound_v2.py')),runtime=dict(path=str(p),sha256=H(p)),manifest=dict(path=str(m),sha256=H(m)),package=dict(path=str(pack),bytes=pack.stat().st_size,sha256=H(pack)),actual_native120_scope_pass_reused_by_path_size_SHA=True,firstphysics_initial_and_legacy_prewrapper_initial_phases_separately_saved=True,physical_loop_ASTexact=True,original80_27_27_26_9m_50mm_040approach_15s_1N_200mmafter_unmodified=True,full1500_GPU_NOT_launched=True,qualified50=False)
metadata['runtime']=dict(path=str(Q/'full80_runtime_native_v1.py'),sha256=H(Q/'full80_runtime_native_v1.py'))
(R/'reports/FULL80_NATIVE_CPU_PORT_PREPARED_ACTUAL.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')
deploy=(OLD/'deploy_full80_parameter_bound_native120_once.py').read_text().replace('MOD4_3060_FULL80_PARAMETER_BOUND_20261014','MOD4_3060_FULL80_FROZEN_CURRENT_20261014').replace('native3060_Linux20k_final_full80_parameter_bound_native120_v2','native3060_Linux20k_final_full80_frozen1500_v1').replace('MOD4_Linux20kFinalFull80ParameterBound_20261014_Native120_v2','MOD4_Linux20kFinalFull80Frozen_20261014_Frozen1500_v1').replace('FULL80_NATIVE_SOURCE_V2.zip','FULL80_FROZEN1500_SOURCE_V1.zip').replace('steps=120,num_envs=80','steps=1500,num_envs=80').replace('demand_full80_native120_parent_launcher_unique_once.py','demand_full80_frozen1500_parent_launcher_unique_once.py').replace('native120_only_not_full15s_or_qualification=True','full_original1500_protocol_qualification_requires_complete_review=True')
(R/'deploy_full80_frozen1500_unique_once.py').write_text(deploy,encoding='utf8');compile(deploy,'deploy_full80_frozen1500_unique_once.py','exec')
collect=(OLD/'collect_full80_parameter_bound_native120_readonly.py').read_text().replace('MOD4_3060_FULL80_PARAMETER_BOUND_20261014','MOD4_3060_FULL80_FROZEN_CURRENT_20261014').replace('native3060_Linux20k_final_full80_parameter_bound_native120_v2','native3060_Linux20k_final_full80_frozen1500_v1')
(R/'collect_full80_frozen1500_readonly.py').write_text(collect,encoding='utf8')
print(json.dumps(dict(root=str(R),prepared=True,physical_loop_ASTexact=True,sourceSHA=metadata['source_SHA'],packageSHA=H(pack),GPU_NOT_started=True)))
