"""Only serialize actual numeric hardware constants without a tensor conversion."""
from pathlib import Path
import ast,hashlib,json,time,zipfile
D=Path(__file__).resolve().parent;P=D/'payload';R=D/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
report_path=R/'HARDWARE_SCALAR_V5_FAILURE_AND_V6_CPU_PREPARED.json';assert not report_path.exists()
A=D/'actual_collections/retention_baseline1aa_flat_120_v5/1791948960682246800/attempts/retention_baseline1aa_flat_120_v5/output'
failure=A/'ORIGINAL_ERROR.json';query=A/'QUERY_first_physics_ALLHITS_ACTUAL.json';f=json.loads(failure.read_bytes());q=json.loads(query.read_bytes())
assert "'float' object has no attribute 'requires_grad'" in f['error'] and f['no_PPO']
assert q['complete_all_envs'] is True and len(q['all_rays'])==80 and q['actual_USD_scene_query_support'] is True
for row in q['all_rays']:
 assert not row['serializer_errors'] and row['selected_plane_hits']
 hit=min(row['selected_plane_hits'],key=lambda x:x['hit']['distance'])['hit']
 assert abs(hit['position'][2])<=1e-6 and abs(hit['normal'][2]-1.)<=1e-6
old=P/'retention_native_witness_v5.py';text=old.read_text(encoding='utf8')
FUNCTION='''def scalar_or_tensor_json(value):
 """Keep exact native scalars; all tensor/ProxyArray reads use original js."""
 import numbers
 if isinstance(value,np.generic):value=value.item()
 if isinstance(value,bool):return value
 if isinstance(value,numbers.Integral):return int(value)
 if isinstance(value,numbers.Real):
  result=float(value);assert math.isfinite(result),'Nonfinite actual hardware constant';return result
 return js(value)

'''
text=text.replace('class Witness:',FUNCTION+'class Witness:')
oldcall="key:js(getattr(r.actuators[name],key))";newcall="key:scalar_or_tensor_json(getattr(r.actuators[name],key))";assert text.count(oldcall)==1;text=text.replace(oldcall,newcall)
path=P/'retention_native_witness_v6.py';assert not path.exists();compile(text,str(path),'exec');path.write_text(text,encoding='utf8',newline='\n')
new_ast=ast.parse(text);new_ast.body=[n for n in new_ast.body if not (isinstance(n,ast.FunctionDef) and n.name=='scalar_or_tensor_json')]
class RevertSingleCall(ast.NodeTransformer):
 def visit_Name(self,n):
  if n.id=='scalar_or_tensor_json':n.id='js'
  return n
new_ast=RevertSingleCall().visit(new_ast);assert ast.dump(new_ast,include_attributes=False)==ast.dump(ast.parse(old.read_text(encoding='utf8')),include_attributes=False)
for kind in ('flat','spin','world'):
 oldport=P/('retention_'+kind+'_native_v5.py');text=oldport.read_text(encoding='utf8').replace('retention_native_witness_v5','retention_native_witness_v6');path=P/('retention_'+kind+'_native_v6.py');assert not path.exists();compile(text,str(path),'exec');path.write_text(text,encoding='utf8',newline='\n')
 oldfn=next(n for n in ast.parse(oldport.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef));newfn=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef));assert ast.dump(oldfn,include_attributes=False)==ast.dump(newfn,include_attributes=False)
path=P/'retention_worker_v6.py';assert not path.exists();text=(P/'retention_worker_v5.py').read_text(encoding='utf8').replace('RETENTION_CPU_MANIFEST_V5.json','RETENTION_CPU_MANIFEST_V6.json').replace('retention_native_witness_v5','retention_native_witness_v6').replace("'_native_v5.py'","'_native_v6.py'").replace("+'_native_v5'","+'_native_v6'");compile(text,str(path),'exec');path.write_text(text,encoding='utf8',newline='\n')
path=P/'retention_parent_v6.py';assert not path.exists();text=(P/'retention_parent_v5.py').read_text(encoding='utf8').replace('retention_worker_v5.py','retention_worker_v6.py').replace('RETENTION_CPU_MANIFEST_V5.json','RETENTION_CPU_MANIFEST_V6.json');compile(text,str(path),'exec');path.write_text(text,encoding='utf8',newline='\n')
path=D/'review_retention_full_actual_CPU_v6.py';assert not path.exists();text=(D/'review_retention_full_actual_CPU_v5.py').read_text(encoding='utf8').replace('RETENTION_CPU_MANIFEST_V5.json','RETENTION_CPU_MANIFEST_V6.json');compile(text,str(path),'exec');path.write_text(text,encoding='utf8',newline='\n')
dc_source=D.parent/'MOD4_3060_DIRECT_FACTOR_20261013/sdk_hardware_readonly_source/isaaclab__actuators__actuator_pd.py';assert 'self._saturation_effort = self.cfg.saturation_effort' in dc_source.read_text(encoding='utf8')
report=dict(epoch=time.time(),status='V6_CPU_PREPARED_ONLY',approved_GPU=False,original_V5_failure=dict(path=str(failure),sha256=H(failure),no_PPO=True,original_PASS_not_claimed=True),own_V5_complete_all80_actual_query_subcontract=dict(path=str(query),bytes=query.stat().st_size,sha256=H(query),all80_actual_firstphysics_hits_original1e6_passed=True,scope_not_native_control_PASS=True),new_axis='Only scalar-aware actual hardware constant JSON serializer; native Python/NumPy numbers kept as scalars, tensor/ProxyArray original js path exact',only_single_constant_serializer_call_changed_and_other_witness_AST_exact=True,all_three_main_AST_exact_to_V5=True,actual_query_serializer_V5_preserved=dict(path=str(P/'raycast_hit_serializer_v5.py'),sha256=H(P/'raycast_hit_serializer_v5.py')),actual_DC_source=dict(path=str(dc_source),sha256=H(dc_source),observed_initializer='self._saturation_effort = self.cfg.saturation_effort; other velocity/effort limits are tensor buffers'),other_direct_js_calls_reviewed='Only root_state_w and joint_pos in witness; actual V5 reached and captured these fields before hardware_constants; factor params already completed',no_hardware_coefficient_or_shape_threshold_RNG_reset_reward_solver_change=True,no_SSH_no_GPU_no_PPO=True)
manifest=json.loads((P/'RETENTION_CPU_MANIFEST_V5.json').read_bytes());manifest['v6_hardware_scalar_serializer_repair']=report;manifest['prepared_files_v6']=[dict(path=str(x),relative=x.relative_to(P).as_posix(),bytes=x.stat().st_size,sha256=H(x)) for x in sorted(P.glob('*v6.py'))]
(P/'RETENTION_CPU_MANIFEST_V6.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
files=[P/'retention_worker_v6.py',P/'retention_parent_v6.py',P/'retention_native_witness_v6.py',P/'raycast_hit_serializer_v5.py',P/'SDK_RAYCAST_HIT_DECLARATION_V5.json']+[P/('retention_'+k+'_native_v6.py') for k in ('flat','spin','world')]+[P/'RETENTION_CPU_MANIFEST_V6.json']+list((P/'original').glob('*.py'))+list((P/'cpu_contracts').glob('*.py'))
zip_path=D/'retention_hardware_scalar_serializer_v6_CPU_COMPONENTS.zip';assert not zip_path.exists()
with zipfile.ZipFile(zip_path,'x',compression=zipfile.ZIP_DEFLATED) as z:
 for x in files:z.write(x,x.relative_to(P).as_posix())
report['package']=dict(path=str(zip_path),bytes=zip_path.stat().st_size,sha256=H(zip_path));report['package_files']=[dict(relative=x.relative_to(P).as_posix(),bytes=x.stat().st_size,sha256=H(x)) for x in files];report_path.write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({k:report[k] for k in ('status','approved_GPU','new_axis','package')}))
