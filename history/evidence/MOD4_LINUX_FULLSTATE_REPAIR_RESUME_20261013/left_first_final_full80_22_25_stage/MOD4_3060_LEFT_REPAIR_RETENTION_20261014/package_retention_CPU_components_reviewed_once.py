"""CPU packaging after independent phase fixtures. Does not grant or launch GPU."""
from pathlib import Path
import ast,hashlib,json,time,zipfile,sys
import numpy as np
D=Path(__file__).resolve().parent;P=D/'payload';R=D/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=R/'FINAL_CPU_PREPARED_PACKAGE_ACTUAL.json';zip_path=D/'retention_native_v3_CPU_PREPARED_COMPONENTS.zip';assert not out.exists() and not zip_path.exists()
files=[P/'retention_worker_v3.py',P/'retention_parent_v3.py',P/'retention_native_witness_v3.py']+[P/('retention_'+k+'_native_v3.py') for k in ('flat','spin','world')]+[P/'RETENTION_CPU_MANIFEST_V3.json']
files+=list((P/'original').glob('*.py'))+list((P/'cpu_contracts').glob('*.py'))
for file in D.rglob('*.py'):compile(file.read_text(encoding='utf8'),str(file),'exec')
manifest=json.loads((P/'RETENTION_CPU_MANIFEST_V3.json').read_bytes())
for row in manifest['origins']:
 kind=row['kind'];old=next(n for n in ast.parse(Path(row['source']).read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='main')
 new=next(n for n in ast.parse((P/('retention_'+kind+'_native_v3.py')).read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef))
 select=lambda fn:{ast.unparse(n.targets[0]):ast.dump(n.value,include_attributes=False) for n in ast.walk(fn) if isinstance(n,ast.Assign) and len(n.targets)==1 and ast.unparse(n.targets[0]) in ('common','strict','strict_integrated','skill','skill_legacy_reference','physical')}
 assert select(old)==select(new),(kind,'numeric gates')
sys.path.insert(0,str((P/'cpu_contracts').resolve()));from world_cycle_metrics import measure_world_cycles
math_fixture=[]
for sign in (-1,1):
 t=np.arange(1501)*.01;heading=sign*2*t;xy=np.stack((.5*t,.01*np.sin(heading)),-1);v=measure_world_cycles(t,xy,heading,0.,sign,-1)
 assert v['complete_cycle_count']==4 and abs(v['complete_prefix_along_m_s']-.5)<1e-12 and abs(v['complete_prefix_cross_m_s'])<max(.03,.1*.5)
 cut=measure_world_cycles(t,xy,heading,0.,sign,302);assert cut['whole_prefix_duration_s']==float(t[301]) and cut['complete_cycle_count']==0 and not cut['post_failure_samples_used']
 math_fixture.append(dict(sign=sign,complete_prefix=v,failure_prefix=cut))
assert math_fixture[0]['complete_prefix']['complete_prefix_cross_m_s']==-math_fixture[1]['complete_prefix']['complete_prefix_cross_m_s']
rows=[dict(relative=f.relative_to(P).as_posix(),bytes=f.stat().st_size,sha256=H(f)) for f in files]
with zipfile.ZipFile(zip_path,'x',compression=zipfile.ZIP_DEFLATED) as z:
 for file in files:z.write(file,file.relative_to(P).as_posix())
report=dict(epoch=time.time(),status='CPU_PREPARED_ONLY',approved_GPU=False,package=dict(path=str(zip_path),bytes=zip_path.stat().st_size,sha256=H(zip_path)),package_files=rows,all_current_local_sources_compile=True,original_numeric_gate_AST_untouched_source_comparison=True,original_signed_cycle_CPUmath_positive_negative_and_failure_prefix_passed=True,CPU_analytic_fixture=math_fixture,original_fixture_error_retained=str(R/'ORIGINAL_CPU_PACKAGE_SYNTHETIC_ASSERTION_ERROR.json'),observer_phase_CPUfixture_actual=str(R/'OBSERVER_SYNTHETIC_CPU_PHASE_CALL_PASSED.json'),shared_payload_target=manifest['shared_payload_target'],worker='retention_worker_v3.py',parent='retention_parent_v3.py',ports=['retention_'+k+'_native_v3.py' for k in ('flat','spin','world')],sources=manifest['sources'],seed=20261002,cases=[{k:x[k] for k in ('kind','num_envs','steps','seed')} for x in manifest['cases']],only_actor_loaded_no_fullstate_DR_restore=True,actual_plane_native_query_API_unverified=True,API_reference=dict(get_current_stage_saved_actual_source='MOD4_3060_DIRECT_FACTOR_20261013/sdk_readonly_source/11_isaaclab__sim____init__.py',native_ground_existing_source='shared runtime/isaac/mod4/ground_plane_candidate.py',raycast_all='New omni.physx scene_query Interface call; own native actual result required, no prior PASS claimed'),no_transport_no_GPU_no_PPO=True,pending_Git_by_root=True)
out.write_text(json.dumps(report,indent=2),encoding='utf8')
template=dict(target_host='10.24.4.249',namespace='MOD4_3060_LEFT_REPAIR_RETENTION_20261014',GPU_lease_granted_by_root=False,actual_shared_slot_idle_verified=False,case_id='ROOT_TO_ASSIGN_UNUSED_CASE',checkpoint_sha256=manifest['sources']['baseline1aa']['sha256'],checkpoint_path='ROOT_TO_BIND_ACTUAL_REMOTE_SOURCE_PATH',worker_sha256=H(P/'retention_worker_v3.py'),port_sources_sha256={n:H(P/n) for n in ['retention_native_witness_v3.py','retention_flat_native_v3.py']},shared_payload_target=manifest['shared_payload_target'],source_manifest_sha256=H(P/'RETENTION_CPU_MANIFEST_V3.json'),case_parameters=dict(kind='flat',steps=120,num_envs=80,seed=20261002,headless=True,device='cuda:0'))
(R/'ROOT_LEASE_TEMPLATE_UNAPPROVED.json').write_text(json.dumps(template,indent=2),encoding='utf8')
print(json.dumps({k:report[k] for k in ('status','approved_GPU','package','cases','worker','parent','actual_plane_native_query_API_unverified')},ensure_ascii=False))
