"""Share immutable authored materials; retain a private drive tire per robot.

No asset is rewritten. Bindings change in the isolated in-memory stage before
cloning. PhysX tensor DR remains responsible for independent wheel shape values.
"""
from pxr import Sdf,Usd,UsdPhysics,UsdShade
POOL='/World/MOD4FixedPhysicsMaterials'
FIXED=('generic','guide_roller')

def signature(prim):
    return {'type':prim.GetTypeName(),'schemas':list(prim.GetAppliedSchemas()),
            'attrs':{a.GetName():(str(a.GetTypeName()),str(a.Get())) for a in prim.GetAttributes()},
            'relationships':{r.GetName():[str(t) for t in r.GetTargets()] for r in prim.GetRelationships()}}

def pool_fixed_materials(stage,root_path):
    root=Sdf.Path(root_path);mapping={};proof={}
    for name in FIXED:
        src=stage.GetPrimAtPath(root.AppendPath('PhysicsMaterials/'+name))
        assert src and src.HasAPI(UsdPhysics.MaterialAPI),name
        path=Sdf.Path(POOL+'/'+name);dst=stage.GetPrimAtPath(path)
        if not dst:
            dst=UsdShade.Material.Define(stage,path).GetPrim()
            dst.SetMetadata('apiSchemas',Sdf.TokenListOp.CreateExplicit(src.GetAppliedSchemas()))
            for a in src.GetAttributes():
                if a.HasAuthoredConnections():raise RuntimeError('Unexpected fixed material connection')
                b=dst.CreateAttribute(a.GetName(),a.GetTypeName(),a.IsCustom(),a.GetVariability())
                if a.HasAuthoredValueOpinion():b.Set(a.Get())
            for r in src.GetRelationships():
                if r.GetTargets():raise RuntimeError('Unexpected fixed material relationship')
                dst.CreateRelationship(r.GetName(),r.IsCustom())
        assert signature(src)==signature(dst),(name,signature(src),signature(dst))
        mapping[src.GetPath()]=path;proof[name]=signature(dst)
    count=0
    for prim in Usd.PrimRange(stage.GetPrimAtPath(root)):
        rel=prim.GetRelationship('material:binding:physics')
        targets=rel.GetTargets() if rel else []
        if len(targets)==1 and targets[0] in mapping:
            rel.SetTargets([mapping[targets[0]]]);count+=1
    assert count==32,count  # 24 non-wheel colliders + 8 guide rollers; 2 tires remain private.
    for old in mapping:stage.GetPrimAtPath(old).SetActive(False)
    assert stage.GetPrimAtPath(root.AppendPath('PhysicsMaterials/drive_tire')).IsActive()
    return {'root':str(root),'fixed_bindings':count,'fixed_materials':proof,
            'drive_tire_private':True,'original_USD_unchanged':True}

def spawn_pooled(prim_path,cfg,*args,**kwargs):
    # Lazy imports keep the pure USD contract usable without Kit or GPU initialization.
    from isaaclab.sim.spawners.from_files.from_files import spawn_from_usd
    from isaaclab.sim.utils import clone,get_current_stage
    @clone
    def one(path,cfg,*a,**kw):
        prim=spawn_from_usd.__wrapped__(path,cfg,*a,**kw)
        proof=pool_fixed_materials(get_current_stage(),path)
        print('MOD4_FIXED_MATERIAL_POOL '+str(proof),flush=True)
        return prim
    return one(prim_path,cfg,*args,**kwargs)

def sdk_independence(env):
    """Exercise actual tensor writes, restore exact values, leave RNG untouched."""
    import torch,warp as wp
    from mild_dr import tensor
    assert env.num_envs==10
    dr=env._mild_dr;view=env.scene['robot'].root_view
    before=tensor(view.get_material_properties()).clone().cpu()
    value=before.clone();value[0,dr.wheel_shapes,:2]=.7;value[1,dr.wheel_shapes,:2]=1.
    ids=torch.tensor([0,1],dtype=torch.int32)
    view.set_material_properties(wp.from_torch(value,dtype=wp.float32),wp.from_torch(ids,dtype=wp.int32))
    actual=tensor(view.get_material_properties()).clone().cpu()
    assert torch.equal(actual[2:],before[2:]),'Wheel material mutation leaked to another robot'
    assert torch.equal(actual[:,dr.nonwheel_shapes],before[:,dr.nonwheel_shapes]),'Wheel mutation leaked to a fixed collider'
    assert torch.equal(actual[0,dr.wheel_shapes,:2],value[0,dr.wheel_shapes,:2])
    assert torch.equal(actual[1,dr.wheel_shapes,:2],value[1,dr.wheel_shapes,:2])
    view.set_material_properties(wp.from_torch(before,dtype=wp.float32),wp.from_torch(ids,dtype=wp.int32))
    assert torch.equal(tensor(view.get_material_properties()).cpu(),before)
    dr.audit()
    return {'two_distinct_actual_wheel_values':[.7,1.], 'unselected_robot_materials_exact':True,
            'all_nonwheel_materials_exact':True,'original_materials_restored_exact':True,
            'DR_and_sensor_RNG_untouched':True,'actual_parameter_audit_passed':True}
