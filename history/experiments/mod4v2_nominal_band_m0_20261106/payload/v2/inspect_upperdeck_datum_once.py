"""Bounded root-cause question for rejected published level, two source points only."""
from pathlib import Path
import json,xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial import ConvexHull
R=Path(__file__).resolve().parent;D=R/'PUBLIC_UPPERDECK_CORRIDOR_V1/DATUM_INSPECT001'
def main():
 prior=json.loads((R/'PUBLIC_UPPERDECK_CORRIDOR_V1/RESULT.json').read_text(encoding='utf-8'))
 if prior['status']!='NO_PUBLIC_ANCHOR_HORIZONTAL_SOURCE_FACE':raise ValueError('Unexpected first outcome')
 D.mkdir(exist_ok=False);(D/'PREEXEC.json').write_text(json.dumps(dict(points_xy_m=[[-1.5,0.],[0.,0.]],source_parse_passes_planned=1,SDK=False,models=0,physics=0,raw_reads=0,LP=0,old_queries_replayed=False)),encoding='utf-8')
 L=Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player');xml=ET.parse(L/'rm7v7_latest_moe.xml').getroot();assets={m.get('name'):m for m in xml.find('asset').findall('mesh')};points=[np.array([-1.5,0.]),np.array([0.,0.])];answers=[[],[]];hulls=0
 for g in xml.find('worldbody').findall('geom'):
  if not(int(g.get('contype','1'))|int(g.get('conaffinity','1'))):continue
  m=assets[g.get('mesh')];v=np.fromstring(m.get('vertex'),sep=' ').reshape(-1,3)*np.fromstring(m.get('scale','1 1 1'),sep=' ');w,x,y,z=np.fromstring(g.get('quat','1 0 0 0'),sep=' ')
  T=np.array([[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],[2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],[2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]])
  v=v@T.T+np.fromstring(g.get('pos','0 0 0'),sep=' ');lo=v.min(axis=0);hi=v.max(axis=0)
  hits=[i for i,p in enumerate(points)if np.all(p>=lo[:2]-1e-8)and np.all(p<=hi[:2]+1e-8)]
  if not hits:continue
  E=ConvexHull(v).equations;hulls+=1;up=E[E[:,2]>1e-10]
  if not len(up):continue
  for i in hits:
   p=points[i];zz=-(up[:,:2]@p+up[:,3])/up[:,2];j=int(np.argmin(zz));top=float(zz[j]);f=up[j];res=float(np.max(E[:,:3]@np.r_[p,top]+E[:,3]))
   if res>1e-8:continue
   answers[i].append(dict(source_geom=g.get('name'),top_z_m=top,top_minus_published_deck_z_m=top-.4000000059604645,plane_z_ax_by_c=(-f[[0,1,3]]/f[2]).tolist(),halfspace_max_residual_m=res))
 for rows in answers:rows.sort(key=lambda r:(abs(r['top_minus_published_deck_z_m']),r['source_geom']))
 result=dict(source_parse_passes=1,point_count=2,source_hulls=hulls,SDK=False,models=0,physics_steps=0,raw_reads=0,LP_calls=0,
  points=[dict(xy_m=p.tolist(),exact_source_point_surfaces=rows)for p,rows in zip(points,answers)],limits='Source datum diagnosis only;no alternate control/coordinate score search/physics qualification')
 (D/'RESULT.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
