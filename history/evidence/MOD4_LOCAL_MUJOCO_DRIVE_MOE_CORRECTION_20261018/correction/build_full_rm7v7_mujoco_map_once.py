"""Convert the supplied whole-field terrain to MuJoCo without one arena hull.

Static non-convex CAD contact surfaces are unions of convex planar patches or
individual triangular prisms. Thin 20um inward/outward skins retain overhangs;
there is no infinite z=0 plane or heightfield that fills tunnels or trenches.
"""
from pathlib import Path
import copy, json, time, hashlib, traceback
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
from scipy.spatial import ConvexHull
from pxr import Usd, UsdGeom

B=Path(__file__).resolve().parent;W=B.parent
D=W/'MOD4_LOCAL_MUJOCO_DRIVE_20261008';A=W/'rmuc2026_training'
OUT=D/'rm7v7_assets_20261018';XML=D/'rm7v7_latest_moe.xml'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def numbers(x):return ' '.join(f'{float(v):.10g}' for v in np.asarray(x).ravel())
def obj(path,v,f):
    with path.open('x',encoding='ascii') as out:
        for p in v:out.write('v '+numbers(p)+'\n')
        for face in f:out.write('f '+' '.join(str(int(i)+1) for i in face)+'\n')
def main():
    assert not OUT.exists() and not XML.exists()
    OUT.mkdir()
    root=ET.parse(D/'playground.xml').getroot()
    root.set('model','MOD4 latest MoE - supplied RMUC2026 full 7v7 terrain')
    world=root.find('worldbody');robot=world.find("body[@name='chassis']")
    assert robot is not None
    original_robot=ET.tostring(robot)
    for child in list(world):
        if child.tag!='body' or child.get('name')!='chassis':world.remove(child)
    # Camera/light are presentation only; keep the robot's entire tree unchanged.
    ET.SubElement(world,'light',pos='0 0 12',dir='0 0 -1',diffuse='.8 .8 .8',directional='true')
    ET.SubElement(world,'light',pos='-10 -6 7',dir='1 1 -1',diffuse='.5 .5 .5',directional='true')
    asset=root.find('asset');assert asset is not None
    for h in list(asset.findall('hfield')):asset.remove(h)
    raw=np.load(A/'data/arena_visual.npz');v=raw['vertices'];f=raw['faces']
    stage=Usd.Stage.Open(str(A/'assets/arena_visual.usdc'))
    prim=next(p for p in stage.Traverse() if p.IsA(UsdGeom.Mesh))
    pv=UsdGeom.PrimvarsAPI(prim).GetPrimvar('displayColor')
    colors=np.asarray(pv.Get(),dtype=float)
    assert colors.shape==(len(f),3),colors.shape
    unique,groups=np.unique(np.round(colors,5),axis=0,return_inverse=True)
    for i,c in enumerate(unique):
        faces=f[groups==i];ids,new=np.unique(faces.ravel(),return_inverse=True)
        name=f'rm_visual_{i}';p=OUT/f'{name}.obj';obj(p,v[ids],new.reshape(-1,3))
        ET.SubElement(asset,'mesh',name=name,file=str(p))
        ET.SubElement(world,'geom',name=name,type='mesh',mesh=name,rgba=numbers([*c,1]),
            contype='0',conaffinity='0',group='0',density='0')
    audit=json.loads((A/'reports/collision_audit.json').read_text())
    count=0;source_faces=0;patches=0;fallback=0;convex=0;maxdev=0.
    EPS=2e-5
    def emit(vertices,label):
        nonlocal count
        name=f'rm_col_{count}'
        # Mesh vertices are world coordinates. Static meshes have no inertia.
        ET.SubElement(asset,'mesh',name=name,vertex=numbers(vertices),inertia='shell')
        ET.SubElement(world,'geom',name=name,type='mesh',mesh=name,contype='1',conaffinity='2',
            group='3',rgba='.3 .3 .3 0',friction='.9 .003 .0001',density='0',margin='0')
        count+=1
    for row in audit['parts']:
        if not row.get('collision'):continue
        p=W/'rmuc2026_work/processed'/f"part_{row['part']:03}.npz"
        d=np.load(p);mesh=trimesh.Trimesh(d['vertices'],d['faces'],process=True)
        mesh.update_faces(mesh.area_faces>1e-12);mesh.remove_unreferenced_vertices()
        source_faces+=len(mesh.faces)
        if mesh.is_convex:
            emit(mesh.vertices,'convex_part');convex+=1;continue
        covered=set()
        for facet in mesh.facets:
            ids=np.unique(mesh.faces[facet]);points=mesh.vertices[ids]
            normal=mesh.face_normals[facet[0]];origin=points.mean(0)
            _,_,vh=np.linalg.svd(points-origin,full_matrices=False)
            xy=(points-origin)@vh[:2].T
            try:area=ConvexHull(xy).volume
            except Exception:continue
            deviation=float(np.max(np.abs((points-origin)@normal)))
            source_area=float(mesh.area_faces[facet].sum())
            if abs(area-source_area)>max(1e-10,source_area*1e-5) or deviation>1e-6:continue
            emit(np.vstack((points+EPS*normal,points-EPS*normal)),'planar_convex_patch')
            covered.update(int(i) for i in facet);patches+=1;maxdev=max(maxdev,deviation)
        for i,face in enumerate(mesh.faces):
            if i in covered:continue
            points=mesh.vertices[face];normal=mesh.face_normals[i]
            emit(np.vstack((points+EPS*normal,points-EPS*normal)),'triangle_prism');fallback+=1
        print(json.dumps(dict(part=row['part'],static_geoms_so_far=count)),flush=True)
    assert ET.tostring(world.find("body[@name='chassis']"))==original_robot
    root.find('statistic').set('center','0 0 .5');root.find('statistic').set('extent','18')
    ET.ElementTree(root).write(XML,encoding='utf-8',xml_declaration=True)
    report=dict(epoch=time.time(),map=str(XML),map_SHA=H(XML),source_CAD=json.loads((A/'reports/source.json').read_text()),
        source_collision_mesh=dict(path=str(A/'data/arena_collision.npz'),bytes=(A/'data/arena_collision.npz').stat().st_size,SHA=H(A/'data/arena_collision.npz')),
        full_field_bounds=v[[np.argmin(v[:,0]),np.argmax(v[:,0])]].tolist(),
        field_bbox=[v.min(0).tolist(),v.max(0).tolist()],visual_faces=len(f),collision_source_faces=source_faces,
        static_convex_geoms=count,whole_convex_parts=convex,convex_planar_patches=patches,individual_triangle_prisms=fallback,
        contact_skin_halfthickness_m=EPS,maximum_patch_planarity_m=maxdev,
        original_robot_actuator_constraints_unchanged=True,no_extra_floor_plane=True,
        tunnels_overhangs_trenches_not_heightfield_filled=True,
        machinery_assemblies_omitted_in_existing_source=True,full_supplied_ground_assembly_not_a_schematic_road=True,
        collision_method_primary_source='https://mujoco.readthedocs.io/en/stable/computation/index.html')
    (B/'reports/FULL_RM7V7_MUJOCO_BUILD_ACTUAL.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':
    try:main()
    except BaseException:
        (B/f'reports/FULL_MAP_BUILD_ORIGINAL_ERROR_{time.time_ns()}.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
