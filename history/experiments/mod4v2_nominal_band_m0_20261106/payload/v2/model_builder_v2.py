"""P0 MOD4v2 robot + unchanged latest user CAD, not a v1 robot replacement.
No controller/step/SDK import at build time. Extra flat is linearization only.
"""
from pathlib import Path
import hashlib,sys,xml.etree.ElementTree as ET
import numpy as np
import mujoco
ROOT=Path(__file__).resolve().parent
V1=ROOT.parent/'mod4v1_lqr_mpc_robust_20261102'
PACKAGE=ROOT.parent/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package'
SOURCE=PACKAGE/'mjcf/scene.xml'
SOURCE_SHA='c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125'
sys.path.insert(0,str(V1))
from RM_FPS_PLAYER_V1.terrain import _latest_scene,_box

def build_model(scene='latest_rm',difficulty=.5,seed=520110,imu_offset=(.03,0.,.04)):
 if scene not in ('latest_rm','flat'):raise ValueError('Explicit latest_rm or extra linearization flat only')
 raw=SOURCE.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError('P0 MJCF identity changed')
 xml=ET.fromstring(raw);compiler=xml.find('compiler');asset=xml.find('asset');wb=xml.find('worldbody')
 meshbase=(SOURCE.parent/compiler.get('meshdir','')).resolve();texbase=(SOURCE.parent/compiler.get('texturedir','')).resolve()
 for item in asset:
  if item.get('file'):
   path=((meshbase if item.tag=='mesh' else texbase)/item.get('file')).resolve()
   if not path.is_file():raise ValueError('Missing P0 asset '+str(path))
   item.set('file',str(path))
 compiler.set('meshdir',str(meshbase));compiler.set('texturedir',str(texbase))
 xml.find('option').set('timestep','.0005');xml.find('option').set('iterations','100')
 xml.find('option').set('integrator','implicitfast');xml.find('option').set('solver','Newton')
 xml.find('.//site[@name="imu"]').set('pos',' '.join(map(str,imu_offset)))
 robot_before=ET.tostring(wb.find('body[@name="chassis"]'))
 constants_before=[ET.tostring(xml.find(t)) for t in ('default','actuator','equality')]
 for g in list(wb.findall('geom')):wb.remove(g)
 meta=dict(scene=scene,model_source=str(SOURCE),model_SHA=SOURCE_SHA,robot_version='MOD4v2-HW300N60',
  physics_dt_s=.0005,control_dt_s=.01,source_physics_dt_s=.0025,source_iterations=32,configured_iterations=100,
  imu_offset_m=list(imu_offset),nominal_gas_N=300,stroke_mm=60,eye_distance_mm=[140,200],
  gas_force_curve_calibrated=False,old_v1_model_used=False,Isaac_PhysX_runtime_equivalence=False,
  collision_representation='P0 authored cylinders for tires (r=.0625,halfwidth=.01) and guides (r=.015); body meshes retained; NOT v1 faceted tire meshes',
  difficulty=float(difficulty),seed=int(seed),new_physics_steps=0)
 if scene=='latest_rm':
  zones,latest=_latest_scene(wb,asset);meta.update(latest);meta['zones']=zones
 else:
  _box(wb,'ground',(-50.,50.,-50.,50.),color=(.44,.48,.53,1.))
  meta.update(zones=[dict(key='linearization_flat_fixture',spawn=[0.,0.,0.],yaw=0.)],
   origin_spawn=[0.,0.,0.],extra_flat_fixture=True,not_CAD_acceptance=True)
 if ET.tostring(wb.find('body[@name="chassis"]'))!=robot_before or constants_before!=[ET.tostring(xml.find(t))for t in ('default','actuator','equality')]:raise AssertionError('Unexpected P0 robot/constraint edit')
 m=mujoco.MjModel.from_xml_string(ET.tostring(xml,encoding='unicode'))
 if (m.nbody,m.nq,m.nv,m.nu,m.neq)!=(32,37,36,6,10):raise ValueError('Wrong complete robot dimensions')
 if scene=='latest_rm':m.opt.disableflags|=int(mujoco.mjtDisableBit.mjDSBL_MULTICCD)
 meta.update(compiled_nbody=m.nbody,compiled_ngeom=m.ngeom,compiled_nmesh=m.nmesh,
  dimensions=[m.nq,m.nv,m.nu],neq=m.neq,mass_kg=float(m.body_mass.sum()),
  latest_rm_MULTICCD_disabled=(scene=='latest_rm'),compiled_gravity=m.opt.gravity.tolist())
 return m,meta
