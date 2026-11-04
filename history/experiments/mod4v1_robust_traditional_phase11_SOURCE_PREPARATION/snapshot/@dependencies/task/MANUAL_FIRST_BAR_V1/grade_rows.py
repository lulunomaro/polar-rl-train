"""Private geometric bounds appended after the sealed cached-stage force audit.
No simulator state writes and no data are exposed to the hop controller. Bounds
are conservative spheres around each collision geom, not new collision shapes.
"""
import math
import numpy as np
from streamed_trace_rows_v1 import StreamedRows

class BoundsRows(StreamedRows):
    def bind(self,plant):
        self.plant=plant;m=plant.m
        explicit=np.isin(np.arange(m.ngeom),np.r_[m.pair_geom1,m.pair_geom2])
        self.ids=np.flatnonzero((m.geom_bodyid>0)&((m.geom_contype!=0)|(m.geom_conaffinity!=0)|explicit))
        assert self.ids.size>0
        self.radius=np.asarray(m.geom_rbound[self.ids],float).copy()+1e-8
        assert np.isfinite(self.radius).all()and np.all(self.radius>0)
        self.maximum_front_x=-math.inf
        self.minimum_final_x=None;self.last_bounds=None
        # Static rigid-local enclosure checks. No forward or step here.
        for gid,r in zip(self.ids,self.radius):
            typ=int(m.geom_type[gid]);size=np.asarray(m.geom_size[gid],float)
            if typ==7:
                mid=int(m.geom_dataid[gid]);a=int(m.mesh_vertadr[mid]);n=int(m.mesh_vertnum[mid])
                need=float(np.linalg.norm(m.mesh_vert[a:a+n],axis=1).max())
            elif typ==2:need=float(size[0])
            elif typ==3:need=float(size[0]+size[1])
            elif typ==4:need=float(size.max())
            elif typ==5:need=float(np.linalg.norm(size[:2]))
            elif typ==6:need=float(np.linalg.norm(size))
            else:raise ValueError('Unbound collision geometry type '+str(typ))
            assert math.isfinite(need)and need<=r,(int(gid),need,r)
        self.first_bar=None;self.next_bar=None
        bars=[]
        for i in range(m.ngeom):
            name=m.geom(i).name
            if m.geom_bodyid[i]!=0 or not name.startswith('rm_bar_'):continue
            assert int(m.geom_type[i])==6
            p=np.asarray(plant.d.geom_xpos[i],float);half=np.asarray(m.geom_size[i],float)
            if p[1]-half[1]<=-.3 and p[1]+half[1]>=.3 and p[0]-half[0]>.8:
                bars.append(dict(name=name,front_x_m=float(p[0]-half[0]),back_x_m=float(p[0]+half[0]),top_z_m=float(p[2]+half[2])))
        bars.sort(key=lambda b:b['front_x_m'])
        if bars:self.first_bar=bars[0]
        if len(bars)>1:self.next_bar=bars[1]
        self.clean_air_main_rear_crossing_s=None
    def append(self,row):
        p=self.plant
        xyz=np.asarray(p.d.geom_xpos[self.ids],float)
        assert np.isfinite(xyz).all()
        low=(xyz-self.radius[:,None]).min(axis=0);high=(xyz+self.radius[:,None]).max(axis=0)
        env=p.exact_support.envelopes(p.d)
        rear=min(v['rear_x_m']for v in env.values());front=max(v['front_x_m']for v in env.values())
        b=dict(kind='CONSERVATIVE_COMPILED_RBOUND_PLUS_1e-8_PRIVATE_ONLY',stage_time_s=row['stage_time_s'],
               collision_geoms=int(self.ids.size),min_xyz_m=low.tolist(),max_xyz_m=high.tolist(),
               exact_main_rear_x_m=float(rear),exact_main_front_x_m=float(front))
        augmented=dict(row,private_full_collision_bounds=b)
        super().append(augmented)
        self.last_bounds=b;self.minimum_final_x=float(low[0]);self.maximum_front_x=max(self.maximum_front_x,float(high[0]))
        if self.first_bar and row['air_qualified']and rear>self.first_bar['back_x_m']and self.clean_air_main_rear_crossing_s is None:
            self.clean_air_main_rear_crossing_s=float(row['stage_time_s'])
