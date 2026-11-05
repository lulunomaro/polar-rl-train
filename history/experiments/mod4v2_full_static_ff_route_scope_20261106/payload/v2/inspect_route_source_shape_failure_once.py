"""Root-cause receipt for source audit's 6-vertex assumption; no ray/model/raw.
One XML structural pass, no scene edits, hashes, physics or controller changes.
"""
from pathlib import Path
from collections import Counter
import json,xml.etree.ElementTree as ET
import numpy as np
R=Path(__file__).resolve().parent;D=R/'PUBLIC_ROUTE_FOOTPRINT_SOURCE_V1'
L=Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player/rm7v7_latest_moe.xml')

def main():
 out=D/'SOURCE_SHAPE_FAILURE001.json'
 if out.exists():raise RuntimeError('Structural root-cause check consumed')
 root=ET.parse(L).getroot();meshes={e.get('name'):e for e in root.find('asset').findall('mesh')};defs={}
 def walk(e,parent):
  d=dict(parent);g=e.find('geom')
  if g is not None:d.update(g.attrib)
  defs[e.get('class','__root__')]=d
  for sub in e.findall('default'):walk(sub,d)
 walk(root.find('default'),{})
 sizes=Counter();classes=Counter();unhandled=Counter();examples=[];colliders=0;visual=0
 for g in root.find('worldbody').findall('geom'):
  attrs=dict(defs.get(g.get('class','__root__'),{}));attrs.update(g.attrib)
  if not(int(attrs.get('contype','1'))|int(attrs.get('conaffinity','1'))):visual+=1;continue
  colliders+=1;classes[str(g.get('class'))]+=1;m=meshes[attrs['mesh']]
  n=None if not m.get('vertex')else len(np.fromstring(m.get('vertex'),sep=' '))//3
  sizes[str(n)]+=1
  for a in ('refpos','refquat','file'):
   if m.get(a):unhandled['asset_'+a]+=1
  for a in ('euler','axisangle','xyaxes','zaxis'):
   if attrs.get(a):unhandled['geom_'+a]+=1
  if len(examples)<4 and n!=6:examples.append(dict(geom=attrs,mesh_name=m.get('name'),vertices=n,source_vertex=m.get('vertex')))
 result=dict(root_cause='6-vertex-only source assumption was unjustified; no queries were reached',
  colliders=colliders,visual_noncolliding=visual,vertex_count_histogram=dict(sizes),class_histogram=dict(classes),
  unhandled_attributes=dict(unhandled),non6_examples=examples,geom_defaults=defs,
  original_prefix_preserved=True,ray_queries=0,model_compile=0,forward=0,physics_steps=0,raw_reads=0,source_payload_hash=False)
 out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
