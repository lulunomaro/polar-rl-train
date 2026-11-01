import json,numpy as np
from control_core import ROOT
rows=json.load(open(ROOT/'results/cross_trace_v1/trajectory.json'))
for r in rows:
    if .85<=r['time']<=1.65:print(json.dumps({k:r[k] for k in ['time','xyz','state','wheel_xyz','phase','tau','tops','nonwheel']}),flush=True)
