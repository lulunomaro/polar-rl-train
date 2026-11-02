"""Grade predeclared numeric budgets; never tune profiles or delete failures."""
from pathlib import Path
import json,csv,traceback
import numpy as np
HERE=Path(__file__).resolve().parent
def load(n):return json.loads((HERE/n).read_text(encoding='utf-8-sig'))
def main():
 budget=load('NUMERICAL_BUDGET.json');layout=load('REFERENCE_LAYOUT.json');offset=layout['offsets'];actual=[json.loads(s) for s in (HERE/'C_H2_REPLAY_01.jsonl').read_text().splitlines()]
 with (HERE/'REFERENCE_H2.csv').open() as f:expected=list(csv.reader(f))[1:]
 assert len(actual)==len(expected)==5400
 groups=[('state_original','x14','ORIGINAL_X14',budget['state14_abs']),('state_Cparams','x14','MATCHED_X14',budget['state14_abs']),('torque_original','tau','ORIGINAL_TAU',budget['pipeline_torque_abs_Nm']),('torque_Cparams','tau','MATCHED_TAU',budget['pipeline_torque_abs_Nm']),('isolated_tau','iso_tau','ISOLATED_TAU',budget['isolated_H2_torque_abs_Nm']),('base_nominal_tau','base_tau','BASE_TAU',budget['pipeline_torque_abs_Nm'])]
 for name,field,column in [('relative_xy','xy','XY'),('pivot_xy','pivot_xy','PIVOT_XY'),('target_xy','target_xy','TARGET_XY'),('error_xy','error_xy','ERROR_XY'),('isolated_xy','iso_xy','ISO_XY'),('isolated_pivot_xy','iso_pivot_xy','ISO_PIVOT_XY'),('isolated_target_xy','iso_target_xy','ISO_TARGET_XY'),('isolated_error_xy','iso_error_xy','ISO_ERROR_XY')]:groups.append((name,field,column,budget['relative_xy_abs_m']))
 groups += [('body_pivot','body_pivot','BODY_PIVOT',budget['body_pivot_abs_m']),('vy','vy','VY',budget['no_side_slip_vy_abs_m_s']),('projection','projection','PROJECTION',budget['lead_projection_abs_m']),('center_request','corr','CENTER_REQUEST',budget['center_torque_request_abs_Nm']),('isolated_vy','iso_vy','ISO_VY',budget['no_side_slip_vy_abs_m_s']),('isolated_projection','iso_projection','ISO_PROJECTION',budget['lead_projection_abs_m']),('isolated_center','iso_corr','ISO_CENTER_REQUEST',budget['isolated_center_torque_abs_Nm']),('isolated_reference','iso_ref14','ISO_REF14',budget['reference_shaper_integral_abs']),('isolated_shaper','iso_shaper','ISO_SHAPER',budget['reference_shaper_integral_abs'])]
 maxima={};percase={};exceed=[];statuses=[];flags=[];proxy_delta=0.;forward_range=0.;heading_range=0.;relative_norm=0.;maxdiff_preserve=0.
 for row,(a,tokens) in enumerate(zip(actual,expected)):
  v=np.asarray(tokens,dtype=float);case=layout['cases'][a['case']]['name'];percase.setdefault(case,{})
  if a['pipeline_status'] or a['isolated_status']:statuses.append({'row':row,'case':case,'pipeline':a['pipeline_status'],'isolated':a['isolated_status']})
  for name,field,col,tol in groups:
   start,n=offset[col];want=v[start:start+n];got=np.atleast_1d(np.asarray(a[field],dtype=np.float32).astype(float));assert np.isfinite(got).all() and len(got)==n;error=np.abs(got-want);limits=np.broadcast_to(np.asarray(tol,float),error.shape);j=int(np.argmax(error));m=float(error[j])
   if name not in maxima:maxima[name]={'max_abs':0.,'componentwise_max':[0.]*n,'worst':None,'budget':limits.tolist()}
   maxima[name]['componentwise_max']=np.maximum(maxima[name]['componentwise_max'],error).tolist()
   if m>maxima[name]['max_abs']:maxima[name]['max_abs']=m;maxima[name]['worst']={'row':row,'case':case,'component':j,'C32':float(got[j]),'reference64':float(want[j])}
   percase[case][name]=max(percase[case].get(name,0.),m)
   for j in np.flatnonzero(error>limits):exceed.append({'row':row,'case':case,'group':name,'component':int(j),'C32':float(got[j]),'reference64':float(want[j]),'error':float(error[j]),'budget':float(limits[j])})
  for field,col in [('active','ACTIVE'),('target_valid','TARGET_VALID')]:
   if a[field]!=int(v[offset[col][0]]):flags.append({'row':row,'field':field})
  assert a['actuation_qualified']==0 and a['velocity_center']==0
  tau=np.asarray(a['tau'],dtype=np.float32).astype(float);base=np.asarray(a['base_tau'],dtype=np.float32).astype(float)
  for i,x in enumerate(tau):assert abs(x)<=float(np.float32(5.775909774436091 if i in [2,5] else 40.))
  assert abs(float(np.float32(a['corr'])))<=float(np.float32(1.8))
  maxdiff_preserve=max(maxdiff_preserve,abs(.5*(tau[5]-tau[2])-.5*(base[5]-base[2])));proxy_delta=max(proxy_delta,abs(a['proxy_minus_raw_epoch']));forward_range=max(forward_range,abs(a['x14'][0]));heading_range=max(heading_range,abs(a['x14'][1]));relative_norm=max(relative_norm,float(np.linalg.norm(a['xy'])))
 assert maxdiff_preserve<=2e-6
 report={'rows':len(actual),'cases':len(layout['cases']),'status_failures':statuses,'flag_mismatches':flags,'budget_exceedance_points':len(exceed),'maxima':maxima,'per_case':percase,
 'source_temporal_proxy_difference_max_m_s':proxy_delta,'wheel_differential_preservation_error_max_Nm':maxdiff_preserve,'range':{'max_absolute_forward_gauge_m':forward_range,'max_absolute_heading_rad':heading_range,'max_relative_xy_norm_m':relative_norm,'longest_synthetic_s':26.},
 'limits':'math engineering only. Fixed positive4pi H2 physical scope unchanged; synthetic reverse/stop do not qualify physics; full dispatch deferred.', 'new_physics_steps':0,'actuation_qualified':False}
 (HERE/'NUMERICAL_COMPARISON.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 with (HERE/'NUMERICAL_EXCEEDANCES_01.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['row','case','group','component','C32','reference64','error','budget']);w.writeheader();w.writerows(exceed)
 print(json.dumps({'rows':len(actual),'status_failures':len(statuses),'flag_mismatches':len(flags),'budget_exceedance_points':len(exceed),'max_abs':{k:v['max_abs'] for k,v in maxima.items()},'range':report['range'],'source_temporal_proxy_difference_max_m_s':proxy_delta,'wheel_diff_error_Nm':maxdiff_preserve},indent=2))
 if statuses or flags or exceed:raise SystemExit(1)
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'comparison_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
