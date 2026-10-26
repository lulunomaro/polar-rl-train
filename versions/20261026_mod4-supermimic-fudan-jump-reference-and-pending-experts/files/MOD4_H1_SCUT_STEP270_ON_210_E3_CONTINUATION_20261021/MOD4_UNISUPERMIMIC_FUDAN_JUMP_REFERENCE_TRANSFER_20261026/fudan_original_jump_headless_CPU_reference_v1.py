"""Bounded original-robot CPU reference capture. Never imports or controls MOD4/our policy."""
from pathlib import Path
import ast,copy,hashlib,json,os,sys,time,traceback,types
os.environ['CUDA_VISIBLE_DEVICES']=''
import mujoco,numpy as np
ROOT=Path(__file__).resolve().parent;VENDOR=ROOT/'vendor/fudan_rl_wheel_leg';OUT=ROOT/'reference_capture';OUT.mkdir(exist_ok=False)
SCRIPT=VENDOR/'mujoco/python_tools/onnx_mj_chuanlian.py'
FIELDS=('time','root_position','root_quaternion_wxyz','full_qpos','full_qvel','body_position','body_quaternion_wxyz','wheel_bottom_world_z','wheel_normal_contact_N','wheel_partner_geom','raw_action6','executed_action6','actuator_torque6','obs25','obs_history125','jump_mode')
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def compile_headless(case,case_dir):
 tree=ast.parse(SCRIPT.read_bytes());original=copy.deepcopy(tree);original_main=next(x for x in original.body if isinstance(x,ast.FunctionDef) and x.name=='main');main=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='main')
 tree.body=[x for x in tree.body if not (isinstance(x,ast.Import) and any(a.name in ('mujoco.viewer','torch') for a in x.names)) and not (isinstance(x,ast.ImportFrom) and x.module=='pynput')]
 tree.body=[x for x in tree.body if not isinstance(x,ast.If) or not any(isinstance(y,ast.Name) and y.id=='__name__' for y in ast.walk(x.test))]
 globals_node=next(x for x in main.body if isinstance(x,ast.Global));globals_node.names+=['requested_policy_name','requested_policy_return_name','requested_policy_duration_s','cmd_lin_vel_target']
 viewer=next(x for x in main.body if isinstance(x,ast.With) and any(isinstance(y,ast.Attribute) and y.attr=='launch_passive' for y in ast.walk(x)));loop=next(x for x in viewer.body if isinstance(x,ast.While));body=copy.deepcopy(loop.body)
 def unwanted(x):
  return isinstance(x,ast.Expr) and isinstance(x.value,ast.Call) and ((isinstance(x.value.func,ast.Attribute) and isinstance(x.value.func.value,ast.Name) and x.value.func.value.id=='viewer') or (isinstance(x.value.func,ast.Name) and x.value.func.id=='print'))
 body=[x for x in body if not unwanted(x)]
 before=ast.parse("""if not reference_triggered and float(d.time)>=1.5:
 requested_policy_name=JUMP_POLICY_NAME
 requested_policy_return_name=RECOVER_POLICY_NAME
 requested_policy_duration_s=jump_policy_duration_s
 cmd_lin_vel_target=float(REFERENCE_CASE['jump_command_m_s'])
 reference_triggered=True
if reference_triggered and float(d.time)>=1.5+jump_policy_duration_s:
 cmd_lin_vel_target=0.
assert time.monotonic()-reference_wall_start<180,'Bounded original-reference CPU case timeout'
""").body
 after=ast.parse("capture(m,d,base_bid,action_raw,actions,u,obs,history,active_policy_name,REFERENCE_ROWS)").body
 bounded=ast.While(test=ast.parse("float(d.time)<6.0 and i<4000",mode='eval').body,body=before+body+after,orelse=[])
 new=[]
 for node in main.body:
  if node is viewer:
   new+=ast.parse('reference_triggered=False\nreference_wall_start=time.monotonic()').body+[bounded];continue
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='listener' for t in node.targets):continue
  if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and isinstance(node.value.func.value,ast.Name) and node.value.func.value.id=='listener':continue
  if isinstance(node,ast.Try) and any(isinstance(t,ast.Name) and t.id=='listener' for t in ast.walk(node)):continue
  new.append(node)
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='m' for t in node.targets):
   new+=ast.parse("REFERENCE_MODEL_INFO['original_timestep']=float(m.opt.timestep)\nif REFERENCE_CASE['explicit_declared_dt'] is not None: m.opt.timestep=float(REFERENCE_CASE['explicit_declared_dt'])\nREFERENCE_MODEL_INFO['actual_timestep']=float(m.opt.timestep)").body
 main.body=new
 old_nested={x.name:ast.dump(x) for x in original_main.body if isinstance(x,ast.FunctionDef)};new_nested={x.name:ast.dump(x) for x in main.body if isinstance(x,ast.FunctionDef)};assert old_nested==new_nested
 old_funcs={x.name:ast.dump(x) for x in original.body if isinstance(x,ast.FunctionDef) and x.name!='main'};new_funcs={x.name:ast.dump(x) for x in tree.body if isinstance(x,ast.FunctionDef) and x.name!='main'};assert old_funcs==new_funcs
 ast.fix_missing_locations(tree);(case_dir/'HEADLESS_REVIEWED_AST_SOURCE.py').write_text(ast.unparse(tree)+'\n',encoding='utf8');return compile(tree,str(SCRIPT),'exec')
def capture(m,d,base_bid,raw,actions,u,obs,history,policy,rows):
 wheels=[mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,x) for x in ('l_wheel_Link','r_wheel_Link')];assert min(wheels)>=0
 normal=np.zeros(2);partners=np.full(2,-1,dtype=np.int64)
 for contact_id,c in enumerate(d.contact[:d.ncon]):
  pair=(int(c.geom1),int(c.geom2))
  for i,b in enumerate(wheels):
   if b not in (int(m.geom_bodyid[pair[0]]),int(m.geom_bodyid[pair[1]])):continue
   force=np.zeros(6);mujoco.mj_contactForce(m,d,contact_id,force);normal[i]+=max(0.,float(force[0]));partners[i]=pair[1] if int(m.geom_bodyid[pair[0]])==b else pair[0]
 bottoms=[]
 for b in wheels:
  geoms=np.flatnonzero(m.geom_bodyid==b);g=next(int(x) for x in geoms if int(m.geom_type[x])==int(mujoco.mjtGeom.mjGEOM_CYLINDER));rot=d.geom_xmat[g].reshape(3,3);r,h=m.geom_size[g,:2];bottoms.append(d.geom_xpos[g,2]-r*np.linalg.norm(rot[2,:2])-h*abs(rot[2,2]))
 values=(float(d.time),d.xpos[base_bid].copy(),d.xquat[base_bid].copy(),d.qpos.copy(),d.qvel.copy(),d.xpos.copy(),d.xquat.copy(),np.array(bottoms),normal,partners,np.asarray(raw).copy(),np.asarray(actions).copy(),np.asarray(u).copy(),np.asarray(obs).copy(),np.asarray(history).reshape(-1).copy(),policy=='jump')
 assert all(np.isfinite(np.asarray(x)).all() for x in values)
 rows.append(dict(zip(FIELDS,values)))
def main():
 cases=[dict(name='upstream_actual_default_dt_standing_jump',explicit_declared_dt=None,jump_command_m_s=0.),dict(name='declared_5ms_dt_standing_jump',explicit_declared_dt=.005,jump_command_m_s=0.),dict(name='declared_5ms_dt_jump_forward_command',explicit_declared_dt=.005,jump_command_m_s=.8)];summaries=[]
 for case in cases:
  folder=OUT/case['name'];folder.mkdir();rows=[];model_info={};ns=dict(__name__='reviewed_headless_reference_module',__file__=str(SCRIPT),REFERENCE_CASE=case,REFERENCE_ROWS=rows,REFERENCE_MODEL_INFO=model_info,capture=capture,torch=types.SimpleNamespace(cuda=types.SimpleNamespace(is_available=lambda:False),device=lambda s:types.SimpleNamespace(type='cpu')))
  try:
   code=compile_headless(case,folder);exec(code,ns);previous=sys.argv;sys.argv=[str(SCRIPT),'--device','cpu']
   try:ns['main']()
   finally:sys.argv=previous
   status='COMPLETE_BOUNDED_ORIGINAL_ROBOT_CPU_ROLLOUT'
  except BaseException:
   status='ORIGINAL_REFERENCE_CASE_ERROR';put(folder/'ORIGINAL_REFERENCE_ERROR.json',dict(error=traceback.format_exc(),rows=len(rows),case=case,not_MOD4_training_failure=True))
  arrays={key:np.stack([r[key] for r in rows]) for key in FIELDS} if rows else {};artifact=None
  if rows:
   path=folder/'ORIGINAL_ROBOT_REFERENCE_CONTROL_ROWS.npz';np.savez_compressed(path,**arrays);artifact=dict(path=str(path),bytes=path.stat().st_size,SHA=hashlib.sha256(path.read_bytes()).hexdigest())
   airborne=(arrays['wheel_normal_contact_N']<1.).all(-1);jump=arrays['jump_mode'];height=arrays['wheel_bottom_world_z'].min(-1);pre=arrays['time']<1.4;ground=float(np.median(height[pre])) if pre.any() else None
   summary=dict(case=case,status=status,controls=len(rows),model_timestep=model_info,artifact=artifact,jump_mode_controls=int(jump.sum()),both_wheels_contact_absent_jump_controls=int((airborne&jump).sum()),minimum_wheel_bottom_max_world_z_m=float(height.max()),relative_to_initial_supported_bottom_peak_m=float(height.max()-ground) if ground is not None else None,initial_supported_bottom_estimate_world_z_m=ground,post_jump_both_wheel_contact_controls=int(((arrays['wheel_normal_contact_N']>1).all(-1)&(arrays['time']>2.1)).sum()),no_forced_robot_pose_action_or_modified_policy=True,not_our270mm_step_or_frozen_skill_success=True)
  else:summary=dict(case=case,status=status,controls=0,model_timestep=model_info,artifact=None)
  put(folder/'REFERENCE_CASE_SUMMARY_ACTUAL.json',summary);summaries.append(summary)
 put(OUT/'BOUNDED_FUDAN_JUMP_REFERENCE_CASES_CPU_ACTUAL.json',dict(cases=summaries,pinned_source_full_SHA=hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),headless_adaptation_original_observation_history_torque_and_mode_switch_functions_AST_exact=True,original_default_MJCF_dt_and_declared_script_dt_variants_separately_recorded=True,no_original_failure_overwritten_or_chosen_by_filename_success=True,no_MOD4_policy_physics_GPU_or_budget_writer=True,foreign_transitions_are_reference_demonstrations_only_not_our_WM_groundtruth=True))
 print(json.dumps(dict(cases=[dict(name=x['case']['name'],status=x['status'],controls=x['controls']) for x in summaries])))
if __name__=='__main__':main()
