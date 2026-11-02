"""Pure sensor geometry for a proposed front ToF, not contact/step identity.
No MuJoCo/world-map import. Flat-supported approach is an EXPLICIT assumption.
A positive elevated-surface candidate may also be a slope/riser; no actuation.
"""
from dataclasses import dataclass
import math
import numpy as np


@dataclass(frozen=True)
class SupportView:
    sampled_s: float
    rotation_body_to_local: np.ndarray
    joint_q4: tuple
    assumed_flat_supported_approach: bool = False
    root_height_error_bound_m: float | None = None
    attitude_error_bound_rad: float | None = None


def infer_front(packet, support, geometry, now_s, max_age_s=.05, max_skew_s=.015):
    result = dict(kind='UNKNOWN', qualified_for_actuation=False, hardware_binding=False,
                  synthetic_fixture=True, reason='not_bound', sampled_s=None)
    if packet is None:
        result['reason'] = 'no_range'
        return result
    result['sampled_s'] = packet.sampled_s
    if not packet.valid or packet.range_m is None:
        result['reason'] = 'invalid_or_no_return'
        return result
    if not (math.isfinite(packet.range_m) and packet.range_m >= 0 and
            packet.sampled_s <= packet.arrival_s <= now_s and now_s - packet.sampled_s <= max_age_s):
        result['reason'] = 'range_time_or_value'
        return result
    if not math.isfinite(support.sampled_s) or abs(support.sampled_s - packet.sampled_s) > max_skew_s:
        result['reason'] = 'support_range_skew'
        return result
    if not support.assumed_flat_supported_approach:
        result['reason'] = 'approach_support_assumption_unbound'
        return result
    if support.root_height_error_bound_m is None or support.attitude_error_bound_rad is None:
        result['reason'] = 'geometry_error_budget_unbound'
        return result
    origin = np.asarray(packet.origin_B, float)
    direction = np.asarray(packet.direction_B, float)
    bounds = (packet.range_error_bound_m, support.root_height_error_bound_m, support.attitude_error_bound_rad)
    if origin.shape != (3,) or direction.shape != (3,) or not np.isfinite(origin).all() or not np.isfinite(direction).all() or abs(float(np.linalg.norm(direction)) - 1.) > 1e-5 or not all(math.isfinite(x) and x >= 0 for x in bounds):
        result['reason'] = 'mount_or_error_budget_invalid'
        return result
    rotation = np.asarray(support.rotation_body_to_local, float)
    q = np.asarray(support.joint_q4, float)
    if rotation.shape != (3, 3) or q.shape != (4,) or not np.isfinite(rotation).all() or not np.isfinite(q).all():
        result['reason'] = 'shape_or_finite'
        return result
    if np.max(np.abs(rotation.T @ rotation - np.eye(3))) > 1e-4 or np.linalg.det(rotation) < .999:
        result['reason'] = 'rotation_invalid'
        return result
    wheel_points = [geometry.wheel_kinematics(q[2*i], q[2*i+1], 0., 0., 0., np.zeros(3), i)[1] for i in range(2)]
    root_height = geometry.radius - min(float((rotation @ p)[2]) for p in wheel_points)
    local_point = rotation @ (np.asarray(packet.origin_B) + packet.range_m * np.asarray(packet.direction_B))
    heading = rotation[:, 0].copy()
    heading[2] = 0.
    norm = float(np.linalg.norm(heading))
    if norm < .5:
        result['reason'] = 'heading_degenerate'
        return result
    heading /= norm
    distance = float(heading @ local_point)
    height = root_height + float(local_point[2])
    bound = float(support.root_height_error_bound_m + packet.range_error_bound_m +
                  (np.linalg.norm(packet.origin_B) + packet.range_m) * support.attitude_error_bound_rad)
    if not math.isfinite(bound) or bound < 0:
        result['reason'] = 'invalid_error_bound'
        return result
    candidate = height - bound > .01 and height + bound < .30 and .1 < distance < .8
    result.update(kind='ELEVATED_SURFACE_CANDIDATE' if candidate else 'NO_QUALIFIED_CANDIDATE',
                  reason='conditional_geometry_only', height_est_m=height, height_error_bound_m=bound,
                  distance_from_chassis_forward_m=distance, root_height_est_m=root_height,
                  flat_support_assumption=True, step_identity=False, external_sensor_proposed=True)
    return result
