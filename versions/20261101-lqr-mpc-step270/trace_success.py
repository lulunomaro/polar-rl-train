import json,sys
from control_core import ROOT
from hybrid_trial import run
cfg=json.load(open(ROOT/'results/strict_landing_v1/best_config.json'));cfg['duration']=5.
folder=ROOT/'results/strict_success_trace_v1';folder.mkdir(exist_ok=False);r,rows=run(cfg,True);(folder/'result.json').write_text(json.dumps(r,indent=2));(folder/'trajectory.json').write_text(json.dumps(rows));(ROOT/'strict_candidate.json').write_text(json.dumps(cfg,indent=2));print(json.dumps(r),flush=True)
for row in rows:
    if .59<row['time']<.8:print(json.dumps({'time':row['time'],'xyz':row['xyz'],'state':row['state'],'phase':row['phase']}),flush=True)
