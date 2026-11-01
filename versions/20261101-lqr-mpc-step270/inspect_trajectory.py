import json
from pathlib import Path
from jump_trial import run
from control_core import ROOT
cfg=json.load(open(ROOT/'results/cem_step_v1/best_config.json'));cfg['duration']=2.
r,rows=run(cfg,True)
(ROOT/'results/cem_step_v1/best_trace.json').write_text(json.dumps(rows));(ROOT/'results/cem_step_v1/trace_summary.json').write_text(json.dumps(r,indent=2))
for row in rows[::5]:print(json.dumps({k:row[k] for k in ['time','xyz','state','wheel_xyz','phase','tau','nonwheel']}),flush=True)
print(json.dumps(r),flush=True)
