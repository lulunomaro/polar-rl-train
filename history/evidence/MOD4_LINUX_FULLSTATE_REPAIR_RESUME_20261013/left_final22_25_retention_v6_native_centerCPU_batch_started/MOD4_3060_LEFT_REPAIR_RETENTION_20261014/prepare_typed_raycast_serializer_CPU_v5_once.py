"""Independent typed-hit serializer repair; no transport, GPU or training."""
from pathlib import Path
import ast,hashlib,json,time,zipfile
D=Path(__file__).resolve().parent;P=D/'payload';R=D/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
report_path=R/'RAYCAST_TYPED_V4_FAILURE_AND_V5_CPU_PREPARED.json';assert not report_path.exists()
collection=D/'actual_collections/retention_baseline1aa_flat_native120_v4/1791948359316913600/attempts/retention_baseline1aa_flat_native120_v4'
failure_path=collection/'output/ORIGINAL_ERROR.json';log=collection/'worker.log';query=collection/'output/QUERY_first_physics_ALLHITS_ACTUAL.json'
assert all(x.exists() for x in (failure_path,log,query));assert "RaycastHit' object has no attribute 'items'" in log.read_text(encoding='utf8',errors='replace')
actual_query=json.loads(query.read_bytes());assert actual_query['actual_USD_scene_query_support'] and actual_query['all_rays'][0]['query_return'] is True
stub_path=R/'INSTALLED_RAYCAST_HIT_API_STUB_ACTUAL_1791948423570368200.json';stub=json.loads(stub_path.read_bytes())['rows'][0]
assert stub['sha256']=='49430e3d566a559253408948bae508a174f633cee2359d9b61c91b9cb426d73f'
assert hashlib.sha256(stub['text'].encode('utf8')).hexdigest()==stub['sha256']
classes=[n for n in ast.parse(stub['text']).body if isinstance(n,ast.ClassDef) and n.name in ('RaycastHit','SceneQueryHitLocation','SceneQueryHitObject')]
fields=[n.name for c in classes for n in c.body if isinstance(n,ast.FunctionDef) and any(isinstance(d,ast.Name) and d.id=='property' for d in n.decorator_list)]
assert set(fields)=={'distance','face_index','material','material_encoded','normal','position','collision','collision_encoded','protoIndex','rigid_body','rigid_body_encoded'}
declaration=dict(actual_installed_stub_path=stub['path'],actual_bytes=stub['bytes'],actual_sha256=stub['sha256'],source_report_path=str(stub_path),source_report_sha256=H(stub_path),classes_AST=ast.unparse(ast.Module(body=classes,type_ignores=[])),declared_properties=fields,current_native_typed_object_vs_previous_mapping_disclosed=True)
(P/'SDK_RAYCAST_HIT_DECLARATION_V5.json').write_text(json.dumps(declaration,indent=2),encoding='utf8')
old=P/'retention_native_witness_v4.py';text=old.read_text(encoding='utf8')
text=text.replace(' from omni.physx import get_physx_scene_query_interface',' from omni.physx import get_physx_scene_query_interface\n from raycast_hit_serializer_v5 import serialize_raycast_hit')
text=text.replace("   allhits.append({str(k):value(v) for k,v in hit.items()});return True", "   allhits.append(serialize_raycast_hit(hit));return True")
text=text.replace("  evidence['all_rays'].append(ray);persist()", "  ray['serializer_errors']=[h for h in allhits if h.get('_serializer_error')]\n  evidence['all_rays'].append(ray);persist()\n  assert not ray['serializer_errors'],('Actual typed hit serialization failed',phase,i,ray['serializer_errors'])")
path=P/'retention_native_witness_v5.py';assert not path.exists();compile(text,str(path),'exec');path.write_text(text,encoding='utf8',newline='\n')
old_ast=ast.parse(old.read_text(encoding='utf8'));new_ast=ast.parse(text)
old_nonquery=[n for n in old_ast.body if not (isinstance(n,ast.FunctionDef) and n.name=='plane_query_actual')];new_nonquery=[n for n in new_ast.body if not (isinstance(n,ast.FunctionDef) and n.name=='plane_query_actual')]
assert ast.dump(ast.Module(body=old_nonquery,type_ignores=[]),include_attributes=False)==ast.dump(ast.Module(body=new_nonquery,type_ignores=[]),include_attributes=False)
for kind in ('flat','spin','world'):
 old=P/('retention_'+kind+'_native_v4.py');text=old.read_text(encoding='utf8').replace('retention_native_witness_v4','retention_native_witness_v5');path=P/('retention_'+kind+'_native_v5.py');assert not path.exists();compile(text,str(path),'exec');path.write_text(text,encoding='utf8',newline='\n')
 old_fn=next(n for n in ast.parse(old.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef));new_fn=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef));assert ast.dump(old_fn,include_attributes=False)==ast.dump(new_fn,include_attributes=False)
path=P/'retention_worker_v5.py';assert not path.exists();text=(P/'retention_worker_v4.py').read_text(encoding='utf8').replace('RETENTION_CPU_MANIFEST_V4.json','RETENTION_CPU_MANIFEST_V5.json').replace('retention_native_witness_v4','retention_native_witness_v5').replace("'_native_v4.py'","'_native_v5.py'").replace("+'_native_v4'","+'_native_v5'")
text=text.replace("('retention_native_witness_v5.py','retention_'+a.kind+'_native_v5.py')", "('retention_native_witness_v5.py','retention_'+a.kind+'_native_v5.py','raycast_hit_serializer_v5.py')")
text=text.replace("sdk=json.loads", "assert H(manifest['v5_sdk_primary_stub']['actual_installed_stub_path'])==manifest['v5_sdk_primary_stub']['actual_sha256']\nsdk=json.loads")
compile(text,str(path),'exec');path.write_text(text,encoding='utf8',newline='\n')
path=P/'retention_parent_v5.py';assert not path.exists();text=(P/'retention_parent_v4.py').read_text(encoding='utf8').replace('retention_worker_v4.py','retention_worker_v5.py').replace('RETENTION_CPU_MANIFEST_V4.json','RETENTION_CPU_MANIFEST_V5.json');compile(text,str(path),'exec');path.write_text(text,encoding='utf8',newline='\n')
path=D/'review_retention_full_actual_CPU_v4.py';assert not path.exists();text=(D/'review_retention_full_actual_CPU_v3.py').read_text(encoding='utf8').replace('RETENTION_CPU_MANIFEST_V4.json','RETENTION_CPU_MANIFEST_V5.json');compile(text,str(path),'exec');path.write_text(text,encoding='utf8',newline='\n')
report=dict(epoch=time.time(),status='V5_CPU_PREPARED_ONLY',approved_GPU=False,original_V4_failure=dict(error_path=str(failure_path),error_sha256=H(failure_path),stdout_path=str(log),stdout_sha256=H(log),original_query_receipt_path=str(query),original_query_sha256=H(query),no_PPO=True,original_PASS_not_claimed=True),actual_found='V4 enable-query flag and actual USD flag True; raycast_all callback received actual installed typed RaycastHit; .items serializer failed then empty-hit strict rejection was secondary',primary_stub=declaration,new_axis='Readonly Mapping vs typed-object hit serializer; no scene-query, geometry, step, reset, reward, command, solver, contact, RNG or tolerance changes',nonquery_witness_AST_exact=True,all_three_main_AST_exact_to_V4=True,ground_tolerance_m=1e-6,all_declared_and_public_readable_fields_preserved=True,uint64_encoded_paths_never_cast_through_float=True,callback_serializer_errors_persisted_then_raise_outside_PyBind_callback=True,no_emptyhit_misclassification_of_serializer_error=True,no_SSH_no_GPU_no_PPO=True)
manifest=json.loads((P/'RETENTION_CPU_MANIFEST_V4.json').read_bytes());manifest['v5_sdk_primary_stub']=declaration;manifest['v5_typed_hit_serializer_repair']=report
manifest['prepared_files_v5']=[dict(path=str(x),relative=x.relative_to(P).as_posix(),bytes=x.stat().st_size,sha256=H(x)) for x in sorted(P.glob('*v5.py'))]
(P/'RETENTION_CPU_MANIFEST_V5.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
files=[P/'retention_worker_v5.py',P/'retention_parent_v5.py',P/'retention_native_witness_v5.py',P/'raycast_hit_serializer_v5.py',P/'SDK_RAYCAST_HIT_DECLARATION_V5.json']+[P/('retention_'+k+'_native_v5.py') for k in ('flat','spin','world')]+[P/'RETENTION_CPU_MANIFEST_V5.json']+list((P/'original').glob('*.py'))+list((P/'cpu_contracts').glob('*.py'))
zip_path=D/'retention_typed_raycast_serializer_v5_CPU_COMPONENTS.zip';assert not zip_path.exists()
with zipfile.ZipFile(zip_path,'x',compression=zipfile.ZIP_DEFLATED) as z:
 for x in files:z.write(x,x.relative_to(P).as_posix())
report['package']=dict(path=str(zip_path),bytes=zip_path.stat().st_size,sha256=H(zip_path));report['package_files']=[dict(relative=x.relative_to(P).as_posix(),bytes=x.stat().st_size,sha256=H(x)) for x in files]
report_path.write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({k:report[k] for k in ('status','approved_GPU','new_axis','package')}))
