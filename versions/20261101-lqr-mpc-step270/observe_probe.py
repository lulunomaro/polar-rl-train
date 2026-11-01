import json,numpy as np,mujoco
from control_core import Plant,ROOT
p=Plant(False);g=p.lqr(-.6);p.reset(g,-.35)
for k in range(8):
    s=p.state();o=p.observe();d=p.d;R=d.xmat[p.chassis].reshape(3,3)
    print(json.dumps({'tick':k,'s':s.tolist(),'o':o.tolist(),'omega':p.observed['omega3'].tolist(),'gravity':p.observed['gravity3'].tolist(),'qvel':d.qvel[:6].tolist(),'R':R.tolist()}),flush=True)
    p.torque_control(np.array([0,0,4.]))
