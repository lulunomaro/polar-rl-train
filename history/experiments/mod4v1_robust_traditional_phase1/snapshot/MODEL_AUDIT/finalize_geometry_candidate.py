"""Carry actual USD tire convex-hull meshes into a new revision, preserving all evidence.
No simulation/state APIs. Previous candidate is intentionally retained as preliminary.
"""
from pathlib import Path
import json, hashlib, struct, difflib, traceback, xml.etree.ElementTree as ET
import numpy as np
from pxr import Usd, UsdGeom, UsdPhysics
from generate_mjcf import compile_only
HERE=Path(__file__).resolve().parent
USD=Path(r'F:\RMPOLAR-RL\mod4_usd_scut_fudan_20261101\candidates\v1\assets\robot.usd')
BASE=Path(r'F:\RMPOLAR-RL\traditional_control_20261101\model\mod4_400N.xml')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def meta(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def js(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def serial(v):
    if v is None or isinstance(v,(str,bool,int)):return v
    if isinstance(v,float):return v if np.isfinite(v) else str(v)
    if hasattr(v,'GetReal'):return [float(v.GetReal()),*map(float,v.GetImaginary())]
    try:return [serial(x) for x in v]
    except TypeError:return str(v)

def main():
    previous=HERE/'mod4v1_fullaligned_candidate.xml';assert sha(previous)=='6bbc56fdc6ae7b1447b8452d18ec37507ca95b0b0d6eb29ea1d14c6f2cc780bf'
    assert sha(USD)=='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
    path=HERE/'mod4v1_usd_source_aligned.xml';assert not path.exists()
    root=ET.parse(previous).getroot();stage=Usd.Stage.Open(str(USD));assets=root.find('asset')
    # Resolve old references relative to this XML, and use new local tire meshes.
    root.find('compiler').set('meshdir','.')
    for m in assets.findall('mesh'):m.set('file','../../traditional_control_20261101/model/assets/'+m.get('file'))
    meshdir=HERE/'usd_meshes';meshdir.mkdir(exist_ok=True);rows=[]
    for side in ['left','right']:
        name=side+'_tire';p=stage.GetPrimAtPath('/Robot/links/'+side+'_wheel/'+name);assert p.GetTypeName()=='Mesh'
        approx=p.GetAttribute('physics:approximation').Get();assert approx=='convexHull',(p.GetPath(),approx)
        vertices=np.asarray(p.GetAttribute('points').Get(),dtype=float);counts=np.asarray(p.GetAttribute('faceVertexCounts').Get(),int)
        indices=np.asarray(p.GetAttribute('faceVertexIndices').Get(),int)
        # USD tire uses polygon faces; fan triangulation preserves its vertices/hull.
        tris=[];offset=0
        for count in counts:
            face=indices[offset:offset+count];offset+=count
            for k in range(1,int(count)-1):tris.append([face[0],face[k],face[k+1]])
        assert offset==len(indices);faces=np.asarray(tris,dtype=int)
        M=np.asarray(UsdGeom.Xformable(p).GetLocalTransformation(),float);body_vertices=vertices@M[:3,:3]+M[3,:3]
        triangles=body_vertices[faces]; normals=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]);norms=np.linalg.norm(normals,axis=1)
        normals=normals/np.maximum(norms[:,None],1e-300)
        dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')]);data=np.zeros(len(triangles),dtype=dtype);data['normal']=normals;data['vertices']=triangles
        target=meshdir/(name+'.stl');assert not target.exists()
        target.write_bytes(b'MOD4v1 actual USD convexHull collision; SRC_ONLY'.ljust(80,b' ')+struct.pack('<I',len(data))+data.tobytes())
        meshname='usd_source_'+name;ET.SubElement(assets,'mesh',name=meshname,file='usd_meshes/'+name+'.stl')
        geom=root.find(".//geom[@name='%s']"%name);oldattrs=dict(geom.attrib)
        geom.set('type','mesh');geom.set('mesh',meshname)
        for key in ['size','quat','pos','fromto','euler','axisangle','xyaxes','zaxis']:geom.attrib.pop(key,None)
        rows.append({'USD_prim':str(p.GetPath()),'USD_approximation':approx,'USD_collision_attrs':{a.GetName():serial(a.Get()) for a in p.GetAttributes() if a.GetName().startswith(('physics:','physx')) and a.HasAuthoredValueOpinion()},'USD_vertices':len(vertices),'USD_triangles':len(faces),'USD_points_array_sha256':hashlib.sha256(vertices.astype('<f4').tobytes()).hexdigest(),'USD_faces_array_sha256':hashlib.sha256(indices.astype('<i4').tobytes()).hexdigest(),
            'USD_body_local_min_m':body_vertices.min(axis=0).tolist(),'USD_body_local_max_m':body_vertices.max(axis=0).tolist(),'extracted_STL':meta(target),'old_MJCF_geom':oldattrs,'new_MJCF_geom':dict(geom.attrib),'interpretation':'Both formats use the convex hull of these actual points; solver/contact algorithms remain engine-specific. Analytic rolling radius 0.0625m in old controller metadata is retained as a nominal wheel kinematic parameter, not the exact USD collision surface.'})
    ET.indent(root)
    text="<?xml version='1.0' encoding='utf-8'?>\n"+ET.tostring(root,encoding='unicode');path.write_bytes(text.encode('utf-8'))
    original=BASE.read_text(encoding='utf-8');(HERE/'mod4v1_usd_source_aligned.xml.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile=str(BASE),tofile=str(path))),encoding='utf-8')
    deriv=js(HERE/'DERIVATION_RECEIPT.json');targets={c['usd_body']:{'mass_kg':float(c['after_xml']['mass']),'com_m':np.fromstring(c['after_xml']['pos'],sep=' ').tolist(),'I':[[0.,0,0],[0,0,0],[0,0,0]]} for c in deriv['mci_changes']}
    for c in deriv['mci_changes']:
        n=c['usd_body'];v=np.fromstring(c['after_xml']['fullinertia'],sep=' ');targets[n]['I']=[[v[0],v[3],v[4]],[v[3],v[1],v[5]],[v[4],v[5],v[2]]]
    receipt={'mode':'SRC_ONLY','status':'ACTUAL_USD_GEOMETRY_REVISION_WITH_COMPILE_ONLY','primary':meta(path),'superseded_preliminary_candidate':meta(previous),'source_usd':meta(USD),'source_contract':meta(USD.parent/'import_contract.json'),'tire_meshes':rows,
             'critical_flags':deriv['critical_flags']+['CONTRACT_TIRE_GEOMETRY_TYPE_AND_RADIUS_STALE','CONTRACT_GUIDE_GEOMETRY_ORIGINS_STALE','VISUAL_MESH_PCA_METADATA_ENGINE_VERSION_DEPENDENT'],
             'damping_decision':deriv['guide_semantic_choices'],'compile':compile_only(path,targets),'source_files_unchanged':all(not r['exists'] or sha(r['path'])==r['sha256'] for r in js(HERE/'SOURCE_AUDIT_DATA.json')['source_files'])}
    dependencies=[]
    for m in root.findall('asset/mesh'):
        fp=(HERE/m.get('file')).resolve();assert fp.is_file();dependencies.append(dict(meta(fp),mesh_name=m.get('name'),xml_reference=m.get('file')))
    receipt['mesh_dependencies']={'meshdir':'.','count':len(dependencies),'all_exist':True,'files':dependencies}
    (HERE/'USD_SOURCE_DERIVATION_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    (HERE/'USD_TIRE_MESHES.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps({'primary':receipt['primary'],'compile':{k:v for k,v in receipt['compile'].items() if k not in ['body_com_inertia_max_errors','joint_table','actuator_table']},'tire_meshes':[{k:r[k] for k in ['USD_prim','USD_approximation','USD_vertices','USD_triangles','USD_body_local_min_m','USD_body_local_max_m','extracted_STL']} for r in rows],'sources_unchanged':receipt['source_files_unchanged']},indent=2))
if __name__=='__main__':
    try:main()
    except Exception:
        (HERE/'USD_SOURCE_DERIVATION_FAILURE_001.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
