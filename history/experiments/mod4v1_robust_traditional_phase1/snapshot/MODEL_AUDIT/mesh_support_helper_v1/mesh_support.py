"""Actual compiled-mesh support geometry; read-only, no forward/step/state changes.
For initialization and grading ONLY, not deployable sensor/controller observations.
Requires existing numpy/scipy. Rebuild this cache if model mesh vertices change.
MuJoCo has already applied mesh scale/centering/PCA: use mesh_vert then
geom_xmat/geom_xpos exactly once. Do NOT apply mesh_pos/mesh_quat again.
"""
from dataclasses import dataclass
import numpy as np
from scipy.spatial import ConvexHull


def _unit_xy(value):
    v=np.asarray(value,dtype=float).reshape(2);norm=float(np.linalg.norm(v))
    if not np.isfinite(v).all() or norm==0:raise ValueError('forward_xy must be finite and nonzero')
    return v/norm


def footprint_polygon_xy(points):
    """Exact convex XY projection polygon, CCW; no circular/spherical surrogate."""
    p=np.unique(np.asarray(points,dtype=float)[:,:2],axis=0)
    if len(p)<=2:return p
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    lower=[];upper=[]
    for x in p:
        while len(lower)>=2 and cross(lower[-2],lower[-1],x)<=0:lower.pop()
        lower.append(x)
    for x in p[::-1]:
        while len(upper)>=2 and cross(upper[-2],upper[-1],x)<=0:upper.pop()
        upper.append(x)
    return np.asarray(lower[:-1]+upper[:-1])


@dataclass(frozen=True)
class StepPatch:
    """Vertical rectangular solid: s=[0,depth], lateral=[-width/2,+width/2].
    edge_xy is the CENTER of its front edge; forward_xy points into the step.
    No acceptance thresholds, stable-window/contact-force gates are implied.
    """
    edge_xy: tuple=(0.0,0.0)
    forward_xy: tuple=(1.0,0.0)
    width_m: float=2.0
    depth_m: float=3.0
    top_z_m: float=0.270
    base_z_m: float=0.0

    def frame(self):
        f=_unit_xy(self.forward_xy);l=np.array([-f[1],f[0]])
        e=np.asarray(self.edge_xy,dtype=float).reshape(2)
        vals=[self.width_m,self.depth_m,self.top_z_m,self.base_z_m]
        if not np.isfinite(e).all() or not np.isfinite(vals).all():raise ValueError('step values must be finite')
        if self.width_m<=0 or self.depth_m<=0 or self.top_z_m<self.base_z_m:raise ValueError('invalid step dimensions')
        return e,f,l


def _clip_polygon(poly,normal,offset):
    """Keep n.dot(x)+offset >= 0, including exact geometric boundaries."""
    if len(poly)==0:return poly
    output=[];prev=poly[-1];dp=float(prev@normal+offset)
    for cur in poly:
        dc=float(cur@normal+offset);pin=dp>=0;cin=dc>=0
        if pin!=cin:
            t=dp/(dp-dc);output.append(prev+t*(cur-prev))
        if cin:output.append(cur)
        prev=cur;dp=dc
    return np.asarray(output,dtype=float).reshape(-1,3)


def _hull_z_interval_in_prism(vertices,triangles,step):
    """Exact polyhedral-hull vertical interval over the finite step top footprint.
    Clip hull surface triangles against four vertical planes. Linear extrema of
    each clipped polygon occur at its vertices; this includes edge intersections.
    """
    e,f,l=step.frame();p=vertices[:,:2]-e;s=p@f;t=p@l;half=step.width_m/2
    if s.max()<0 or s.min()>step.depth_m or t.max()<-half or t.min()>half:return None
    if s.min()>=0 and s.max()<=step.depth_m and t.min()>=-half and t.max()<=half:
        return float(vertices[:,2].min()),float(vertices[:,2].max())
    planes=[(np.r_[f,0.],-float(e@f)),(-np.r_[f,0.],step.depth_m+float(e@f)),
            (np.r_[l,0.],half-float(e@l)),(-np.r_[l,0.],half+float(e@l))]
    lo=np.inf;hi=-np.inf
    for face in triangles:
        poly=vertices[face]
        for normal,offset in planes:
            poly=_clip_polygon(poly,normal,offset)
            if not len(poly):break
        if len(poly):lo=min(lo,float(poly[:,2].min()));hi=max(hi,float(poly[:,2].max()))
    return None if not np.isfinite(lo) else (lo,hi)


class TireMeshSupport:
    """Cache ONLY immutable compiled local mesh vertices/hull topology.
    Constructor takes an existing MjModel; methods read an already-forwarded
    MjData. It creates no MjData and calls no MuJoCo API/physics functions.
    """
    def __init__(self,model,geom_names=('left_tire','right_tire')):
        self.meshes={}
        for name in geom_names:
            gid=int(model.geom(name).id)
            if int(model.geom_type[gid])!=7:raise ValueError(name+' is not a MuJoCo mesh geom')
            mid=int(model.geom_dataid[gid]);adr=int(model.mesh_vertadr[mid]);num=int(model.mesh_vertnum[mid])
            v=np.asarray(model.mesh_vert[adr:adr+num],dtype=float).copy()
            if len(v)<4 or not np.isfinite(v).all():raise ValueError(name+' has invalid mesh vertices')
            # MuJoCo mesh collision and the source USD tire both use this point hull.
            faces=ConvexHull(v).simplices.copy()
            self.meshes[name]={'geom_id':gid,'mesh_id':mid,'vertices_local_compiled':v,'hull_triangles':faces}

    def world_vertices(self,data,name):
        m=self.meshes[name];gid=m['geom_id']
        R=np.asarray(data.geom_xmat[gid],dtype=float).reshape(3,3)
        pos=np.asarray(data.geom_xpos[gid],dtype=float)
        return m['vertices_local_compiled']@R.T+pos

    def envelopes(self,data,forward_xy=(1.0,0.0)):
        """World extrema/footprint per tire; returned arrays are independent copies."""
        f=_unit_xy(forward_xy);result={}
        for name,m in self.meshes.items():
            v=self.world_vertices(data,name);mn=v.min(axis=0);mx=v.max(axis=0);s=v[:,:2]@f
            result[name]={'geom_id':m['geom_id'],'mesh_id':m['mesh_id'],'world_vertices':v,
                'min_xyz_m':mn,'max_xyz_m':mx,'lowest_z_m':float(mn[2]),'highest_z_m':float(mx[2]),
                'front_x_m':float(mx[0]),'rear_x_m':float(mn[0]),'forward_min_m':float(s.min()),'forward_max_m':float(s.max()),
                'lowest_point_world':v[int(np.argmin(v[:,2]))].copy(),'highest_point_world':v[int(np.argmax(v[:,2]))].copy(),
                'foremost_point_world':v[int(np.argmax(s))].copy(),'footprint_xy_ccw_m':footprint_polygon_xy(v)}
        return result

    def root_z_translation(self,data,plane_z_m=0.0,clearance_m=0.0):
        """Unique MINIMAL rigid root-Z shift making all tire vertices >= plane+clearance.
        No qpos change is applied. For roll/asymmetric legs, both tires need not
        touch simultaneously: their individual residual gaps are returned.
        No static equilibrium, contact force, or non-wheel clearance is inferred.
        """
        if not np.isfinite([plane_z_m,clearance_m]).all():raise ValueError('non-finite support plane')
        env=self.envelopes(data);low={n:r['lowest_z_m'] for n,r in env.items()};zmin=min(low.values())
        dz=float(plane_z_m+clearance_m-zmin)
        return {'root_dz_m':dz,'plane_z_m':float(plane_z_m),'requested_clearance_m':float(clearance_m),
            'lowest_z_before_m':low,'tire_gap_after_shift_m':{n:float(z+dz-plane_z_m) for n,z in low.items()},
            'two_tire_lowest_z_difference_m':float(max(low.values())-min(low.values())),
            'meaning':'minimal nonpenetrating tire-only initialization shift; not a physical equilibrium or a runtime root correction'}

    def step_envelope(self,data,step=StepPatch()):
        """Continuous geometric margins for a 270mm (or explicitly supplied) step.
        Truth-geometry grading only. Contact/bearing/stability/success remain the
        caller's separately logged tests. No new acceptance margins are invented.
        """
        e,f,l=step.frame();env=self.envelopes(data,f);rows={}
        for name,r in env.items():
            v=r['world_vertices'];p=v[:,:2]-e;s=p@f;t=p@l;half=step.width_m/2
            margins={'front_m':float(s.min()),'back_m':float(step.depth_m-s.max()),
                     'lateral_minus_m':float(t.min()+half),'lateral_plus_m':float(half-t.max())}
            interval=_hull_z_interval_in_prism(v,self.meshes[name]['hull_triangles'],step)
            zlo,zhi=(None,None) if interval is None else interval
            rows[name]={'rear_crossing_margin_m':float(s.min()),'leading_front_margin_m':float(s.max()),
                'entire_wheel_bottom_above_top_m':float(r['lowest_z_m']-step.top_z_m),
                'footprint_margins_m':margins,'footprint_containment_margin_m':min(margins.values()),
                'fully_over_top_footprint_geometric':bool(min(margins.values())>=0),
                'footprint_xy_ccw_m':r['footprint_xy_ccw_m'].tolist(),
                'overlaps_top_projection':interval is not None,'z_min_over_top_footprint_m':zlo,'z_max_over_top_footprint_m':zhi,
                'top_clearance_where_overlapping_m':None if interval is None else float(zlo-step.top_z_m),
                'step_solid_z_overlap_span_m':0.0 if interval is None else float(max(0.,min(zhi,step.top_z_m)-max(zlo,step.base_z_m)))}
        return {'step':{'edge_xy':e.tolist(),'forward_xy':f.tolist(),'width_m':step.width_m,'depth_m':step.depth_m,'top_z_m':step.top_z_m,'base_z_m':step.base_z_m},
            'per_tire':rows,'both_rear_crossing_margin_m':min(r['rear_crossing_margin_m'] for r in rows.values()),
            'both_full_footprint_margin_m':min(r['footprint_containment_margin_m'] for r in rows.values()),
            'both_entire_bottom_above_top_m':min(r['entire_wheel_bottom_above_top_m'] for r in rows.values()),
            'all_footprints_within_top_geometric':all(r['fully_over_top_footprint_geometric'] for r in rows.values()),
            'contact_or_stability_inferred':False,'acceptance_thresholds_added':False}
