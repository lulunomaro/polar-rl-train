"""Bind future-only final collection/review to this new cohort without running either."""
from pathlib import Path
import json,time,ast
B=Path(__file__).resolve().parent;T=B.parent/'MOD4_THREE_GPU_REAL_TRAINING_HOUR_COHORT_20261018'
def main():
 d=json.loads((B/'reports/THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').read_bytes());assert d['owner']['detached_pid']==150567
 names=[('collect_three_hour_only_missing_closed_finals_cost_exit_once.py','collect_next_hour_only_missing_closed_finals_cost_exit_once.py'),('review_three_closed_hour_finals_whole_model_original_cost_CPU_once.py','review_next_closed_hour_finals_whole_model_original_cost_CPU_once.py')]
 for old,new in names:
  s=(T/old).read_text('utf8').replace('import deploy_three_actual_hour_learning_closed_H1_continuation_V2_once as d','import deploy_three_next_closed_source_hours_once as d').replace('THREE_REAL_GPU_ONE_HOUR_NATIVE_REUSE_AND_LEARNING_DETACHED_ACTUAL.json','THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').replace('137670','150567').replace("('e2_paid' if key=='e2' else key)",'key');ast.parse(s);assert '137670' not in s and '150567' in s
  with (B/new).open('x',encoding='utf8') as f:f.write(s)
 with (B/'reports/NEXT_HOUR_FINAL_HELPERS_ACTUAL_OWNER150567_LOCAL_BINDING_AST_PREPARED.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),prepared_only_AST_passed=[n for _,n in names],actual_new_owner=150567,three_latest_source_manifests=True,no_execution_or_future_FINAL_or_GPU_claim=True),f,indent=2)
if __name__=='__main__':main()
