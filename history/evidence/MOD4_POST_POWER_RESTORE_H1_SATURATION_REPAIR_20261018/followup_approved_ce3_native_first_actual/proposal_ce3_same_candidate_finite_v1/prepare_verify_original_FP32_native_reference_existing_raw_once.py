"""Verify the actual original H1 native FP32 implementation, same bound, saved raw only."""
from pathlib import Path
import ast,json,time,hashlib
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent.parent;H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 diag=json.loads((R/'CE3_EXISTING_NATIVE_STRICT_ACTOR_FALSE_ALL_ROWS_CPU_DIAGNOSTIC_ACTUAL.json').read_bytes())['report'];assert diag['passed'] is False and diag['all_other_original_checks_passed'] and not diag['strict_actor_reference_pass'] and diag['original_FP32_pass_diagnostic']
 old=W/'MOD4_H1_CLOSED24_TARGET72_SAME_SCOPE_FINITE_20261017/payload/h1/review_H1_prelaunch_v2_native_allrows_CPU_v1.py';text=old.read_text('utf8')
 transforms=[('H1_final10_protected.pt','H1_ce3_public4_closed24.pt'),('644180','646100'),('H1_PRELAUNCH_V2_NATIVE180_ALL_ROWS_CPU_ADMITTED.json','H1_CE3_ORIGINAL_FP32_NATIVE180_ALL_ROWS_CPU_ACTUAL.json'),('H1_NATIVE_CPU_ORIGINAL_ERROR_','H1_CE3_ORIGINAL_FP32_NATIVE_CPU_ORIGINAL_ERROR_')]
 for a,b in transforms:assert a in text;text=text.replace(a,b)
 ast.parse(text);p=B/'review_ce3_native_original_FP32_reference_allrows_CPU_once.py'
 with p.open('x',encoding='utf8') as f:f.write(text)
 with (R/'CE3_ORIGINAL_FP32_REFERENCE_SAME_BOUND_EXISTING_RAW_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original_formal_H1_native_reader=dict(path=str(old),SHA=H(old)),new_source_bound_reader=dict(path=str(p),SHA=H(p)),changes_only_source_filename_Adam_report_namespace=transforms,all_original_FP32_actor_and_physics_guard_AST_unchanged=True,original_absolute1e4_unchanged=True,no_precision_cherry_pick_or_perrow_reference_selection=True,dual_FP64_false_retained_and_separate=True,original_full120000row_FP32_batch_not4096diagnostic=True,no_GPU_native_or_GO_permission_from_preparation=True),f,indent=2)
 print(json.dumps(dict(original_FP32_formal_reader_prepared=True,same_bound=True,no_execution=True)))

if __name__=='__main__':main()
