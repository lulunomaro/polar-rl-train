"""Offline, local native PhysX plane for an isolated flat-floor diagnostic.

This file is not imported by the production task. It creates no robot changes.
Physical floor z=0, native Plane instead of a 4km x 4km x 0.1m scaled Cube.
"""
def spawn_local_native_plane(prim_path,cfg,translation=None,orientation=None,**kwargs):
    from pxr import UsdGeom,UsdPhysics,Sdf
    from isaaclab.sim import get_current_stage,define_collision_properties,bind_physics_material
    stage=get_current_stage()
    root=UsdGeom.Xform.Define(stage,prim_path).GetPrim()
    UsdGeom.Xform.Define(stage,prim_path+'/geometry')
    plane_path=prim_path+'/geometry/mesh'
    plane=stage.DefinePrim(plane_path,'Plane')
    plane.CreateAttribute('axis',Sdf.ValueTypeNames.Token).Set('Z')
    plane.CreateAttribute('width',Sdf.ValueTypeNames.Double).Set(4000.)
    plane.CreateAttribute('length',Sdf.ValueTypeNames.Double).Set(4000.)
    UsdPhysics.CollisionAPI.Apply(plane)
    if cfg.collision_props is not None:define_collision_properties(plane_path,cfg.collision_props,stage=stage)
    if cfg.physics_material is not None:
        material_path=prim_path+'/physicsMaterial'
        cfg.physics_material.func(material_path,cfg.physics_material)
        bind_physics_material(plane_path,material_path,stage=stage)
    return root
