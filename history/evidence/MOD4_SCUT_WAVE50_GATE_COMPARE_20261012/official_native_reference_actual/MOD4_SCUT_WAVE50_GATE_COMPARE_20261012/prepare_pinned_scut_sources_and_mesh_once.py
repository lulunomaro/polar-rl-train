"""New independent reference: public rough models, original robot, actual MOD4 test mesh."""
from scut_wave_io import *
import subprocess,zipfile,shutil,numpy as np

def main():
    assert not (R/'SCUT_REFERENCE_PREPARED.json').exists()
    pin='b8ff79f3df855faf9dc92f4a282bd80c42649466';repo=W/'audits/20260925/scutrobotlab_wheeled-legged_RL'
    prefixes=['pretrained/26_infantry/rough_rotation_stair/2026-07-23_16-23-21','pretrained/26_infantry/rough_rotation_stair/2026-07-30_09-16-27']
    names=subprocess.check_output(['git','-C',str(repo),'ls-tree','-r','--name-only',pin,'--','source','scripts','LICENSE']).decode().splitlines()
    names=[x for x in names if not x.endswith(('.pyc','.png','.jpg','.gif'))]
    names+= [p+'/'+x for p in prefixes for x in ('model_1000.pt','params/env.yaml','params/agent.yaml')]
    original=D/'original';assert not original.exists();original.mkdir();manifest=dict(commit=pin,repository='https://github.com/scutrobotlab/wheeled-legged_RL',files={},models=prefixes,new_learning=False)
    with zipfile.ZipFile(D/'reference_original.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
        for name in names:
            raw=subprocess.check_output(['git','-C',str(repo),'show',pin+':'+name]);assert not raw.startswith(b'version https://git-lfs'),name
            p=original/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);manifest['files'][name]=dict(bytes=len(raw),sha256=H(raw));z.writestr(name,raw)
        raw=json.dumps(manifest,indent=2).encode();(original/'SOURCE_MANIFEST.json').write_bytes(raw);z.writestr('SOURCE_MANIFEST.json',raw)
    prior=W/'MOD4_E1_WAVE50_EPISODE_DIRECTION_PREPARE_20261012/reports/cases/clk2500-closure-episode-d3-150-e1-wave50-direction-repair-terrain-flat'
    probe=json.loads((prior/'probe.json').read_bytes());query=probe['route_scope']['query_worldmesh_evidence'];q=prior/Path(query['path']).name;assert H(q.read_bytes())==query['sha256'] and q.stat().st_size==query['bytes']
    shutil.copyfile(q,D/'actual_mod4_wave50_query.npz')
    with np.load(q,allow_pickle=False) as z:tri=z['world_triangles'].copy();expected=z['expected_actual_ground'].copy();rays=z['actual_world_ray_origins'].copy()
    assert tri.shape[0]==80 and tri.shape[-2:]==(3,3) and tri.dtype==np.float32 and np.isfinite(tri).all()
    mesh=D/'exact_wave50_test.usda';points=tri.reshape(-1,3);faces=np.arange(len(points),dtype=np.int32)
    with mesh.open('x',encoding='utf8') as f:
        f.write('#usda 1.0\n(\n defaultPrim = "Terrain"\n metersPerUnit = 1\n upAxis = "Z"\n)\ndef Xform "Terrain" {\n def Mesh "mesh" (prepend apiSchemas = ["PhysicsCollisionAPI", "PhysicsMeshCollisionAPI"]) {\n  uniform token subdivisionScheme = "none"\n  bool physics:collisionEnabled = true\n  uniform token physics:approximation = "none"\n  point3f[] points = [\n')
        f.write(',\n'.join('('+','.join(repr(float(y)) for y in x)+')' for x in points));f.write('\n  ]\n  int[] faceVertexCounts = [');f.write(','.join(['3']*(len(points)//3)));f.write(']\n  int[] faceVertexIndices = [');f.write(','.join(map(str,faces)));f.write(']\n }\n}\n')
    fixture=dict(source_MOD4_probe=str(prior/'probe.json'),source_MOD4_probe_SHA=H((prior/'probe.json').read_bytes()),source_query=q.name,source_query_SHA=query['sha256'],source_query_bytes=query['bytes'],world_triangles_shape=list(tri.shape),actual80cells_triangle_f32_byte_SHA=H(tri.tobytes()),centers=probe['route_scope']['tile_centers'],starts=probe['route_scope']['requested_starts'],halfspan=probe['route_scope']['wave_x_halfspan_m'],approach_m=.4,after_m=.2,seconds=15.,groups=[i%3 for i in range(80)],seed=20260928,mesh_file=mesh.name,mesh_SHA=H(mesh.read_bytes()),mesh_bytes=mesh.stat().st_size,robot_not_MOD4=True,original_SCUT_clock_DR_not_replaced=True,MOD4_health_shadow_only_no_SCUT_closure_reset_added=True)
    (D/'FIXTURE.json').write_bytes(json.dumps(fixture,indent=2).encode())
    asset=original/'source/agent_world/agent_world/assets/usd_files/wheelbipeV14_2_1/wheelbipeV14_2.usd';assert H(asset.read_bytes())=='48f2d53ac589391a37f3df550e8e537af3ecb5bdb6ebb632fb8c7b83fa9af325'
    v=dict(epoch=time.time(),prepared=True,public_pin=pin,source_files=len(names),source_manifest=manifest,public_models=prefixes,original_USD_SHA=H(asset.read_bytes()),runtime_archive=dict(path=str(D/'reference_original.zip'),bytes=(D/'reference_original.zip').stat().st_size,sha256=H((D/'reference_original.zip').read_bytes())),fixture=fixture,scope='Two public rough_rotation_stair original models on exactly saved MOD4 Wave50 collider; same15s/approach/contact/exit behavior criteria, original50Hz/DR/robot disclosed, data-validity per originalplant, shadowMOD4closure2mm',new_GPU_not_yet_launched=True,no_MOD4_weights_actor_or_budget_mutation=True)
    save('SCUT_REFERENCE_PREPARED.json',v);print(json.dumps(dict(prepared=True,models=prefixes,mesh_bytes=mesh.stat().st_size,original_USD_exact=True,physics_steps_per_model=3000)))

if __name__=='__main__':
    try:main()
    except BaseException:save('SCUT_REFERENCE_PREPARATION_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),original_partial_source_retained=True,no_GPU_or_budget_replay=True));raise
