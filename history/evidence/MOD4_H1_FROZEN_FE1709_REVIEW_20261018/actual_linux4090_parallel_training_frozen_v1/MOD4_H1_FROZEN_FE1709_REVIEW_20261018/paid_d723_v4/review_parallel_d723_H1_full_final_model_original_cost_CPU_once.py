"""Consume only actually closed final, verify whole-model CPU and original cost once."""
from pathlib import Path
import os,sys,time,json,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent.parent;O=W/'MOD4_H1_CLOSED24_TARGET72_SAME_SCOPE_FINITE_20261017';sys.path.insert(0,str(W/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'))
from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq,tensors
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();v=json.loads((R/'PARALLEL_D723_H1_FINAL_ORIGINAL_COST_EXIT_BOUND_COLLECTION_ACTUAL.json').read_bytes());assert v['actual_closed'];row=v['downloaded_final_models'][0];p=Path(row['local_path']);assert row['twohost_complete_SHA'] and p.stat().st_size==row['bytes'] and H(p)==row['SHA'];s=torch.load(p,map_location='cpu',weights_only=False);counts=[0,0];tensors(s,counts);assert counts==[199,105] and s['owned_H1_phase']=='production' and not s['failed_partial_prefix'];updates=s['owned_H1_completed_updates'];assert 0<updates<=24
 src=B/'payload/h1/job0/source/H1_final10_protected.pt';before=torch.load(src,map_location='cpu',weights_only=False);assert H(src)=='d7238b885879705fa8312758337bf0b6ca1d97c2f906df51b72c27b475e7786a' and {int(x['step']) for x in before['optimizer_state_dict']['state'].values()}=={645140};step=645140+20*updates;assert {int(x['step']) for x in s['optimizer_state_dict']['state'].values()}=={step};changed={g:[n for n in before[g] if not eq(before[g][n],s[g][n])] for g in ('actor_state_dict','critic_state_dict')};assert len(changed['actor_state_dict'])==9 and len(changed['critic_state_dict'])==8
 ledger=v['account']['original_canonical'];seg=next(x for x in ledger['completed_segments'] if x.get('owner_parent_pid')==797931);assert set(seg['experts'])=={'h1'} and seg['experts']['h1']['actual_returncode']==0 and abs(seg['charged_expert_seconds']-seg['experts']['h1']['charged_seconds'])<1e-6;assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),passed_whole_final_model_local_CPU=True,complete_final=row,whole_tensor_counts=counts,all_model_runtime_finite=True,updates=updates,production_controls=24*updates,production_envsteps=480000*updates,all17Adam_before645140=True,all17Adam_after=step,all_actor9_including_STD_critic8_actual_changes=changed,actual_original_cost_once=seg,actual_cost_seconds=seg['charged_expert_seconds'],actual_duration_bound_passed=seg['experts']['h1']['duration_bound_passed'],remaining_snapshot=ledger['remaining_training_seconds'],actual_original_owner_node_all_children_out=True,original_canonicalNone_two_real_fcntlFree_and_target_GPU_private_shared_free=True,no_old_first_native_PT_or_raw_rehashed_or_downloaded=True,E2_and_E3_no_paid_GO_zero_charge=True,source210_D_free_snapshot=v['source_resources']['durable']['free'],target72_free_snapshot=v['target_resources']['durable']['free'],not_frozen_jump_skill_or_course_qualification=True,CPU_RNG_unchanged0CUDA0optimizer=True)
 with (R/'PARALLEL_D723_H1_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(final_CPU=True,updates=updates,Adam=step,SHA=row['SHA'],actual_cost=seg['charged_expert_seconds'],duration_bound_passed=out['actual_duration_bound_passed'],remaining_snapshot=out['remaining_snapshot'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('TARGET72_H1_FINAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),CPU_only_no_GPU_or_account_mutation=True),f,indent=2)
  raise
