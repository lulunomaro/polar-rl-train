import json,math,numpy as np
from pathlib import Path
from control_core import Plant,ROOT
p=Plant(False);rows=[]
for delta in [-1.,-.8,-.6,-.4,-.2,0.,.2,.4,.6,.8]:
    try:
        q,tau,res=p.equilibrium(delta);qp,G=p.chart(q)
        m=p.m;d=p.tmp
        joints={s:{n:float(d.joint(s+'_'+n).qpos[0]) for n in ['hip','crank','knee','gas_slide']} for s in ['left','right']}
        bad=[]
        for j in range(m.njnt):
            if m.jnt_limited[j] and not m.jnt_range[j,0]-1e-6<=qp[m.jnt_qposadr[j]]<=m.jnt_range[j,1]+1e-6:bad.append(m.joint(j).name)
        rows.append({'delta':delta,'q':q.tolist(),'root_z':float(qp[2]),'tau':tau.tolist(),'residual':res,'joints':joints,'limits_bad':bad})
    except Exception as e:rows.append({'delta':delta,'error':str(e)})
print(json.dumps(rows),flush=True)
(ROOT/'results/pose_scan.json').write_text(json.dumps(rows,indent=2))
