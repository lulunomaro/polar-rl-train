import sys,numpy as np
sys.path.insert(0,r"D:/claude2/fangzhen/scripts")
from leg2d import Kite2D, CAD
L=Kite2D(CAD,"chk")
HIP_Z=0.2121; R=0.073
def base_z(thigh,crank):
    q=L.qpos_full(thigh,crank)
    if q is None: return None,None
    return R-HIP_Z-q["pts"]["axle"][1]/1000.0, q["pts"]["axle"][1]
print("stance height of base_link (m) vs the two hip-axis joint angles (rad, MJCF sign)")
print("  MuJoCo qpos front1=%+.4f rear1=%+.4f  ->  thigh=%+.4f crank=%+.4f"%(-0.2023,-0.2479,-0.2023,-0.2479))
for th,cr,lab in [(0.0,0.0,"qpos0 / training keyframe"),
                  (-0.2479,-0.2023,"DEPLOYED idle (rear1 +0.2479, front1 +0.2023)"),
                  (-0.300,-0.135,"DEPLOYED commanded targets"),
                  (0.0019*1,0.0,"MJLAB idle (front1 target 0.0019, rear1 0.19)"),
                  (-0.19,-0.0019,"MJLAB idle, signed"),
                  (0.2479,0.2023,"deployed angles with the OPPOSITE sign")]:
    z,ax=base_z(th,cr)
    print("   %-52s thigh %+6.3f crank %+6.3f -> base_z %s  axle %s"%(
        lab,th,cr,("%7.4f"%z) if z is not None else "  n/a ",("%+7.1f mm"%ax) if ax is not None else "n/a"))
print("\nworkspace: min/max hip->axle distance")
best=(9e9,-9e9)
for th in np.arange(-1.2,1.25,0.05):
    for cr in np.arange(-1.2,1.25,0.05):
        q=L.qpos_full(th,cr)
        if q is None: continue
        d=-q["pts"]["axle"][1]
        best=(min(best[0],d),max(best[1],d))
print("   hip->axle vertical drop ranges %.1f .. %.1f mm"%(best[0],best[1]))
print("   => base_z can range %.4f .. %.4f m with the wheels on the floor"%(R-HIP_Z+best[1]/1000,R-HIP_Z-best[0]/1000))