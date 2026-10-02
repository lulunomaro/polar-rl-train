"""Bake the source USD visual meshes into a display-only MuJoCo scene.

No MuJoCo dynamics: body world poses come directly from the live Isaac simulation.
"""
from pathlib import Path
import hashlib
import json
import struct
import xml.etree.ElementTree as ET
import numpy as np
from pxr import Usd, UsdGeom, UsdPhysics

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'display'
OUT.mkdir(exist_ok=True);(OUT/'meshes').mkdir(exist_ok=True)
SOURCE=ROOT/'src_snapshot/robot.usd'
stage=Usd.Stage.Open(str(SOURCE));cache=UsdGeom.XformCache()
root=ET.Element('mujoco',model='MOD4 live Isaac poses - DISPLAY ONLY')
ET.SubElement(root,'compiler',angle='radian',meshdir='meshes')
ET.SubElement(root,'option',gravity='0 0 0')
visual=ET.SubElement(root,'visual');ET.SubElement(visual,'global',offwidth='1280',offheight='720')
ET.SubElement(visual,'rgba',haze='.85 .9 .95 1')
asset=ET.SubElement(root,'asset')
ET.SubElement(asset,'texture',name='floor_tex',type='2d',builtin='checker',rgb1='.20 .23 .27',rgb2='.34 .38 .42',width='512',height='512')
ET.SubElement(asset,'material',name='floor_mat',texture='floor_tex',texrepeat='20 20',texuniform='true',reflectance='.05')
world=ET.SubElement(root,'worldbody')
ET.SubElement(world,'geom',name='display_floor',type='plane',size='10 10 .01',material='floor_mat',contype='0',conaffinity='0')
ET.SubElement(world,'light',pos='0 0 4',dir='0 0 -1',directional='true',diffuse='.8 .8 .8')
ET.SubElement(world,'light',pos='3 -3 2',dir='-1 1 -1',directional='true',diffuse='.4 .4 .4')
records=[];triangles=0
for body in [p for p in stage.Traverse() if p.HasAPI(UsdPhysics.RigidBodyAPI)]:
    name=body.GetName();bm=cache.GetLocalToWorldTransform(body)
    pos=bm.ExtractTranslation();quat=bm.ExtractRotationQuat();qw=quat.GetReal();qi=quat.GetImaginary()
    node=ET.SubElement(world,'body',name=name,mocap='true',pos=' '.join(map(str,pos)),quat=' '.join(map(str,[qw,*qi])))
    for prim in Usd.PrimRange(body):
        if not prim.IsA(UsdGeom.Mesh):continue
        mesh=UsdGeom.Mesh(prim)
        if mesh.ComputeVisibility()==UsdGeom.Tokens.invisible or prim.HasAPI(UsdPhysics.CollisionAPI):continue
        points=np.asarray(mesh.GetPointsAttr().Get(),dtype=np.float64)
        transform=np.asarray(cache.GetLocalToWorldTransform(prim)*bm.GetInverse(),dtype=np.float64)
        local=np.c_[points,np.ones(len(points))]@transform
        local=local[:,:3]
        counts=mesh.GetFaceVertexCountsAttr().Get();indices=mesh.GetFaceVertexIndicesAttr().Get()
        faces=[];offset=0
        for count in counts:
            poly=indices[offset:offset+count];offset+=count
            for j in range(1,count-1):faces.append((poly[0],poly[j],poly[j+1]))
        verts=local[np.asarray(faces,dtype=np.int64)]
        normals=np.cross(verts[:,1]-verts[:,0],verts[:,2]-verts[:,0]);length=np.linalg.norm(normals,axis=1)
        valid=length>1e-15;verts=verts[valid];normals=normals[valid]/length[valid,None]
        data=np.zeros(len(verts),dtype=[('normal','<f4',(3,)),('vertex','<f4',(3,3)),('attribute','<u2')])
        data['normal']=normals;data['vertex']=verts
        key=f'visual_{len(records):03d}';file=OUT/'meshes'/f'{key}.stl'
        file.write_bytes(b'MOD4 source USD visual mesh'.ljust(80,b'\0')+struct.pack('<I',len(data))+data.tobytes())
        ET.SubElement(asset,'mesh',name=key,file=f'{key}.stl')
        color=mesh.GetDisplayColorAttr().Get();opacity=mesh.GetDisplayOpacityAttr().Get()
        rgba=[*(color[0] if color else (.5,.5,.5)),float(opacity[0] if opacity else 1.)]
        ET.SubElement(node,'geom',name=key,type='mesh',mesh=key,rgba=' '.join(map(str,rgba)),contype='0',conaffinity='0',density='0')
        records.append({'mesh':key,'usd_prim':str(prim.GetPath()),'body':name,'triangles':len(data)})
        triangles+=len(data)
ET.indent(root,space='  ');ET.ElementTree(root).write(OUT/'live_display.xml',encoding='utf8',xml_declaration=True)
audit={'source_usd_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'body_count':len(world.findall('body')),
       'visual_count':len(records),'triangles':triangles,'physics':'None. Display only; all live body poses from Isaac PhysX.',
       'meshes':records}
(OUT/'DISPLAY_SOURCE_AUDIT.json').write_text(json.dumps(audit,indent=2),encoding='utf8')
print({k:v for k,v in audit.items()if k!='meshes'})
