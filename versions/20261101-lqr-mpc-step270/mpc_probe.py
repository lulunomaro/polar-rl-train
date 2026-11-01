import json,time,numpy as np
from full_lqr import AsymmetricPlant
from linear_mpc import LinearMPC
from control_core import ROOT
p=AsymmetricPlant(False);p.use_full_lqr=True;g=p.full_lqr(-.2);p.reset(g['symmetric'],-.8);ctl=LinearMPC(g,horizon=15);ref=np.r_[g['q'],np.zeros(7)];ref[0]=-.8
logs=[]
for k in range(250):
    x=p.full_state(True);ref[0]=-.8+.6*k*.01;ref[7]=.6
    tau=ctl.command(x,ref,p.d.qvel[p.vids]);p.torque_control(tau);h=p.health();logs.append(ctl.last_log)
    if h['upright_cos']<.7:break
out={'steps':k+1,'last':h,'solver_ms_median':float(np.median([v['solve_ms'] for v in logs])),'solver_ms_max':max(v['solve_ms'] for v in logs),'last_solver':logs[-1],'all_logs':logs};(ROOT/'results/mpc_approach_v1.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='all_logs'}),flush=True)
