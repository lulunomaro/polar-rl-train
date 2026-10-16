"""New readonly Plane metadata/query stage; never runs a policy or control loop."""
from pathlib import Path
import functools, hashlib, json, os, time
import numpy as np
from raycast_hit_serializer_v5 import plain, serialize_raycast_hit
from represented_native_plane_CPU_component_v2 import (
    SOURCE_COMMIT, source_sha_manifest, represented_plane_from_readonly_metadata,
    compare_actual_hit_readonly,
)

SMALL_EVAL_CAPACITY = dict(gpu_max_rigid_contact_count=2**20,
    gpu_max_rigid_patch_count=2**16, gpu_found_lost_pairs_capacity=2**18,
    gpu_found_lost_aggregate_pairs_capacity=2**22, gpu_total_aggregate_pairs_capacity=2**20)


def hash_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def describe(value):
    return dict(qualified_class=type(value).__module__+'.'+type(value).__qualname__,
                value=plain(value))


class SDKCallAudit:
    """Count original SDK calls once; no extra calls and no installed-file edits.

    These are exposed SimulationContext method calls, not a promise to count all
    internal engine simulation instructions. Initialization is disclosed apart
    from the explicitly zero requested evaluation controls.
    """
    def __init__(self, cls):
        self.cls=cls; self.original={}; self.phase='SDK_environment_initialization'
        self.rows=[]; self.counts={}; self.owned={}

    def install(self):
        for name in ('reset','step','forward','render'):
            if not hasattr(self.cls,name): continue
            original=getattr(self.cls,name); self.original[name]=original
            self.owned[name]=name in self.cls.__dict__
            @functools.wraps(original)
            def observed(instance,*args,__original=original,__name=name,**kwargs):
                key=self.phase+'/'+__name; self.counts[key]=self.counts.get(key,0)+1
                self.rows.append(dict(phase=self.phase,method=__name,epoch=time.time()))
                return __original(instance,*args,**kwargs)
            setattr(self.cls,name,observed)
        return self

    def restore(self):
        for name,original in self.original.items():
            if self.owned[name]:setattr(self.cls,name,original)
            else:delattr(self.cls,name)

    def snapshot(self):
        return dict(counts=dict(self.counts),calls=list(self.rows),
                    requested_evaluation_controls=0,policy_calls=0,
                    complete_engine_internal_step_count_claimed=False)


def actor_metadata_from_USD(env, save):
    from isaaclab.sim import get_current_stage
    from pxr import UsdGeom, UsdPhysics, Gf
    from omni.physx import get_physx_interface
    stage=get_current_stage(); path='/World/ground/geometry/mesh'
    prim=stage.GetPrimAtPath(path)
    assert prim and prim.GetTypeName()=='Plane',('Actual native Plane missing',path)
    tf=UsdGeom.XformCache().GetLocalToWorldTransform(prim)
    transform=Gf.Transform(tf); rotation=transform.GetRotation().GetQuat()
    xyz=rotation.GetImaginary(); q=[float(xyz[0]),float(xyz[1]),float(xyz[2]),float(rotation.GetReal())]
    point=[float(v) for v in tf.Transform(Gf.Vec3d(0,0,0))]
    normal=[float(v) for v in tf.TransformDir(Gf.Vec3d(0,0,1))]
    ancestors=[]; p=prim
    while p and not p.IsPseudoRoot():
        ancestors.append(dict(path=str(p.GetPath()),type=p.GetTypeName(),
                              applied_schemas=list(p.GetAppliedSchemas()),
                              RigidBodyAPI=p.HasAPI(UsdPhysics.RigidBodyAPI)))
        p=p.GetParent()
    scene=stage.GetPrimAtPath(env.cfg.sim.physics_prim_path)
    flag=scene.GetAttribute('physxScene:enableSceneQuerySupport').Get()
    interface=get_physx_interface()
    actual=interface.get_rigidbody_transformation(path)  # Exactly one native getter.
    row=dict(source_commit=SOURCE_COMMIT,source_file_sha256=source_sha_manifest(),approved_axis='Z',
             actual_USD_plane=dict(path=path,type=prim.GetTypeName(),axis=prim.GetAttribute('axis').Get(),
                 CollisionAPI=prim.HasAPI(UsdPhysics.CollisionAPI),
                 RigidBodyAPI_ancestor_paths=[x['path'] for x in ancestors if x['RigidBodyAPI']],
                 world_position=point,world_rotation_xyzw=q,world_normal=normal,
                 world_transform_4x4=[[float(tf[i][j]) for j in range(4)] for i in range(4)],
                 ancestors=ancestors,meters_per_unit=float(UsdGeom.GetStageMetersPerUnit(stage)),
                 up_axis=str(UsdGeom.GetStageUpAxis(stage))),
             actual_actor_getter_raw=describe(actual),
             actual_actor_getter_field_types={str(k):describe(v) for k,v in actual.items()} if isinstance(actual,dict) else None,
             actual_actor_interface_class=type(interface).__module__+'.'+type(interface).__qualname__,
             query_support=dict(configured=env.cfg.sim.enable_scene_query_support,actual_USD=plain(flag),
                                scene_path=str(scene.GetPath())),
             actual_shape_local_pose_read=False,public_source_to_installed_binary_bitexact_proven=False)
    save('ACTUAL_USD_NATIVE_ACTOR_METADATA_BEFORE_VALIDATION.json',row)
    assert isinstance(actual,dict),('Native actor getter returned unexpected type',row)
    assert set(('ret_val','position','rotation'))<=set(actual),('Native getter fields missing',row)
    row['actual_actor_getter']=dict(path=path,ret_val=actual['ret_val'],
                                  position=plain(actual['position']),rotation_xyzw=plain(actual['rotation']))
    assert flag is True and env.cfg.sim.enable_scene_query_support is True,row['query_support']
    assert row['actual_USD_plane']['meters_per_unit']==1.0 and row['actual_USD_plane']['up_axis']=='Z'
    assert prim.HasAPI(UsdPhysics.CollisionAPI) and row['actual_USD_plane']['axis']=='Z'
    assert np.array_equal(np.asarray(point),[0,0,0]) and np.array_equal(np.asarray(normal),[0,0,1])
    reference=represented_plane_from_readonly_metadata(row)
    save('ACTUAL_NATIVE_ACTOR_AND_SOURCE_REFERENCE_VALIDATED.json',dict(metadata=row,reference=reference))
    return stage,path,row,reference


def resolve_plane_hit(stage, path, hit):
    collision=str(hit.get('collision',''))
    if collision==path or collision.startswith(path+'/'):
        return dict(resolved_plane_path=path,identity_resolution='actual collision exact or Plane child')
    if collision and path.startswith(collision+'/'):
        from pxr import Usd, UsdPhysics
        ancestor=stage.GetPrimAtPath(collision)
        colliders=[str(p.GetPath()) for p in Usd.PrimRange(ancestor) if p.HasAPI(UsdPhysics.CollisionAPI)]
        if colliders==[path]:
            return dict(resolved_plane_path=path,identity_resolution='actual ancestor has only the configured Plane collision')
    return None


def query_positions_only(query, source, reference, resolver, persist):
    """Only actual scene queries; no world pose or query expectation from hits."""
    evidence=dict(source_positions=source,source_reference=reference,tolerance_m=1e-6,
                  scope='new represented-Plane query consistency only; not inherited behavior or old-case completion',
                  requested_evaluation_controls=0,policy_calls=0,query_only_no_rng_draws=True,
                  actual_shape_local_pose_read=False,all_rays=[])
    for phase in ('first_before_control','last_after_reset'):
        values=np.asarray(source['positions'][phase],dtype=np.float32)
        assert values.shape==(80,2) and np.isfinite(values).all()
        for env_id,xy in enumerate(values):
            hits=[]
            def callback(hit):
                hits.append(serialize_raycast_hit(hit)); return True
            returned=query.raycast_all((float(xy[0]),float(xy[1]),10.0),(0.0,0.0,-1.0),20.0,callback)
            selected=[]
            for hit in hits:
                resolution=resolver(hit)
                if resolution is not None: selected.append(dict(hit=hit,**resolution))
            row=dict(phase=phase,env_id=env_id,origin=[float(xy[0]),float(xy[1]),10.0],
                     direction=[0,0,-1],maximum_distance=20.0,query_return=plain(returned),
                     all_reported_hits=hits,selected_plane_hits=selected)
            evidence['all_rays'].append(row);persist(evidence)
            errors=[h for h in hits if h.get('_serializer_error')]
            assert not errors,('Typed native hit serialization failed',phase,env_id,errors)
            assert returned and len(selected)==1,('Actual Plane query or unique identity missing',phase,env_id,row)
            hit=selected[0]['hit']; comparison=compare_actual_hit_readonly(reference,hit)
            row['independent_source_reference_comparison']=comparison
            row['original_ideal_Z0_within_1e6']=bool(abs(float(hit['position'][2]))<=1e-6)
            row['original_ideal_normalZ1_within_1e6']=bool(abs(float(hit['normal'][2])-1.0)<=1e-6)
            persist(evidence)
            assert comparison['represented_query_within_original_1e6'],('Independent represented Plane query exceeds unchanged 1e-6',phase,env_id,row)
            assert comparison['normal_crosscheck_maxabs']<=1e-6,('Independent normal crosscheck exceeds unchanged 1e-6',phase,env_id,row)
    assert len(evidence['all_rays'])==160
    evidence['completed_160_actual_rays']=True
    evidence['old_V6_fullcase_failed_unchanged']=True
    persist(evidence)
    return evidence


def run_metadata(args, output, save, manifest, backend):
    import torch
    import mod4_task as task
    from isaaclab.sim import SimulationContext
    from chassis_pd_training_env import ChassisPDMod4Env
    from factor_runtime_3060_reference17b_v1 import params, private_rng
    from omni.physx import get_physx_scene_query_interface
    torch.manual_seed(args.seed)  # Original fixture seeding, outside readonly query phase.
    cfg=task.Mod4EnvCfg();cfg.seed=args.seed;cfg.scene.num_envs=args.num_envs
    cfg.sim.device=args.device;cfg.sim.enable_scene_query_support=True
    for key,value in SMALL_EVAL_CAPACITY.items():setattr(cfg.sim.physics,key,value)
    from isaaclab.sensors import ContactSensorCfg
    cfg.scene.wheel_contact_legacy_capture=ContactSensorCfg(prim_path='{ENV_REGEX_NS}/Robot/links/(left|right)_wheel',update_period=.005,history_length=3,track_air_time=False,debug_vis=False)
    assert args.num_envs==80 and args.seed==20261002 and args.requested_controls==0
    assert cfg.sim.dt==.0025 and cfg.decimation==4
    audit=SDKCallAudit(SimulationContext).install();env=None
    try:
        env=ChassisPDMod4Env(cfg=cfg)
        save('SDK_ENVIRONMENT_INITIALIZATION_ACTUAL.json',dict(exposed_SDK_call_audit=audit.snapshot(),
             native_physical_actors_created_by_original_factory=True,no_policy_actor_constructed=True,
             total_physics_zero_not_claimed=True,original_factory_no_extra_reset=True,
             original_env_sim_step_counter=getattr(env,'_sim_step_counter',None),
             actual_scene_num_envs=env.num_envs,actual_dt=env.physics_dt,actual_step_dt=env.step_dt,
             actual_sim_physics_configuration=plain(cfg.sim.physics.to_dict())))
        audit.phase='readonly_metadata_and_queries'
        before_calls=dict(audit.counts);before_rng=private_rng(env);physical= params(env)
        save('POST_INIT_PHYSICAL_PARAMETERS_AND_CAPTURED_RNG.json',physical)
        stage,path,metadata,reference=actor_metadata_from_USD(env,save)
        source=json.loads(Path(args.xy_input).read_bytes())
        assert hash_file(args.xy_input)==manifest['source_positions']['sha256']
        assert source['source_raw']['sha256']==manifest['source_positions']['source_raw_sha256']
        evidence_path=output/'ACTUAL160_NATIVE_PLANE_QUERY_ALLHITS.json'
        def persist(value):
            temporary=evidence_path.with_suffix('.json.partial')
            with temporary.open('wb') as f:f.write(json.dumps(value,indent=2).encode('utf8'));f.flush();os.fsync(f.fileno())
            os.replace(temporary,evidence_path)
        evidence=query_positions_only(get_physx_scene_query_interface(),source,reference,
                                      lambda h:resolve_plane_hit(stage,path,h),persist)
        after_rng=private_rng(env)
        assert before_rng==after_rng,'Readonly metadata/query phase consumed a captured RNG draw'
        assert before_calls==audit.counts,'Readonly metadata/query phase called extra SDK reset/step/forward/render'
        import omni.physx.bindings._physx as native
        module_file=Path(native.__file__)
        installed=dict(backend_versions=backend['versions'],backend_files_actual=backend['files'],
                       actual_physx_binding=dict(path=str(module_file),bytes=module_file.stat().st_size,sha256=hash_file(module_file)),
                       primary_stub=manifest['actual_primary_stub'],public_source_commit=SOURCE_COMMIT,
                       public_source_to_installed_binary_bitexact_proven=False)
        save('INSTALLED_BACKEND_AND_NATIVE_BINDING_ACTUAL.json',installed)
        save('COMPLETE_ACTUAL.json',dict(epoch=time.time(),case_id=args.case_id,kind='Plane_metadata_query_only',
             fixture_num_envs=80,seed=args.seed,requested_evaluation_controls=0,no_policy_actor_constructed=True,
             no_PPO=True,SDK_initialization_calls_disclosed=audit.snapshot(),total_physics_zero_not_claimed=True,
             actual_metadata=metadata,source_reference=reference,actual_shape_local_pose_read=False,
             public_source_to_installed_binary_bitexact_proven=False,source_reference_only=True,
             all_160_actual_queries_complete=True,captured_RNG_before=before_rng,captured_RNG_after=after_rng,
             query_file=dict(path=str(evidence_path),bytes=evidence_path.stat().st_size,sha256=hash_file(evidence_path)),
             ideal_Z0_failure_count=sum(not r['original_ideal_Z0_within_1e6'] for r in evidence['all_rays']),
             original_V6_fullcase_failed_unchanged=True,three_inherited_skills_complete=False,
             stage_result='INDEPENDENT_METADATA_QUERY_CONSISTENCY_ONLY',old_failed_raw_not_replayed=True,
             no_canonical_budget_operation=True))
    finally:
        audit.phase='SDK_environment_close'
        try:
            if env is not None:env.close()
        finally:audit.restore()
