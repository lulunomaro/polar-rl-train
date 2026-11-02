"""Double regrade all original f32 problems; retain every MAX/failure point."""
from pathlib import Path
import json,csv,traceback
import numpy as np
HERE=Path(__file__).resolve().parent
STATUS=['CONVERGED','MAX_PIVOTS','DEADLINE','CLOCK_ERROR','BAD_ARGUMENT','BAD_SHAPE','BAD_OPTIONS','BAD_ALIAS','NONFINITE','ASYMMETRIC','NOT_SPD','NUMERIC','NO_PROGRESS','CYCLE','ROUNDOFF_LIMIT','BAD_BOX']
def main():
 problems=json.loads((HERE/'PROBLEMS.json').read_text())['cases'];runs=[json.loads(x) for x in (HERE/'C_RUNS_01.jsonl').read_text().splitlines()];budget=json.loads((HERE/'NUMERICAL_BUDGET.json').read_text());old=json.loads((HERE.parent/'C_MPC8_NUMERIC_V1/actual_model_vectors.json').read_text())['cases'];table={};rows=[];failures=[];accuracy=[];certificate=[];maximum_z=maximum_gap=maximum_kkt=0.
 for r in runs:
  q=problems[r['case_id']];kind='real_free' if r['real_H15'] and old[r['case_id']]['unconstrained_feasible'] else ('real_active' if r['real_H15'] else 'independent_stress');key=f"{kind}_b{r['budget']}_m{r['mode']}";table.setdefault(key,{'total':0,'converged':0,'statuses':{},'max_pivots':0,'max_factor_cells':0,'max_releases':0,'max_bound_hits':0,'max_z_error':0.,'max_cost_gap':0.,'max_exact_kkt':0.})
  t=table[key];t['total']+=1;name=STATUS[r['status']];t['statuses'][name]=t['statuses'].get(name,0)+1;t['max_pivots']=max(t['max_pivots'],r['pivots']);t['max_factor_cells']=max(t['max_factor_cells'],r['factor_cells']);t['max_releases']=max(t['max_releases'],r['releases']);t['max_bound_hits']=max(t['max_bound_hits'],r['bound_hits'])
  record={'case_id':r['case_id'],'name':q['name'],'family':q['family'],'kind':kind,'mode':r['mode'],'budget':r['budget'],'status':name,'valid':r['valid'],'pivots':r['pivots'],'factor_cells':r['factor_cells'],'releases':r['releases'],'bound_hits':r['bound_hits'],'kkt_exact':r['kkt_exact_double'],'z_error':None,'cost_gap':None}
  H=np.asarray(q['H'],float);f=np.asarray(q['f'],float);lo=np.asarray(q['lo'],float);hi=np.asarray(q['hi'],float);oracle=np.asarray(q['oracle']['z'],float)
  if r['valid']:
   t['converged']+=1;z=np.asarray(r['z'],dtype=np.float32).astype(float);assert np.all(z>=lo) and np.all(z<=hi);g=H@z+f;v=np.abs(g);v=np.where(z==lo,np.maximum(-g,0),v);v=np.where(z==hi,np.maximum(g,0),v);v=np.where(lo==hi,0,v);kkt=float(np.max(v));cost=float(.5*z@H@z+f@z);gap=cost-q['oracle']['cost'];err=float(np.max(np.abs(z-oracle)));record.update(kkt_exact=kkt,z_error=err,cost_gap=gap)
   if kkt>float(np.float32(.002)) or kkt>r['kkt_upper']+1e-10:certificate.append(record)
   t['max_z_error']=max(t['max_z_error'],err);t['max_cost_gap']=max(t['max_cost_gap'],gap);t['max_exact_kkt']=max(t['max_exact_kkt'],kkt);maximum_z=max(maximum_z,err);maximum_gap=max(maximum_gap,gap);maximum_kkt=max(maximum_kkt,kkt)
   if r['real_H15'] and (err>budget['actual_H15_success_z_inf_vs_quantized_oracle_max'] or gap>1e-4*(1+abs(q['oracle']['cost']))):accuracy.append(record)
  else:
   assert not any(r['z']) and r['cost_f32']==0 and r['kkt_upper']==0;failures.append(record|{'private_diagnostic_not_output':r['private_iterate'],'private_kkt':r['private_iterate_kkt']})
  rows.append(record)
 summary={'runs':len(runs),'table':table,'nonconverged_runs':len(failures),'certificate_failures':certificate,'actual_accuracy_budget_failures':accuracy,'all_success_max_z_error':maximum_z,'all_success_max_cost_gap':maximum_gap,'all_success_max_exact_KKT':maximum_kkt,'private_failure_points':'diagnostic workspace iterates retained, never accepted outputs','original_CCD64_cold_real':2,'original_CCD256_cold_real':7,'comparison_limits':'AS pivots/factor cells are not CCD sweeps or equal work; no robot/3ms/ARM timing claim','new_physics_steps':0}
 (HERE/'COMPARISON.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');(HERE/'ALL_NONCONVERGED.json').write_text(json.dumps(failures,indent=2)+'\n',encoding='utf-8')
 with (HERE/'RUN_COMPARISON.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 report={k:v for k,v in table.items() if '_b64_' in k or '_b256_' in k}
 print(json.dumps({'runs':len(runs),'primary_and_extended':report,'certificate_failures':len(certificate),'actual_accuracy_failures':len(accuracy),'success_max_exact_KKT':maximum_kkt,'all_nonconverged_preserved':len(failures)},indent=2))
 if certificate or accuracy:raise SystemExit(1)
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'analysis_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
