from pathlib import Path
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
import hashlib,io,json,time,traceback
from types import SimpleNamespace
import numpy as np
import torch
N=Path(__file__).resolve().parent;R=N/'reports'
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 p=json.loads((R/'FROZEN244_USER_NUMERICAL_CLOSURE_PURPOSE_BEFORE_POSE_IO.json').read_bytes());r=p['pose']
 put('ROOT244_USER_CLOSURE_POSE_PASS_ONCE_CONSUMED.json',dict(epoch=time.time(),kind=p['kind'],pose=r,member_reads_each=1,model_SDK_remote_reads=0,CPU_float32_only=True))
 with Path(r['path']).open('rb')as f:raw=f.read()
 assert len(raw)==r['bytes']and hashlib.sha256(raw).hexdigest()==r['SHA']
 with np.load(io.BytesIO(raw),allow_pickle=False)as z:arrays={k:z[k].copy()for k in p['selected_npz_members']}
 del raw
 assert arrays['body_position_w'].shape==(17,31,3)and arrays['body_quat_xyzw'].shape==(17,31,4)
 assert all(a.dtype==np.float32 and np.isfinite(a).all()for a in arrays.values());assert not torch.cuda.is_initialized()
 rng=torch.get_rng_state().clone()
 def quat_apply(q,v):
  t=2.0*torch.cross(q[...,:3],v,dim=-1)
  return v+q[...,3:4]*t+torch.cross(q[...,:3],t,dim=-1)
 # Two known rotations verify only the CPU xyzw binding, not an SDK/physics fixture.
 assert torch.equal(quat_apply(torch.tensor([[0.,0.,0.,1.]]),torch.tensor([[1.,2.,3.]])),torch.tensor([[1.,2.,3.]]))
 robot=SimpleNamespace(body_names=p['body_names'],data=SimpleNamespace(body_pos_w=torch.from_numpy(arrays['body_position_w']),body_quat_w=torch.from_numpy(arrays['body_quat_xyzw'])))
 env=SimpleNamespace(scene={'robot':robot},device='cpu',num_envs=17,episode_length_buf=torch.arange(1,18))
 os.environ['RM_SPAWN_GRACE_STEPS']=str(p['actual_original_spawn_grace_steps'])
 scope=dict(torch=torch,os=os,CONTRACT={'closures':p['closure_contract']},quat_apply=quat_apply)
 for name,source in p['original_function_segments'].items():exec(compile(source,p['source_identity']['payload/job0/runtime/isaac/mod4/mod4_task.py']['path']+'::'+name,'exec'),scope)
 values=scope['closure_errors'](env);broken=scope['closure_broken'](env,threshold=p['original_threshold_m']);worst=env._mod4_closure_now;terminal={k:float(v[-1])*1000 for k,v in values.items()};winner=max(terminal,key=terminal.get)
 assert bool(broken[-1])and torch.isfinite(worst).all()and torch.equal(rng,torch.get_rng_state())and not torch.cuda.is_initialized()
 row=dict(passed=True,epoch=time.time(),human_question=p['human_exact'],source_case='Actual242 literal_jump /trained240 iter2135',original_model_SHA='0f5de75a488b79bfe9513b2cd01664d8bf98450800b785b8e787301276552a07',terminal_control=17,terminal_seconds=.34,original_closure_threshold_mm=2.,terminal_errors_mm=terminal,worst_loop=winner,terminal_worst_error_mm=terminal[winner],terminal_excess_over_threshold_mm=terminal[winner]-2.,previous_control=16,previous_worst_error_mm=float(worst[-2])*1000,original_function_CPU_reconstructed_first_active_broken_control=next((i+1 for i,b in enumerate(broken.tolist())if b),None),saved_17_endpoint_worst_error_mm=[float(v)*1000 for v in worst],original_anchors=p['closure_contract'][winner],local_pose_byte_opens=1,integrity_and_decode_from_same_bytes=True,selected_npz_members_each_once=p['selected_npz_members'],model_reads=0,SDK_or_neural_GPU_or_remote=0,CUDA_initialized=False,RNG_unchanged=True,numerical_scope=p['CPU_rotation_binding'],not_new_physics_or_original_runtime_GPU_scalar=True)
 put('ROOT244_ACTUAL_SAVED_TERMINAL_CLOSURE_EXCESS_CPU_RETURNED.json',row)
 print(json.dumps({k:row[k]for k in('passed','worst_loop','terminal_worst_error_mm','terminal_excess_over_threshold_mm','previous_worst_error_mm','original_function_CPU_reconstructed_first_active_broken_control','terminal_errors_mm')}))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT244_ORIGINAL_CPU_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_retry=True));raise
