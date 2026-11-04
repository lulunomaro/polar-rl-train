"""Render actual MOD4v1 saved poses with enhanced contract collision geometry."""
from pathlib import Path
import argparse
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import hashlib
N=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--returned',type=Path,default=N/'reports/EVAL80_INFERENCE_FIX01_RETURNED.json')
parser.add_argument('--directory',type=Path,default=N/'evaluation80_inference_fix01');parser.add_argument('--prefix',default='actual80')
parser.add_argument('--times',type=float,nargs='+',default=[.02,.08,.14,.2,.3,.42])
parser.add_argument('--output-subdir',default='recorded_native')
args=parser.parse_args()
returned_raw=args.returned.read_bytes()
returned=json.loads(returned_raw)['files']
result=returned['evaluation/RESULT.json'];rows=returned['evaluation/ALL80.json']['first_episodes']
# evaluate.observe reads b.reward.robot.data (DataView), which already converts
# the native SDK xyzw tensors to wxyz before saving root AND body quaternions.
# The saved file convention therefore differs from the raw SDK convention.
saved_pose_order='wxyz'
data=np.load(args.directory/'selected_actual_poses.npz')
contract=json.loads(Path('F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/assets/import_contract.json').read_bytes())
names=result['body_names'];bodyids={n:i for i,n in enumerate(names)}
def rot(q):
    w,x,y,z=q
    return np.array([[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],
        [2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],
        [2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]])
out=args.directory/args.output_subdir;out.mkdir(exist_ok=True)
media=[]
for view,axes in [('side',(0,2)),('top',(0,1))]:
    fig,panels=plt.subplots(4,len(args.times),figsize=(17,10),layout='constrained',squeeze=False)
    for rowid,eid in enumerate(result['recorded_envs']):
        origins=result.get('environment_origins')
        origin=np.array(origins[eid] if origins else [(eid//9)*8.,(eid%9)*8.,0.])
        valid=np.flatnonzero(data['active'][:,rowid])
        for col,t in enumerate(args.times):
            idx=valid[min(len(valid)-1,max(0,round(t/.02)-1))]
            ax=panels[rowid,col]
            stair_key='terrain_vertices_'+str(eid)
            if stair_key in data:
                from matplotlib.collections import PolyCollection
                vertices=data[stair_key];faces=data['terrain_faces_'+str(eid)]
                near=(abs(vertices[:,:2])<1.).all(-1)
                triangles=vertices[faces[near[faces].all(-1)]]
                if view=='side':
                    centre=vertices[abs(vertices[:,1])<.055]
                    centre=centre[abs(centre[:,0])<1.]
                    centre=np.unique(centre[:,[0,2]],axis=0)
                    order=np.lexsort((centre[:,1],centre[:,0]));centre=centre[order]
                    ax.plot(centre[:,0],centre[:,1],color='#337eb0',linewidth=1.5)
                else:
                    pc=PolyCollection(triangles[:,:,[0,1]],array=triangles[:,:,2].mean(-1),
                        cmap='Blues',alpha=.35,edgecolors='none')
                    ax.add_collection(pc)
            for geom in contract['geometry'].values():
                if geom['visual'] or geom['body']not in bodyids:continue
                bid=bodyids[geom['body']]
                pos=data['body_pos'][idx,rowid,bid]-origin
                q=data['body_quat'][idx,rowid,bid]
                R=rot(q);Rlocal=rot(geom['quat_wxyz']);offset=np.array(geom['position_m'])
                size=np.array(geom['size']);kind=geom['type']
                if kind==6:
                    a=np.array([[x,y,z]for x in [-size[0],size[0]]for y in [-size[1],size[1]]for z in [-size[2],size[2]]])
                elif kind==5:
                    angle=np.linspace(0,2*np.pi,25)
                    a=np.array([[size[0]*np.cos(v),size[0]*np.sin(v),z]for z in [-size[1],size[1]]for v in angle])
                else:continue
                world=(a@Rlocal.T+offset)@R.T+pos
                p=world[:,axes]
                from scipy.spatial import ConvexHull
                if np.linalg.matrix_rank(p-p.mean(0))>=2:
                    hull=ConvexHull(p)
                    ax.add_patch(Polygon(p[hull.vertices],closed=True,alpha=.6,facecolor='#df953d'if 'wheel'in geom['body']else'#556c86',edgecolor='#29394a',linewidth=.35))
            if view=='side':
                if stair_key not in data:
                    ax.axhline(0,color='black',linewidth=.5)
                    ax.plot([-1,-.5,-.5,.5,.5,1],[.27,.27,0,0,.27,.27],color='#337eb0',linewidth=2)
                    ax.set_ylim(-.15,.8)
                else:
                    zmin=float(centre[:,1].min());ax.set_ylim(zmin-.1,zmin+.85)
                ax.set_ylabel('z m')
            else:
                ax.add_patch(Polygon([[-.5,-.5],[.5,-.5],[.5,.5],[-.5,.5]],fill=False,edgecolor='#337eb0',linewidth=2))
                ax.set_ylim(-.8,.8);ax.set_ylabel('y m')
            ax.set_xlim(-.8,.8);ax.set_aspect('equal');ax.grid(alpha=.15)
            seconds=float(data['tick'][idx])*.0025
            ax.set_title(f'env{eid} actual {seconds:.2f}s'+(' END'if seconds>=rows[eid]['controls']*.02-.001 else ''),fontsize=9)
    fig.suptitle('Actual MOD4v1 first episodes | enhanced contract collision shapes | no NN / no new physics | '+view)
    path=out/f'{args.prefix}_{view}.png';fig.savefig(path,dpi=130);plt.close(fig);media.append(str(path))
report=dict(media=media,model_SHA=result['source_SHA'],actual_saved_body_poses=True,enhanced_contract_geometry=True,
    saved_body_quaternion_order=saved_pose_order,contract_quaternion_order='wxyz',
    capture_boundary='evaluate.observe b.reward.robot.data DataView, already normalized before npz',
    returned_source=dict(path=str(args.returned),bytes=len(returned_raw),SHA=hashlib.sha256(returned_raw).hexdigest()),
    render_representation='authored collision boxes and tire cylinders, visual meshes omitted',physics_steps=0,NN=0,
    first_episodes_terminated_controls=[r['controls'] for r in rows])
with (out/'RENDER_REPORT.json').open('x',encoding='utf8')as f:json.dump(report,f,indent=2)
print(json.dumps(report))
