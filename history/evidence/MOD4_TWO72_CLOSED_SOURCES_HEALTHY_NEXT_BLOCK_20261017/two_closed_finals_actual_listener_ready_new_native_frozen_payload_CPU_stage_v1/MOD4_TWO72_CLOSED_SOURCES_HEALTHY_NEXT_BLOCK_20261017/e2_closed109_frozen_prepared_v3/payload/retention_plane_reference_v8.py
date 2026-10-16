"""Disclosed represented-native-Plane consistency around unchanged skill loops.

No reported hit is used to define the expected Plane. Every scene supplies its
own actual USD and native actor metadata. The shape-local pose is source-derived,
not directly read; compiled source equivalence remains unproven.
"""
from pathlib import Path
import hashlib,json,os
import numpy as np
from raycast_hit_serializer_v5 import serialize_raycast_hit,plain
from retention_plane_metadata_v7 import actor_metadata_from_USD,resolve_plane_hit
from represented_native_plane_CPU_component_v2 import compare_actual_hit_readonly
NATIVE_BINDING_SHA256='89e49ac6b44a01794bbb658452d0146c0f798a457f0504a455c57ee4b633663a'


def binary_stream_sha256(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as f:
        while chunk:=f.read(4*1024*1024):digest.update(chunk)
    return digest.hexdigest()


def loaded_PhysX_binary_fingerprints():
    """Read only this process' already loaded binaries; never load a DLL."""
    import psutil
    process=psutil.Process(os.getpid());rows=[];seen=set()
    for item in process.memory_maps(grouped=True):
        path=Path(item.path);name=path.name.lower()
        if path.suffix.lower() not in ('.dll','.pyd'):continue
        if 'physx' not in name and not ('physics' in name and 'omni' in name):continue
        key=str(path).replace('\\','/').lower()
        if key in seen:continue
        seen.add(key);assert path.is_file(),('Actual loaded native binary path absent',str(path))
        rows.append(dict(path=str(path),normalized_path=key,bytes=path.stat().st_size,
                         sha256=binary_stream_sha256(path)))
    rows.sort(key=lambda r:r['normalized_path'])
    return dict(pid=process.pid,process_creation=process.create_time(),files=rows,
                core_PhysX_plugin_identified=any('omni.physx.plugin' in Path(r['path']).name.lower() for r in rows),
                all_physics_engine_binaries_globally_claimed=False,
                own_already_loaded_PhysX_named_modules_only=True)


def query_current_positions(query,xy,phase,reference,resolver,persist):
    xy=np.asarray(xy,dtype=np.float32)
    assert xy.shape in ((80,2),(88,2)) and np.isfinite(xy).all()
    evidence=dict(phase=phase,reference=reference,tolerance_m=1e-6,
                  source_reference_only=True,actual_shape_local_pose_read=False,
                  public_source_to_installed_binary_bitexact_proven=False,
                  reference_defined_from_reported_hits=False,all_rays=[],
                  ideal_Z0_flags_separately_preserved=True)
    rows=[]
    for i,point in enumerate(xy):
        allhits=[]
        def callback(hit):allhits.append(serialize_raycast_hit(hit));return True
        returned=query.raycast_all((float(point[0]),float(point[1]),10.),(0.,0.,-1.),20.,callback)
        selected=[]
        for hit in allhits:
            resolution=resolver(hit)
            if resolution is not None:selected.append(dict(hit=hit,**resolution))
        row=dict(env_id=i,origin=[float(point[0]),float(point[1]),10.],direction=[0.,0.,-1.],
                 maximum_distance=20.,query_return=plain(returned),all_reported_hits=allhits,
                 selected_plane_hits=selected)
        evidence['all_rays'].append(row);persist(evidence)
        errors=[h for h in allhits if h.get('_serializer_error')]
        assert not errors,('Typed native serializer failure',phase,i,errors)
        assert returned and len(selected)==1,('Unique actual Plane hit missing',phase,i,row)
        item=selected[0];hit=item['hit'];check=compare_actual_hit_readonly(reference,hit)
        row['independent_source_reference_comparison']=check
        row['original_ideal_Z0_within_1e6']=bool(abs(float(hit['position'][2]))<=1e-6)
        row['original_ideal_normalZ1_within_1e6']=bool(abs(float(hit['normal'][2])-1.)<=1e-6)
        persist(evidence)
        assert check['represented_query_within_original_1e6'],('Represented Plane query violates unchanged 1e-6',phase,i,row)
        assert check['normal_crosscheck_maxabs']<=1e-6,('Independent normal crosscheck violates unchanged 1e-6',phase,i,row)
        rows.append(dict(env_id=i,origin=row['origin'],hit=hit,
                         resolved_plane_path=item['resolved_plane_path'],identity_resolution=item['identity_resolution'],
                         independent_source_reference_comparison=check,
                         original_ideal_Z0_within_1e6=row['original_ideal_Z0_within_1e6'],
                         original_ideal_normalZ1_within_1e6=row['original_ideal_normalZ1_within_1e6']))
    evidence['complete_all_envs']=True;persist(evidence)
    return evidence,rows


def plane_query_actual(env,phase,context):
    from factor_runtime_3060_reference17b_v1 import cpu,private_rng
    from omni.physx import get_physx_scene_query_interface
    import omni.physx.bindings._physx as native
    O=Path(context['output_dir']);save=context['save'];before_rng=private_rng(env)
    binding=Path(native.__file__);digest=binary_stream_sha256(binding)
    assert digest==NATIVE_BINDING_SHA256,('Native binding differs from independently completed V7',str(binding),digest)
    binding_evidence=dict(path=str(binding),bytes=binding.stat().st_size,sha256=digest,
                          pin_source='Actual independently completed V7 binding fingerprint',
                          physics_engine_plugin_all_DLLs_pinned=False)
    # The V7 helper is reused byteexact. Namespaced saves retain each scene/phase
    # independently, and its native actor getter is called once per phase.
    def save_phase(name,value):save('REFERENCE_'+phase+'_'+name,value)
    stage,path,metadata,reference=actor_metadata_from_USD(env,save_phase)
    save_phase('NATIVE_BINDING_ACTUAL.json',binding_evidence)
    binaries=loaded_PhysX_binary_fingerprints()
    save_phase('LOADED_PhysX_BINARY_FINGERPRINTS_ACTUAL.json',binaries)
    assert binaries['core_PhysX_plugin_identified'],('Actual core PhysX plugin binary identity missing',binaries)
    destination=O/('QUERY_'+phase+'_ALLHITS_ACTUAL.json');assert not destination.exists()
    def persist(value):
        temporary=destination.with_suffix('.json.partial')
        with temporary.open('wb') as f:f.write(json.dumps(value,indent=2).encode('utf8'));f.flush();os.fsync(f.fileno())
        os.replace(temporary,destination)
    evidence,rows=query_current_positions(get_physx_scene_query_interface(),cpu(env.scene['robot'].data.root_pos_w)[:,:2],
                                          phase,reference,lambda h:resolve_plane_hit(stage,path,h),persist)
    after_rng=private_rng(env);assert before_rng==after_rng,'Readonly Plane metadata/query consumed a captured RNG draw'
    return dict(phase=phase,query_rows=rows,
                authored_plane=dict(path=path,type=metadata['actual_USD_plane']['type'],axis=metadata['actual_USD_plane']['axis'],
                                    point=metadata['actual_USD_plane']['world_position'],normal=metadata['actual_USD_plane']['world_normal']),
                tolerance_m=1e-6,no_physical_step_no_RNG=True,scene_query_support_requested=True,actual_USD_scene_query_support=True,
                actual_USD_and_native_actor_metadata=metadata,source_reference=reference,
                source_reference_only=True,actual_shape_local_pose_read=False,
                public_source_to_installed_binary_bitexact_proven=False,native_binding_actual=binding_evidence,
                loaded_PhysX_binary_fingerprints=binaries,
                physics_engine_plugin_all_DLLs_pinned=False,captured_RNG_before=before_rng,captured_RNG_after=after_rng,
                reference_defined_from_reported_hits=False,ideal_Z0_failure_count=sum(not r['original_ideal_Z0_within_1e6'] for r in rows),
                original_V6_fullcase_failed_unchanged=True,
                allhits_evidence=dict(path=str(destination),bytes=destination.stat().st_size,sha256=hashlib.sha256(destination.read_bytes()).hexdigest()))
