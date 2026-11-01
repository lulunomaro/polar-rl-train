import json,sys
from pathlib import Path
from control_core import ROOT
src=ROOT/'results/landing_sweep_v1/best_config.json';cfg=json.load(open(src));cfg['duration']=5.
(ROOT/'nominal_candidate.json').write_text(json.dumps(cfg,indent=2))
from hybrid_trial import run
r,rows=run(cfg,True);out=ROOT/'results/nominal_strict_trace_v1';out.mkdir(exist_ok=False);(out/'result.json').write_text(json.dumps(r,indent=2));(out/'trajectory.json').write_text(json.dumps(rows));print(json.dumps(r),flush=True)
