"""R01firstspintraceanalysis, no physicalreplay."""
from pathlib import Path
import json,hashlib
import numpy as np
R=Path(__file__).resolve().parent;out=R/'reports/r01_spin_analysis.json';assert not out.exists();D=R/'results/r01_spin_midpoint';raw=(D/'trace.jsonl').read_bytes();rows=[json.loads(a)for a in raw.splitlines()];tail=[r for r in rows if r['time']>=6.]
fields={
 'requested_tau6':np.array([r['raw_requested_tau']for r in tail]),'actual_tau6':np.array([r['actual_tau']for r in tail]),'wheel_rates2':np.array([r['wheel_rate2']for r in tail]),'gyro3':np.array([r['raw_gyro']for r in tail]),'true_gyro3':np.array([r['ground_truth']['gyro_true']for r in tail]),'estimated14':np.array([r['estimated14']for r in tail]),'joint4':np.array([r['encoder4']for r in tail]),'normal_N2':np.array([r['physics_wheel_mean_force_N2']for r in tail])}
s={k:{'mean':v.mean(0).tolist(),'min':v.min(0).tolist(),'max':v.max(0).tolist()}for k,v in fields.items()};samples=[]
for t in(1.,2.,3.,4.,5.,6.,7.,8.):
 r=min(rows,key=lambda r:abs(r['time']-t));samples.append({k:r[k]for k in('time','shaped','estimated14','raw_requested_tau','actual_tau','wheel_rate2','encoder4','physics_wheel_mean_force_N2','ground_truth')})
res={'kind':'R01_SPIN_OBSERVED_STATISTICS_NOT_CAUSAL_PROOF','trace_SHA':hashlib.sha256(raw).hexdigest(),'trace_read_count_thispurpose':1,'tail':s,'samples':samples};out.write_text(json.dumps(res,indent=2),encoding='utf-8');print(json.dumps(s,indent=2));print('REPORT',out)
