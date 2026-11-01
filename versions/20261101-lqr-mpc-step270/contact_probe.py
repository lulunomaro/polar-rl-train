import json,numpy as np
from control_core import Plant,ROOT
p=Plant(False);g=p.lqr(-.6);p.reset(g,-.35)
print(json.dumps({'state':p.health(),'contacts':[{'a':p.m.geom(int(c.geom1)).name,'b':p.m.geom(int(c.geom2)).name,'distance':float(c.dist),'position':c.pos.tolist()} for c in p.d.contact],'qref':g['q'].tolist(),'tau':g['tau'].tolist()}),flush=True)
