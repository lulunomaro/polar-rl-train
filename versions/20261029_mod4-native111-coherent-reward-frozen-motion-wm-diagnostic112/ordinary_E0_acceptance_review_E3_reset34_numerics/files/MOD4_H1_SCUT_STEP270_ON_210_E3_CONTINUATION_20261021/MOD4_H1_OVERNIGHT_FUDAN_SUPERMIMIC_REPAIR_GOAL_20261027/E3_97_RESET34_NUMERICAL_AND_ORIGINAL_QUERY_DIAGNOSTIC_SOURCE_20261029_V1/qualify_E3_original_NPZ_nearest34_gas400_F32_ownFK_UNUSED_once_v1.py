"""Explicit NEW necessary reset-source qualification, ONE original NPZ byte read.

No model/PT/other raw/SDK/host/physics. Never clamps or rewrites q/placement.
Original 2mm closure rule only; authored clearance is diagnostic, not manifold.
"""
from pathlib import Path
import ast,hashlib,importlib.util,io,json,os,time,traceback
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent;W=T.parent
M=L/'E3_97_SOURCE210_ENTRY_RECEIPT_CLI_CLOSURE_REPAIR_SOURCE_20261029_V4/E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json'
N=T/'MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029/payloads_v2/seed27'
SHA='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83'
def H(raw):return hashlib.sha256(raw).hexdigest()
def put(n,v):
 with (B/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 import numpy as np,torch
 manifest_raw=M.read_bytes();m=json.loads(manifest_raw);rows={r['relative']:r for r in m['files']}
 br=rows['runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz'];p=Path(br['local_path']);assert br['SHA']==SHA and br['bytes']==32022178 and p.resolve().is_relative_to(W.resolve())
 cr=rows['runtime/assets/import_contract.json'];craw=Path(cr['local_path']).read_bytes();assert H(craw)==cr['SHA']=='517cd6a4cc469455af08da75dc4b7f7cb596b375bafb4c3e566c7df5bc51df49';contract=json.loads(craw)
 same=(N/'job0/assets/import_contract.json').read_bytes();assert same==craw
 gpath=N/'source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json';graw=gpath.read_bytes();assert H(graw)=='461f6b44e6014c72a755a0db5136fa8d45bd5b53b6318ee4b38221a4c597bc4d';geom=json.loads(graw);assert len(geom['shapes'])==34
 fkpath=N/'source/own_step_differentiable_geometry_v1.py';fkraw=fkpath.read_bytes();assert b'class OwnStepWheelGeometry' in fkraw
 cachep=Path(rows['runtime/isaac/mod4/e3_reset_bank_cache_v1.py']['local_path']);cache_raw=cachep.read_bytes();assert H(cache_raw)==rows['runtime/isaac/mod4/e3_reset_bank_cache_v1.py']['SHA']
 cp=ast.parse(cache_raw);geometry_fn=next(n for n in cp.body if isinstance(n,ast.FunctionDef) and n.name=='_geometry')
 evalp=Path(rows['runtime/isaac/mod4/h1_authored_full_collider_plane_reference_v1.py']['local_path']);evalraw=evalp.read_bytes();assert H(evalraw)==rows['runtime/isaac/mod4/h1_authored_full_collider_plane_reference_v1.py']['SHA']
 assert not torch.cuda.is_initialized()
 put('NPZ_NUMERICAL_QUALIFICATION_CONSUMED_BEFORE_ONE_READ.json',dict(epoch=time.time(),purpose='NEW E3 actual selected q34 numeric gas400/ownFK qualification; not stats/Git',input_manifest=str(M),input_manifest_SHA=H(manifest_raw),producer=br,maximum_original_NPZ_byte_read_count=1,no_PT_other_raw_SDK_remote_or_physics=True))
 reads=0
 with p.open('rb') as f:
  before=os.fstat(f.fileno());data=f.read();reads+=1;after=os.fstat(f.fileno())
 assert (before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns) and len(data)==br['bytes'] and H(data)==SHA
 with np.load(io.BytesIO(data),allow_pickle=False) as bank:
  names_array=bank['joint_names'];height_array=bank['root_height'];q_array=bank['q'];points_array=bank['points_root']
  assert np.isfinite(height_array).all();pick=int(np.argmin(abs(height_array-.25)))
  names=[x.decode() if isinstance(x,bytes) else str(x) for x in names_array.tolist()]
  assert pick==34 and len(names)==len(set(names))==30 and set(names)==set(contract['joints'])
  q_source=np.array(q_array[pick],copy=True);points_source=np.array(points_array[pick],copy=True)
 assert reads==1 and q_source.shape==(30,) and points_source.ndim==2 and points_source.shape[1]==3
 assert np.isfinite(q_source).all() and np.isfinite(points_source).all()
 q=torch.tensor(q_source,dtype=torch.float32);points=torch.tensor(points_source,dtype=torch.float32)
 limit_rows=[];violations=[]
 for i,name in enumerate(names):
  spec=contract['joints'][name];limits=spec['limits_si'];r=dict(name=name,bank_column=i,q_actual_float32=float(q[i]),joint_type=spec['type'],limits_si=limits)
  if limits is not None:
   lower,upper=(torch.tensor(v,dtype=torch.float32) for v in limits);lo=float((lower-q[i]).clamp_min(0));hi=float((q[i]-upper).clamp_min(0));r.update(lower_overshoot=lo,upper_overshoot=hi,out_of_domain=bool(q[i]<lower or q[i]>upper))
   if r['out_of_domain']:violations.append(r)
  else:r.update(out_of_domain=False,unbounded_original_joint=True)
  limit_rows.append(r)
 # Original reset geometry function, original float32 q/points and13 recipes.
 scope={'torch':torch};exec(compile(ast.Module(body=[geometry_fn],type_ignores=[]),str(cachep),'exec'),scope)
 recipes=torch.arange(13,dtype=torch.long);quat,minima,initial=scope['_geometry'](points,recipes)
 spec=importlib.util.spec_from_file_location('_new_E3_q34_qualified_ownFK_no_model',fkpath);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 tree=module.OwnStepWheelGeometry(contract,geom,names).cpu();R=module.qmat(quat[:,[3,0,1,2]]);root=torch.zeros(13,3);root[:,2]=.0001-minima
 qq=q[None].expand(13,30).clone();zero=torch.zeros(13,3);state=(root,R,zero,zero,qq,torch.zeros_like(qq),torch.zeros(13,54))
 with torch.inference_mode():fk=tree(state)
 positions=fk['body_position'];rotations=fk['body_rotation'];assert positions.dtype==rotations.dtype==torch.float32 and torch.isfinite(positions).all() and torch.isfinite(rotations).all()
 loops={};body=tree.body_names
 for name,row in contract['closures'].items():
  i=body.index(row['body0']);j=body.index(row['body1']);a0=torch.tensor(row['anchor0_m'],dtype=torch.float32);a1=torch.tensor(row['anchor1_m'],dtype=torch.float32)
  p0=positions[:,i]+(rotations[:,i]@a0[:,None]).squeeze(-1);p1=positions[:,j]+(rotations[:,j]@a1[:,None]).squeeze(-1)
  loops[name]=(p0-p1).norm(dim=-1)
 worst=torch.stack(list(loops.values())).amax(0)
 # Reuse exact authored-shape evaluator; matrix row supplied directly instead of re-encoding quaternions.
 evaltree=ast.parse(evalraw);fn=next(n for n in evaltree.body if isinstance(n,ast.FunctionDef) and n.name=='evaluate');old=ast.dump(fn,include_attributes=False)
 found=0
 for node in ast.walk(fn):
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='rz' for t in node.targets):
   assert isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='body_world_z_row';node.value=ast.parse('quat[:,ids,2,:]',mode='eval').body;found+=1
 assert found==1
 env={'torch':torch};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(evalp),'exec'),env)
 clear=env['evaluate'](positions,rotations,geom['shapes']);assert clear.shape==(13,34) and torch.isfinite(clear).all()
 recipe_rows=[];degrees=[-90,-60,-30,30,60,90]
 for k in range(13):
  recipe_rows.append(dict(recipe=k,axis='roll_X' if k<6 else 'pitch_Y' if k<12 else 'identity',angle_degrees=degrees[k%6] if k<12 else 0,quat_xyzw=quat[k].tolist(),original_sampled_minimum_m=float(minima[k]),requested_root_z_m=float(root[k,2]),initial_peak_upright=float(initial[k]),F32_tree_loop_residuals_m={name:float(value[k]) for name,value in loops.items()},F32_worst_loop_m=float(worst[k]),within_original_2mm_tree_residual=bool(worst[k]<=.002),authored_F32_minimum_clearance_m=float(clear[k].min()),authored_F32_clearance34_m=clear[k].tolist(),negative_authored_clearance_shape_paths=[geom['shapes'][i]['path'] for i in range(34) if float(clear[k,i])<0],not_cooked_manifold_or_PhysX_result=True))
 result=dict(kind='E3_nearest34_original_NPZ_numeric_gas400_and_F32_ownFK_qualification_v1',epoch=time.time(),new_necessary_purpose_not_Git_statistics=True,original_NPZ_byte_read_count=reads,decoded_original_array_names_once=['joint_names','root_height','q','points_root'],producer=dict(path=str(p),bytes=len(data),SHA=H(data),manifest_path=str(M),manifest_SHA=H(manifest_raw),original_fstat_before_after_equal=True),selected_bank_pose_index=pick,pose_index34_is_NOT_34_pose_count=True,root_height_selected_m=float(height_array[pick]),q_original_dtype=str(q_source.dtype),points_original_dtype=str(points_source.dtype),actual_runtime_cast='float32 exactly as original E3ResetBankCache',q30_named_values=[dict(name=n,q_source=float(q_source[i]),q_actual_float32=float(q[i])) for i,n in enumerate(names)],selected_points_shape=list(points_source.shape),all_selected_q_points_finite=True,joint_name_set_exact30=True,joint_name_order_handled_by_original_names_not_assumed_columns=True,gas=[r for r in limit_rows if r['name'] in ('left_gas_slide','right_gas_slide')],all_joint_limit_checks=limit_rows,out_of_domain=violations,hard_limits_passed=not violations,F32_tree_all13_original_2mm_passed=bool((worst<=.002).all()),F32_tree_max_loop_residual_m=float(worst.max()),source_contract=dict(path=str(Path(cr['local_path'])),SHA=cr['SHA'],same111_400_contract_bytes=True),source_ownFK=dict(path=str(fkpath),SHA=H(fkraw),state30_actual_coordinates_no_mimic_imposition=True,no_SDK_USD_or_model_read=True),source_geometry=dict(path=str(gpath),SHA=H(graw),authored_shapes=34),source_original_cache=dict(path=str(cachep),SHA=H(cache_raw)),source_authored_support=dict(path=str(evalp),SHA=H(evalraw),only_pure_matrix_row_adaptation=True),recipes=recipe_rows,
  numerical_scope_passed=not violations and bool((worst<=.002).all()),no_q_clamp_or_source_NPZ_recipe_guard_asset_physics_change=True,no_FP64_1um_or_new_triangle_health_gate=True,initial_authored_clearance_is_not_actual_cooked_contact_or_write_order_proof=True,original74bank_qerr_before_E3_override_not_used_as_q34_proof=True,normal_policy_later_instability_still_requires_new_actual_trace=True,skill_graduation=False)
 put('E3_Q34_ONE_NPZ_NUMERICAL_GAS400_F32_OWNFK_ACTUAL.json',result)
 print(json.dumps(dict(passed_numeric_scope=result['numerical_scope_passed'],NPZ_reads=reads,gas=result['gas'],out_of_domain=violations,max_F32_tree_closure_m=float(worst.max()),min_authored_clearance_by_recipe=[x['authored_F32_minimum_clearance_m'] for x in recipe_rows],no_physics_or_model=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('ORIGINAL_Q34_NUMERICAL_QUALIFICATION_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),old_model_or_SDK_or_remote_reads=0,do_not_repeat_consumed_NPZ_purpose_without_parent=True));raise
