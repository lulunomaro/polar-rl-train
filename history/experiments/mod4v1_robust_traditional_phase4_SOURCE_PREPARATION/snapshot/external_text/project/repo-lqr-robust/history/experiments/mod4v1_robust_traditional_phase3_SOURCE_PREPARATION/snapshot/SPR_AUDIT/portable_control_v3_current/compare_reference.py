"""Numerical grading only; original budgets/data kept unchanged on failure."""
from pathlib import Path
import json,csv,math,traceback
import numpy as np
HERE=Path(__file__).resolve().parent

def load(n):return json.loads((HERE/n).read_text(encoding='utf-8-sig'))
def main():
 budget=load('NUMERICAL_BUDGET.json');layout=load('REFERENCE_LAYOUT.json');offsets=layout['offsets'];records=[json.loads(x) for x in (HERE/'C_REPLAY_01.jsonl').read_text().splitlines()]
 with (HERE/'REFERENCE_VECTORS.csv').open(encoding='utf-8') as f:expected=list(csv.reader(f))[1:]
 assert len(records)==len(expected)==3200
 groups=[('state_vs_frozen','state14','FROZEN_X14',budget['state14_abs']),('state_vs_Cparams','state14','PARAM_X14',budget['state14_abs']),
  ('roll','roll','ROLL',budget['roll_abs']),('proper_origin','proper','PROPER',budget['proper_origin_abs']),('Joseph_covariance','P','P4',budget['covariance_abs']),
  ('wheel_forward','wheel','WHEEL2',budget['wheel_forward_abs']),('wheel_innovation','slip','SLIP',budget['wheel_innovation_abs']),('contact_proxy','contact','CONTACT',budget['contact_proxy_abs']),
  ('alpha','alpha','ALPHA',budget['alpha_abs']),('pivot','pivot','PIVOT',budget['pivot_abs']),('lateral_proxy','proxy','PROXY',budget['lateral_proxy_abs']),
  ('linear_origin','linear','LINEAR',budget['origin_linear_abs']),('vx_accel','vx_accel','VX_ACCEL',budget['vx_propagation_accel_abs']),('vector_gate','confidence','CONF4',budget['confidence_fields_abs']),
  ('quaternion','quaternion','QUAT',budget['quaternion_abs']),('wheel_accel','wheel_accel','WHEEL_ACC',budget['wheel_accel_abs']),('bias','bias','BIAS',budget['bias_abs']),
  ('torque_vs_frozen','tau','FROZEN_TAU',budget['pipeline_torque_abs']),('torque_vs_Cparams','tau','PARAM_TAU',budget['pipeline_torque_abs']),
  ('isolated_torque','isolated_tau','ISOLATED_TAU',budget['isolated_controller_torque_abs']),('isolated_reference','isolated_ref','ISOLATED_REF14',budget['isolated_controller_reference_abs']),
  ('isolated_shaper_integral','isolated_shape','ISOLATED_SHAPER',budget['isolated_controller_shaper_integral_abs'])]
 maxima={};per_case={};exceedances=[];bad_status=[]
 for index,(r,values) in enumerate(zip(records,expected)):
  if any(r[k]!=0 for k in ['est_status','control_status','isolated_status']):bad_status.append({'row':index,'scenario':r['scenario'],'statuses':[r[k] for k in ['est_status','control_status','isolated_status']]})
  v=np.asarray(values,dtype=float);case=layout['cases'][r['scenario']]['name'];per_case.setdefault(case,{})
  for name,field,reference,tolerance in groups:
   start,n=offsets[reference];want=v[start:start+n];actual=np.atleast_1d(np.asarray(r[field],dtype=np.float32).astype(float));assert len(actual)==n and np.isfinite(actual).all()
   error=np.abs(actual-want);limit=np.broadcast_to(np.asarray(tolerance,float),error.shape);worst=int(np.argmax(error));maximum=float(error[worst])
   if name not in maxima:maxima[name]={'max_abs':0.,'componentwise_max':[0.]*n,'worst':None,'budget':np.broadcast_to(np.asarray(tolerance,float),error.shape).tolist()}
   m=maxima[name];m['componentwise_max']=np.maximum(m['componentwise_max'],error).tolist()
   if maximum>m['max_abs']:m['max_abs']=maximum;m['worst']={'row':index,'scenario':case,'component':worst,'C32':float(actual[worst]),'reference64':float(want[worst])}
   per_case[case][name]=max(per_case[case].get(name,0.),maximum)
   for j in np.flatnonzero(error>limit):exceedances.append({'row':index,'scenario':case,'group':name,'component':int(j),'C32':float(actual[j]),'reference64':float(want[j]),'abs_error':float(error[j]),'budget':float(limit[j])})
 report={'rows':len(records),'scenarios':len(layout['cases']),'all_status_OK':not bad_status,'budget_exceedance_points':len(exceedances),'bad_status':bad_status,'maxima':maxima,'per_scenario_max_abs':per_case,
         'limits':'Numerical prototype engineering budgets, not physical/ARM/robot acceptance. Original Python uses eps1e-5; C parameter reference quantizes pins/config/K/input and uses declared eps1e-3.',
         'no_physics':True,'H2_feedback_deferred':True}
 (HERE/'NUMERICAL_COMPARISON.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
 with (HERE/'NUMERICAL_EXCEEDANCES_01.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=['row','scenario','group','component','C32','reference64','abs_error','budget']);w.writeheader();w.writerows(exceedances)
 print(json.dumps({'rows':len(records),'bad_status_count':len(bad_status),'budget_exceedance_points':len(exceedances),'max_abs':{k:v['max_abs'] for k,v in maxima.items()}},indent=2))
 if bad_status or exceedances:raise SystemExit(1)
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'comparison_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
