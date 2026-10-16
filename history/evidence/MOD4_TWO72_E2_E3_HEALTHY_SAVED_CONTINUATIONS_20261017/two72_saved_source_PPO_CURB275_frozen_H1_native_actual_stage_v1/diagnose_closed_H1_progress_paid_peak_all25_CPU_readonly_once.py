from pathlib import Path
import sys,os,time,json,getpass,traceback
N=Path(__file__).resolve().parent;R=N/'reports';P=N.parent/'MOD4_E1_CURB275_BRIDGE_FROM_CURB35_40_20261016';sys.path.insert(0,str(P))
from collect_hourly0044_existing_V9_FINAL_and_CURB275_production_readonly_once import code,connect72,PY
ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_GROUNDED_PRELAUNCH_PROGRESS_V2_20261016'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('H1_PAID_PEAK_ALL25_DIAGNOSTIC_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport_owner=True,CPU_no_GPU_no_budget=True));pw=getpass.getpass('Host72 saved H1 numerical reference diagnosis only (hidden): ');c=None
 try:
  c=connect72(pw);pw=None;v=code(c,PY,r'''
from pathlib import Path
import sys,json,time,hashlib,os
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
R=Path(sys.argv[1]);O=R/'job0/production';index=json.loads((O/'control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').read_bytes());rows=[];maximum=0.;bad=0
for b,row in enumerate(index['index']):
 p=Path(row['path']);assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
 with np.load(p,allow_pickle=False) as z:a=z['progress_paid'];k=z['progress_peak'];e=z['progress_expected'];req=z['public_request'];finite=bool(np.isfinite(a).all() and np.isfinite(k).all());assert finite;err=np.abs(a.astype(np.float64)-k.astype(np.float64));count=int(np.count_nonzero(err));maximum=max(maximum,float(err.max()));bad+=count;loc=np.unravel_index(err.argmax(),err.shape);rows.append(dict(block=b,raw_SHA=row['SHA'],paid_dtype=str(a.dtype),peak_dtype=str(k.dtype),paid_min=float(a.min()),paid_max=float(a.max()),peak_min=float(k.min()),peak_max=float(k.max()),array_equal=bool(np.array_equal(a,k)),differing_elements=count,maxabs=float(err.max()),worst_example=dict(control=int(loc[0]),env=int(loc[1]),paid=float(a[loc]),peak=float(k[loc]),request=bool(req[loc]),expected_credit=float(e[loc]))))
v=dict(epoch=time.time(),all25_original_raw_SHA_checked=True,blocks=len(rows),raw_control_rows=index['controls']*20000,original_paid_peak_array_equal_false_preserved=bad>0,differing_elements=bad,maxabs_paid_minus_peak=maximum,original_live_source_arithmetic='paid += clamp_min(peak-paid,0) in FP32; subtract then add not assumed bit-identical to peak',rows=rows,no_GPU_optimizer_physics_or_budget_write=True,not_a_repaired_full_control_audit_or_jump_skill_pass=True);A=R/'all25_paid_peak_reference_diagnostic_20261017_v1';assert not A.exists();A.mkdir();(A/'DIAGNOSIS_ACTUAL.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
''',ROOT,timeout=300);put('H1_PAID_PEAK_ALL25_RAW_SHA_NUMERIC_DIAGNOSIS_ACTUAL.json',v);print(json.dumps({k:v[k] for k in ('blocks','raw_control_rows','differing_elements','maxabs_paid_minus_peak')}),flush=True)
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_PAID_PEAK_DIAGNOSIS_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True));raise
