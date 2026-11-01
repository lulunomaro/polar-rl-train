import os,sys,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
os.chdir(ROOT);sys.path.insert(0,str(ROOT))
import numpy as np,scipy,mujoco,torch
import kinematics as kin
m=mujoco.MjModel.from_xml_path(str(ROOT/'model/mod4_400N.xml'));d=mujoco.MjData(m)
print(json.dumps({'mujoco':mujoco.__version__,'scipy':scipy.__version__,'torch':torch.__version__,'cuda_available':torch.cuda.is_available(),'gpu':torch.cuda.get_device_name(0),'nq':m.nq,'nv':m.nv,'bodies':m.nbody-1,'actuators':[m.actuator(i).name for i in range(m.nu)],'mass':float(m.body_mass.sum())}),flush=True)
kin.PARAMS['limits']['left']['input_difference_rad']=[-1.0843,.85]
kin.PARAMS['limits']['right']['input_difference_rad']=[-1.0843,.85]
rows=[]
for hip,diff in [(0.,0.),(0.,-.4),(0.,-.7),(0.,-1.),(-.3,-.7),(.3,-.7),(-.3,.3),(.3,.3)]:
    mujoco.mj_resetData(m,d)
    try:
        kin.set_configuration(m,d,(hip,diff),(hip,diff),check_limits=False)
        wc=d.site('left_wheel_center').xpos.copy()-d.qpos[:3]
        j=[]
        for x in [0,1]:
            off=[hip,diff];off[x]+=1e-5
            kin.set_configuration(m,d,tuple(off),tuple(off),check_limits=False)
            j.append((d.site('left_wheel_center').xpos.copy()-d.qpos[:3]-wc)/1e-5)
        rows.append({'hip':hip,'difference':diff,'wheel_relative':wc.tolist(),'jac_hip_diff':np.array(j).tolist()})
    except Exception as e:rows.append({'hip':hip,'difference':diff,'error':str(e)})
print(json.dumps({'kinematic_samples':rows}),flush=True)
(ROOT/'results').mkdir(exist_ok=True)
(ROOT/'results/initial_model_probe.json').write_text(json.dumps({'samples':rows,'mass':float(m.body_mass.sum())},indent=2))
