"""Whole immutable update8 CPU audit; not a final, skill pass or unique cause proof."""
from pathlib import Path
import os,sys,time,json,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;N=B/'paid_mean_public4_v2';R=N/'reports';sys.path.insert(0,str(B.parent/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'));from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq,tensors
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();proof=json.loads((R/'PUBLIC4_V2_H1_IMMUTABLE_FIRST_COMPLETE_LOCAL_CPU_V3_ACTUAL.json').read_bytes());assert proof['passed_real_immutable_first_complete_local_CPU'];collection=json.loads((R/'PUBLIC4_V2_H1_IMMUTABLE_UPDATE8_BOUND_COLLECTION_ACTUAL.json').read_bytes());rows=collection['downloaded_models'];assert len(rows)==1 and rows[0]['kind']=='immutable_update8';row=rows[0];p=Path(row['local_path']);assert row['twohost_complete_SHA'] and p.stat().st_size==row['bytes'] and H(p)==row['SHA'];ck=torch.load(p,map_location='cpu',weights_only=False);counts=[0,0];tensors(ck,counts);assert counts==[199,105] and ck['owned_H1_phase']=='production' and ck['owned_H1_completed_updates']==8 and not ck['failed_partial_prefix']
 source=N/'payload/h1/job0/source/H1_final10_protected.pt';assert H(source)==proof['source_SHA']=='b32656cf3bfec37cef4ccfcbe06b6ce421054194f8ad627425e367d67240ccce';before=torch.load(source,map_location='cpu',weights_only=False);assert {int(x['step']) for x in before['optimizer_state_dict']['state'].values()}=={645620} and {int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}=={645780};task=ck['owned_H1_learning_task'];assert task['optimization_candidate']['name']=='public4_only_mean_overflow_regularizer_v2' and task['optimization_candidate']['coefficient']==.001
 changes={g:[k for k in before[g] if not eq(before[g][k],ck[g][k])] for g in ('actor_state_dict','critic_state_dict')};assert len(changes['actor_state_dict'])==9 and len(changes['critic_state_dict'])==8;w=collection['actual_public4_auxiliary_runtime_witnesses'];assert all(x['runtime']['completed']<=8 and x['runtime']['last_batch']['actual_public4_rows']>0 for x in w);assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),passed_whole_immutable_update8_model_local_CPU=True,complete_model=row,whole_tensor_counts=counts,all_model_runtime_finite=True,owned_updates=8,all17Adam_before645620_after645780=True,all17actorcritic_changes=changes,actual_published_public4_auxiliary_witnesses=w,actual_auxiliary_positive_witness_observed=any(x['runtime']['last_batch']['loss']>0 for x in w),same_values_do_not_replace_source_namespace_manifest_candidate_SHA=True,not_cohort_FINAL_or_exit_cost_or_frozen_skill_PASS=True,first_startup_sourceexact_proof=str(R/'PUBLIC4_V2_H1_IMMUTABLE_FIRST_COMPLETE_LOCAL_CPU_V3_ACTUAL.json'),CPU_RNG_unchanged0CUDA0optimizer=True)
 with (R/'PUBLIC4_V2_IMMUTABLE_UPDATE8_COMPLETE_LOCAL_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(update8_whole_CPU=True,SHA=row['SHA'],Adam=645780,actual_aux_witnesses=len(w))),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('PUBLIC4_V2_UPDATE8_LOCAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_model_mutation=True),f,indent=2)
  raise
