"""Static triangle/collider comparison. No MuJoCo import, compile, or time APIs.
Compares real USD point arrays transformed into body coordinates with referenced STL.
Canonical MuJoCo mesh PCA frames/sizes are not themselves physical geometry identity.
"""
from pathlib import Path
import json, hashlib, struct, traceback, xml.etree.ElementTree as ET
import numpy as np
from pxr import Usd, UsdGeom
from scipy.spatial import cKDTree

HERE=Path(__file__).resolve().parent
BASE=Path(r'F:\RMPOLAR-RL\traditional_control_20261101\model\mod4_400N.xml')
USD=Path(r'F:\RMPOLAR-RL\mod4_usd_scut_fudan_20261101\candidates\v1\assets\robot.usd')
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def rot(q):
    w,x,y,z=np.array(q,float)/np.linalg.norm(q)
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)], [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)], [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def sorted_faces(f):
    f=np.sort(np.asarray(f,dtype=np.int64),axis=1)
    return f[np.lexsort((f[:,2],f[:,1],f[:,0]))]

def main():
    out=HERE/'GEOMETRY_EQUIVALENCE.json';assert not out.exists()
    source=load(HERE/'SOURCE_AUDIT_DATA.json');o=source['old_compile'];us=source['usd'];a=load(HERE/'ALIGNMENT_MEASUREMENTS.json')
    stage=Usd.Stage.Open(str(USD));root=ET.parse(BASE).getroot();meshmap={x.get('name'):x for x in root.findall('asset/mesh')}
    rows=[];primitives=[];collider_type_changes=[]
    for r in a['geometry_mapping']:
        n=r['usd_geometry'];on=r['old_mjcf_geometry'];ug=us['geometry'][n];og=o['geometry'][on]
        p=stage.GetPrimAtPath(ug['path']);M=np.asarray(UsdGeom.Xformable(p).GetLocalTransformation(),float)
        if ug['type']!='Mesh':
            scales=np.linalg.norm(M[:3,:3],axis=1);R=(M[:3,:3]/scales[:,None]).T
            attrs=ug['attrs'];size=None
            if ug['type']=='Cube':size=np.array([attrs['size']/2]*3)*scales
            if ug['type'] in ['Cylinder','Capsule']:size=np.array([attrs['radius'],attrs['height']/2,0])
            if ug['type']=='Sphere':size=np.array([attrs['radius'],0,0])
            oldR=rot(og['quat_wxyz'])
            axiserr=float(np.max(np.abs(np.outer(R[:,2],R[:,2])-np.outer(oldR[:,2],oldR[:,2])))) if ug['type'] in ['Cylinder','Capsule'] else float(np.max(np.abs(R-oldR)))
            primitives.append({'USD_geometry':n,'old_MJCF_geometry':on,'guide':r['usd_body'].startswith('guide_roller'),'body':r['usd_body'],'type':ug['type'],'USD_body_local_center_m':M[3,:3].tolist(),'old_body_local_center_m':og['position_m'],
                               'center_max_error_m':float(np.max(np.abs(M[3,:3]-og['position_m']))),'axis_or_rotation_max_error':axiserr,'USD_shape_size':size.tolist(),'old_shape_size':og['size'],'size_max_error_m':float(np.max(np.abs(size-og['size'])))})
            continue
        el=root.find(".//geom[@name='%s']"%on)
        if el.get('mesh') is None:
            points=np.asarray(p.GetAttribute('points').Get(),float);body_points=points@M[:3,:3]+M[3,:3]
            collider_type_changes.append({'USD_geometry':n,'old_MJCF_geometry':on,'old_MJCF_type':el.get('type'),'USD_type':ug['type'],'USD_approximation':p.GetAttribute('physics:approximation').Get(),'USD_body_min_m':body_points.min(axis=0).tolist(),'USD_body_max_m':body_points.max(axis=0).tolist(),'old_MJCF_size':og['size'],'action':'Actual USD mesh extracted in revision mod4v1_usd_source_aligned.xml'})
            continue
        asset=meshmap[el.get('mesh')];path=BASE.parent/'assets'/asset.get('file')
        raw=path.read_bytes();count=struct.unpack_from('<I',raw,80)[0]
        assert len(raw)==84+50*count,(path,len(raw),count)
        dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')])
        tri=np.frombuffer(raw,dtype=dtype,count=count,offset=84)['vertices'].astype(float)
        scale=np.fromstring(asset.get('scale','1 1 1'),sep=' ');gpos=np.fromstring(el.get('pos','0 0 0'),sep=' ');gR=rot(np.fromstring(el.get('quat','1 0 0 0'),sep=' '))
        tri=(tri*scale)@gR.T+gpos
        points=np.asarray(p.GetAttribute('points').Get(),float);counts=np.asarray(p.GetAttribute('faceVertexCounts').Get(),int);faces=np.asarray(p.GetAttribute('faceVertexIndices').Get(),int).reshape(-1,3)
        assert np.all(counts==3)
        world=points@M[:3,:3]+M[3,:3]
        distances,inds=cKDTree(world).query(tri.reshape(-1,3),workers=1)
        reverse,_=cKDTree(tri.reshape(-1,3)).query(world,workers=1)
        mapped=inds.reshape(-1,3)
        same_count=len(mapped)==len(faces)
        topo=bool(same_count and np.array_equal(sorted_faces(mapped),sorted_faces(faces)))
        rows.append({'USD_geometry':n,'mesh_file':str(path),'mesh_sha256':hashlib.sha256(raw).hexdigest(),'STL_triangle_count':count,'USD_triangle_count':len(faces),'USD_vertex_count':len(points),
                     'STL_to_USD_vertex_max_distance_m':float(np.max(distances)),'USD_to_STL_vertex_max_distance_m':float(np.max(reverse)),
                     'unoriented_triangle_topology_matches_after_nearest_vertex_mapping':topo})
    nonroller=[r for r in primitives if not r['guide']]
    summary={'mode':'SRC_ONLY_TRIANGLES_AND_PRIMITIVES','mesh_count':len(rows),'robot_primitive_count':len(primitives),'actual_USD_mesh_collision_replacing_old_primitives':collider_type_changes,'world_ground_excluded':True,
             'max_STL_to_USD_vertex_distance_m':max(r['STL_to_USD_vertex_max_distance_m'] for r in rows),
             'max_USD_to_STL_vertex_distance_m':max(r['USD_to_STL_vertex_max_distance_m'] for r in rows),
             'mesh_topology_matches':sum(r['unoriented_triangle_topology_matches_after_nearest_vertex_mapping'] for r in rows),
             'nonroller_primitive_count':len(nonroller),'nonroller_primitive_max_errors':{k:max(r[k] for r in nonroller) for k in ['center_max_error_m','axis_or_rotation_max_error','size_max_error_m']},
             'guide_size_changes':[{'USD_geometry':r['USD_geometry'],'old_MJCF_geometry':r['old_MJCF_geometry'],'old_size':r['old_shape_size'],'USD_actual_size':r['USD_shape_size'],'actual_USD_center_m':r['USD_body_local_center_m']} for r in primitives if r['guide']],
             'interpretation':'Nonzero old-compiler versus new-compiler mesh PCA metadata differences are evaluated by actual transformed triangles, not treated as geometry changes. Guide size differences are real and explicitly carried into primary candidate.'}
    out.write_text(json.dumps({'summary':summary,'meshes':rows,'primitives':primitives},ensure_ascii=False,indent=2),encoding='utf-8')
    (HERE/'GEOMETRY_EQUIVALENCE_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    try:main()
    except Exception:
        (HERE/'GEOMETRY_EQUIVALENCE_FAILURE_002.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
