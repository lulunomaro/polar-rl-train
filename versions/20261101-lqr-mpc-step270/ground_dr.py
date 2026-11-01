import json,numpy as np
from control_core import ROOT
from hybrid_trial import run
for seed in [0,1,2,20261101]:
    cfg={'step':False,'duration':2.,'push_at':3.,'start_x':-.6,'start_delta':-.2,'speed':0.,'full_dr':True,'seed':seed}
    r,rows=run(cfg,False);(ROOT/f'results/ground_fullDR_seed{seed}.json').write_text(json.dumps(r,indent=2));print(json.dumps({'seed':seed,'steps':r['steps'],'last':r['last'],'stop':r['stop_reason'],'queues':r['queues']}),flush=True)
