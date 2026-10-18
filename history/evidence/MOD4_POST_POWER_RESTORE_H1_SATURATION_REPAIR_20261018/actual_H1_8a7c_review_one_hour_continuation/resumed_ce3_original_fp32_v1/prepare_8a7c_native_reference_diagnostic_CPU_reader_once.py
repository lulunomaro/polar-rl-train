"""Preserve fixed-FP32 refusal and finish all other existing native data checks."""
from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent
def main():
 source=B/'review_8a7c_GPU1_allrow_source_FP32_CPU_once.py';s=source.read_text(encoding='utf8');old="assert mean_error<=1e-4,('Original H1 actor CPUmean tolerance',mean_error)";assert s.count(old)==1
 s=s.replace(old,"original_actor_fp32_pass=mean_error<=1e-4;assert not original_actor_fp32_pass, 'This diagnostic belongs to the actual refused native, not a new admission'\n from h1_8a7c_reference_diagnostic_CPU_v1 import compare_references\n precision_diagnostic=compare_references(sd,flat,actual,mean_error)")
 s=s.replace('passed_complete_data_and_source_CPU=True,','passed_complete_data_and_source_CPU=False,original_fixed_FP32_actor_reference_failed=True,all_other_original_checks_passed=True,precision_diagnostic_only=precision_diagnostic,not_new_native_admission=True,')
 s=s.replace("'_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_ACTUAL.json'","'_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_DIAGNOSTIC_FALSE_ACTUAL.json'").replace('H1_LINUX72_FROZEN_ALLROW_CPU_ORIGINAL_ERROR_','H1_8A7C_DIAGNOSTIC_ORIGINAL_ERROR_')
 ast.parse(s)
 with (B/'review_8a7c_native_existing_allrows_physical_and_precision_diagnostic_CPU_once.py').open('x',encoding='utf8') as f:f.write(s)
 with (B/'reports/H1_8A7C_NATIVE_ORIGINAL_FP32_REFUSAL_CPU_DIAGNOSTIC_PLAN.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),actual_native_fixed_FP32_max=.000118255615234375,original_absolute_bound=.0001,original_reader_false_retained=True,additional_references_diagnostic_only_not_eligibility=True,all_remaining_physical_source_phase_checks_original_thresholds=True,no_full1500_dispatch_or_GPU_replay=True),f,indent=2)
if __name__=='__main__':main()
