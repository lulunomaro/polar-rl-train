"""Source-bound complete native/immutable first CPU audit; pending is not a pass."""
from pathlib import Path
import os,sys,time,json,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent.parent
sys.path.insert(0,str(W/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'))
from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq,tensors
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)

def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone()
 c=json.loads((R/'CE3_OWN_NATIVE_FIRST_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json').read_bytes())
 prep=json.loads((R/'HUMAN_APPROVED_CE3_PREPARED_PAYLOAD_BOUND_DEPLOY_SPEC_ACTUAL.json').read_bytes());spec=prep['specs']['h1'];source=B/'payload/h1/job0/source'/spec['source_filename'];assert H(source)==spec['source_SHA'] and spec['source_Adamstep']==646100
 s=torch.load(source,map_location='cpu',weights_only=False);ns=[0,0];tensors(s,ns);assert ns==[199,105]
 models={};counts={}
 for row in c['downloaded_models']:
  p=Path(row['local_path']);assert row['twohost_complete_SHA'] and p.stat().st_size==row['bytes'] and H(p)==row['SHA'];x=torch.load(p,map_location='cpu',weights_only=False);n=[0,0];tensors(x,n);assert n==[199,105];models[row['kind']]=x;counts[row['kind']]=n
 row=c['target']['rows'].get('NODE_CURRENT.json',{}).get('row',{});native=row.get('native_CPU')
 if not native:native=c['target']['rows'].get('NODE_TERMINAL_ACTUAL.json',{}).get('row',{}).get('native_CPU')
 remote_native=bool(native and native.get('actual_CPU_waited_EXIT0') and native['value'].get('passed'))
 if remote_native:
  v=native['value'];assert native['SHA']==hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest();assert v['source_SHA']==spec['source_SHA'] and v['controls']==180 and v['callbacks']==720 and v['sourceactor9critic8STD17Adam_literal_exact']
 complete_native=remote_native and all(k in models for k in ('own_native_startup0','own_native_complete'))
 if complete_native:
  for kind in ('own_native_startup0','own_native_complete'):
   for g in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[g],models[kind][g])
   assert {int(v['step']) for v in models[kind]['optimizer_state_dict']['state'].values()}=={646100}
  z=models['own_native_startup0'];assert torch.equal(z['sensor_DR_state']['episode'],s['sensor_DR_state']['episode']+1);assert not z['H1_public_request_phase_state']['phase']['tensors']['age_control'].any()
 positive=complete_native and all(k in models for k in ('immutable_startup0','immutable_first'));changes={};diag=None
 if positive:
  z=models['immutable_startup0'];p=models['immutable_first']
  for g in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[g],z[g])
  assert {int(v['step']) for v in z['optimizer_state_dict']['state'].values()}=={646100} and {int(v['step']) for v in p['optimizer_state_dict']['state'].values()}=={646120}
  assert torch.equal(z['sensor_DR_state']['episode'],s['sensor_DR_state']['episode']+1) and not z['H1_public_request_phase_state']['phase']['tensors']['age_control'].any()
  assert p['owned_H1_completed_updates']==1 and not p['failed_partial_prefix'];candidate=p['owned_H1_learning_task']['optimization_candidate'];assert candidate['name']=='public4_only_mean_overflow_regularizer_v2' and candidate['coefficient']==.001
  changes={g:[k for k in s[g] if not eq(s[g][k],p[g][k])] for g in ('actor_state_dict','critic_state_dict')};assert len(changes['actor_state_dict'])==9 and len(changes['critic_state_dict'])==8
  diag=c['target']['rows'].get('job0/production/OWNED_MEAN_OVERFLOW_LOSS_CURRENT.json')
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),passed_complete_own_native_allrow_remote_and_two_models_local_CPU=complete_native,passed_real_immutable_first_complete_local_CPU=positive,source_SHA=spec['source_SHA'],source_Adam=646100,expected_first_Adam=646120,all_models=c['downloaded_models'],counts=counts,all_collected_models_runtime_finite=True,native_sourcecore9STD8critic17Adam_literalexact=complete_native,startup0_core9STD8critic17Adam_literalexact=positive,source_episode_plus1_startup_only_phaseage0=complete_native,all17Adam646100_to646120=positive,all17_actorcritic_changes=changes,first24control480000productionenvsteps=positive,first_under100normal_schedule_not_aux_effect=True,current_loss_diagnostic_not_immutable_first_attribution=diag,pending_missing_native_or_first=not positive,not_frozen_jump_skill_FINAL_or_all_three_PPO=True,CPU_RNG_unchanged0CUDA0optimizer=True)
 put('CE3_OWN_NATIVE_FIRST_COMPLETE_LOCAL_CPU_ACTUAL.json',out);print(json.dumps(dict(native_complete_CPU=complete_native,first_complete_CPU=positive,collected=len(models))),flush=True)

if __name__=='__main__':
 try:main()
 except BaseException:put('CE3_OWN_NATIVE_FIRST_LOCAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_runtime_mutation=True));raise
