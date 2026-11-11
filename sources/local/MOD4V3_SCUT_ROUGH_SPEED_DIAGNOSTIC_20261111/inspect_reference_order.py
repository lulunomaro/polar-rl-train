"""Inspect original SCUT articulation DOF order without stepping or training."""
from pathlib import Path
import os,json,sys,traceback
base=Path(__file__).resolve().parent;plan=json.loads((base/'PLAN.json').read_text());out=base/'inspect_reference_order_r1';out.mkdir(exist_ok=False)
storage=out/'kit_isolation';(storage/'data').mkdir(parents=True);(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
os.environ.update(MOD4V1_E0_JOB_ROOT=str(out),MOD4V1_E0_KIT_STORAGE_ROOT=str(storage));sys.path.insert(0,plan['runtime'])
from launcher_mod4v1_e0 import IsolatedAppLauncher208
app=IsolatedAppLauncher208(dict(headless=True,device='cuda:0',enable_cameras=False)).app
try:
 import isaaclab.sim as sim_utils
 from isaaclab.assets import Articulation,ArticulationCfg
 sim=sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=.005,device='cuda:0'))
 source='/home/egde/fangzhen_linux/refs/wheeled-legged_RL-main/source/agent_world/agent_world/assets/usd_files/wheelbipeV14_2_1/wheelbipeV14_2.usd'
 cfg=ArticulationCfg(prim_path='/World/Reference',spawn=sim_utils.UsdFileCfg(usd_path=source),actuators={})
 robot=Articulation(cfg);sim.reset()
 names=list(robot.joint_names);idx,legs=robot.find_joints(['.*_rear1_joint','.*_front1_joint']);wi,wheels=robot.find_joints('.*_wheel_joint')
 value=dict(source_asset=source,joint_names=names,active_legs=legs,active_wheels=wheels,policy_order=legs+wheels,no_physics_steps=True,no_optimizer=True)
 (out/'RESULT.json').write_text(json.dumps(value,indent=2));print('REFERENCE_ORDER_RESULT',json.dumps(value))
except BaseException:
 (out/'ERROR.json').write_text(json.dumps(dict(traceback=traceback.format_exc())));raise
finally:
 (out/'SAFE_CLOSED.json').write_text(json.dumps(dict(result=(out/'RESULT.json').exists(),error=(out/'ERROR.json').exists())))
 app.close()
