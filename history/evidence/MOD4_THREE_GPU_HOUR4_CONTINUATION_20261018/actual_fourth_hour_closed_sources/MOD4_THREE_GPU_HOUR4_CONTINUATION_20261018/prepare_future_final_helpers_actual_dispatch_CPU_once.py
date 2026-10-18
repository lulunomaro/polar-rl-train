"""Prepare the next hour's readers only after the new actual dispatch exists."""
from pathlib import Path
import json,time,ast
B=Path(__file__).resolve().parent;V=B.parent/'MOD4_THREE_GPU_HOUR3_CONTINUATION_20261018'
def main():
 d=json.loads((B/'reports/THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').read_bytes());owner=d['owner']['detached_pid'];assert owner>0 and owner!=162530
 names=['collect_next_hour_missing_closed_finals_bounded_owner_wait_V2_once.py','review_next_closed_hour_finals_whole_model_original_cost_CPU_once.py']
 for n in names:
  s=(V/n).read_text('utf8').replace('162530',str(owner));ast.parse(s);assert '162530' not in s and str(owner) in s
  with (B/n).open('x',encoding='utf8') as f:f.write(s)
 with (B/'reports/FOURTH_HOUR_FINAL_HELPERS_ACTUAL_DISPATCH_BINDING_AST_PREPARED.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),actual_new_owner=owner,prepared_only_AST_passed=names,same_source_connection_metadata_wait_max900=True,no_execution_or_future_FINAL_or_GPU_claim=True),f,indent=2)
if __name__=='__main__':main()
