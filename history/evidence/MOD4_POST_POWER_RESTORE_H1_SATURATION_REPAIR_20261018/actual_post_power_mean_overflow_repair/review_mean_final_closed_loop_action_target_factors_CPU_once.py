"""Recorded closed-loop action and guarded-target diagnostics only; no new skill gate."""
from pathlib import Path
import json,time,sys,os,ast,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
B=Path(__file__).resolve().parent;R=B/'reports'
def main():
 label=sys.argv[1];assert label in ('NATIVE120','FULL1500');collection=Path(sys.argv[2]);j=json.loads(collection.read_bytes());assert not j['original_error'] and j['parent_child_launcher_actual_absent']
 raw=next(r for r in j['files'] if r['relative'].endswith('/retention_full_control_substep_actual.npz'));assert raw['twohost_complete_SHA']
 source=B/'frozen_mean_final_linux_v2/payload/frozen_shared/runtime/isaac/mod4/mod4_task.py';tree=ast.parse(source.read_text('utf8'));order=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='LEG_ORDER' for x in n.targets));assert order==['left_crank','left_hip','right_crank','right_hip']
 with np.load(raw['local_path'],allow_pickle=False) as z:
  done=z['terminated']|z['truncated'];S,N=done.shape;first=np.where(done.any(0),done.argmax(0),S);valid=np.arange(S)[:,None]<first[None,:];request=z['H1_public_request']&valid;mu=z['raw_actor_action'];clipped=z['processed_action'];target=z['guarded_leg_targets'];assert np.array_equal(np.clip(mu,-6,6),clipped);rows=[]
  for label2,mask in [('all_valid_first_episode',valid),('actual_public4_valid_first_episode',request),('normal_valid_first_episode',valid&~z['H1_public_request'])]:
   assert mask.any();v=mu[...,0][mask];delta=(target[...,0]-target[...,1])[mask]
   rows.append(dict(label=label2,rows=int(mask.sum()),raw_left_crank_min_median_max=[float(v.min()),float(np.median(v)),float(v.max())],raw_left_crank_within_clip_fraction=float((abs(v)<=6).mean()),raw_left_crank_below_minus6_fraction=float((v < -6).mean()),guarded_target_left_crank_minus_left_hip_min_median_max=[float(delta.min()),float(np.median(delta)),float(delta.max())],guarded_target_is_not_measured_joint_stop_or_torque=True))
 out=dict(epoch=time.time(),case_label=label,actual_original_source_LEG_ORDER=order,raw_actual_index=raw,source_manifest='H1_MEANREPAIR_FINAL_LINUX4090_MANIFEST_V2.json',rows=rows,valid_control_count=int(valid.sum()),source_checkpoint_Adam646100=True,no_GPU_RNG_optimizer_or_source_mutation=True,no_new_threshold_or_gate_no_unique_cause_claim=True,not_same_input_counterfactual_physics=True)
 with (R/('MEAN_REPAIR_FINAL_'+label+'_ACTUAL_CLOSED_LOOP_ACTION_TARGET_FACTORS_CPU_ACTUAL.json')).open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(case=label,rows=rows)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('MEAN_FINAL_ACTION_FACTOR_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_threshold_change=True),f,indent=2)
  raise
