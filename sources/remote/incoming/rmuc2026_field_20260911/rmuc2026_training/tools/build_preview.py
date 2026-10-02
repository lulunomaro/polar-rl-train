"""Build a single-arena USD viewing scene. No extra ground plane is added."""
from pathlib import Path
from pxr import Usd,UsdGeom,UsdLux,UsdPhysics,Gf

ROOT=Path(__file__).resolve().parents[1]

def main():
    stage=Usd.Stage.CreateNew(str(ROOT/'maps/arena_preview.usda'))
    UsdGeom.SetStageUpAxis(stage,'Z');UsdGeom.SetStageMetersPerUnit(stage,1.)
    root=UsdGeom.Xform.Define(stage,'/World');stage.SetDefaultPrim(root.GetPrim())
    arena=UsdGeom.Xform.Define(stage,'/World/Arena')
    arena.GetPrim().GetReferences().AddReference('arena.usda')
    sky=UsdLux.DomeLight.Define(stage,'/World/Sky');sky.CreateIntensityAttr(800.)
    sun=UsdLux.DistantLight.Define(stage,'/World/Sun');sun.CreateIntensityAttr(2000.)
    sun.CreateAngleAttr(.8);sun.AddRotateXYZOp().Set(Gf.Vec3f(-35.,-25.,-25.))
    camera=UsdGeom.Camera.Define(stage,'/World/Overview')
    view=Gf.Matrix4d().SetLookAt(Gf.Vec3d(22.,-26.,23.),Gf.Vec3d(0,0,0),Gf.Vec3d(0,0,1))
    camera.AddTransformOp().Set(view.GetInverse());camera.CreateFocalLengthAttr(30.)
    camera.CreateClippingRangeAttr(Gf.Vec2f(.05,200.))
    scene=UsdPhysics.Scene.Define(stage,'/World/PhysicsScene')
    scene.CreateGravityDirectionAttr(Gf.Vec3f(0,0,-1));scene.CreateGravityMagnitudeAttr(9.81)
    stage.GetRootLayer().Save()

if __name__=='__main__':main()
