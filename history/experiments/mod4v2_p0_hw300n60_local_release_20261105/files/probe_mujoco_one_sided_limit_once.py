"""Single existing-engine syntax capability check needed for CAD one-sided hard stops."""
from pathlib import Path
import json,mujoco
out=Path(__file__).resolve().parent/'ENGINE_ONE_SIDED_LIMIT_RECEIPT.json';assert not out.exists()
xml='<mujoco><worldbody><body><joint name="j" type="hinge" limited="true" range="-0.7828277184955518 inf"/><geom type="capsule" size=".01 .1" mass="1"/></body></worldbody></mujoco>'
m=mujoco.MjModel.from_xml_string(xml)
r=dict(mujoco_version=mujoco.__version__,one_sided_hinge_loads=True,joint_limited=bool(m.jnt_limited[0]),lower=float(m.jnt_range[0,0]),upper_is_positive_infinity=bool(m.jnt_range[0,1]==float('inf')),SDK_GPU_models_or_training=False)
out.write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r))
