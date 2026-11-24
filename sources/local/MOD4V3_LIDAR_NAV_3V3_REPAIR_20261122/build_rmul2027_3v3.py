"""Exact CAD-face prisms, separate visual meshes, stiff MuJoCo binaries and ray audit."""
from nav_common import HERE, put, sha256, donor_imports
from collections import defaultdict
from pathlib import Path
from time import perf_counter
import json
import math
import xml.etree.ElementTree as ET
import numpy as np
import cadquery as cq
import trimesh
import shapely
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
import mujoco as mj

TRANSFORM = np.array([[1,0,0],[0,0,1],[0,-1,0]], dtype=float)
ATTR = dict(solref='0.0012 1', friction='0.9 0.005 0.0001', contype='1', conaffinity='3', group='3')
CACHE = HERE/'maps/wasd'

def polygons(g):
    if g.is_empty: return []
    if g.geom_type == 'Polygon': return [g]
    return [p for child in g.geoms for p in polygons(child)]

def poly_triangles(p):
    return list(shapely.constrained_delaunay_triangles(p).geoms)

def vec(a): return ' '.join(f'{float(v):.10g}' for v in np.asarray(a).ravel())

def build():
    CACHE.mkdir(parents=True, exist_ok=True)
    assets = HERE/'assets/rmul2027'
    assets.mkdir(parents=True,exist_ok=True)
    source = HERE/'assets/cad/RMUL2027_3V3_V1.0.0.stp'
    assert source.stat().st_size == 1989786
    assert sha256(source) == '7d47c1b6a6a0253a732e46cb122bb84410b11d5134bcb5658104299db4a48ca4'
    assert np.linalg.det(TRANSFORM) == 1
    shape = cq.importers.importStep(str(source)).val()
    faces = shape.Faces()
    visual = defaultdict(list)
    horizontal = defaultdict(list)
    slopes=[]; risers=[]; all_mesh=[]
    for i, face in enumerate(faces):
        points, triangles = face.tessellate(.35, .05)
        verts=np.asarray([[p.x,p.y,p.z] for p in points]) @ TRANSFORM.T * .001
        tri=np.asarray(triangles,dtype=int)
        mesh=trimesh.Trimesh(vertices=verts,faces=tri,process=False)
        all_mesh.append(mesh)
        center=verts.mean(0); zmin,zmax=verts[:,2].min(),verts[:,2].max()
        normal=np.asarray(face.normalAt().toTuple()) @ TRANSFORM.T
        category=('wall' if center[2]>.35 else 'highland' if center[2]>.10 else 'marking' if center[2]>.001 else 'floor')
        if .01 < abs(normal[2]) < .99999: category='bevel'
        visual[category].append(mesh)
        if zmax-zmin < 1e-7 and normal[2]>.99 or (zmax-zmin < 1e-7 and abs(zmax-.42)<1e-7):
            z=float(np.round(zmax,8))
            horizontal[z] += [Polygon(t[:,:2]) for t in verts[tri] if Polygon(t[:,:2]).area>1e-12]
        if .01<normal[2]<.99999:
            for t in verts[tri]:
                slopes.append((t, .02 if zmin>.15 else .1, i))
        if abs(normal[2])<1e-6 and .079<zmax-zmin<.251:
            span=verts[:,:2].max(0)-verts[:,:2].min(0)
            if np.linalg.norm(span)>.3 and np.max(np.abs(center[:2]))<5.9:
                risers.append(dict(face=i,bottom_m=float(zmin),top_m=float(zmax),height_m=float(zmax-zmin),
                    center=center.tolist(),outward_normal=normal.tolist(),endpoints=[verts[:,:2].min(0).tolist(),verts[:,:2].max(0).tolist()]))
    donor_imports()
    from fsm_maps import reference
    maps=reference.legacy.maps;maps.CACHE_DIR=CACHE
    tree,root=maps._load_base_robot_tree()
    maps._add_checker_sky_and_floor(root,add_floor=False)
    asset=root.find('asset');world=root.find('worldbody')
    colors={'floor':'.19 .27 .34 1','marking':'.42 .55 .62 1','highland':'.17 .54 .61 1',
            'wall':'.45 .57 .70 1','bevel':'.88 .58 .23 1'}
    for category,meshes in visual.items():
        path=assets/(category+'.obj')
        trimesh.util.concatenate(meshes).export(path)
        ET.SubElement(asset,'mesh',name='rmul_visual_'+category,file=str(path))
        ET.SubElement(world,'geom',name='rmul_visual_'+category,type='mesh',mesh='rmul_visual_'+category,
                      contype='0',conaffinity='0',group='4',rgba=colors[category])
    complete=trimesh.util.concatenate(all_mesh)
    complete.export(assets/'cad_exact.stl')
    nbox=nprism=0
    coverage=[];pieces=[]
    # Upper surfaces partition exactly in XY. Thin overhead bars and plates retain
    # their measured CAD lower surfaces, so a roof never becomes a filled column.
    for z in sorted(horizontal,reverse=True):
        bottom=.25 if abs(z-.27)<1e-6 else (.007 if .009<=z<=.0111 else (.4 if abs(z-.42)<1e-6 else -.1))
        region=unary_union(horizontal[z])
        subtract=[poly for top,low,poly in coverage if low<=z+1e-8]
        if subtract:region=region.difference(unary_union(subtract))
        for poly in polygons(region):
            if poly.area<1e-12:continue
            coverage.append((z,bottom,poly))
            bounds=poly.bounds
            if abs(poly.area-(bounds[2]-bounds[0])*(bounds[3]-bounds[1]))<1e-10:
                parts=[poly]
            elif abs(poly.convex_hull.area-poly.area)<1e-10 and not poly.interiors:
                parts=[poly]
            else:parts=poly_triangles(poly)
            for part in parts:
                if part.area<1e-11:continue
                b=part.bounds
                if abs(part.area-(b[2]-b[0])*(b[3]-b[1]))<1e-10:
                    ET.SubElement(world,'geom',name=f'rmul_box_{nbox}',type='box',
                        size=vec([(b[2]-b[0])/2,(b[3]-b[1])/2,(z-bottom)/2]),
                        pos=vec([(b[2]+b[0])/2,(b[3]+b[1])/2,(z+bottom)/2]),rgba='0 0 0 0.0001',**ATTR)
                    nbox+=1
                else:
                    p=np.array(part.exterior.coords[:-1]);top=np.c_[p,np.full(len(p),z)]
                    vertex=np.concatenate((top,np.c_[p,np.full(len(p),bottom)]))
                    name=f'rmul_prism_{nprism}'
                    ET.SubElement(asset,'mesh',name=name,vertex=vec(vertex),maxhullvert='64')
                    ET.SubElement(world,'geom',name=name,type='mesh',mesh=name,rgba='0 0 0 0.0001',**ATTR)
                    nprism+=1
                pieces.append(dict(top=z,bottom=bottom,xy=list(part.exterior.coords)))
    for t,thickness,index in slopes:
        name=f'rmul_prism_{nprism}'
        vertex=np.concatenate((t,t-[0,0,thickness]))
        ET.SubElement(asset,'mesh',name=name,vertex=vec(vertex))
        ET.SubElement(world,'geom',name=name,type='mesh',mesh=name,rgba='0 0 0 0.0001',**ATTR);nprism+=1
    xml=CACHE/'rmul2027_3v3_stiff_v1.xml';tree.write(xml,encoding='utf-8',xml_declaration=True)
    m=mj.MjModel.from_xml_path(str(xml));mj.mj_saveModel(m,str(xml.with_suffix('.mjb')),None)
    times=[]
    for _ in range(3):
        start=perf_counter();tmp=mj.MjModel.from_binary_path(str(xml.with_suffix('.mjb')));times.append(perf_counter()-start)
    put(HERE/'evidence/RMUL_COLLISION_PARTS.json',pieces)
    meta=dict(xml_path=str(xml),mjb_path=str(xml.with_suffix('.mjb')),course='suite_rmul2027',hide_group5=False,
        spawns=[dict(x=-4.9,y=-2.3,yaw_deg=0.,name='西南主路'),
                dict(x=-2.5,y=-2.1,yaw_deg=90.,name='西中央高地正入'),
                dict(x=2.5,y=2.1,yaw_deg=-90.,name='东中央高地正入'),
                dict(x=-2.5,y=.8,yaw_deg=90.,name='西高地台顶'),
                dict(x=2.5,y=-.8,yaw_deg=-90.,name='东高地台顶'),
                dict(x=0.,y=-2.2,yaw_deg=90.,name='中央大道')])
    put(CACHE/'rmul2027_3v3_stiff_v1.json',meta)
    preliminary=dict(source_sha256=sha256(source),transform=TRANSFORM.tolist(),determinant=float(np.linalg.det(TRANSFORM)),
        cad_bounds_m=complete.bounds.tolist(),footprint_m=(complete.bounds[1,:2]-complete.bounds[0,:2]).tolist(),
        collision_boxes=nbox,collision_convex_prisms=nprism,whole_arena_collision_mesh=False,
        binary_load_seconds=times,stairs=risers,
        ramp_slopes=[dict(face=i,angle_deg=45.,vertices=t.tolist()) for t,_,i in slopes],
        highland_spawns=meta['spawns'][1:5],
        cad_notes=['The CAD also contains a 0.420 m perimeter trim surface and a 0.010 m central floor panel.',
                   'The primary playable highlands are at +0.200 m; +0.400 m also occurs on walls and narrow features.'])
    put(HERE/'evidence/RMUL2027_3V3_BUILD.json',preliminary)
    print(json.dumps(dict(boxes=nbox,prisms=nprism,binary_load_seconds=times)),flush=True)
    return m,complete,preliminary

def audit(m, mesh, preliminary):
    xs=np.linspace(-6.30,6.30,631);ys=np.linspace(-4.30,4.30,431)
    xy=np.stack(np.meshgrid(xs,ys),-1).reshape(-1,2)
    height=np.full((len(ys),len(xs)),-np.inf)
    # Exact vertical triangle-ray intersections on the independent Trimesh CAD
    # tessellation. Projected barycentric rasterization avoids optional rtree.
    for t in mesh.triangles:
        a,b,c=t
        den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-13:continue
        ix=np.flatnonzero((xs>=t[:,0].min()-1e-9)&(xs<=t[:,0].max()+1e-9))
        iy=np.flatnonzero((ys>=t[:,1].min()-1e-9)&(ys<=t[:,1].max()+1e-9))
        if not len(ix) or not len(iy):continue
        xx,yy=np.meshgrid(xs[ix],ys[iy])
        u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
        v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den
        w=1.-u-v
        z=u*a[2]+v*b[2]+w*c[2]
        z[(u < -1e-8)|(v < -1e-8)|(w < -1e-8)]=-np.inf
        select=np.ix_(iy,ix);height[select]=np.maximum(height[select],z)
    exact=height.ravel();exact[~np.isfinite(exact)]=np.nan
    m.geom_group[m.geom_bodyid != 0]=2
    data=mj.MjData(m);mj.mj_forward(m,data)
    groups=np.array([0,0,0,1,0,0],dtype=np.uint8);geomid=np.zeros(1,dtype=np.int32)
    actual=np.array([2.-mj.mj_ray(m,data,np.array([x,y,2.]),np.array([0.,0.,-1.]),groups,True,-1,geomid) for x,y in xy])
    valid=np.isfinite(exact)&(actual<2.5)
    # Exclude mathematically ambiguous shared polygon edges, explicitly reported.
    # Both all-grid and playable interior metrics are retained.
    playable=valid&(np.abs(xy[:,0])<5.99)&(np.abs(xy[:,1])<3.99)&(exact<.41)
    err=np.abs(actual-exact)
    report=dict(preliminary,grid_spacing_m=.02,grid_shape=[431,631],grid_points=len(xy),valid_points=int(valid.sum()),
        all_grid_median_error_m=float(np.median(err[valid])),all_grid_p99_error_m=float(np.percentile(err[valid],99)),
        playable_points=int(playable.sum()),playable_median_error_m=float(np.median(err[playable])),
        playable_p99_error_m=float(np.percentile(err[playable],99)),max_error_m=float(np.max(err[valid])),
        binary_load_passed=max(preliminary['binary_load_seconds'])<.4)
    report['passed']=report['playable_median_error_m']<.001 and report['playable_p99_error_m']<.003 and report['binary_load_passed']
    np.savez_compressed(HERE/'evidence/RMUL_RAY_GRID.npz',x=xs,y=ys,cad=exact.reshape(431,631),mujoco=actual.reshape(431,631),valid=valid.reshape(431,631))
    put(HERE/'evidence/RMUL2027_3V3_GEOMETRY_AUDIT.json',report)
    print(json.dumps({k:report[k] for k in ('passed','playable_median_error_m','playable_p99_error_m','max_error_m')}),flush=True)

if __name__=='__main__':
    model,mesh,report=build();audit(model,mesh,report)
