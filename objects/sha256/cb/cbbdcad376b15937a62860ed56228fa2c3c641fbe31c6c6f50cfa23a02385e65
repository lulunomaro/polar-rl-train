"""MuJoCo graphics for streamed Isaac body poses. Never calls mj_step."""
from pathlib import Path
import argparse
import json
import time
import mujoco
import mujoco.viewer
import numpy as np

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--since',type=float,default=time.time())
args=parser.parse_args()
model=mujoco.MjModel.from_xml_path(str(ROOT/'display/live_display.xml'));data=mujoco.MjData(model)
assert model.nq==0 and model.nv==0 and model.nmocap==31
mapping={mujoco.mj_id2name(model,mujoco.mjtObj.mjOBJ_BODY,i):int(model.body_mocapid[i])
         for i in range(1,model.nbody)if model.body_mocapid[i]>=0}
last=None
while True:
    try:
        if json.loads((ROOT/'operator_command.json').read_text()).get('quit'):raise SystemExit
        value=json.loads((ROOT/'isaac_telemetry.json').read_text())
        if value.get('updated_epoch',0)>args.since and 'body_world_poses' in value:last=value;break
    except (OSError,ValueError):pass
    time.sleep(.1)


def update_pose(value):
    poses=value['body_world_poses']
    assert set(poses)==set(mapping), 'Live body set differs from source USD display'
    for name,pose in poses.items():
        index=mapping[name];data.mocap_pos[index]=pose[:3];data.mocap_quat[index]=pose[3:]
    data.time=value['sim_time_s'];mujoco.mj_forward(model,data)
    # Independent display check: transform error must remain floating-point small.
    error=max(float(np.linalg.norm(data.xpos[mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_BODY,name)]-pose[:3]))
              for name,pose in poses.items())
    return error

error=update_pose(last)
print(f'LIVE_DISPLAY_READY body_count={len(mapping)} pose_position_error_m={error:.3g} source=Isaac_PhysX',flush=True)
with mujoco.viewer.launch_passive(model,data,show_left_ui=False,show_right_ui=False)as viewer:
    viewer.cam.type=mujoco.mjtCamera.mjCAMERA_FREE
    viewer.cam.distance=1.3;viewer.cam.azimuth=135;viewer.cam.elevation=-20
    while viewer.is_running():
        try:
            if json.loads((ROOT/'operator_command.json').read_text()).get('quit'):break
            value=json.loads((ROOT/'isaac_telemetry.json').read_text())
            if value.get('updated_epoch',0)>args.since and 'body_world_poses' in value:
                error=update_pose(value);viewer.cam.lookat[:]=value['root_xyz']
                (ROOT/'display_status.json').write_text(json.dumps({'epoch':time.time(),'body_count':31,
                    'position_error_m':error,'sim_time_s':value['sim_time_s'],
                    'physics':'Isaac Lab PhysX; MuJoCo display only'}),encoding='utf8')
        except (OSError,ValueError):pass
        viewer.sync();time.sleep(1/60)
