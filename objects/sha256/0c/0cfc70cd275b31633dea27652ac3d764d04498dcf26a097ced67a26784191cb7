"""Offline geometry/reference validation. Does not run Isaac or PhysX."""
from pathlib import Path
import json,time,sys
import numpy as np
import trimesh
from pxr import Usd,UsdGeom,UsdPhysics,UsdUtils
ROOT=Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding='utf8')

def main():
    started=time.perf_counter()
    raw=np.load(ROOT/'data/arena_collision.npz')
    vertices=raw['vertices'];faces=raw['faces']
    assert np.isfinite(vertices).all() and faces.min()>=0 and faces.max()<len(vertices)
    mesh=trimesh.Trimesh(vertices,faces,process=False)
    assert mesh.area_faces.min()>1e-12
    source=json.loads((ROOT/'reports/collision_audit.json').read_text())
    assert len(faces)==source['collision_triangles']
    featured=json.loads((ROOT/'data/features.json').read_text(encoding='utf8'))
    included={p['part'] for p in source['parts'] if p['collision']}
    assert all(set(f['source_part_ids'])<=included for f in featured)
    stage=Usd.Stage.Open(str(ROOT/'maps/arena_1024.usda'))
    assert UsdGeom.GetStageMetersPerUnit(stage)==1. and UsdGeom.GetStageUpAxis(stage)=='Z'
    root=stage.GetDefaultPrim();cells=root.GetChildren()
    layout=json.loads((ROOT/'maps/arena_1024.json').read_text())
    assert len(cells)==layout['num_envs']==1024
    prototypes=set();transforms=[]
    for prim,expected in zip(cells,layout['origins']):
        assert prim.IsInstance(),prim.GetPath()
        prototypes.add(str(prim.GetPrototype().GetPath()))
        translation=UsdGeom.Xformable(prim).GetLocalTransformation().ExtractTranslation()
        assert np.allclose(translation,expected,atol=1e-9)
        transforms.append(list(translation))
    assert len(prototypes)==1
    bounds=mesh.bounds
    assert np.all(np.ptp(mesh.vertices,axis=0)[:2]<np.array(layout['spacing_xy_m']))
    collider=Usd.Stage.Open(str(ROOT/'assets/arena_collision.usdc'))
    objects=[p for p in collider.Traverse() if p.HasAPI(UsdPhysics.CollisionAPI)]
    assert len(objects)==1
    p=objects[0]
    usd_mesh=UsdGeom.Mesh(p)
    assert np.array_equal(np.asarray(usd_mesh.GetPointsAttr().Get()),vertices)
    assert np.array_equal(np.asarray(usd_mesh.GetFaceVertexIndicesAttr().Get()).reshape(-1,3),faces)
    assert UsdPhysics.MeshCollisionAPI(p).GetApproximationAttr().Get()=='none'
    assert not any(p.HasAPI(UsdPhysics.RigidBodyAPI) for p in collider.Traverse())
    for stagepath in ['maps/arena.usda','maps/arena_1.usda','maps/arena_1024.usda','maps/arena_preview.usda']:
        layers,assets,unresolved=UsdUtils.ComputeAllDependencies(str(ROOT/stagepath))
        assert not unresolved,(stagepath,unresolved)
        for layer in layers:
            path=Path(layer.realPath).resolve()
            assert path.is_relative_to(ROOT.resolve()),path
    checks=json.loads((ROOT/'data/source_ray_checks.json').read_text())
    points=np.array([c['origin_m'] for c in checks]);dirs=np.array([c['direction'] for c in checks])
    loc,ray,tri=mesh.ray.intersects_location(points,dirs,multiple_hits=True)
    distances=np.full(len(checks),np.inf)
    hit_dist=np.linalg.norm(loc-points[ray],axis=1)
    np.minimum.at(distances,ray,hit_dist)
    first=np.abs(hit_dist-distances[ray])<1e-7
    backface=(mesh.face_normals[tri[first]]*dirs[ray[first]]).sum(axis=1)>0
    assert not backface.any(), f'{backface.sum()} first hits face away from the ray; audit CAD winding.'
    expected=np.array([c['expected_distance_m'] for c in checks])
    errors=np.abs(distances-expected);tol=np.array([c['tolerance_m'] for c in checks])
    failures=[dict(id=checks[i]['id'],error_m=float(errors[i]),expected_m=float(expected[i]),actual_m=float(distances[i])) for i in np.where(errors>tol)[0]]
    groups={}
    for name in ['arena','rough','fly','upper','lip','ramp','tunnel_roof','tunnel_floor']:
        ids=[i for i,c in enumerate(checks) if c['id'].startswith(name+'_')]
        groups[name]=dict(count=len(ids),max_distance_error_m=float(errors[ids].max()))
    report=dict(status='PASS_OFFLINE_MAP' if not failures else 'FAIL_OFFLINE_MAP',num_envs=1024,
                arena_prototype_count=len(prototypes),colliders_per_arena=len(objects),visual_triangles=source['visual_triangles'],
                collision_triangles=len(faces),collision_vertices=len(vertices),bounds_m=bounds.tolist(),
                environment_gap_xy_m=(np.array(layout['spacing_xy_m'])-np.ptp(mesh.vertices,axis=0)[:2]).tolist(),
                ray_checks=len(checks),first_hit_backfaces=int(backface.sum()),groups=groups,failures=failures,seconds=time.perf_counter()-started,
                runtime_tested=False,scope='CAD triangle parity, underpass clearance, asset composition and separated instance layout. No Isaac/PhysX execution.')
    (ROOT/'reports/offline_validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(report,indent=2),flush=True)
    assert not failures,failures[:5]

if __name__=='__main__':main()
