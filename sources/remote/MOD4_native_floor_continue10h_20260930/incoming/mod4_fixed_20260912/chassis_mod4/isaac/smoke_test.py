"""Run with Isaac Lab's Python on the target computer; fails on topology loss.

./isaaclab.sh -p /path/to/chassis_mod4/isaac/smoke_test.py --device cuda:0 --num-envs 1
"""
import argparse
from pathlib import Path
import json, math, time, traceback
from isaaclab.app import AppLauncher

parser=argparse.ArgumentParser()
parser.add_argument('--num-envs',type=int,default=1)
parser.add_argument('--steps',type=int,default=6000)
parser.add_argument('--report',default=str(Path(__file__).parent/'runtime_report.json'))
AppLauncher.add_app_launcher_args(parser)
args=parser.parse_args()
if args.steps<1000 or args.num_envs<1:parser.error('Use at least 1000 physics steps and one environment')
launcher=AppLauncher(args);app=launcher.app

import torch
from pxr import Usd, UsdGeom
import isaaclab.sim as sim_utils
from isaaclab.assets import Articulation
from robot_cfg import make_robot_cfg,TorqueInterface,CONTRACT,HERE
from audit_import import audit_stage,RuntimeGuard,audit_runtime_parameters

result={'status':'FAIL','device':args.device,'num_envs':args.num_envs,'steps_requested':args.steps}
try:
    torch.manual_seed(2026)
    sim=sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=CONTRACT['physics_dt_s'],device=args.device,render_interval=20))
    stage=sim_utils.get_current_stage()
    sim.set_camera_view([.9,1.,.7],[0.,0.,.2])
    ground=sim_utils.CuboidCfg(size=(200.,200.,.1),
        collision_props=sim_utils.CollisionPropertiesCfg(),
        physics_material=sim_utils.RigidBodyMaterialCfg(static_friction=.9,dynamic_friction=.9,restitution=0.))
    ground.func('/World/Ground',ground,translation=(0.,0.,-.05))
    light=sim_utils.DomeLightCfg(intensity=2500.);light.func('/World/Light',light)
    # Author individual references so closing-joint relationships are remapped per environment.
    # This startup path intentionally avoids PhysX replication until that path is separately validated.
    origins=[];width=math.ceil(math.sqrt(args.num_envs))
    for i in range(args.num_envs):
        origin=[float(i%width)*2.,float(i//width)*2.,0.];origins.append(origin)
        node=UsdGeom.Xform.Define(stage,f'/World/envs/env_{i}')
        node.AddTranslateOp().Set(tuple(origin))
        cfg=make_robot_cfg(f'/World/envs/env_{i}/Robot')
        cfg.spawn.func(cfg.prim_path,cfg.spawn,translation=cfg.init_state.pos)
        audit_stage(stage,cfg.prim_path,require_physx=True)
    cfg=make_robot_cfg('/World/envs/env_.*/Robot');cfg.spawn=None
    robot=Articulation(cfg);sim.reset();robot.update(CONTRACT['physics_dt_s'])
    if robot.is_fixed_base:raise RuntimeError('Free chassis was imported as fixed base')
    if robot.num_instances!=args.num_envs:raise RuntimeError('Environment count changed during articulation creation')
    interface=TorqueInterface(robot);guard=RuntimeGuard(robot)
    result['parameter_audit']=audit_runtime_parameters(robot)
    origins=torch.tensor(origins,device=sim.device)
    def reset():
        state=robot.data.default_root_state.clone();state[:,:3]+=origins
        robot.write_root_pose_to_sim(state[:,:7]);robot.write_root_velocity_to_sim(state[:,7:])
        robot.write_joint_state_to_sim(robot.data.default_joint_pos.clone(),robot.data.default_joint_vel.clone())
        robot.reset();interface.apply(torch.zeros((args.num_envs,6),device=sim.device));robot.write_data_to_sim()
    reset();start=time.perf_counter();resets=1
    for step in range(args.steps):
        if not app.is_running():raise RuntimeError('Application closed before acceptance run finished')
        if step and step%1000==0:reset();resets+=1
        q=robot.data.joint_pos[:,interface.motor_ids];v=robot.data.joint_vel[:,interface.motor_ids]
        t=step*CONTRACT['physics_dt_s']
        if step<args.steps//3:
            target=torch.zeros_like(q);target[:,[0,1,3,4]]=.12*math.sin(t*3)
            command=(45*(target-q)-2*v)/interface.limits
            command[:,[2,5]]=.1*math.sin(t*5)
        elif step<2*args.steps//3:
            if step%40==0 or 'command' not in locals():command=torch.rand_like(q)*2-1
        else:
            if step%200==0:command=(torch.randint(0,2,q.shape,device=sim.device)*2-1).float()
        interface.apply(command);robot.write_data_to_sim()
        sim.step(render=(not args.headless and step%20==0));robot.update(CONTRACT['physics_dt_s'])
        # [handoff 2026-09-12 §1.3] Firmware-style limit: PhysX joint limits are compliant, so the
        # crank-hip couple is clamped right after every physics step, exactly where a real
        # controller would refuse to keep driving into the CAD stop.
        interface._enforce_coupling(training=False)
        robot.write_data_to_sim()
        guard.check()
    result.update(status='PASS_RUNTIME_BOUNDED',steps_completed=args.steps,resets=resets,
        max_closure_error_m=guard.max_closure,max_chain_error_rad=guard.max_mimic,
        min_input_difference_rad=guard.min_difference,
        elapsed_seconds=time.perf_counter()-start,
        source_mjcf_sha256=CONTRACT['source_mjcf_sha256'],
        scope='PhysX runtime acceptance only for this engine/device/count/dt. Increase environment count and rerun before PPO.')
except Exception as exc:
    result['error']=str(exc);result['traceback']=traceback.format_exc()
    raise
finally:
    Path(args.report).write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result,indent=2));app.close()
