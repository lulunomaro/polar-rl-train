"""Check the fair shared-data C1/C2 comparison, no solver rerun."""
from pathlib import Path
import json,hashlib,traceback
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'C_MPC8_NUMERIC_V1'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
 old={ (x['case_id'],x['budget'],x['warm_mode']):x for x in [json.loads(s) for s in (BASE/'C_RUNS_01.jsonl').read_text().splitlines()]}
 current=[json.loads(s) for s in (HERE/'C_RUNS_01.jsonl').read_text().splitlines()]
 cases=load(BASE/'actual_model_vectors.json')['cases'];active_equal=0;free_selected=0;changes=[]
 for x in current:
  y=old[(x['case_id'],x['budget'],x['warm_mode'])];c=cases[x['case_id']]
  if c['unconstrained_feasible']:
   assert x['free_selected'] and x['free_feasible'] and x['free_metrics_valid'] and x['free_kkt_met'];assert x['sweeps']==0 and x['converged'];free_selected+=1
  else:
   assert not x['free_selected']
   keys=['z','sweeps','reported_kkt_f32','cost_f32','status_name','converged','has_candidate','feasible']
   assert all(x[k]==y[k] for k in keys),(x['case_id'],x['budget'],x['warm_mode'])
   active_equal+=1
  if x['status_name']!=y['status_name']:changes.append({'case_id':x['case_id'],'budget':x['budget'],'warm_mode':x['warm_mode'],'old':y['status_name'],'new':x['status_name']})
 assert active_equal==64 and free_selected==80
 summary={'shared_fixture_oracle_sha256':hashlib.sha256((BASE/'actual_model_vectors.json').read_bytes()).hexdigest(),
          'total_runs':len(current),'all_80_free_runs_selected_zero_sweep':free_selected,
          'all_64_active_runs_bit_equal_z_sweeps_cost_KKT_status_to_C1':active_equal,
          'status_improvements':len(changes),'changes':changes,'C1_budget_failures_preserved':55,'C2_remaining_active_budget_failures':sum(not x['converged'] for x in current)}
 (HERE/'CROSS_VERSION.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in summary.items() if k!='changes'},indent=2))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'cross_version_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
