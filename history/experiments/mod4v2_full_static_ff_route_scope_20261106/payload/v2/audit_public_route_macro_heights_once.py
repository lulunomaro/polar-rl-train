"""ONE source-only MACRO public-plan tire-strip height question after 3/3 freeze.
Not a contact/microgap probe: no simulator/model/robot state/raw/control input.
Each prism's upper convex envelope uses source vertices; no fake floor/hole fill.
"""
from pathlib import Path
import itertools,json,xml.etree.ElementTree as ET
import numpy as np
R=Path(__file__).resolve().parent;D=R/'PUBLIC_ROUTE_FOOTPRINT_SOURCE_V1'
L=Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player')

def main():
 D.mkdir(exist_ok=False)
 pre=dict(question='Does public flat_run centerline also put BOTH nominal tire strips on equal-height CAD?',
  source=str(L/'rm7v7_latest_moe.xml'),source_XML_passes=1,source_payload_hash=False,
  nominal_root_x_m=[-9.,-8.,-7.5,-5.5],root_y_m=-1.,nominal_wheel_root_x_m=-.034202394678846726,
  half_track_m=.2188,half_tire_width_m=.01,point_queries_planned=24,
  physics_steps=0,model_compile=0,MjData=0,forward=0,SDK_import=False,raw_reads=0,
  use='private source/plan suitability audit only;not feedback,map rewrite,new control mechanism or qualification',
  limits='nominal heading0 tire-strip points,not actual trajectory/full swept vehicle/force or contact-gap test')
 (D/'PREEXEC.json').write_text(json.dumps(pre,indent=2),encoding='utf-8')
 route=next(v for v in json.loads((L/'routes.json').read_text(encoding='utf-8'))if v['id']=='flat_run')
 assert route['waypoints_m'][0][:2]==[-9.,-1.]and route['waypoints_m'][-1][:2]==[-5.5,-1.]
 tree=ET.parse(L/'rm7v7_latest_moe.xml');root=tree.getroot();meshes={e.get('name'):e for e in root.find('asset').findall('mesh')}
 world=root.find('worldbody');assert all(b.get('name')=='chassis'for b in world.findall('body'))
 records=[]
 for g in world.findall('geom'):
  if not(int(g.get('contype','1'))|int(g.get('conaffinity','1'))):continue
  if g.get('type')!='mesh':raise ValueError('Unexpected static source collider')
  m=meshes[g.get('mesh')]
  if not m.get('vertex')or m.get('file')or any(k in m.attrib for k in ('refpos','refquat')):raise ValueError('Not direct inline prism source')
  if any(k in g.attrib for k in ('euler','axisangle','xyaxes','zaxis','class')):raise ValueError('Unexpected source transform/default class')
  v=np.fromstring(m.get('vertex'),sep=' ').reshape(-1,3)
  if len(v)!=6:raise ValueError('Not 6-vertex convex triangle prism')
  v*=np.fromstring(m.get('scale','1 1 1'),sep=' ')
  q=np.fromstring(g.get('quat','1 0 0 0'),sep=' ')
  if len(q)!=4 or abs(np.linalg.norm(q)-1)>1e-8:raise ValueError('Bad source quaternion')
  w,x,y,z=q;rot=np.array([[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],
   [2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],
   [2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]])
  v=v@rot.T+np.fromstring(g.get('pos','0 0 0'),sep=' ')
  records.append((g.get('name'),v))
 if len(records)!=47282:raise ValueError('Source collider coverage differs from runtime')
 verts=np.array([v for _,v in records]);lo=verts[:,:,:2].min(axis=1);hi=verts[:,:,:2].max(axis=1)
 combinations=list(itertools.combinations(range(6),3));queries=0
 def top(x,y):
  nonlocal queries
  queries+=1;point=np.array([x,y]);ids=np.flatnonzero(np.all(lo<=point+1e-10,axis=1)&np.all(hi>=point-1e-10,axis=1));best=None;hit=None
  # Max z in a convex 6-vertex prism at xy is attained by a <=3-vertex
  # convex combination. Enumerate source triplets, including actual upper faces.
  for i in ids:
   for tri in combinations:
    a,b,c=verts[i,list(tri)];M=np.column_stack((b[:2]-a[:2],c[:2]-a[:2]));det=float(np.linalg.det(M))
    if abs(det)<1e-13:continue
    u,v=np.linalg.solve(M,point-a[:2])
    if min(u,v,1-u-v)<-1e-10:continue
    h=float(a[2]+u*(b[2]-a[2])+v*(c[2]-a[2]))
    if best is None or h>best:best=h;hit=records[int(i)][0]
  return dict(x_m=x,y_m=y,top_z_m=best,top_source_geom=hit,candidate_prisms=len(ids),unknown=best is None)
 rows=[]
 for x in pre['nominal_root_x_m']:
  sides=[]
  for side,dy in [('left',.2188),('right',-.2188)]:
   points=[top(x+pre['nominal_wheel_root_x_m'],-1+dy+offset)for offset in(-.01,0.,.01)]
   sides.append(dict(side=side,strip_points=points))
  lc,rc=[v['strip_points'][1]['top_z_m']for v in sides]
  rows.append(dict(public_root_x_m=x,sides=sides,left_minus_right_center_top_m=None if lc is None or rc is None else lc-rc))
 result=dict(status='SOURCE_ONLY_PUBLIC_NOMINAL_TIRE_STRIP_MACRO_HEIGHTS',protocol=pre,route=route,
  actual_collision_prisms=len(records),actual_point_queries=queries,rows=rows,
  limits=['Source convex-prism geometry heights,not native contact physics,normal forces or micron gaps',
   'Public nominal x-offset/width only; no actual robot root/contact/raw read or actor feedback',
   'No route/gates/model rewrite; old failed screens and 3/3 mechanism freeze remain'])
 assert queries==24
 (D/'RESULT.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
