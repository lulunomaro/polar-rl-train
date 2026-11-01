import json,numpy as np
from full_lqr import AsymmetricPlant
from control_core import ROOT
p=AsymmetricPlant(False);p.use_full_lqr=True;g=p.full_lqr(-.2);p.reset(g['symmetric'],-.6);ref=np.r_[g['q'],np.zeros(7)];ref[0]=-.6
rows=[]
for k in range(700):
    x=p.full_state(True);tau=g['tau']-g['K']@(x-ref);p.torque_control(tau);hh=p.health()
    if k%50==0:rows.append(hh)
    if hh['upright_cos']<.6:break
out={'steps':k+1,'last':hh,'rows':rows,'q':g['q'].tolist(),'tau':g['tau'].tolist(),'gain':g['K'].tolist()};(ROOT/'results/ground_full_lqr_v1.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
