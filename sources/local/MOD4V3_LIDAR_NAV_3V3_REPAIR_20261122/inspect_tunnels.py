from nav_common import HERE
import mujoco as mj
import numpy as np
m=mj.MjModel.from_binary_path(str(HERE/'maps/wasd/rmuc2027_stiff_v1.mjb'))
d=mj.MjData(m);mj.mj_forward(m,d)
m.geom_group[:]=np.where((m.body_weldid[m.geom_bodyid]==0)&((m.geom_contype!=0)|(m.geom_conaffinity!=0)),3,2)
g=np.zeros(1,np.int32);ray=np.array([0.,0.,-1.]);groups=np.array([0,0,0,1,0,0],np.uint8)
for name in ('rmuc_tunnel_roof_a_red','rmuc_tunnel_roof_b_red','rmuc_tunnel_roof_c_red'):
    gid=m.geom(name).id;p=d.geom_xpos[gid].copy();p[2]=5.
    print(name,d.geom_xpos[gid])
    for i in range(5):
        dist=mj.mj_ray(m,d,p,ray,groups,True,-1,g)
        print(i,p[2]-dist,int(g[0]),m.geom(int(g[0])).name if dist>=0 else None)
        p[2]-=dist+.0001
        if dist<0:break
