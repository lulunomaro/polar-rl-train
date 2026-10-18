"""One fresh read-only auxiliary-host probe, executed only after transport handback."""
from pathlib import Path
import ast,time,json
B=Path(__file__).resolve().parent;T=B.parent/'MOD4_THREE_GPU_REAL_TRAINING_HOUR_COHORT_20261018'
def main():
 s=(T/'collect_3060_current_eval_surface_readonly_once.py').read_text('utf8');a=';import transport_249_E3_current_exact_desktop_2145_v1 as t';assert a in s
 pre="\nfor rel in ('MOD4_H1_TARGET72_CLOSED_FINAL_E3_FROZEN_REVIEW_20261017','MOD4_TWO72_CLOSED_SOURCES_HEALTHY_NEXT_BLOCK_20261017','MOD4_TWO72_E2_E3_HEALTHY_SAVED_CONTINUATIONS_20261017/curb275_final87_frozen3060_v1','MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'):sys.path.insert(0,str(W/rel))\nimport transport_249_E3_current_exact_desktop_2145_v1 as t"
 s=s.replace(a,pre);ast.parse(s)
 with (B/'collect_3060_one_current_surface_readonly_once.py').open('x',encoding='utf8') as f:f.write(s)
 with (B/'reports/CURRENT3060_ONE_READONLY_PROBE_LOCAL_AST_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),prepared_AST_only=True,not_executed=True,execute_only_after_current_finite_transport_actual_handback=True,original_py_transport_inspected_SSH_stdin_only=True,no_Task_UI_GPU_or_model_or_training_change=True,not_a_current_desktop_MSVCRT_admission=True,one_new_probe_not_repeat_old_consumed_helpers=True),f,indent=2)
if __name__=='__main__':main()
