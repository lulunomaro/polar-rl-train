"""Workspace-owned scene staging and 2 cm collision-derived elevation/ceiling maps."""
from nav_common import HERE, put, donor_imports
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import time
import numpy as np
import mujoco as mj

COURSES=('suite_rmul2027','suite_rmuc2027','suite_proving','step_20','oblique_20',
         'oblique_20_negative','curb_11','rm27_west_400','rm27_east_400','flat','rough_L9')
CACHE=HERE/'maps/wasd'

def _portable_meta(meta):
    for k in ('mjb_path','xml_path'):
        if k in meta and not Path(meta[k]).exists():
            cand=CACHE/Path(str(meta[k]).replace('\\','/')).name
            if cand.exists() or k=='mjb_path':meta[k]=str(cand)
    if 'mjb_path' in meta and not Path(meta['mjb_path']).exists() and 'xml_path' in meta and Path(meta['xml_path']).exists():
        tree=ET.parse(meta['xml_path']);root=tree.getroot()
        comp=root.find('compiler')
        if comp is not None and not Path(comp.get('meshdir','')).is_dir():
            assets=HERE.parents[2]/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/plant/MOD4v3_HW300N60_R3/mjcf/assets'
            if assets.is_dir():comp.set('meshdir',str(assets))
        for elem in root.findall('.//mesh'):
            f_attr=elem.get('file','')
            if 'assets/rmul2027/' in f_attr.replace('\\','/'):
                elem.set('file',str(HERE/'assets/rmul2027'/Path(f_attr.replace('\\','/')).name))
        tmp_xml=Path(meta['xml_path']).with_suffix('.compile.xml')
        tree.write(tmp_xml,encoding='utf-8',xml_declaration=True)
        mj.mj_saveModel(mj.MjModel.from_xml_path(str(tmp_xml)),meta['mjb_path'],None)
        tmp_xml.unlink(missing_ok=True)
    return meta

def stage_scene(course):
    CACHE.mkdir(parents=True,exist_ok=True)
    if course=='suite_rmul2027':
        return _portable_meta(json.loads((CACHE/'rmul2027_3v3_stiff_v1.json').read_text(encoding='utf-8')))
    manifest=CACHE/(course+'.json')
    if manifest.exists():
        old=_portable_meta(json.loads(manifest.read_text(encoding='utf-8')))
        if old.get('collision_version')==2 and Path(old['mjb_path']).exists():return old
    donor_imports()
    import play_manual_fsm_wasd as donor
    donor.HERE=HERE  # Redirect builder caches in memory; never edit the donor.
    donor.reference.legacy.maps.CACHE_DIR=CACHE
    meta=donor.build_player_scene('suite_serial','17° 坡道与碎石') if course=='serial_17' else donor.build_player_scene(course)
    tree=ET.parse(meta['xml_path']);root=tree.getroot()
    terrain_geoms=list(root.findall('worldbody/geom'))
    for body in root.findall('worldbody/body'):
        if body.find('.//joint') is None and body.find('.//freejoint') is None:
            terrain_geoms.extend(body.iter('geom'))
    for g in terrain_geoms:
        if g.get('contype','1')!='0':
            g.set('solref','0.0012 1');g.set('friction','0.9 0.005 0.0001')
            g.set('contype','1');g.set('conaffinity','3');g.set('group','3')
            rgba=list(map(float,g.get('rgba','.3 .4 .5 1').split()))
            if rgba[3]==0:rgba[3]=.0001
            g.set('rgba',' '.join(map(str,rgba)))
    filename='rmuc2027_stiff_v1' if course=='suite_rmuc2027' else course+'_stiff_v1'
    xml=CACHE/(filename+'.xml');tree.write(xml,encoding='utf-8',xml_declaration=True)
    model=mj.MjModel.from_xml_path(str(xml));binary=xml.with_suffix('.mjb')
    mj.mj_saveModel(model,str(binary),None)
    meta={key:meta[key] for key in ('spawns','hide_group5') if key in meta}
    meta.update(xml_path=str(xml),mjb_path=str(binary),course=course,collision_version=2)
    put(manifest,meta)
    return meta

def extent(course):
    if course=='suite_rmul2027':return (-6.3,6.3,-4.3,4.3)
    if course=='suite_rmuc2027':return (-25.3,2.9,-12.6,2.7)
    if course=='suite_proving':return (-3.,19.,-8.,8.)
    if course.startswith('rm27_'):return (-2.,7.,-2.,2.)
    if course in ('flat','rough_L9'):return (-10.,14.,-4.,4.)
    return (-3.,9.,-3.,3.)

def build_elevation(course):
    out=HERE/'maps/elevation'/f'{course}.npz';out.parent.mkdir(parents=True,exist_ok=True)
    meta=stage_scene(course)
    m=mj.MjModel.from_binary_path(meta['mjb_path'])
    for g in range(m.ngeom):
        m.geom_group[g]=3 if m.body_weldid[m.geom_bodyid[g]]==0 and (m.geom_contype[g] or m.geom_conaffinity[g]) else 2
        if m.geom_group[g]==3 and m.geom_rgba[g,3]==0:m.geom_rgba[g,3]=.0001
    d=mj.MjData(m);mj.mj_forward(m,d)
    bounds=extent(course);res=.02
    x=np.arange(bounds[0],bounds[1]+res*.1,res);y=np.arange(bounds[2],bounds[3]+res*.1,res)
    height=np.full((len(y),len(x)),np.nan,np.float32);ceiling=np.full_like(height,np.inf)
    groups=np.array([0,0,0,1,0,0],np.uint8);gid=np.zeros(1,np.int32)
    ray=np.array([0.,0.,-1.]);p=np.zeros(3);p[2]=5.
    start=time.perf_counter()
    for iy,yy in enumerate(y):
        for ix,xx in enumerate(x):
            p[:]=xx,yy,5.
            dist=mj.mj_ray(m,d,p,ray,groups,True,-1,gid)
            if dist<0:continue
            top=5.-dist;first=int(gid[0]);height[iy,ix]=top
            # Only thin overhead solids require a second supporting layer.
            if m.geom_type[first]==mj.mjtGeom.mjGEOM_BOX:
                half=m.geom_size[first,2]
                if half<.045 and top> .13:
                    bottom=m.geom_pos[first,2]-half
                    p[2]=bottom-.0001
                    below=mj.mj_ray(m,d,p,ray,groups,True,-1,gid)
                    floor=p[2]-below if below>=0 else np.nan
                    if np.isfinite(floor) and bottom-floor>.12:
                        height[iy,ix]=floor;ceiling[iy,ix]=bottom-floor
            elif course=='suite_rmul2027' and first>=0:
                # CAD canopy location is measured directly from its underside faces.
                if 2.324<abs(xx)<2.676 and 3.059<abs(yy)<3.861 and top>.24:
                    height[iy,ix]=.0005;ceiling[iy,ix]=.2495
            if course=='suite_rmuc2027' and 'roof' in (m.geom(first).name or ''):
                p[2]=top-.0001
                exit_distance=mj.mj_ray(m,d,p,ray,groups,True,-1,gid)
                if exit_distance>=0 and int(gid[0])==first:
                    underside=p[2]-exit_distance;p[2]=underside-.0001
                    normal=np.zeros(3)
                    lower=mj.mj_ray(m,d,p,ray,groups,True,-1,gid,normal)
                    if lower>=0 and normal[2]>.3:
                        floor=p[2]-lower
                        if underside-floor>.10:height[iy,ix]=floor;ceiling[iy,ix]=underside-floor
        if iy%150==0:print(course,iy,'/',len(y),flush=True)
    valid=np.isfinite(height)
    dy,dx=np.gradient(np.nan_to_num(height,nan=0.),res)
    diffx=np.abs(np.diff(height,axis=1,prepend=height[:,:1]));diffy=np.abs(np.diff(height,axis=0,prepend=height[:1]))
    dh=np.maximum(diffx,diffy)
    semantic=np.zeros_like(height,dtype=np.uint8)
    semantic[(np.hypot(dx,dy)>.04)&(dh<.075)]=1 # ramp/rough
    semantic[(dh>=.08)&(dh<=.255)]=2
    semantic[(dh>=.26)|~valid]=3
    semantic[ceiling<.36]=4
    np.savez_compressed(out,x=x,y=y,height=height,ceiling=ceiling,semantic=semantic,valid=valid,
        resolution=res,course=course,coordinate_reference='robot_base_center_horizontal')
    put(HERE/'evidence'/f'MAP_{course}.json',dict(course=course,shape=list(height.shape),resolution_m=res,
        elapsed_s=time.perf_counter()-start,finite_points=int(valid.sum()),
        semantic_counts={str(k):int((semantic==k).sum()) for k in range(5)},meta=meta))
    print('SAVED',out.name,flush=True)
    return out

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--course',nargs='*',default=list(COURSES));args=parser.parse_args()
    for course in args.course:build_elevation(course)
