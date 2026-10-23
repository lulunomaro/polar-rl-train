"""Publish complete camera settings under the passive viewer's render lock."""
import mujoco


def set_player_camera(viewer, chassis_id, overview):
    with viewer.lock():
        if not 0 <= chassis_id < viewer.m.nbody:
            raise ValueError(f'Invalid camera body {chassis_id} for {viewer.m.nbody} bodies')
        # Install a valid body before enabling tracking. The render thread must
        # never observe mjCAMERA_TRACKING with the default trackbodyid=-1.
        viewer.cam.trackbodyid = chassis_id
        if overview:
            viewer.cam.type = mujoco.mjtCamera.mjCAMERA_FREE
            viewer.cam.lookat[:] = [0, 0, .3]
            viewer.cam.distance = 24
            viewer.cam.azimuth = 110
            viewer.cam.elevation = -65
        else:
            viewer.cam.distance = 2.4
            viewer.cam.azimuth = 140
            viewer.cam.elevation = -25
            viewer.cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
