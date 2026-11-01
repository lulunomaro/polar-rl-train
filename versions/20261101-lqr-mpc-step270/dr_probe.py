import json,sys,numpy as np
from control_core import ROOT,Plant
from dr_components import FullDR
from jump_trial import run
cfg={'step':False,'duration':.25,'push_at':1.,'start_x':-.6,'start_delta':-.2,'speed':0.,'full_dr':True,'seed':20261101}
r,trace=run(cfg,True)
print(json.dumps({'dr_sample':r['dr_sample'],'queues':r['dr_queue_receipt'],'last':r['last'],'success':r['success']}),flush=True)
(ROOT/'results/full_dr_integration_v1.json').write_text(json.dumps(r,indent=2))
