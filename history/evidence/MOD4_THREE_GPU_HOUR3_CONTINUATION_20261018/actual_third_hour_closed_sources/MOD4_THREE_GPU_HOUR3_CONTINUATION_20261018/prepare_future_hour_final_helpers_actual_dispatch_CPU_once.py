"""Prepare hour-end readers bound to this actual new writer, without running them."""
from pathlib import Path
import json,time,ast
B=Path(__file__).resolve().parent;U=B.parent/'MOD4_THREE_GPU_HOUR2_CONTINUATION_20261018'
def main():
 d=json.loads((B/'reports/THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').read_bytes());owner=d['owner']['detached_pid'];assert owner==162530
 names=['collect_next_hour_only_missing_closed_finals_cost_exit_once.py','review_next_closed_hour_finals_whole_model_original_cost_CPU_once.py']
 for n in names:
  s=(U/n).read_text('utf8').replace('150567',str(owner));ast.parse(s);assert '150567' not in s and str(owner) in s
  with (B/n).open('x',encoding='utf8') as f:f.write(s)
 with (B/'reports/THIRD_HOUR_FINAL_HELPERS_ACTUAL_OWNER_LOCAL_BINDING_AST_PREPARED.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),prepared_only_AST_passed=names,actual_new_owner=owner,source_manifests_from_actual_third_hour=True,no_execution_or_future_FINAL_or_GPU_claim=True),f,indent=2)
if __name__=='__main__':main()
