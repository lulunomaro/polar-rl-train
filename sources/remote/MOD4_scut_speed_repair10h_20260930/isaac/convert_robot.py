
# Convert the RL plant (MJCF, closed chain) into an Isaac USD articulation.
#   .venv-isaaclab\Scripts\python.exe isaac/convert_robot.py
import argparse, os, sys, time
ROOT = r'D:/claude2/fangzhen'
sys.path.insert(0, os.path.join(ROOT, 'isaac'))
ap0 = argparse.ArgumentParser()
ap0.add_argument('--xml', default=os.path.join(ROOT, 'robot', 'out_cc_linkfix', 'rm_vehicle_cc.xml'))
ap0.add_argument('--out', default=os.path.join(ROOT, 'isaac', 'assets', 'rm_vehicle_cc.usd'))
a0, rest = ap0.parse_known_args()
from isaaclab.app import AppLauncher
p = argparse.ArgumentParser()
AppLauncher.add_app_launcher_args(p)
args = p.parse_args(args=rest)
al = AppLauncher(args)
app = al.app
t0 = time.time()
from isaaclab.sim.converters import MjcfConverter, MjcfConverterCfg
cfg = MjcfConverterCfg(
    asset_path=a0.xml, usd_dir=os.path.dirname(a0.out), usd_file_name=os.path.basename(a0.out),
    force_usd_conversion=True,
    fix_base=False, self_collision=False, collision_from_visuals=False,
    import_physics_scene=False, link_density=0.0, robot_type='Wheeled', merge_mesh=False)
conv = MjcfConverter(cfg)
print('CONVERTED ->', conv.usd_path, 'in %.1f s' % (time.time() - t0), flush=True)
import omni.usd
from pxr import Usd, UsdPhysics, UsdGeom
stage = omni.usd.get_context().get_stage()
paths = [str(x.GetPath()) for x in Usd.PrimRange(stage.GetPseudoRoot())]
print('prims', len(paths))
joints = [(str(x.GetPath()), x.GetTypeName()) for x in stage.Traverse()
          if x.GetTypeName().startswith(('Revolute', 'Prismatic', 'FixedJoint', 'Sphere', 'RevoluteJoint', 'PrismaticJoint'))]
print('joints', len(joints))
for j in joints[:40]:
    print('   ', j)
app.close()
