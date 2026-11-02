"""New host facts vs unmodified parent v2; read saved evidence, no test/physics rerun."""
from pathlib import Path
import json,hashlib,struct,importlib.util,sys,csv,traceback,collections
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def f32(a):return np.asarray(a,dtype=np.float32)
def bits(a):return f32(a).tobytes()
def dump(n,v):
 p=HERE/n;assert not p.exists(),n;p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
 B=json.loads((HERE/'NUMERICAL_BUDGET.json').read_text());freeze=json.loads((HERE/'SOURCE_FREEZE.json').read_text());parent=ROOT/'C_ACTIVE_MPC_SUPERVISOR_V1/supervisor_v2.py';assert sha(parent)==next(x['sha256']for x in freeze['sources']if x['path']==str(parent))
 sp=importlib.util.spec_from_file_location('parent_native_compare',parent);m=importlib.util.module_from_spec(sp);sys.modules[sp.name]=m;sp.loader.exec_module(m)
 model=json.loads((ROOT/'MPC8_V1/MODEL_AND_QP_CHECKS.json').read_text());eq=np.r_[json.loads((ROOT/'nominal_gain_v1.json').read_text())['gain']['q'],np.zeros(7)]
 refs=[json.loads(s)for s in(HERE/'REFERENCE_INPUTS.jsonl').read_text().splitlines()];allrows=[json.loads(s)for s in(HERE/'host_run_01.log').read_text().splitlines()if s.startswith('{')];rows=[r for r in allrows if r['kind']=='frame'];assert len(refs)==len(rows)==3717
 errors=[];stats=collections.Counter();maxima=dict(f=0.,tau=0.,warm=0.,last_u=0.,caller_KKT=0.);f_bitdiff_rows=[];details=[]
 def ck(ok,tag,k):
  if not ok:errors.append(dict(row=k,tag=tag))
 for k,(a,r)in enumerate(zip(refs,rows)):
  if a['reset']:
   sup=m.ActiveMPCSupervisor(model,eq,None,clock_ns=lambda:0);sup.last_u=a['initial_last_u'];sup.warm=f32(a['initial_warm'])
  native_before=f32(a['initial_warm'])if a['reset']else f32(rows[k-1]['warm']);called=[]
  def solver(p):
   ck(bits(p['warm'])==bits(np.r_[native_before[1:],native_before[-1]]),'shifted_warm_bits',k)
   called.append(p);ck(bits(p['H'])==bits(json.loads((HERE/'MODEL_EXPORT.json').read_text())['arrays']['nm1_H']),'H_bits',k);ck(p['max_pivots']==64 and p['tolerance']==B['unchanged_solver_tol']and p['budget_us']==3000,'solver_constants',k)
   got=f32(r['f']).astype(float);want=p['f'].astype(float);delta=float(np.max(np.abs(got-want)));maxima['f']=max(maxima['f'],delta);ck(bool(np.all(np.abs(got-want)<=B['f_absolute']+B['f_relative']*np.abs(want))),'f_budget',k)
   if bits(got)!=bits(want):f_bitdiff_rows.append(k)
   ck(bits(p['lo'])==bits([r['lo']]*15)and bits(p['hi'])==bits([r['hi']]*15),'box_bits',k)
   return dict(valid=bool(r['qvalid']),status=r['qstatus'],z=f32(r['qz']).astype(float).tolist(),kkt_upper=float(f32(r['qupper'])))
  sup.solver=solver
  base=dict(valid=bool(a['valid']),STATE14=a['state'],REF14=a['reference'],MATH_TAU=a['math_tau'],GUARDED_TAU=a['guarded'],SHAPER_V=a['shaper'])
  tau,log=sup.select(base,a['drive'],a['start_ns'],enabled=bool(a['enabled']));ck(bool(called)==bool(r['qp_called']),'actual_call_branch',k)
  reason=log['reason'];rid=0 if reason is None else 1 if reason=='invalid_C_estimator_or_P25'else 2 if reason=='MPC_disabled_explicitly'else 3 if reason=='QP_worker_fault_latched'else 4 if reason=='outside_zero_yaw_small_pitch_model'else 5 if reason=='no_common_headroom_preserving_LQR_yaw'else 6 if reason=='nonfinite_QP_gradient'else 9 if reason.startswith('QP_nonconverged_status_')else 10 if reason=='QP_transport_or_certificate_fault'else -1
  ck(rid==r['reason'],'reason_decision',k);accepted=log['selected']=='C_ASQP_SEQUENCE_PYTHON_MUX';ck(accepted==bool(r['accepted']),'accept_decision',k);ck(bool(a['valid'])==bool(r['valid']),'valid',k)
  for name,got,want,tol in [('tau',r['tau'],tau,B['torque_absolute_Nm']),('warm',f32(r['warm']).astype(float),sup.warm.astype(float),B['warm_absolute_Nm']),('last_u',[r['last_u']],[sup.last_u],B['last_u_absolute_Nm'])]:
   err=float(np.max(np.abs(np.asarray(got)-want)));maxima[name]=max(maxima[name],err);ck(err<=tol,name+'_budget',k)
  ck(sup.usage['mpc_accepted']==r['accepted_count']and sup.usage['lqr_fallback']==r['fallback_count'],'transactional_counters',k);ck(sup.solver_fault_latched==bool(r['latch']),'fault_latch',k)
  if 'common_box_f32'in log:ck(bits(log['common_box_f32'])==bits([r['lo'],r['hi']]),'inward_box',k)
  if 'caller_double_KKT'in log:
   err=abs(log['caller_double_KKT']-r['caller_KKT']);maxima['caller_KKT']=max(maxima['caller_KKT'],err);ck(err<=B['caller_KKT_absolute'],'caller_KKT_budget',k)
  if r['accepted']:
   ck(r['caller_KKT']<=B['unchanged_solver_tol']and float(f32(r['qupper']))<=B['unchanged_solver_tol'],'exact_original_KKT_gate',k)
   ck(all(r['tau'][j]==a['guarded'][j]for j in [0,1,3,4]),'unchanged_leg_four',k)
  else:
   ck(r['tau']==(a['guarded']if a['valid']else[0.]*6),'independent_fallback_exact',k)
  stats[str(r['reason'])]+=1;details.append(dict(row=k,family=a['family'],reason=r['reason'],accepted=r['accepted'],qp_called=r['qp_called'],qstatus=r['qstatus'],pivots=r['pivots']))
 raw=[r for r in allrows if r['kind']=='old_H15'];old=[json.loads(s)for s in(ROOT/'SPR_AUDIT/ACTIVE_BOX_QP_V3/C_RUNS_02.jsonl').read_text().splitlines()];old={(r['case_id'],r['mode']):r for r in old if r['real_H15']and r['budget']==64};ck(len(raw)==36,'raw_H_count',-1)
 for r in raw:
  expected=old[(r['case'],r['mode'])];ck(r['status']==expected['status']==0 and r['valid']==1 and r['pivots']==expected['pivots']and bits(r['z'])==bits(expected['z'])and bits(r['upper'])==bits(expected['kkt_upper']),'raw_H15_same_core_existing',r['case'])
 native=next(r for r in allrows if r['kind']=='native_summary');ck(native['failures']==0,'native_contracts',-1);clock=[r for r in allrows if r['kind']=='clock_test'];ck(len(clock)==45 and all(r['fired']and r['valid']and not r['accepted']for r in clock),'clock_45',-1)
 ck('NM1_CPP_EXTERN_C accepted=1'in(HERE/'cpp_run_01.log').read_text(),'cpp',-1)
 with(HERE/'FRAME_COMPARISON.csv').open('x',newline='',encoding='utf-8')as f:w=csv.DictWriter(f,fieldnames=list(details[0]));w.writeheader();w.writerows(details)
 with(HERE/'CLOCK_INSERTIONS.csv').open('x',newline='',encoding='utf-8')as f:w=csv.DictWriter(f,fieldnames=list(clock[0]));w.writeheader();w.writerows(clock)
 dump('COMPARISON.json',dict(scope='NEW_NATIVE_CORE_REAL_ASQP_AND_UNMODIFIED_PARENT_SUPERVISOR_REPLAY',rows=len(rows),saved_C3=3200,independent_algebra=512,branch_fixtures=5,raw_old_H15_cold_warm=len(raw),raw_H15_bit_exact=True,reason_counts=dict(stats),maximum_errors=maxima,f_bit_different_rows=f_bitdiff_rows,error_count=len(errors),errors=errors,native_contract=native,clock_insertions=45,CPP=True,reference_method='Unmodified parent v2 consumes exactly the saved real native ASQP answers; verifies its original H/f/bounds/counters/selection and KKT. If f bits differ, this is numerical mapping parity, not a second independent solver run on parent f. The 36 raw existing H15 calls independently check unchanged solver/link outputs.',all_attempts_preserved=True,budget_sha=sha(HERE/'NUMERICAL_BUDGET.json'),new_physics_steps=0))
 print(json.dumps(dict(rows=len(rows),maxima=maxima,f_bit_different=len(f_bitdiff_rows),errors=len(errors),native=native,reason_counts=dict(stats),raw_H15=len(raw))))
 assert not errors
 assert 'mujoco'not in sys.modules and 'physics_bridge'not in sys.modules
if __name__=='__main__':
 try:main()
 except Exception:(HERE/'analysis_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
