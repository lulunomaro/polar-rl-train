import json,time,numpy as np
from control_core import ROOT
from hybrid_trial import run
cfg={'step':False,'start_x':-.8,'start_delta':-.2,'duration':2.0,'push_at':3.,'speed':.8}
r,rows=run(cfg,True)
print(json.dumps({'last':r['last'],'samples':[{'time':v['time'],'x':v['xyz'][0],'state':v['state'],'phase':v['phase']} for v in rows[::10]]}),flush=True)
(ROOT/'results/approach_v1.json').write_text(json.dumps({'summary':r,'rows':rows}))
