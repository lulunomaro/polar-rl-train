"""Compare immutable C output to independent double oracles, no control replay."""
from pathlib import Path
import json,csv,math,traceback
import numpy as np
HERE=Path(__file__).resolve().parent

def kkt(H,f,z,lo,hi):
 g=H@z+f;r=g.copy();r[lo==hi]=0;r[(z==lo)&(g>0)]=0;r[(z==hi)&(g<0)]=0
 return float(np.max(np.abs(r)))
def objective(H,f,z):return .5*float(z@H@z)+float(f@z)
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
 v=json.loads((HERE.parent/'C_MPC8_NUMERIC_V1/actual_model_vectors.json').read_text(encoding='utf-8'));cases=v['cases'];H=np.asarray(v['H64']);Hq=np.asarray(v['H32'])
 results=[]
 for line in (HERE/'C_RUNS_01.jsonl').read_text(encoding='utf-8').splitlines():
  r=json.loads(line);c=cases[r['case_id']];z=np.asarray(r['z'],dtype=np.float32).astype(float);f=np.asarray(c['f32']);lo=np.asarray(c['lo32']);hi=np.asarray(c['hi32']);oq=c['oracle_quantized'];zq=np.asarray(oq['z']);z64=np.asarray(c['oracle64']['z'])
  assert np.all(np.isfinite(z)) and np.all(z>=lo) and np.all(z<=hi)
  kk=kkt(Hq,f,z,lo,hi);cost=objective(Hq,f,z);scale=float(np.max(np.abs(f)+np.abs(Hq)@np.abs(z)));gamma=float((31*np.finfo(np.float32).eps)/(1-31*np.finfo(np.float32).eps))
  r.update({'kkt_quantized_problem_recomputed_float64':kk,'reported_vs_double_KKT_difference':abs(float(r['reported_kkt_f32'])-kk),
    'float_gradient_rounding_bound_conservative':gamma*scale,'z_error_inf_vs_quantized_oracle':float(np.max(np.abs(z-zq))),
    'u0_error_vs_quantized_oracle':abs(float(z[0]-zq[0])),'z_error_inf_vs_original64_oracle':float(np.max(np.abs(z-z64))),
    'cost_recomputed64':cost,'cost_gap_vs_quantized_oracle':cost-oq['cost'],
    'original64_primal_box_violation':float(max(0.,np.max(np.asarray(c['lo'])-z),np.max(z-np.asarray(c['hi'])))),
    'double_KKT_same_tolerance_met':kk<=r['tolerance'],
    'required_numerical_fallback':not bool(r['converged']),
    'fixture_has_active_bound':bool(oq['active_lower'] or oq['active_upper'] or oq['fixed']),
    'original_free_case':c['unconstrained_feasible']})
  if r['converged']:assert r['status_name']=='CONVERGED' and r['reported_kkt_f32']<=r['tolerance']
  else:assert r['status_name']=='MAX_SWEEPS' and r['sweeps']==r['budget'] and r['reported_kkt_f32']>r['tolerance']
  results.append(r)
 assert len(results)==144
 summary=[]
 for budget in [64,256,4096,20000]:
  for mode in [0,1]:
   subset=[r for r in results if r['budget']==budget and r['warm_mode']==mode];accepted=[r for r in subset if r['converged']]
   summary.append({'budget':budget,'start':'cold' if mode==0 else 'shifted_previous_fixture_oracle_warm',
    'runs':len(subset),'C_converged':len(accepted),'honest_MAX_SWEEPS':sum(not r['converged'] for r in subset),
    'free_case_converged':sum(r['converged'] and r['original_free_case'] for r in subset),
    'active_case_converged':sum(r['converged'] and not r['original_free_case'] for r in subset),
    'max_completed_sweeps':max(r['sweeps'] for r in subset),'max_z_error_inf':max(r['z_error_inf_vs_quantized_oracle'] for r in subset),
    'max_u0_error':max(r['u0_error_vs_quantized_oracle'] for r in subset),
    'max_KKT64_all':max(r['kkt_quantized_problem_recomputed_float64'] for r in subset),
    'max_KKT64_Caccepted':max((r['kkt_quantized_problem_recomputed_float64'] for r in accepted),default=0.),
    'Caccepted_but_double_same_tol_not_met':sum(not r['double_KKT_same_tolerance_met'] for r in accepted)})
 dump('COMPARISON.json',{'summary':summary,'runs':results})
 with (HERE/'BUDGET_SUMMARY.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
 detailed=[{k:r[k] for k in ['case_id','name','warm_mode','budget','status_name','sweeps','reported_kkt_f32','kkt_quantized_problem_recomputed_float64','z_error_inf_vs_quantized_oracle','u0_error_vs_quantized_oracle','cost_gap_vs_quantized_oracle','required_numerical_fallback']} for r in results]
 with (HERE/'RUN_COMPARISON.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(detailed[0]));w.writeheader();w.writerows(detailed)
 print(json.dumps(summary,indent=2))
 print('C_CONVERGED_DOUBLE_KKT_DISAGREEMENT',sum(r['converged'] and not r['double_KKT_same_tolerance_met'] for r in results))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'fast_comparison_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
