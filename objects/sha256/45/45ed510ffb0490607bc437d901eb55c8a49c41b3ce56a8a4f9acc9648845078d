import sys,numpy as np
sys.path.insert(0,r"D:/claude2/fangzhen/scripts")
from leg2d import Kite2D, CAD
L=Kite2D(CAD,"c"); HIP_Z=0.2121; R=0.073
def z_for(front1_qpos, rear1_qpos):
    # MJCF qpos = -analytic angle  =>  analytic thigh = -rear1_qpos, crank = -front1_qpos
    q=L.qpos_full(-rear1_qpos, -front1_qpos)
    if q is None: return None
    return R-HIP_Z-q["pts"]["axle"][1]/1000.0
print("Is the DEPLOYMENT's reported (base_z, leg qpos) self-consistent with the closed chain?")
cases=[("v11 probe idle",       0.2023, 0.2479, 0.1800),
       ("v11 armed",            0.1680, 0.2694, 0.1764),
       ("v12 probe armed#1 pre",-0.1741,-0.4878, 0.1789),
       ("v12 probe armed#2 pre",-0.1132,-0.4384, 0.1719),
       ("plant qpos0",           0.0,    0.0,    0.0750)]
print("  %-24s front1     rear1    reported_z   chain_z    residual"%"")
for lab,f,r,zrep in cases:
    zc=z_for(f,r)
    print("  %-24s %+7.4f  %+7.4f   %7.4f      %s   %s"%(
        lab,f,r,zrep, ("%7.4f"%zc) if zc is not None else "  n/a  ",
        ("%+7.4f"%(zrep-zc)) if zc is not None else "n/a"))
print("""
If `residual` is far from 0 the two numbers cannot come from the same rigid closed chain:
either the equality constraints are not enforced at runtime, or the published joint names
do not correspond to the joints we think they do.""")