"""Summarize HOST QPC only; never convert it into ARM/WCET qualification."""
from pathlib import Path
import csv,json,statistics
HERE=Path(__file__).resolve().parent

def main():
 cases=json.loads((HERE.parent/'C_MPC8_NUMERIC_V1/actual_model_vectors.json').read_text(encoding='utf-8'))['cases']
 rows=list(csv.DictReader((HERE/'HOST_TIMING_01.csv').open(encoding='utf-8')));assert len(rows)==72
 summary=[]
 for budget in [64,256]:
  for mode in ['CCD_BASE','OPTIONAL_FREE_FAST']:
   for free in [True,False]:
    group=[r for r in rows if int(r['budget'])==budget and r['mode']==mode and bool(cases[int(r['case_id'])]['unconstrained_feasible'])==free]
    means=[float(r['mean_host_us']) for r in group]
    summary.append({'budget':budget,'mode':mode,'category':'original_free_feasible' if free else 'active_bound',
       'cases':len(group),'repeats_per_case':40,'median_of_case_mean_us':statistics.median(means),
       'mean_of_case_mean_us':statistics.mean(means),'observed_max_single_host_us':max(float(r['max_host_us']) for r in group),
       'converged_calls':sum(int(r['converged_count']) for r in group),'total_calls':40*len(group)})
 out={'method':'Windows QueryPerformanceCounter around API call, cold numerical start, no progress or clock callback, diagnostics NULL',
      'limits':'existing shared host, repeated hardware-cache-warm calls; excludes caller model build/IO, not cold/ISR or ARM/WCET',
      'summary':summary}
 (HERE/'HOST_TIMING_SUMMARY.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
