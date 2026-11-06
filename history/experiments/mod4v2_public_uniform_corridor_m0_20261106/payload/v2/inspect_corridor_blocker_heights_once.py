"""One bounded source-structure question: are full-Y blockers above a finite robot?"""
from pathlib import Path
import json,xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial import ConvexHull
R=Path(__file__).resolve().parent;D=R/'PUBLIC_UNIFORM_CORRIDOR_V1/HEIGHT_INSPECT001'
def main():
 result=json.loads((R/'PUBLIC_UNIFORM_CORRIDOR_V1/RESULT.json').read_text(encoding='utf-8'));fy=result['source_floor_y_interval_m']
 names=[x['source_geom']for x in result['obstacle_y_intervals']if x['y_range_m'][0]<=fy[0]+1e-8 and x['y_range_m'][1]>=fy[1]-1e-8][:2]
 if not names:raise ValueError('No full-Y source blocker; no additional source parse')
 D.mkdir(exist_ok=False);(D/'PREEXEC.json').write_text(json.dumps(dict(source_names=names,source_parse_passes_planned=1,models=0,physics=0,raw_reads=0,LP=0,control_changed=False)),encoding='utf-8')
 root=ET.parse(result['protocol']['source']).getroot();assets={m.get('name'):m for m in root.find('asset').findall('mesh')};wanted=set(names+['rm_col_3553']);pts={}
 for g in root.find('worldbody').findall('geom'):
  if g.get('name')not in wanted:continue
  m=assets[g.get('mesh')];v=np.fromstring(m.get('vertex'),sep=' ').reshape(-1,3)*np.fromstring(m.get('scale','1 1 1'),sep=' ')
  w,x,y,z=np.fromstring(g.get('quat','1 0 0 0'),sep=' ');rot=np.array([[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],[2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],[2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]])
  pts[g.get('name')]=v@rot.T+np.fromstring(g.get('pos','0 0 0'),sep=' ')
 E=ConvexHull(pts['rm_col_3553']).equations;up=E[E[:,2]>1e-10];xy=np.array([-9.034202394678847,-1.2188]);f=up[np.argmin(-(up[:,:2]@xy+up[:,3])/up[:,2])];abc=-f[[0,1,3]]/f[2]
 rows=[]
 for name in names:
  v=pts[name];h=v[:,2]-v[:,:2]@abc[:2]-abc[2];rows.append(dict(source_geom=name,world_bbox_min_m=v.min(axis=0).tolist(),world_bbox_max_m=v.max(axis=0).tolist(),height_above_reference_plane_vertex_range_m=[float(h.min()),float(h.max())]))
 answer=dict(source_parse_passes=1,selected_blocker_count=len(names),floor_hulls=1,LP_calls=0,models=0,physics_steps=0,raw_reads=0,source_floor_plane_z_ax_by_c=abc.tolist(),blockers=rows,limits='Source vertex extents,not actual robot trajectory/contact or new route pass;original infinite-column NO_CORRIDOR remains true')
 (D/'RESULT.json').write_text(json.dumps(answer,indent=2),encoding='utf-8');print(json.dumps(answer,indent=2))
if __name__=='__main__':main()
