"""Render saved physical body poses with the original SCUT USD mesh. No policy/physics."""
from pathlib import Path
import os
import sys
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--headless',action='store_true')
parser.add_argument('--directory',default='')
args=parser.parse_args()
ISAAC=Path('C:/Users/lulu/miniconda3/envs/env_isaaclab/Lib/site-packages/isaacsim')
USD_LIB=ISAAC/'extscache/omni.usd.libs-1.0.1+69cbf6ad.wx64.r.cp311'
handles=[os.add_dll_directory(str(ISAAC/'kit')),os.add_dll_directory(str(USD_LIB/'bin'))]
sys.path.insert(0,str(USD_LIB))
ROOT=Path(__file__).resolve().parent
def mark(message):
    with (ROOT/'render_trace.log').open('a',encoding='utf-8') as f:f.write(message+'\n')
mark('standalone_usd_no_simulation')
try:
    import json, hashlib
    import numpy as np
    mark('numpy_imported')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection,LineCollection
    from scipy.spatial import ConvexHull
    from pxr import Usd, UsdGeom
    mark('plot_and_pxr_imported')
    ROOT=Path(__file__).resolve().parent
    REF=Path('C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL')
    usd=REF/'source/agent_world/agent_world/assets/usd_files/wheelbipeV14_2_1/wheelbipeV14_2.usd'
    asset=Usd.Stage.Open(str(usd))
    mark('usd_opened')
    m=json.loads((ROOT/'matrix01/CASES.json').read_text())
    names=m['body_names']; cache=UsdGeom.XformCache()
    meshes=[]
    for prim in Usd.PrimRange.Stage(asset, Usd.TraverseInstanceProxies()):
        if not prim.IsA(UsdGeom.Mesh): continue
        body=prim
        while body and body.GetName() not in names:
            body=body.GetParent()
        if not body: continue
        mesh=UsdGeom.Mesh(prim)
        points=np.asarray(mesh.GetPointsAttr().Get(),dtype=float)
        if not len(points): continue
        local=np.array(cache.GetLocalToWorldTransform(prim)*cache.GetLocalToWorldTransform(body).GetInverse())
        v=(np.column_stack([points,np.ones(len(points))])@local)[:,:3]
        counts=np.array(mesh.GetFaceVertexCountsAttr().Get()); inds=np.array(mesh.GetFaceVertexIndicesAttr().Get()); faces=[]; p=0
        for count in counts:
            idx=inds[p:p+count];p+=count
            for k in range(1,count-1): faces.append([idx[0],idx[k],idx[k+1]])
        if faces:
            if np.linalg.matrix_rank(v-v.mean(0))>=3:
                v=v[ConvexHull(v).vertices]
            meshes.append((names.index(body.GetName()),v,np.asarray(faces),body.GetName()))
    assert meshes
    mark('meshes_parsed '+str(len(meshes)))
    def rotation(q):
        w,x,y,z=q
        return np.array([[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],[2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],[2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]])
    media=[]
    groups=[(args.directory,[0,1,3,6] if args.directory.startswith('native') else [0,9,17,20])] if args.directory else [('matrix01',[0,13,19,21]),('extended01',[0,10,17,20]),('native_rough02',[0,1,3,6])]
    for directory, ids in groups:
        mark('rendering '+directory)
        folder=ROOT/directory;d=np.load(folder/'PHYSICAL.npz');meta=json.loads((folder/'CASES.json').read_text())
        terrain=None
        if (folder/'ACTUAL_TERRAIN.npz').exists():
            raw=np.load(folder/'ACTUAL_TERRAIN.npz')
            assert np.all(raw['counts']==3)
            terrain=raw['vertices'][raw['indices'].reshape(-1,3)]
        fig,axes=plt.subplots(len(ids),6,figsize=(18,10),layout='constrained')
        for row,eid in enumerate(ids):
            origin=np.asarray(meta['origins'][eid]);case=meta['cases'][eid]
            valid=np.flatnonzero(d['active'][:,eid])
            for col,t in enumerate([1.5,2.5,3.5,4.5,6.,8.]):
                ix=int(valid[min(len(valid)-1,round(t/.005)-1)]);ax=axes[row,col]
                root=d['root'][ix,eid,:3]-origin
                for bid,v,faces,name in meshes:
                    world=v@rotation(d['body_quat'][ix,eid,bid]).T+d['body_pos'][ix,eid,bid]-origin
                    projected=world[:,[0,2]]
                    if np.linalg.matrix_rank(projected-projected.mean(0))<2:continue
                    boundary=projected[ConvexHull(projected).vertices]
                    ax.add_collection(PolyCollection([boundary],facecolors=('#d98835' if 'wheel_link' in name else '#647589'),edgecolors='#29394a',linewidths=.25,alpha=.65))
                if terrain is None:
                    ax.axhline(0,color='black',lw=.6)
                else:
                    cut_y=float(d['root'][ix,eid,1]);segments=[]
                    for aa,bb in [(terrain[:,0],terrain[:,1]),(terrain[:,1],terrain[:,2]),(terrain[:,2],terrain[:,0])]:
                        da=aa[:,1]-cut_y;db=bb[:,1]-cut_y
                        selected=(da*db<0)
                        points=aa[selected]+(bb[selected]-aa[selected])*(da[selected]/(da[selected]-db[selected]))[:,None]
                        tid=np.flatnonzero(selected)
                        for j,point in zip(tid,points):segments.append((int(j),point))
                    by_tri={}
                    for j,point in segments:by_tri.setdefault(j,[]).append(point)
                    lines=[(np.asarray(v[:2])-origin)[:,[0,2]] for v in by_tri.values() if len(v)>=2]
                    ax.add_collection(LineCollection(lines,colors='#297bb0',linewidths=1.2))
                if case['kind']=='single200':
                    ax.plot([-1,1.6,1.6,7],[0,0,.2,.2],color='#297bb0',lw=2)
                elif case['kind']=='small_stairs':
                    xs=[-1,1.6];zs=[0,0]
                    for k in range(5):xs.extend([1.6+k*.1,1.6+(k+1)*.1]);zs.extend([.04*(k+1)]*2)
                    ax.plot(xs,zs,color='#297bb0',lw=2)
                else:
                    if case['kind']=='native_inverse_mid' and terrain is None:
                        ax.text(.03,.9,'Native generated terrain omitted',transform=ax.transAxes,fontsize=6)
                ax.set_xlim(root[0]-.65,root[0]+.65);ax.set_ylim(root[2]-.5,root[2]+.5)
                ax.set_aspect('equal');ax.grid(alpha=.15)
                ax.set_title(f'{case["kind"]} env{eid} {t:.1f}s',fontsize=8)
                ax.set_xlabel('x m');ax.set_ylabel('z m')
        fig.suptitle('SCUT original policy / saved physical poses / projected convex silhouettes of original visual meshes / no new physics')
        path=folder/'ACTUAL_MESH_SIDE.png';fig.savefig(path,dpi=120);plt.close(fig);media.append(str(path))
        mark('saved '+str(path))
    (ROOT/(args.directory+'_RENDER_REPORT.json' if args.directory else 'ACTUAL_RENDER_REPORT.json')).write_text(json.dumps({'media':media,'saved_quat':'wxyz','original_usd':str(usd),'usd_sha256':hashlib.sha256(usd.read_bytes()).hexdigest(),'mesh_count':len(meshes),'representation':'Per mesh projected convex silhouettes of original USD geometry at saved physical poses; visual simplification only','policy_operations':0,'physics_operations':0,'native_rough_terrain_omitted':terrain is None},indent=2))
    print(json.dumps({'media':media,'mesh_count':len(meshes)}))
except BaseException:
    import traceback
    message=traceback.format_exc()
    mark(message)
    (ROOT/'RENDER_ERROR.json').write_text(json.dumps({'traceback':message},indent=2),encoding='utf-8')
    print(message,flush=True)
finally:
    mark('done')
