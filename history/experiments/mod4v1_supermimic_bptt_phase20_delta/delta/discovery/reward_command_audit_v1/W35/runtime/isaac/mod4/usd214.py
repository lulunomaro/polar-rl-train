"""Deferred pxr-only original mesh/material composition; no binary read here."""
from pathlib import Path
import json
from material214 import GEOMETRY_PRIM,MATERIAL_PRIM,plan,log


def author_original_shared_material_layout(root,output,origins):
    from pxr import Usd,UsdGeom,UsdShade,Gf
    root=Path(root);output=Path(output);asset=root/'assets/arena_collision.usdc'
    # One geometry-only prototype excludes the original sibling material. All
    # original authored points,faces,collision API and contact/rest offsets come
    # from the exact same immutable CAD mesh prim,with no regeneration.
    proto=output/'original_CAD_geometry_only.usda'
    ps=Usd.Stage.CreateNew(str(proto));UsdGeom.SetStageUpAxis(ps,'Z');UsdGeom.SetStageMetersPerUnit(ps,1.)
    proot=UsdGeom.Xform.Define(ps,'/Prototype');ps.SetDefaultPrim(proot.GetPrim())
    mesh=UsdGeom.Mesh.Define(ps,'/Prototype/mesh')
    mesh.GetPrim().GetReferences().AddReference(str(asset),GEOMETRY_PRIM)
    # Block the subprim's now-outside-scope sibling relationship. The inherited
    # strong root binding below supplies the original material once for all.
    mesh.GetPrim().CreateRelationship('material:binding:physics',custom=False).SetTargets([])
    ps.GetRootLayer().Save()
    path=output/'full_RM70_layout.usda';stage=Usd.Stage.CreateNew(str(path))
    UsdGeom.SetStageUpAxis(stage,'Z');UsdGeom.SetStageMetersPerUnit(stage,1.)
    terrain=UsdGeom.Xform.Define(stage,'/Terrain');stage.SetDefaultPrim(terrain.GetPrim())
    shared=UsdShade.Material.Define(stage,'/Terrain/shared_original_physics_material')
    shared.GetPrim().GetReferences().AddReference(str(asset),MATERIAL_PRIM)
    UsdShade.MaterialBindingAPI.Apply(terrain.GetPrim()).Bind(shared,
        bindingStrength=UsdShade.Tokens.strongerThanDescendants,materialPurpose='physics')
    for index,origin in enumerate(origins):
        obj=UsdGeom.Xform.Define(stage,'/Terrain/env_'+str(index).zfill(5))
        obj.GetPrim().GetReferences().AddReference(str(proto))
        obj.AddTranslateOp().Set(Gf.Vec3d(*origin));obj.GetPrim().SetInstanceable(True)
    stage.GetRootLayer().Save()
    metadata=dict(plan(len(origins)),new_layout=str(path),geometry_only_prototype=str(proto),
        original_asset=str(asset),original_material_reference_not_coefficient_rewrite=True)
    (output/'MATERIAL214_COMPOSITION_PLAN.json').write_text(json.dumps(metadata,indent=2))
    log('NEW_LAYOUT_AUTHORED',**metadata)
    return path


def material_census(stage,prim_root='/World/ground'):
    """Full terrain proxy composition counts,not PhysX material allocation IDs."""
    from pxr import Usd,UsdGeom,UsdPhysics,UsdShade
    root=stage.GetPrimAtPath(prim_root)
    if not root or not root.IsValid():
        return dict(status='UNKNOWN_TERRAIN_ROOT_ABSENT',prim_root=prim_root,
                    PhysX_material_handles='UNKNOWN')
    definitions=[];bindings=set();signatures={};meshes=0;missing=0
    for prim in Usd.PrimRange(root,Usd.TraverseInstanceProxies()):
        if prim.HasAPI(UsdPhysics.MaterialAPI):definitions.append(str(prim.GetPath()))
        if not prim.IsA(UsdGeom.Mesh) or not prim.HasAPI(UsdPhysics.CollisionAPI):continue
        meshes+=1
        material,relationship=UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial(materialPurpose='physics')
        if not material or not material.GetPrim().IsValid():missing+=1;continue
        path=str(material.GetPath());bindings.add(path)
        if path not in signatures:
            attrs={}
            for attribute in material.GetPrim().GetAttributes():
                name=attribute.GetName()
                if name.startswith(('physics:','physxMaterial:')):
                    value=attribute.Get()
                    attrs[name]=value if type(value)in(str,int,float,bool,type(None))else repr(value)
            signatures[path]=attrs
    return dict(status='ACTUAL_TERRAIN_USD_COMPOSITION_ONLY',prim_root=prim_root,
        traversed_instance_proxy_collision_meshes=meshes,material_API_prim_paths=definitions,
        material_API_prim_count=len(definitions),distinct_bound_material_paths=sorted(bindings),
        bound_material_attributes=signatures,missing_material_bindings=missing,
        material_value_signatures=len({json.dumps(v,sort_keys=True)for v in signatures.values()}),
        PhysX_material_handle_count='UNKNOWN_NOT_STAGE_PRIM_COUNT',
        no_contact_or_material_API_setter_called=True)
