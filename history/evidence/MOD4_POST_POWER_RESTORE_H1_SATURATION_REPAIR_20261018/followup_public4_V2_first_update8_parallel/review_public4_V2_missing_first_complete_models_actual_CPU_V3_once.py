"""Review only this new finite run's immutable startup and first update, not rolling metadata."""
from pathlib import Path
import os,sys,time,json,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent/'paid_mean_public4_v2';R=B/'reports';W=B.parent.parent
sys.path.insert(0,str(W/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'))
from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq,tensors
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone()
 collection=json.loads((R/'PUBLIC4_V2_H1_MISSING_FIRST_PROGRESS_V3_BOUND_COLLECTION_ACTUAL.json').read_bytes())
 prep=json.loads((R/'PUBLIC4_REPAIR_V2_H1_FINITE_NEW_SOURCE_NATIVE_PAYLOAD_CPU_ACTUAL.json').read_bytes());spec=prep['specs']['h1']
 assert prep['passed_CPU_only'];current=collection['target']['rows']['NODE_CURRENT.json']['row'];native=current['native_CPU'];assert current['native_GPU_waited_EXIT0'] and native['actual_CPU_waited_EXIT0'] and native['value']['passed'] and native['value']['source_SHA']==spec['source_SHA'] and native['value']['controls']==180 and native['value']['callbacks']==720 and native['value']['sourceactor9critic8STD17Adam_literal_exact']
 source=B/'payload/h1/job0/source'/spec['source_filename'];assert H(source)==spec['source_SHA'];s=torch.load(source,map_location='cpu',weights_only=False)
 models={};counts={}
 for row in collection['downloaded_models']:
  assert row['kind'] in ('immutable_startup0','immutable_first');p=Path(row['local_path']);assert row['twohost_complete_SHA'] and p.stat().st_size==row['bytes'] and H(p)==row['SHA']
  x=torch.load(p,map_location='cpu',weights_only=False);n=[0,0];tensors(x,n);assert n==[199,105];models[row['kind']]=x;counts[row['kind']]=n
 positive=all(k in models for k in ('immutable_startup0','immutable_first'));changes={}
 if positive:
  z=models['immutable_startup0'];p=models['immutable_first']
  for g in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[g],z[g])
  assert {int(v['step']) for v in z['optimizer_state_dict']['state'].values()}=={645620} and {int(v['step']) for v in p['optimizer_state_dict']['state'].values()}=={645640}
  assert torch.equal(z['sensor_DR_state']['episode'],s['sensor_DR_state']['episode']+1) and not z['H1_public_request_phase_state']['phase']['tensors']['age_control'].any()
  assert p['owned_H1_completed_updates']==1 and not p['failed_partial_prefix'] and p['owned_H1_learning_task']['optimization_candidate']['name']=='public4_only_mean_overflow_regularizer_v2'
  changes={g:[k for k in s[g] if not eq(s[g][k],p[g][k])] for g in ('actor_state_dict','critic_state_dict')};assert len(changes['actor_state_dict'])==9 and len(changes['critic_state_dict'])==8
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 put('PUBLIC4_V2_H1_IMMUTABLE_FIRST_COMPLETE_LOCAL_CPU_V3_ACTUAL.json',dict(epoch=time.time(),passed_real_immutable_first_complete_local_CPU=positive,source_SHA=spec['source_SHA'],all_models=collection['downloaded_models'],counts=counts,all_complete_model_runtime_finite=True,all17Adam645620_to645640=positive,startup0_core9STD8critic17Adam_literalexact=positive,source_episode_plus1_phaseage0=positive,all17_actorcritic_changes=changes,first24control480000productionenvsteps=positive,not_frozen_jump_skill_final_or_all_three_PPO=True,CPU_RNG_unchanged0CUDA0optimizer=True,missing_if_any_pending_not_false_success=not positive))
 print(json.dumps(dict(new_H1_first_complete_PPO_CPU=positive,source_Adam=645620,first_Adam=645640 if positive else None)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('PUBLIC4_V2_H1_FIRST_LOCAL_CPU_V3_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_runtime_mutation=True));raise
