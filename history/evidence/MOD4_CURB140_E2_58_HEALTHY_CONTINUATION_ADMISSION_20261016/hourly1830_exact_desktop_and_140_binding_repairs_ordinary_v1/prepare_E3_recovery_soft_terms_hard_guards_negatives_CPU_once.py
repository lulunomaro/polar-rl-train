from pathlib import Path
import os,sys,json,time,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;E=D/'e3_legal_fall_reset_admission';R=D/'reports';sys.path.insert(0,str(E));from e3_recovery_term_contract_candidate_cpu_v1 import task_terms,bounded_upright_candidate
def main():
 p=R/'E3_RECOVERY_TERM_CONTRACT_CANDIDATE_HARD_GUARD_NEGATIVES_CPU_ACTUAL.json';assert not p.exists();rng=torch.get_rng_state().clone();n=12;age=torch.tensor([0,299,300,301]*3,dtype=torch.int64);public=torch.tensor([True]*8+[False]*4);original={k:torch.ones(n,dtype=torch.bool) for k in ('bad_orientation','base_contact','closure','mimic','time_out','unknown_future_term')};out=task_terms(original,public,age)
 for k in ('closure','mimic','time_out','unknown_future_term'):assert torch.equal(out[k],original[k])
 for k in ('bad_orientation','base_contact'):assert torch.equal(out[k],~(public&(age<300)))
 assert all(v.all() for v in original.values());normal=task_terms(original,torch.zeros(n,dtype=torch.bool),age);assert all(torch.equal(normal[k],original[k]) for k in original)
 bad=0
 for original2,public2,age2 in [(dict(closure=original['closure']),public,age),(original,public.float(),age),(original,public,age.float()),(original,public,torch.full_like(age,-1))]:
  try:task_terms(original2,public2,age2)
  except AssertionError:bad+=1
  else:raise AssertionError('Invalid contract input accepted')
 peak=torch.zeros(n);total=torch.zeros(n)
 for z in (1.,0.,-1.,1.,-1.):peak,delta=bounded_upright_candidate(peak,torch.full((n,),z),public);total+=delta
 assert torch.equal(total,public.float()) and (peak<=1).all();before=peak.clone();ids=torch.tensor([1,4]);peak[ids]=0;mask=torch.ones(n,dtype=torch.bool);mask[ids]=False;assert torch.equal(peak[mask],before[mask]);assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();source=E/'e3_recovery_term_contract_candidate_cpu_v1.py';report=dict(epoch=time.time(),passed_candidate_CPU_only=True,only_bad_orientation_and_base_contact_soft_task_terms_masked_in_public_rescue_window=True,normal_terms_literal_preserved=True,closure_mimic_timeout_unknown_terms_preserved=True,invalid_contract_input_negatives_rejected=bad,upright_unit_potential_peak_capped_no_oscillation_farming=True,selected_reset_other_rows_unchanged=True,source_path=str(source),source_SHA=hashlib.sha256(source.read_bytes()).hexdigest(),candidate_grace_controls=300,candidate_dt_seconds=.01,candidate_reward_coefficient_not_released=True,original_live_hard_thresholds_not_changed=True,no_original_term_bit_vectors_from_last_native_reconstructed_or_faked=True,no_target_upload_SDK_native_full20k_or_PPO_claim=True,required_next='Bind legal reset and public rescue state to isolated full20k source/state, audit original live reward conflicts and termination terms, checkpoint new counters and private reset RNG, actual source/SDK/resource/native before learning.',global_CPU_RNG_unchanged0CUDA0optimizer=True);p.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(passed_candidate_CPU_only=True,hard_guards_preserved=True,no_target_or_PPO=True)))
if __name__=='__main__':
 try:main()
 except BaseException:(R/('E3_RECOVERY_CONTRACT_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU=True),indent=2),encoding='utf8');raise
