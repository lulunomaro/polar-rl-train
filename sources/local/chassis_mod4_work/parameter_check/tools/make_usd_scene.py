"""Standalone USD scene for inspection; robot.usd remains the training asset."""
from pathlib import Path
import json
from pxr import Usd,UsdGeom,UsdPhysics,UsdLux,UsdShade,Gf
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'isaac'
c=json.loads((OUT/'import_contract.json').read_text())
stage=Usd.Stage.CreateNew(str(OUT/'scene.usda'))
UsdGeom.SetStageUpAxis(stage,'Z');UsdGeom.SetStageMetersPerUnit(stage,1.)
world=UsdGeom.Xform.Define(stage,'/World');stage.SetDefaultPrim(world.GetPrim())
scene=UsdPhysics.Scene.Define(stage,'/World/PhysicsScene');scene.CreateGravityDirectionAttr(Gf.Vec3f(0,0,-1));scene.CreateGravityMagnitudeAttr(9.81)
robot=UsdGeom.Xform.Define(stage,'/World/Robot');robot.GetPrim().GetReferences().AddReference('robot.usd','/Robot')
robot.AddTranslateOp().Set(Gf.Vec3d(0,0,c['spawn_height_m']))
floor=UsdGeom.Cube.Define(stage,'/World/Ground');floor.CreateSizeAttr(1.)
floor.AddTranslateOp().Set(Gf.Vec3d(0,0,-.05));floor.AddScaleOp().Set(Gf.Vec3f(20,20,.1))
floor.CreateDisplayColorAttr([Gf.Vec3f(.21,.25,.28)]);UsdPhysics.CollisionAPI.Apply(floor.GetPrim())
mat=UsdShade.Material.Define(stage,'/World/FloorMaterial');mp=UsdPhysics.MaterialAPI.Apply(mat.GetPrim())
mp.CreateStaticFrictionAttr(.9);mp.CreateDynamicFrictionAttr(.9);mp.CreateRestitutionAttr(0.)
UsdShade.MaterialBindingAPI.Apply(floor.GetPrim()).Bind(mat,materialPurpose='physics')
UsdLux.DomeLight.Define(stage,'/World/DomeLight').CreateIntensityAttr(1000.)
light=UsdLux.DistantLight.Define(stage,'/World/KeyLight');light.CreateIntensityAttr(2500.);light.AddRotateXYZOp().Set(Gf.Vec3f(-35,25,0))
camera=UsdGeom.Camera.Define(stage,'/World/Camera');camera.CreateFocalLengthAttr(35.)
camera.CreateClippingRangeAttr(Gf.Vec2f(.01,100.));matrix=Gf.Matrix4d().SetLookAt(Gf.Vec3d(.9,-.9,.7),Gf.Vec3d(0,0,.27),Gf.Vec3d(0,0,1)).GetInverse()
camera.AddTransformOp().Set(matrix)
stage.GetRootLayer().Save()
bound=UsdGeom.BBoxCache(0.,['default']).ComputeWorldBound(floor.GetPrim()).ComputeAlignedRange()
assert abs(bound.GetMax()[2])<1e-7,(bound.GetMin(),bound.GetMax())
print('Standalone scene:',OUT/'scene.usda')
