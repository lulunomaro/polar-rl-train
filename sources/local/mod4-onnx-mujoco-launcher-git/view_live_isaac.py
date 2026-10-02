"""Render live Isaac body poses in MuJoCo. Never advances MuJoCo physics."""
from __future__ import annotations

import argparse
from pathlib import Path
import time

import mujoco
import numpy as np

from playback_ipc import atomic_json, read_json


def body_mapping(model):
    if model.nq or model.nv or not model.nmocap:
        raise ValueError('Live display must contain only mocap bodies, without dynamic joints')
    return {mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, i): int(model.body_mocapid[i])
            for i in range(1, model.nbody) if model.body_mocapid[i] >= 0}


def update_pose(model, data, mapping, value):
    poses = value['body_world_poses']
    if set(poses) != set(mapping):
        raise ValueError('Live body set differs from source USD display')
    # Validate the entire packet before mutating any displayed body.
    arrays = {name: np.asarray(pose, dtype=float) for name, pose in poses.items()}
    for pose in arrays.values():
        if pose.shape != (7,) or not np.isfinite(pose).all() or abs(np.linalg.norm(pose[3:]) - 1) > .01:
            raise ValueError('Invalid XYZ + WXYZ pose')
    for name, pose in arrays.items():
        data.mocap_pos[mapping[name]] = pose[:3]
        data.mocap_quat[mapping[name]] = pose[3:]
    data.time = float(value['sim_time_s'])
    mujoco.mj_forward(model, data)
    return max(float(np.linalg.norm(data.xpos[mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, name)] - pose[:3]))
               for name, pose in arrays.items())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--telemetry', type=Path, required=True)
    parser.add_argument('--command-file', type=Path, required=True)
    parser.add_argument('--session-id', required=True)
    args = parser.parse_args()
    model = mujoco.MjModel.from_xml_path(str(args.model))
    data = mujoco.MjData(model)
    mapping = body_mapping(model)
    while True:
        if read_json(args.command_file).get('quit'):
            return
        value = read_json(args.telemetry)
        if value.get('session_id') == args.session_id and 'body_world_poses' in value:
            break
        time.sleep(.1)
    update_pose(model, data, mapping, value)
    from mujoco import viewer as mj_viewer
    with mj_viewer.launch_passive(model, data, show_left_ui=False, show_right_ui=False) as viewer:
        viewer.cam.type = mujoco.mjtCamera.mjCAMERA_FREE
        viewer.cam.distance, viewer.cam.azimuth, viewer.cam.elevation = 1.3, 135, -20
        while viewer.is_running():
            if read_json(args.command_file).get('quit'):
                break
            value = read_json(args.telemetry)
            if value.get('session_id') == args.session_id and 'body_world_poses' in value:
                error = update_pose(model, data, mapping, value)
                viewer.cam.lookat[:] = value['root_xyz']
                atomic_json(args.telemetry.parent / 'display_status.json', dict(
                    session_id=args.session_id, updated_epoch=time.time(), body_count=len(mapping),
                    position_error_m=error, sim_time_s=value['sim_time_s'], physics='Isaac PhysX; MuJoCo display only'))
            viewer.sync()
            time.sleep(1 / 60)


if __name__ == '__main__':
    main()
