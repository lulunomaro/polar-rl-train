"""Create 1..1024 full-arena instances with matching environment origins.

Run with usd-core locally, or Isaac Sim's Python. Geometry is referenced, not copied.
"""
from pathlib import Path
import argparse,json,math
from pxr import Usd,UsdGeom,Gf

ROOT=Path(__file__).resolve().parents[1]

def build_layout(num_envs=1024):
    if not 1<=num_envs<=1024:raise ValueError('Supported packaged layout range: 1..1024')
    cols=math.ceil(math.sqrt(num_envs));rows=math.ceil(num_envs/cols)
    spacing=[34.,20.]
    path=ROOT/f'maps/arena_{num_envs}.usda'
    stage=Usd.Stage.CreateNew(str(path))
    UsdGeom.SetStageUpAxis(stage,'Z');UsdGeom.SetStageMetersPerUnit(stage,1.)
    root=UsdGeom.Xform.Define(stage,'/Terrain');stage.SetDefaultPrim(root.GetPrim())
    origins=[]
    for i in range(num_envs):
        row,col=divmod(i,cols)
        origin=[(row-(rows-1)/2)*spacing[0],(col-(cols-1)/2)*spacing[1],0.]
        obj=UsdGeom.Xform.Define(stage,f'/Terrain/env_{i:04}')
        obj.GetPrim().GetReferences().AddReference('arena.usda')
        obj.AddTranslateOp().Set(Gf.Vec3d(*origin))
        obj.GetPrim().SetInstanceable(True)
        origins.append(origin)
    stage.GetRootLayer().Save()
    manifest=dict(num_envs=num_envs,rows=rows,cols=cols,spacing_xy_m=spacing,origins=origins,
                  usd_file=path.name,geometry='one shared arena prototype, complete locomotion terrain in EVERY environment',
                  runtime_tested=False,performance_note='1024 placement and reference sharing are verified offline; GPU/PhysX throughput must be measured on target hardware.')
    path.with_suffix('.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    return path

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--num-envs',type=int,default=1024)
    print(build_layout(ap.parse_args().num_envs))
