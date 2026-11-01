import json,numpy as np
from control_core import Plant,ROOT
p=Plant(False);g=p.lqr(-.2);p.reset(g,-.6);ref=np.r_[g['q'],np.zeros(4)];ref[0]=-.6
rows=[]
for k in range(600):
    x=p.observe();tau=g['tau']-g['K']@(x-ref);p.torque_control(tau);hh=p.health()
    if k%20==0:rows.append(hh)
    if hh['upright_cos']<.6:break
out={'steps':k+1,'last':hh,'rows':rows,'gain':g['K'].tolist()};(ROOT/'results/ground_lqr_v2.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
