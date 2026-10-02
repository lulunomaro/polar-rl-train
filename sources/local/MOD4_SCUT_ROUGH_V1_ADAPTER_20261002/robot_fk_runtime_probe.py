"""One robot, no policy/PPO: compare USD CPU FK against PhysX link poses.

Gravity is disabled only in this isolated probe. No production task is edited.
This checks joint frames/q ordering before a terrain reset adapter is installed.
"""
import argparse,json,time,faulthandler,sys
from pathlib import Path
faulthandler.enable()
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--production-root',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(p)
a=p.parse_args();launcher=AppLauncher(a);app=launcher.app

import numpy as np
import torch
from pxr import Gf
from isaaclab.sim import SimulationCfg,SimulationContext
from isaaclab_physx.physics import PhysxCfg
from isaaclab.assets import Articulation
from rough_reset_geometry import CollisionFK,quat_matrix
sys.path.insert(0,str(a.production_root/'isaac/mod4'))
import mod4_task


def run():
    sim=SimulationContext(SimulationCfg(dt=.0005,device=a.device,
                          physics=PhysxCfg(enable_external_forces_every_iteration=True)))
    cfg=mod4_task.mod4_robot_cfg('/World/Robot')
    cfg.spawn.rigid_props.disable_gravity=True
    robot=Articulation(cfg)
    sim.reset()
    model=CollisionFK(mod4_task.USD_PATH)
    bank=json.loads((a.production_root/'isaac/mod4/reset_bank.json').read_text())
    samples=[0,16,32,64,96,116,132]
    rows=[]
    for sample in samples:
        qdict=bank['poses'][sample]['joint_pos'].copy()
        qdict['left_wheel_spin']=.731;qdict['right_wheel_spin']=-.923
        for k in range(8):qdict[f'guide_roller_{k:02}']=.123*k
        q=torch.tensor([[qdict.get(n,0.) for n in robot.joint_names]],device=sim.device)
        robot.write_joint_state_to_sim(q,torch.zeros_like(q))
        state=torch.zeros((1,13),device=sim.device);state[:,2]=2.;state[:,6]=1.
        robot.write_root_state_to_sim(state)
        sim.forward();robot.update(.0005)
        positions=robot.data.body_link_pos_w[0].detach().cpu().numpy()
        rotations=robot.data.body_link_quat_w[0].detach().cpu().numpy()
        expected=model.forward(qdict)
        by_name={Path(k).name:v for k,v in expected.items()}
        err_pos=[];err_rot=[]
        for i,name in enumerate(robot.body_names):
            x,y,z,w=rotations[i]
            rot=quat_matrix(Gf.Quatd(float(w),Gf.Vec3d(float(x),float(y),float(z))))
            err_pos.append(float(np.max(np.abs(positions[i]-np.array([0.,0.,2.])-by_name[name][:3,3]))))
            err_rot.append(float(np.max(np.abs(rot-by_name[name][:3,:3]))))
        q_actual=robot.data.joint_pos[0].detach().cpu().numpy()
        rows.append(dict(pose_index=sample,root_height_reference_m=bank['poses'][sample]['root_height_m'],
            max_link_position_error_m=max(err_pos),max_rotation_matrix_error=max(err_rot),
            max_joint_writeback_error_si=float(np.max(np.abs(q_actual-q[0].cpu().numpy())))))
    result=dict(stage='ISOLATED_PHYSX_LINK_FK_COMPARISON',created_epoch=time.time(),
                pass_=all(r['max_link_position_error_m']<2e-6 and r['max_rotation_matrix_error']<2e-5
                          and r['max_joint_writeback_error_si']<1e-6 for r in rows),
                joint_count=len(robot.joint_names),body_count=len(robot.body_names),
                joint_names=robot.joint_names,body_names=robot.body_names,rows=rows,
                q_units='revolute rad/prismatic m',quaternion_order='runtime xyzw/USD real+imaginary',
                gravity_disabled_for_probe_only=True,policy_started=False,ppo_started=False,
                production_modified=False,terrain_reset_installed=False,
                scope='PhysX kinematics before dynamics; not a support/contact/Rough skill acceptance')
    a.output.write_text(json.dumps(result,indent=2))
    print('ROBOT_FK_RESULT',json.dumps(result),flush=True)
    if not result['pass_']:raise RuntimeError('Independent PhysX FK comparison failed')


try:
    run()
except Exception as e:
    import traceback
    a.output.with_suffix('.error.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc())))
    traceback.print_exc()
    raise
finally:
    app.close()
