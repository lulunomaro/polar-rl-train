"""New independent query contract after retained144 precontrol failure; no GPU."""
from second_io import *
import ast, zipfile, importlib.util
import numpy as np

def main():
    assert not (R/'WAVE50_WORLDMESH_QUERY_PREPARED.json').exists()
    failed=json.loads(sorted(R.glob('WAVE50_144_FAILED_ACTUAL_COLLECTION_[0-9]*.json'))[-1].read_bytes())
    assert failed['result']['phase']=='retained_failed' and failed['result']['error_files']==['probe.json.error.txt'] and not failed['result']['result_present']
    err=next(x for x in failed['evidence'] if x['local'].endswith('probe.json.error.txt'))
    assert H(Path(err['local']).read_bytes())==err['sha256'] and 'assert actual_query_height_error<=1e-6' in Path(err['local']).read_text()
    parent=json.loads((R/'WAVE50_COMPONENT_FROZEN_PREPARED.json').read_bytes());pkg=Path(parent['package']['path'])
    assert H(pkg.read_bytes())==parent['package']['sha256']
    with zipfile.ZipFile(pkg) as z:members={name:z.read(name) for name in z.namelist()}
    manifest=json.loads(members['SOURCE_MANIFEST.json']);assert all(H(members[k])==v for k,v in manifest['files'].items())
    impl=D/'wave50_worldmesh_scope';gp='runtime/isaac/mod4/g4_cad_wave_geometry.py';pp='runtime/isaac/mod4/g4_cad_profile.json';fp='runtime/isaac/mod4/frozen_history_flat.py';qp='runtime/isaac/mod4/g4_worldmesh_query_contract.py'
    for name in (gp,pp):
        p=impl/Path(name).name;assert not p.exists();p.write_bytes(members[name])
    sys.path.insert(0,str(impl));import g4_worldmesh_query_contract as contract
    from g4_cad_wave_geometry import make_mesh,profile
    mesh,_=make_mesh((9.,9.));base=mesh.vertices.copy();base[:,:2]-=4.5
    ids=np.arange(80);centers=np.stack(((ids//2+.5)*9.-180.,(34+ids%2+.5)*9.-180.),axis=-1)
    half=profile()['span_m']/2;requested=np.zeros((80,35,3));requested[:,:,:2]=centers[:,None,:];requested[:,:,2]=2.
    requested[:,:,0]+=np.r_[-half-.4,np.linspace(-half,half,33),half+.4][None,:]
    starts=requested.astype(np.float32);vertices=[];faces=[]
    for center in centers:
        v=base.copy();v[:,:2]+=center;faces.append(mesh.faces+len(vertices)*len(base));vertices.append(v.astype(np.float32))
    vertices=np.concatenate(vertices);faces=np.concatenate(faces)
    expected,receipts,triangles=contract.expected_ground(vertices,faces,centers,starts)
    knots=np.r_[np.asarray(profile()['profile_x_m'])[:-1],profile()['span_m']]
    ideal=np.interp(starts[:,:,0].astype(float)-centers[:,None,0]+half,knots,np.asarray(profile()['normalized_height'])*.05,left=0.,right=0.)
    # Separate algebraic interpolation independently agrees with triangle oracle.
    second=[]
    for center,raystarts in zip(centers,starts):
        world=base.copy();world[:,:2]+=center;world=world.astype(np.float32)
        order=np.argsort(world[::2,0]);second.append(np.interp(raystarts[:,0],world[::2,0][order],world[::2,2][order]))
    cross_error=float(np.max(abs(expected-np.asarray(second))));assert cross_error<1e-12
    cpu=save('WAVE50_144_WORLDMESH_INPUT_CPU_DIAGNOSIS.json',dict(epoch=time.time(),original_failed_collection=str(sorted(R.glob('WAVE50_144_FAILED_ACTUAL_COLLECTION_[0-9]*.json'))[-1]),original_failed_GPU_numeric_difference_not_saved=True,original_failed_GPU_cause_not_claimed_measured=True,CPU_emulated_world_float32_mesh_vs_ideal_profile_max_m=float(np.max(abs(expected-ideal))),CPU_independent_triangle_vs_quantized_profile_max_m=cross_error,CPU_rays=2800,all80_float32_world_mesh_triangle_identity_exact=receipts,original_ground_tolerance_m=1e-6,query_expected_surface_identity_changes_only=True,no_geometry_physics_health_contact_hardware_threshold_change=True))
    old=members[fp].decode();new=old
    anchor="    expected_actual_ground=np.interp(actual_canonical_ray_x+half,np.r_[np.asarray(wave_profile['profile_x_m'])[:-1],wave_profile['span_m']],np.asarray(wave_profile['normalized_height'])*.05,left=0.,right=0.)\n"
    assert new.count(anchor)==1
    replacement="""    ideal_profile_ground=np.interp(actual_canonical_ray_x+half,np.r_[np.asarray(wave_profile['profile_x_m'])[:-1],wave_profile['span_m']],np.asarray(wave_profile['normalized_height'])*.05,left=0.,right=0.)
    from g4_worldmesh_query_contract import expected_ground
    expected_actual_ground,world_mesh_receipts,query_world_triangles=expected_ground(ray.geometry.vertices,ray.geometry.faces,centers,actual_world_ray_origins)
    query_evidence_path=Path(args.output).with_name(Path(args.output).name+'.worldmesh_query.npz')
    assert not query_evidence_path.exists()
    np.savez_compressed(query_evidence_path,actual_world_ray_origins=actual_world_ray_origins,actual_canonical_ray_x=actual_canonical_ray_x,actual_sampled_ground=sampled,expected_actual_ground=expected_actual_ground,ideal_profile_ground=ideal_profile_ground,world_triangles=query_world_triangles)
    print('WAVE50_WORLDMESH_QUERY_ACTUAL '+json.dumps(dict(error_m=float(np.max(abs(sampled-expected_actual_ground))),ideal_profile_difference_m=float(np.max(abs(sampled-ideal_profile_ground))),ground_tolerance_m=1e-6,mesh_triangle_identity_exact=True,query_evidence_path=str(query_evidence_path))),flush=True)
"""
    new=new.replace(anchor,replacement)
    new=new.replace('actual_query_ground_tolerance_m=1e-6,','actual_query_ground_tolerance_m=1e-6,world_mesh_receipts=world_mesh_receipts,query_worldmesh_evidence=dict(path=str(query_evidence_path),bytes=query_evidence_path.stat().st_size,sha256=hashlib.sha256(query_evidence_path.read_bytes()).hexdigest()),ideal_profile_difference_m=float(np.max(abs(sampled-ideal_profile_ground))),')
    protocol='approved_E1_G4_derived50mm_worldmesh_actualray_approach040_fullroute_behavior_v2'
    new=new.replace(parent['protocol'],protocol);compile(new,fp,'exec')
    def loop(s):return next(n for n in next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name=='main').body if isinstance(n,ast.For) and ast.unparse(n.target)=='step')
    assert ast.dump(loop(old),include_attributes=False)==ast.dump(loop(new),include_attributes=False)
    (impl/'frozen_history_flat_WAVE50_WORLDMESH.py').write_bytes(new.encode())
    changes={fp:new.encode(),qp:(impl/Path(qp).name).read_bytes()};members.update(changes)
    manifest.update(protocol=protocol,parent_archive_sha256=H(pkg.read_bytes()),query_expected_independent_CPU_triangles_actual_float32_mesh_byteexact=True,old_failed144_retained=True)
    manifest['files']={k:H(v) for k,v in members.items() if k!='SOURCE_MANIFEST.json'};manifest['new_or_changed_members']={k:H(v) for k,v in changes.items()}
    members['SOURCE_MANIFEST.json']=json.dumps(manifest,indent=2).encode()
    target=impl/'e1-g4-derived50mm-worldmesh-query-fullroute-frozen-v2.zip';assert not target.exists()
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for k,v in members.items():z.writestr(k,v)
    with zipfile.ZipFile(target) as z:assert all(H(z.read(k))==v for k,v in manifest['files'].items())
    info=dict(path=str(target.resolve()),bytes=target.stat().st_size,sha256=H(target.read_bytes()))
    save('WAVE50_WORLDMESH_QUERY_PREPARED.json',dict(epoch=time.time(),package=info,protocol=protocol,parent_archive_SHA=H(pkg.read_bytes()),source_checkpoint=parent['source_checkpoint'],profile=parent['profile'],CPU_diagnosis=str(cpu),CPU_rays=2800,independent_triangle_interpolation_error_m=cross_error,geometry_profile_and_all_old_members_exact_except_dispatcher_manifest=True,new_helper=qp,all_file_map_SHA_verified=len(manifest['files']),full_control_loop_AST_exact=True,ground_tolerance_m=1e-6,original144_failure_preserved=True,no_PPO_or_physical_admission_claim=True))
    print(json.dumps(dict(prepared=info,CPU_only=True,CPU_world_float32_vs_ideal_error_m=float(np.max(abs(expected-ideal))),independent_cross_error_m=cross_error)))

if __name__=='__main__':
    try:main()
    except BaseException:save('WAVE50_WORLDMESH_PREPARE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
