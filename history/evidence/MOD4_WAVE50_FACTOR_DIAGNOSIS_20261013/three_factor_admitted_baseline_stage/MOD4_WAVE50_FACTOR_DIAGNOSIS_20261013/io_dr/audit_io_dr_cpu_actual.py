"""Read immutable local/source code and existing153 raw; no GPU/SDK/PPO/Git writes."""
from pathlib import Path
import ast, hashlib, json, time, traceback
import numpy as np

D=Path(__file__).resolve().parent
W=D.parents[1]
L=W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013'
R=L/'runtime/isaac/mod4'
RUN=W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/shutdown_backup_1791808183793797400/training/learning_logs/2026-10-12_19-47-02_e1_WAVE50_episode_lifetime_observation_1791805426881441339'
S=RUN/'e1_source_snapshot'
E=W/'MOD4_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012/reports'
C=E/'cases/clk2500-closure-episode-d3-153-e1-wave50-route-lifecycle-repair-terrain-flat'

def H(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def info(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
def J(p):return json.loads(p.read_bytes())
def symbol(p,name):
 tree=ast.parse(p.read_text(encoding='utf-8-sig'))
 nodes=[n for n in ast.walk(tree) if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name]
 assert len(nodes)==1,(str(p),name,len(nodes))
 n=nodes[0];return dict(first_line=n.lineno,last_line=n.end_lineno,AST=ast.dump(n,include_attributes=False))
def flat80(x,p=''):
 if isinstance(x,dict):
  for k,v in x.items():yield from flat80(v,p+'.'+k)
 else:
  a=np.asarray(x)
  if a.dtype.kind in 'fiu' and a.ndim and a.shape[0]==80 and 'episode' not in p:yield p,a
def stats(x):
 return dict(mean=float(np.mean(x)),std=float(np.std(x)),min=float(np.min(x)),max=float(np.max(x)))
def correlation(x,y):
 return None if np.std(x)==0 or np.std(y)==0 else float(np.corrcoef(x,y)[0,1])

def main():
 D.mkdir(parents=True,exist_ok=True)
 probe=J(C/'probe.json');full=J(E/'RESOURCE449_CANDIDATE_ACTUAL_REVIEW_1791801263865498100.json')
 assert full['review_complete'] is True
 assert H(C/'route_raw.npz')==probe['full_route_raw']['sha256']
 comparisons=[]
 names=['PolicyCfg','CriticCfg','mode_onehot','Mod4DCMotor','DelayedJointPositionAction','DelayedJointVelocityAction','ActionsCfg']
 for name in names:
  a=symbol(R/'mod4_task.py',name);b=symbol(S/'isaac/mod4/mod4_task.py',name)
  comparisons.append(dict(symbol=name,local_lines=[a['first_line'],a['last_line']],source_lines=[b['first_line'],b['last_line']],AST_exact=a['AST']==b['AST']))
 assert all(x['AST_exact'] for x in comparisons),'Unexpected obs/action implementation mutation'
 pairs=['sensor_mild_math.py','sensor_a0_runtime.py','feedback_delay_mild.py','feedback_delay_runtime.py','action_delay_physics_queue.py','chassis_com_component.py','chassis_com_pose_roundtrip_sdk_adapter.py','mild_dr.py']
 files=[]
 for name in pairs:
  a=R/name;b=S/'isaac/mod4'/name
  if a.exists() and b.exists():files.append(dict(name=name,local=info(a),source=info(b),byte_exact=H(a)==H(b)))
 paths=[R/'mod4_task.py',L/'local_physx_api.py',L/'local_training_runtime.py',R/'sensor_a0_runtime.py',R/'sensor_mild_math.py',R/'feedback_delay_runtime.py',R/'chassis_com_pose_roundtrip_sdk_adapter.py',R/'e1_full_pose_reset.py',C/'probe.json',C/'route_raw.npz',E/'RESOURCE449_CANDIDATE_ACTUAL_REVIEW_1791801263865498100.json']
 with np.load(C/'route_raw.npz') as raw:
  root=raw['root'];before=raw['before_root'];targets=raw['targets_m_s'];groups=raw['group_ids'];episode=raw['episode'];term=raw['terminated'];trunc=raw['truncated']
  assert root.shape==before.shape==(1500,80,13)
  assert bool(np.isfinite(root).all()) and bool(np.isfinite(before).all())
  dx=root[:,:,:2]-before[:,:,:2]
  world_signed_speed=dx[:,:,0].sum(0)*np.sign(targets)/15.
  q=before[:,:,3:7]
  # This existing153 raw is original modular backend, explicitly xyzw.
  yaw=np.arctan2(2*(q[:,:,3]*q[:,:,2]+q[:,:,0]*q[:,:,1]),1-2*(q[:,:,1]**2+q[:,:,2]**2))
  body_signed_speed=((dx[:,:,0]*np.cos(yaw)+dx[:,:,1]*np.sin(yaw)).sum(0)*np.sign(targets)/15.)
  maxyaw=np.max(np.abs(np.unwrap(yaw,axis=0)-yaw[0]),axis=0)
  reset_count=(term|trunc).sum(0)
  outcome=np.zeros(80,dtype=bool)
  for row in full['terrain']['full_route_rows']:
   outcome[row['env']]=bool(row['complete_episodes'])
  forward=np.asarray(probe['groups'][0]['env_ids']);reverse=np.asarray(probe['groups'][1]['env_ids'])
  assert np.all(targets[forward]==np.float32(.3)) and np.all(targets[reverse]==np.float32(-.3))
  perenv=[dict(env=int(i),direction='forward' if i in forward else 'reverse' if i in reverse else 'stand',complete=bool(outcome[i]),resets=int(reset_count[i]),world_X_signed_speed=float(world_signed_speed[i]),BODY_signed_speed=float(body_signed_speed[i]),max_abs_departure_from_birth_yaw_rad=float(maxyaw[i])) for i in range(80)]
  features={}
  for name,arr in flat80(probe['initial']['assignments'],'initial.assignments'):
   a=arr.reshape(80,-1).astype(float)
   features[name+'.mean']=a.mean(1)
   if a.shape[1]==2:features[name+'.left_minus_right']=a[:,0]-a[:,1]
   elif a.shape[1] in (3,4):
    for column in range(a.shape[1]):features[name+'.column'+str(column)]=a[:,column]
  receipts=probe['sensor_manager']['actual_feedback_sample_apply']
  for name,row in receipts.items():
   features['final_receipt.feedback_delay.'+name]=np.asarray(row['requested_delay_us'],dtype=float)
  rows=[]
  for name,a in features.items():
   row=dict(feature=name,forward=stats(a[forward]),reverse=stats(a[reverse]),forward_complete=stats(a[forward][outcome[forward]]) if outcome[forward].any() else None,forward_failed=stats(a[forward][~outcome[forward]]) if (~outcome[forward]).any() else None,within_forward_completion_correlation=correlation(a[forward],outcome[forward].astype(float)),within_forward_world_speed_correlation=correlation(a[forward],world_signed_speed[forward]),within_reverse_completion_correlation=correlation(a[reverse],outcome[reverse].astype(float)),paired_geometry_index_forward_reverse_parameter_maxabs=float(np.abs(a[forward]-a[reverse]).max()),observational_not_causal=True)
   if 'final_receipt' in name:row['initial_assignment_not_claimed_from_final_postreset_receipt']=True
   rows.append(row)
  summary={name:dict(n=len(ids),completed=int(outcome[ids].sum()),world_X_signed_speed=stats(world_signed_speed[ids]),BODY_signed_speed=stats(body_signed_speed[ids]),heading_departure_gt45_count=int((maxyaw[ids]>np.pi/4).sum()),completed_heading_departure_gt45=int((outcome[ids]&(maxyaw[ids]>np.pi/4)).sum()),failed_heading_departure_gt45=int(((~outcome[ids])&(maxyaw[ids]>np.pi/4)).sum())) for name,ids in [('forward',forward),('reverse',reverse)]}
 report=dict(schema=1,id='io_dr_cpu_audit_existing153_20261013',epoch=time.time(),no_GPU_SDK_PPO_or_production_edit=True,inputs=[info(p) for p in paths],obs_action_symbol_comparisons=comparisons,unchanged_module_byteSHA_comparisons=files,
 actor_contract=dict(dim35=[['commands',3],['height_command',1],['base_ang_vel',3],['projected_gravity',3],['leg_pos',4],['wheel_pos_slots_fixed_zero',2],['leg_vel',4],['wheel_vel',2],['last_action',6],['mode_onehot',7]],dimension_sum=35,absolute_yaw_field=False,birth_heading_field=False,explicit_integrated_yaw_field=False,heightscan_actor_field=False,current_runner_actor_groups=['policy'],runner_feedforward_MLP=True,explicit_history_encoder_or_RNN=False,last_action_can_carry_indirect_short_term_signal=True,instantaneous_ang_velocity_is_present=True,partial_observability_not_declared_as_sole_cause=True,critic38_adds_BODY_linear_velocity_only=True),
 frame_audit=dict(local_bridge_get_coms_native_xyzw_to_wxyz=True,local_bridge_set_coms_wxyz_to_native_xyzw=True,local_get_link_transforms_native_xyzw_to_wxyz=True,local_SciPy_reset_xyzw_to_wxyz=True,original_evaluation153_root_raw_xyzw=True,COM_receipt_literal_xyzw_is_historical_metadata_under_local_wxyz_bridge_not_measured_rotation_corruption=True,no_confirmed_action_order_or_left_right_motor_sign_mutation=True,odd_motor_envelope_source_AST_exact=True),
 existing153_summary=summary,perenv=perenv,DR_assignment_features=rows,
 missing_perenv_raw_D0_fields=['mass_inertia_factor','motor_strength','wheel_friction','nominal_physical_mask','initial_sensor_bias_vector'],missing_fields_not_reconstructed_from_seed_or_minmax=True,
 conclusions=['Current A0 actor receives no route/birthheading/absoluteyaw/heightscan input; current angle-rate and last requested action remain deployable signals.','Existing153 forward/reverse are independent per-env D4-D7 assignments, not a paired one-factor experiment; subgroup associations cannot prove DR explains asymmetry.','No deterministic obs/action sign mutation or quaternion bridge error was found in reviewed code. Native SDK/backend equivalence is not proven by AST or CPU math.'],
 proposed_GPU_factors=[dict(id='D3_feedback_delay_current_sample',baseline='unchanged noisy feedback through original 0/10ms delay',treatment='call original noisy feedback+delay apply to retain all RNG/queue side effects, return current noisy value instead of delayed cached output',one_factor='feedback latency only; no actor-dimension change/no critic truth',same_initial30q_parameters_geometry_commands_noisestream_start=True,saved_factor_override_receipt_required=True,production_change=False,paired_outcomes=['complete same physical route under original1N/200mm/15s','first effective failure prefix','world X/BODY signed speed','yaw drift','ordinary/reset coverage'])],
 CPU_reader_errors_preserved=[dict(id='exploratory_reader_physical_action_rows_wrong_list_index',error='KeyError: 0',context='physical_action_audit.rows is dict legs/wheels, not list',prewrite_and_no_GPU=True),dict(id='exploratory_missing_file_path_queries',paths=['runtime/isaac/mod4/mod4_task_candidate.py','sensor_mild_runtime.py','history_actor_label_ppo.py','history_latent_component.py','chassis_com_math.py','chassis_com_sdk_adapter.py','full_pose_reset.py','mod4_actuators.py','actuators.py'],classification='read-only missing assumed paths; actual files subsequently selected from rg --files',no_production_error=True)])
 out=D/'IO_DR_CPU_ACTUAL_REVIEW.json';assert not out.exists();out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(dict(report=str(out),summary=summary,top_forward_DR_completion_associations=sorted([dict(feature=r['feature'],correlation=r['within_forward_completion_correlation']) for r in rows if r['within_forward_completion_correlation'] is not None],key=lambda r:abs(r['correlation']),reverse=True)[:8],AST_exact=all(x['AST_exact'] for x in comparisons)),ensure_ascii=False,indent=2))

if __name__=='__main__':
 try:main()
 except BaseException:
  D.mkdir(parents=True,exist_ok=True);p=D/('CPU_AUDIT_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),original_source=info(Path(__file__)),preGPU=True),indent=2),encoding='utf-8');raise
