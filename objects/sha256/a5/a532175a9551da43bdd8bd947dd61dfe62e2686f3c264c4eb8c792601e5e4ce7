"""Create portable map/route previews from the packaged collision triangles."""
from pathlib import Path
import json
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.font_manager import FontProperties,fontManager
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ROOT=Path(__file__).resolve().parents[1]
font=Path('C:/Windows/Fonts/msyh.ttc')
if font.exists():
    fontManager.addfont(str(font));plt.rcParams['font.family']=FontProperties(fname=str(font)).get_name()
plt.rcParams['axes.unicode_minus']=False
raw=np.load(ROOT/'data/arena_collision.npz');mesh=trimesh.Trimesh(raw['vertices'],raw['faces'],process=False)
routes=json.loads((ROOT/'data/routes.json').read_text(encoding='utf8'))
def topdown():
    tri=mesh.triangles;keep=mesh.face_normals[:,2]>.05;tri=tri[keep]
    heights=tri[:,:,2].mean(1);order=np.argsort(heights);tri=tri[order];heights=heights[order]
    fig,ax=plt.subplots(figsize=(17,10),layout='constrained')
    pc=PolyCollection(tri[:,:,:2],array=heights,cmap='terrain',edgecolors='none',clim=(-.25,.85))
    ax.add_collection(pc);ax.autoscale();ax.set_aspect('equal');ax.grid(alpha=.15)
    for i,route in enumerate(routes):
        points=np.array(route['waypoints_m']);ax.plot(points[:,0],points[:,1],'-o',color='#172234',lw=1.3,ms=3)
        ax.text(points[0,0],points[0,1],str(i+1),fontsize=8,weight='bold',color='black',bbox=dict(facecolor='white',alpha=.85,pad=1,edgecolor='none'))
    text='\n'.join(f'{i+1:02}  {r["name_zh"]}' for i,r in enumerate(routes))
    ax.text(1.02,.95,text,transform=ax.transAxes,va='top',fontsize=11,linespacing=1.7)
    ax.set_title('RMUC2026 场地碰撞地图与专项路线（每个环境包含全部场地地形）',fontsize=16)
    ax.set_xlabel('X / m');ax.set_ylabel('Y / m')
    fig.savefig(ROOT/'previews/map_routes.png',dpi=140);plt.close(fig)

def crop(bounds):
    out=mesh.copy()
    for p,n in [([bounds[0],0,0],[1,0,0]),([bounds[1],0,0],[-1,0,0]),([0,bounds[2],0],[0,1,0]),([0,bounds[3],0],[0,-1,0])]:
        out=out.slice_plane(p,n,cap=False)
    return out

def detail_panels():
    fig=plt.figure(figsize=(16,12),layout='constrained')
    specs=[('中心岛二级台面及凸坎',[-4.3,4.3,-5.4,5.4],-65,35),
           ('公路狗洞：保留顶板与侧面',[.0,2.,-6.5,-5.4],-100,8),
           ('飞坡与沟壑',[-2.,1.4,-7.35,-6.5],-70,20),
           ('起伏路段原始波形',[6.1,8.9,5.55,7.35],-75,25)]
    for i,(title,bounds,az,el) in enumerate(specs):
        ax=fig.add_subplot(2,2,i+1,projection='3d');m=crop(bounds)
        z=m.triangles_center[:,2];colors=plt.get_cmap('terrain')(np.clip((z+.22)/1.1,0,1))
        shade=np.clip(m.face_normals@np.array([.2,-.4,.8])+.6,.35,1.)
        colors[:,:3]*=shade[:,None]
        ax.add_collection3d(Poly3DCollection(m.triangles,facecolors=colors,edgecolors='none',zsort='average'))
        lo,hi=m.bounds;ax.set_xlim(bounds[:2]);ax.set_ylim(bounds[2:]);ax.set_zlim(max(-.3,lo[2]),min(1.,hi[2]+.06))
        ax.set_box_aspect([bounds[1]-bounds[0],bounds[3]-bounds[2],max(.45,(hi[2]-lo[2])*1.5)])
        ax.view_init(elev=el,azim=az);ax.set_title(title,fontsize=13)
        ax.set_xlabel('X / m');ax.set_ylabel('Y / m');ax.set_zlabel('Z / m')
    fig.savefig(ROOT/'previews/terrain_details.png',dpi=140);plt.close(fig)

if __name__=='__main__':topdown();detail_panels()
