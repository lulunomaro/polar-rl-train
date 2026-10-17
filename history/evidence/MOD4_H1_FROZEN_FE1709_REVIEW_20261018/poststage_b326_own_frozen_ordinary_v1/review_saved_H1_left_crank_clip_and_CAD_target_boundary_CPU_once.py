"""Read saved control targets and actual sealed source. No actuator or policy mutation."""
from pathlib import Path
import json,time,hashlib,ast,os,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
B=Path(__file__).resolve().parent;R=B/'reports';Q=B/'h1_b326_linux4090_v7/payload';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=Q/'frozen_shared/runtime/isaac/mod4/mod4_task.py';tree=ast.parse(source.read_text('utf8'));order=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='LEG_ORDER' for t in n.targets));assert order==['left_crank','left_hip','right_crank','right_hip'];cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='DelayedJointPositionAction');method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='process_actions');guard_ast=ast.dump(method,include_attributes=False)
 contract=Q/'frozen_shared/runtime/assets/import_contract.json';c=json.loads(contract.read_bytes());m=json.loads((Q/'H1_B326_LINUX4090_MANIFEST_V7.json').read_bytes());assert 'RM_DIFF_MIN' not in m['env'] and 'RM_DIFF_MAX' not in m['env'];lower=float(c['training_window']['input_difference_min_rad']);assert lower==-1.0843;rows=[]
 for label,name in [('FE1709','LINUX_GPU1_V5_FULL1500_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json'),('D723','LINUX_GPU1_D723_FULL1500_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json'),('B326','LINUX_GPU1_B326_FULL1500_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json')]:
  path=R/name
  if not path.exists():continue
  j=json.loads(path.read_bytes());r=next(x for x in j['files'] if x['relative'].endswith('/retention_full_control_substep_actual.npz'));assert r['twohost_complete_SHA']
  with np.load(r['local_path'],allow_pickle=False) as z:
   raw=z['raw_actor_action'];clipped=z['processed_action'];target=z['guarded_leg_targets'];request=z['H1_public_request'];done=z['terminated']|z['truncated'];S,N=done.shape;first=np.where(done.any(0),done.argmax(0),S);valid=np.arange(S)[:,None]<first[None,:];pick=request&valid;assert target.shape==(S,N,4) and pick.any();left=target[...,0]-target[...,1];right=target[...,2]-target[...,3];left_error=abs(left-lower)
   rows.append(dict(source=label,raw_actual_path=r['path'],raw_SHA=r['SHA'],original_first_valid_request_control_rows=int(pick.sum()),action0_source_name='left_crank',raw_action0_request_min_median_max=[float(raw[...,0][pick].min()),float(np.median(raw[...,0][pick])),float(raw[...,0][pick].max())],whole6_clipped_action0_request_values=np.unique(clipped[...,0][pick]).tolist(),saved_guarded_left_crank_minus_left_hip_request_min_median_max=[float(left[pick].min()),float(np.median(left[pick])),float(left[pick].max())],left_guarded_target_lower_bound_maxabs=float(left_error[pick].max()),left_guarded_target_lower_bound_fraction_within1e6=float((left_error[pick]<=1e-6).mean()),right_guarded_crank_minus_hip_request_min_median_max=[float(right[pick].min()),float(np.median(right[pick])),float(right[pick].max())],observed_endcontrol_guarded_targets_not_all_physical_joint_positions_or_contacts=True))
 assert len(rows)==3
 out=dict(epoch=time.time(),passed_saved_control_target_source_binding_CPU=True,sealed_actual_source=dict(path=str(source),SHA=H(source),leg_order=order,guard_process_actions_AST_SHA=hashlib.sha256(guard_ast.encode()).hexdigest()),actual_contract_path=str(contract),actual_contract_SHA=H(contract),original_declared_lower_difference_rad=lower,source_guard_moves_crank_relative_to_hip_not_independent_fixed_position=True,source_rows=rows,all_rows_use_first_failure_excluded_actual_public4_window=True,not_unique_cause_or_statistical_regression_proof=True,stored_STD_parameter_or_action0_saturation_alone_not_cause_proof=True,source_is_endcontrol_target_not_measured_joint_at_CAD_physical_stop=True,no_RNG_GPU_optimizer_reward_or_action_contract_change=True,no_old_remote_raw_or_models_rehashed_or_downloaded=True)
 with (R/'H1_THREE_CLOSED_SOURCES_ACTUAL_LEFT_CRANK_CLIP_AND_GUARDED_TARGET_LOWER_BOUND_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(target_audit_CPU=True,rows=[dict(source=x['source'],raw0=x['raw_action0_request_min_median_max'],clipped0=x['whole6_clipped_action0_request_values'],lower_bound_fraction=x['left_guarded_target_lower_bound_fraction_within1e6']) for x in rows])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_GUARDED_TARGET_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_source_change=True),f,indent=2)
  raise
