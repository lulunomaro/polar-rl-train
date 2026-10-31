"""One necessary two-checkpoint CPU read/decode, not for stats/Git."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import hashlib,io,json,sys,time,traceback
N=Path(__file__).resolve().parent;R=N/'reports'
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False)
def main():
 task=json.loads((N/'TASK224_FROZEN.json').read_bytes())
 assert task['maximum_model_reads_total']==2 and task['frozen_reference_file_no_writes']
 assert task['models'][0]['SHA']=='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a'and task['models'][1]['SHA']=='e6291fc50e692b9921dfe8ddcbfcc678e9b5916441229c2fd7a4f2c2cc75a538'
 put('ROOT224_NECESSARY_TWO_ACTOR_CPU_PURPOSE_ONCE_CONSUMED.json',dict(epoch=time.time(),Task=task,maximum_model_byte_reads=2,maximum_model_decodes=2,old_trajectory_NPZ_raw_reads=0))
 import torch
 assert not torch.cuda.is_initialized();rng=torch.random.get_rng_state().clone()
 r=task['input_small_JSON'];raw=Path(r['path']).read_bytes();assert len(raw)==r['bytes']and hashlib.sha256(raw).hexdigest()==r['SHA'];actual=json.loads(raw);del raw
 case=actual['original_parent']['result'];assert actual['passed_execution']and case['controls']==32
 obs=torch.tensor([x['policy_observation35']for x in case['rows']],dtype=torch.float32);gpu=torch.tensor([x['raw_mean6']for x in case['rows']],dtype=torch.float32)
 assert obs.shape==(32,35)and torch.isfinite(obs).all();inputs={}
 inputs['actual_JUMP_mode1_height']=obs.clone();z=obs.clone();z[:,28:35]=0;z[:,28]=1;inputs['same_input_mode0']=z
 z=obs.clone();z[:,3]=1.25;inputs['same_input_mode1_height1p25']=z
 z=inputs['same_input_mode0'].clone();z[:,3]=1.25;inputs['same_input_mode0_height1p25']=z
 outputs={};full=[]
 with torch.random.fork_rng(devices=[]):
  for ref in task['models']:
   p=Path(ref['path']);before=p.stat();raw=p.read_bytes();assert len(raw)==ref['bytes']and hashlib.sha256(raw).hexdigest()==ref['SHA']
   ck=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False);del raw
   assert ck['iter']==ref['iteration'];a=ck['actor_state_dict'];weights={k.removeprefix('mlp.'):v for k,v in a.items()if k.startswith('mlp.')}
   net=torch.nn.Sequential(torch.nn.Linear(35,256),torch.nn.ELU(),torch.nn.Linear(256,128),torch.nn.ELU(),torch.nn.Linear(128,64),torch.nn.ELU(),torch.nn.Linear(64,6))
   net.load_state_dict(weights,strict=True);net.eval();rows=[]
   with torch.inference_mode():
    for name,x in inputs.items():
     y=net(x);assert torch.isfinite(y).all();left=y[:,0]
     rows.append(dict(condition=name,left_crank_mean_range=[float(left.min()),float(left.max())],left_crank_abs_gt6_count=int((left.abs()>6).sum()),all6_abs_gt6_counts=(y.abs()>6).sum(0).tolist(),mean6_min=y.min(0).values.tolist(),mean6_max=y.max(0).values.tolist(),current_GPU_same_input_max_abs_difference=float((y-gpu).abs().max())if ref['role']=='new_E0_210_branch'and name=='actual_JUMP_mode1_height'else None))
     full.append(dict(model_role=ref['role'],condition=name,mean6=y.tolist()))
   assert p.stat().st_mtime_ns==before.st_mtime_ns and p.stat().st_size==before.st_size
   assert all(torch.equal(v,net.state_dict()[k])for k,v in weights.items())
   outputs[ref['role']]=dict(path=ref['path'],SHA=ref['SHA'],iteration=ref['iteration'],learned_scalar_STD_parameter6=a['distribution.std_param'].tolist(),conditions=rows,physical_byte_reads=1,decodes=1,original_file_unchanged=True)
 assert torch.equal(rng,torch.random.get_rng_state())and not torch.cuda.is_initialized()
 put('ROOT224_FROZEN_E0_VS_NEW_BRANCH_SAME_INPUT_CPU_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,actual_model_reads=2,actual_model_decodes=2,actual_small_JSON_reads=1,models=outputs,full_numeric_predictions=full,
  global_RNG_unchanged=True,CUDA_initialized=False,physical_rollouts=0,parameter_updates=0,
  interpretation='Same fresh223 states only; counterfactual mode/height predictions are not physical E0 walking or jump evaluations; no population or unique cause claim.',
  no_reward_STD_actionclip_guard_or_learning_change=True))
 print(json.dumps(dict(passed=True,models=outputs)))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT224_ORIGINAL_CPU_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_retry=True));raise
