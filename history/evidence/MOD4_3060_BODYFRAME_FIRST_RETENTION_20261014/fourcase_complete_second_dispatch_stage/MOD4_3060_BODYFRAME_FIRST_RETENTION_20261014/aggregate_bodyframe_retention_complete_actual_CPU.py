"""Complete actual three paired scope audit with separate native/old/new provenance."""
from pathlib import Path
import json,sys,time,hashlib,importlib.util
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';OLD=W/'MOD4_3060_LEFT_REPAIR_RETENTION_20261014';PREVIOUS=W/'MOD4_3060_LEFT_SECOND_RETENTION_20261014'
BASE='e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c';OWN='f5166509d297814e3c3fe4f457ae064d9b02a8bd62702914759dc430f20d2139'
spec=importlib.util.spec_from_file_location('original_v8_pure_CPU_audit',OLD/'aggregate_retention_v8_three_skill_pairs_actual_CPU.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
def main():
 out=R/'BODYFRAME_FIRST_F516_THREE_RETENTION_PAIRS_COMPLETE_ACTUAL_CPU_REVIEW.json';assert not out.exists()
 done=a.J(R/'BODYFRAME_FIRST_RETENTION_FIXED_THREE_COMPLETE_ACTUAL.json');assert done['all_three_new_candidates_complete'] and len(done['results'])==3 and done['no_PPO_no_budgetwrite']
 evidence=[];pairs={};cases={};natives={};cost=0.
 for kind in ('flat','spin','world'):
  name=f'retention_bodyframe_first_f516_{kind}_1500_v8';path=R/(name+'_FULL_CPU_REVIEW.json');report=a.J(path);evidence.append(a.file_index(path))
  assert report['original_false_and_failure_prefix_preserved'] and report['no_GPU_no_SSH_no_PPO'] and report['qualification_not_claimed']
  pair=report['result'];assert pair['actual_initial_root_q30_parameters_recipes_RNG_queues_exact'];b=pair['baseline'];c=pair['candidate']
  a.validate_result(b,kind,1500,BASE);a.validate_result(c,kind,1500,OWN)
  a.D=PREVIOUS;cases['baseline_'+kind]=a.actual_case_provenance(PREVIOUS/'reports',f'retention_second_e3_{kind}_1500_v8',b)
  a.D=OLD
  native_path=OLD/'reports'/f'retention_baseline1aa_{kind}_120_v8_FULL_CPU_REVIEW.json';nv=a.J(native_path)['result'];a.validate_result(nv,kind,120,'1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06')
  natives[kind]=a.actual_case_provenance(OLD/'reports',f'retention_baseline1aa_{kind}_120_v8',nv)
  a.D=D;cases['candidate_'+kind]=a.actual_case_provenance(R,name,c);cost+=cases['candidate_'+kind]['actual_parent_unique_zero_PPO_cost_seconds']
  assert cases['baseline_'+kind]['actual_initial_root_q30_parameters_recipes_RNG_queues_SHA']==cases['candidate_'+kind]['actual_initial_root_q30_parameters_recipes_RNG_queues_SHA']
  assert cases['baseline_'+kind]['loaded_PhysX_binary_files']==cases['candidate_'+kind]['loaded_PhysX_binary_files']
  assert cases['baseline_'+kind]['actual_native_actor_and_USD_metadata']==cases['candidate_'+kind]['actual_native_actor_and_USD_metadata']
  diff=a.flat_compare(b,c) if kind=='flat' else a.spin_compare(b,c) if kind=='spin' else a.world_compare(b,c)
  pairs[kind]=dict(comparison=diff,baseline_ordinary=b['data']['ordinary'],candidate_ordinary=c['data']['ordinary'],baseline_truncation=b['data']['truncation'],candidate_truncation=c['data']['truncation'],baseline_original_flags=b['old_original_flags'],candidate_original_flags=c['old_original_flags'],original_false_and_all_failed_prefix_kept=True)
 result=dict(epoch=time.time(),passed=True,all_three_inherited_full1500_complete=True,pending=[],source_base_SHA=BASE,source_own_SHA=OWN,actual_cases=cases,native_actual_proofs_reused_no_GPU_replay=natives,pairs=pairs,complete_report_evidence=evidence,actual_unique_candidate_parent_no_PPO_cost_seconds=cost,root_and_current_training_formal_final_separate=True,no_third_blind_same_axis_PPO=True,no_fixed_percent_gate_or_qualification_claim=True,query_source_to_binding_bitexact_and_shapeLocal_NOT_claimed=True,no_SSH_GPU_signal_RNG_or_budget_action=True)
 out.write_text(json.dumps(result,indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(out),passed=True,flat=pairs['flat']['comparison'],spin=[dict(command=v['command_yaw_rad_s'],baseline_count=v['baseline']['within_original_absolute02_count'],candidate_count=v['candidate']['within_original_absolute02_count'],paired_error_deltas=[x['candidate_minus_baseline_absolute_error'] for x in v['per_paired_sample']]) for v in pairs['spin']['comparison']],world={k:v for k,v in pairs['world']['comparison'].items() if k!='rows'},ordinary={k:[v['baseline_ordinary'],v['candidate_ordinary']] for k,v in pairs.items()},no_PPO_cost=cost)))
if __name__=='__main__':main()
