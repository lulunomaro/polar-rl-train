"""Separate CPU reader reference; preserve the old bit-equality rejection."""
from pathlib import Path
import os,sys,time,json,getpass,traceback,ast
N=Path(__file__).resolve().parent;R=N/'reports';P=N.parent/'MOD4_E1_CURB275_BRIDGE_FROM_CURB35_40_20261016';sys.path.insert(0,str(P))
from collect_hourly0044_existing_V9_FINAL_and_CURB275_production_readonly_once import code,connect72,PY
import consume_closed_H1_V2_all25_saved_control_prefixes_finite_CPU_once as base
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 diag=json.loads((R/'H1_PAID_PEAK_ALL25_RAW_SHA_NUMERIC_DIAGNOSIS_ACTUAL.json').read_bytes());assert diag['all25_original_raw_SHA_checked'] and diag['blocks']==25 and diag['differing_elements']==680 and diag['maxabs_paid_minus_peak']<2e-9
 src=base.SOURCE.read_text('utf8');old="assert (paid>=0).all() and (paid<=1.000001).all() and np.array_equal(paid,peak)";assert src.count(old)==1
 new="assert (paid>=0).all() and (paid<=1.000001).all() and (peak>=0).all() and (peak<=1).all() and (np.abs(paid.astype(np.float64)-peak.astype(np.float64)) <= 2*np.spacing(np.maximum(peak,np.float32(np.finfo(np.float32).tiny))).astype(np.float64)).all()"
 src=src.replace(old,new).replace("passed_integrity_CPU=True,controls=", "passed_integrity_CPU=True,original_paid_peak_bit_equality_rejection_preserved=True,paid_peak_new_reference_two_FP32_operation_rounding_bound_ULP2_not_bitexact=True,physical_query_COM_mimic_closure_thresholds_unchanged=True,controls=")
 ast.parse(src);p=N/'review_H1_all25_control_CPU_two_operation_rounding_v2.py';assert not p.exists();p.write_text(src,encoding='utf8');put('H1_ALL25_V2_CPU_REFERENCE_ORIGINAL_ERROR_AND_CHANGE_DISCLOSURE.json',dict(epoch=time.time(),original_V1_full_audit_false_preserved=True,all25_diagnostic_680_bit_differences_maxabs=diag['maxabs_paid_minus_peak'],source_expression_FP32_paid_add_clamped_peak_minus_paid_not_bit_equal=True,new_reference_only_paid_peak_ULP2_enclosure_for_subtract_and_add=True,existing_credit_delta1e6_and_all_other_checks_exactly_retained=True,no_physics_reward_action_model_RNG_or_budget_change=True,no_new_GPU_replay=True));put('H1_ALL25_V2_CPU_FINITE_TRANSPORT_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True))
 pw=getpass.getpass('Host72 corrected saved H1 CPU arithmetic reference only (hidden): ');c=None;A=base.ROOT+'/all25_control_CPU_20261017_v2'
 try:
  c=connect72(pw);pw=None;code(c,PY,"from pathlib import Path;import sys,json;A=Path(sys.argv[1]);assert A.parent==Path(sys.argv[2]) and not A.exists();A.mkdir();print(json.dumps(dict(new_owned_CPU_reference_folder=str(A))))",A,base.ROOT)
  sf=c.open_sftp()
  try:sf.put(str(p),A+'/review.py')
  finally:sf.close()
  v=code(c,PY,r'''
from pathlib import Path
import sys,os,time,json,subprocess,hashlib,psutil
A=Path(sys.argv[1]);env=dict(os.environ,CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1');log=(A/'CPU_CONSOLE.log').open('xb');p=subprocess.Popen([sys.argv[2],'-u','-B',str(A/'review.py')],cwd=A,env=env,stdout=log,stderr=subprocess.STDOUT);q=psutil.Process(p.pid);ident=dict(pid=q.pid,creation=q.create_time(),argv=q.cmdline(),root=q.cwd());rc=p.wait(timeout=1200);log.close();v=dict(epoch=time.time(),actual_CPU_waited_returncode=rc,identity=ident,files=[])
for name in ('ALL_V2_PRODUCTION_CONTROL_ROWS_CPU_ACTUAL.json','CURRENT_ACTUAL.json','ORIGINAL_ERROR_ACTUAL.json'):
 f=A/name
 if f.exists():
  raw=f.read_bytes();v['files'].append(dict(path=str(f),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=json.loads(raw)))
(A/'CPU_WAITED_EXIT_ACTUAL.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
''',A,PY,timeout=1260);put('H1_ALL25_V2_CORRECTED_CPU_ACTUAL_COMPLETE_OR_ERROR.json',v);report=next((r['value'] for r in v['files'] if r['path'].endswith('/ALL_V2_PRODUCTION_CONTROL_ROWS_CPU_ACTUAL.json')),None);print(json.dumps(dict(returncode=v['actual_CPU_waited_returncode'],report=None if report is None else {k:report[k] for k in ('passed_integrity_CPU','formal_updates','all_policy_rows','candidate_takeoff_landing_recovery_events','candidate_event_env_counts','elapsed_CPU_seconds')})),flush=True)
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_ALL25_V2_REFERENCE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),old_false_retained_no_GPU_replay=True));raise
